# Flash Attention 技术文档

## 目录

1. [算法原理](#算法原理)
2. [Flash Attention 1 vs 2](#flash-attention-1-vs-2)
3. [实现细节](#实现细节)
4. [性能优化](#性能优化)
5. [数学推导](#数学推导)
6. [代码实现](#代码实现)

---

## 算法原理

### 标准注意力机制

给定 Query (Q)、Key (K)、Value (V)，标准的注意力计算为：

```
Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d)) @ V
```

其中：
- Q ∈ ℝ^(N × d) - 查询矩阵
- K ∈ ℝ^(M × d) - 键矩阵
- V ∈ ℝ^(M × d) - 值矩阵
- d - head dimension
- N - query 序列长度
- M - key/value 序列长度

**标准实现的内存复杂度**：
- 注意力矩阵: O(N × M)
- 临时存储: O(N × M)
- 总内存: O(NM + NM + Md) ≈ O(NM) (当 N, M >> d)

### Flash Attention 的核心思想

Flash Attention 通过以下技术降低内存访问：

1. **IO 感知的精确注意力**：将计算与内存访问合并
2. **分块计算 (Tiling)**：将序列分成小块，逐块处理
3. **在线 Softmax**：避免存储完整的注意力矩阵

---

## Flash Attention 1 vs 2

### Flash Attention 1

**特点**：
- 单个 warp 并行化
- 每次处理一个 (Q, K, V) tile
- 通过 online softmax 避免存储注意力矩阵

**缺点**：
- 内存访问模式不够优化
- 无法充分利用共享内存

### Flash Attention 2

**改进**：
1. **更好的并行化**：
   - 逐 head 并行化（而非逐 batch）
   - 多个 warp 协作处理单个 tile

2. **优化的分块**：
   - 更大的 tile 尺寸以减少迭代次数
   - 优化的共享内存使用

3. **循环展开和指令流水线**：
   - 减少分支
   - 隐藏内存延迟

**性能提升**：
- A100: ~2× Flash Attention 1 速度
- H100: ~3× Flash Attention 1 速度

---

## 实现细节

### 分块策略

```
Q [N × d]  K [M × d]  V [M × d]
  ↓ tiling    ↓ tiling    ↓ tiling

┌─────┐   ┌─────┐   ┌─────┐
│  Q  │   │  K  │   │  V  │
└─────┘   └─────┘   └─────┘

逐 block 处理：
for i in range(0, N, BLOCK_M):
    for j in range(0, M, BLOCK_N):
        Process(Q[i:i+BLOCK_M], K[j:j+BLOCK_N], V[j:j+BLOCK_N])
```

### 在线 Softmax

标准 softmax 需要两遍扫描：
1. 第一遍：找到 max
2. 第二遍：计算 exp 和 sum

**Online Softmax** 通过维护状态 `(m, l)` 实现单遍扫描：

```c
struct SoftmaxState {
    float m;  // 当前最大值
    float l;  // exp(x-m) 的和
};

// 合并两个 softmax 状态
SoftmaxState combine(SoftmaxState a, SoftmaxState b) {
    if (b.m > a.m) {
        return {b.m, b.l + a.l * exp(a.m - b.m)};
    } else {
        return {a.m, a.l + b.l * exp(b.m - a.m)};
    }
}

// 更新状态
SoftmaxState update(SoftmaxState s, float x) {
    if (x > s.m) {
        return {x, 1.0f + s.l * exp(s.m - x)};
    } else {
        return {s.m, s.l + exp(x - s.m)};
    }
}
```

### GPU 并行化策略

**Flash Attention 2 的并行层次**：

```
Grid (batch_size × num_heads × (N / BLOCK_M))
    │
    ├─ Block (处理一个 Q tile)
    │   │
    │   └─ Warp (协作处理)
    │       │
    │       └─ Thread (处理部分计算)
```

**CUDA Kernel 配置**：

```cuda
// Kernel launch
dim3 grid(batch_size * num_heads * (seq_len_q / BLOCK_M), 1, 1);
dim3 block(THREADS_PER_BLOCK, 1, 1);
flash_attention_2_forward<<<grid, block>>>(...);
```

---

## 性能优化

### 1. 共享内存使用

共享内存用于缓存 K 和 V tile，减少全局内存访问：

```cuda
__shared__ float shared_k[BLOCK_N * BLOCK_D];
__shared__ float shared_v[BLOCK_N * BLOCK_D];

// 协作加载
for (int j = j_start + tx; j < j_end; j += blockDim.x) {
    for (int d = 0; d < head_dim; d++) {
        shared_k[j * BLOCK_D + d] = k[j * head_dim + d];
    }
}
__syncthreads();  // 确保所有线程完成加载
```

### 2. Warp 级归约

使用 warp shuffle 指令进行高效归约：

```cuda
__device__ inline float warp_max(float x) {
    for (int offset = 16; offset > 0; offset >>= 1) {
        x = fmaxf(x, __shfl_xor_sync(0xffffffff, x, offset));
    }
    return x;
}
```

### 3. 寄存器分配

将频繁访问的数据保存在寄存器中：

```cuda
// Q row 缓存在寄存器
const float* q_row = q + i * head_dim;
float q_reg[head_dim];
for (int d = 0; d < head_dim; d++) {
    q_reg[d] = q_row[d];
}
```

### 4. 循环展开

减少循环开销，提高指令级并行：

```cuda
#pragma unroll
for (int offset = 16; offset > 0; offset >>= 1) {
    x = fmaxf(x, __shfl_xor_sync(mask, x, offset));
}
```

### 5. 流水线化

重叠计算和内存访问：

```
Tile 0: Load K0 → Compute Q0K0 → Load V0 → Compute (Q0K0)V0
Tile 1:    Load K1 → Compute Q0K1 → Load V1 → ...
```

---

## 数学推导

### 在线 Softmax 正确性证明

给定状态 `(m, l)`，其中：
- `m = max(x₁, x₂, ..., xₙ)`
- `l = Σ exp(xᵢ - m)`

考虑合并两个状态 `(m₁, l₁)` 和 `(m₂, l₂)`：

**情况 1**: `m₂ > m₁`

```
m = m₂
l = Σ exp(xᵢ - m)
  = Σ exp(xᵢ - m₂)
  = Σ_{xᵢ ∈ set2} exp(xᵢ - m₂) + Σ_{xᵢ ∈ set1} exp(xᵢ - m₂)
  = l₂ + Σ_{xᵢ ∈ set1} exp(xᵢ - m₁ + m₁ - m₂)
  = l₂ + l₁ × exp(m₁ - m₂)
```

**情况 2**: `m₁ ≥ m₂`

```
m = m₁
l = l₁ + l₂ × exp(m₂ - m₁)
```

因此，合并公式为：

```c
SoftmaxState combine(SoftmaxState a, SoftmaxState b) {
    if (b.m > a.m) {
        return {b.m, b.l + a.l * exp(a.m - b.m)};
    } else {
        return {a.m, a.l + b.l * exp(b.m - a.m)};
    }
}
```

### 输出更新公式

给定 softmax 状态 `(m, l)` 和值 `v`，输出为：

```
o = Σ (exp(score - m) / l) × v
```

当加入新的 `(score, v)` 对时：

```
new_m = max(m, score)
new_l = l × exp(m - new_m) + exp(score - new_m)

old_factor = exp(m - new_m)
new_factor = exp(score - new_m)

o_new = old_factor × o_old + new_factor × v
```

---

## 代码实现

### CPU 实现

**文件**: `flash_attention_cpu.c`

**核心函数**:

```c
static void fa_cpu_flash_forward_tiled(
    const float* q, const float* k, const float* v, float* output,
    float* l_cache, float* m_cache,  // Softmax 累积器
    float* o_tile, float* q_tile,
    float* k_tile, float* v_tile,     // 分块存储
    // ... 参数 ...
) {
    // 初始化累积器
    for (int i = 0; i < seq_len_q; i++) {
        m_cache[i] = -INFINITY;
        l_cache[i] = 0.0f;
    }

    // 分块处理 K, V
    for (int j_start = 0; j_start < seq_len_kv; j_start += block_size_n) {
        // 加载 K, V tile
        // ...

        // 处理 Q tile
        for (int i = start_i; i < end_i; i++) {
            // 计算 Q @ K^T
            // 在线更新 softmax
            // 更新输出
        }
    }

    // 归一化输出
    for (int i = 0; i < seq_len_q; i++) {
        for (int d = 0; d < head_dim; d++) {
            output[i * head_dim + d] /= l_cache[i];
        }
    }
}
```

### CUDA 实现

**文件**: `flash_attention_cuda_kernel.cu`

**核心 Kernel**:

```cuda
__global__ void flash_attention_2_forward(
    const float* __restrict__ q,
    const float* __restrict__ k,
    const float* __restrict__ v,
    float* __restrict__ output,
    int batch_size,
    int num_heads,
    int seq_len_q,
    int seq_len_kv,
    int head_dim,
    float scale,
    int is_causal
) {
    // 获取线程和 block 索引
    int bx = blockIdx.x;
    int by = blockIdx.y;
    int tx = threadIdx.x;

    // 初始化 softmax 状态
    SoftmaxState s = {-INFINITY, 0.0f};
    float acc[BLOCK_DMODEL] = {0.0f};

    // 加载 Q 行
    const float* q_row = q + ...;

    // 分块处理 K, V
    for (int j_start = 0; j_start < seq_len_kv; j_start += BLOCK_N) {
        // 加载 K, V 到共享内存
        // ...

        __syncthreads();

        // 计算注意力
        for (int j = j_start; j < j_end; j++) {
            float score = dot(q_row, shared_k[j]);
            s = softmax_update(s, score);

            float attn = exp(score - s.m);
            for (int d = 0; d < head_dim; d++) {
                acc[d] += attn * shared_v[j][d];
            }
        }

        __syncthreads();
    }

    // 写入输出
    float inv_l = 1.0f / s.l;
    for (int d = 0; d < head_dim; d++) {
        output[d] = acc[d] * inv_l;
    }
}
```

---

## 参考资料

1. **FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning**
   - Tri Dao, 2023
   - https://arxiv.org/abs/2307.08691

2. **FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness**
   - Tri Dao, et al., 2022
   - https://arxiv.org/abs/2205.14135

3. **Optimizing Transformer with Tiled MatMul**
   - NVIDIA GTC, 2023

4. **Efficient Attention: Attention with Linear Complexities**
   - Katharopoulos et al., 2020
