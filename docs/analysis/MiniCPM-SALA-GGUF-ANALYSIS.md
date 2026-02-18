# MiniCPM-SALA GGUF 转换分析报告

> **模型**: OpenBMB/MiniCPM-SALA
> **发布时间**: 2026-02-11
> **分析时间**: 2026-02-18
> **状态**: llama.cpp 暂不支持

---

## 模型概述

MiniCPM-SALA (Sparse Attention and Linear Attention) 是首个有效整合稀疏注意力和线性注意力的大规模混合架构模型。

### 核心特性

| 特性 | 说明 |
|------|------|
| **架构** | 25% InfLLM-V2 (稀疏) + 75% Lightning Attention (线性) |
| **上下文** | 1M+ tokens (524288 训练长度) |
| **参数** | 8.9B |
| **位置编码** | HyPE (Hybrid Positional Embedding) |
| **推理加速** | 相比 Dense 基线 3.5× 速度提升 |

### 技术亮点

1. **SALA 混合注意力机制**
   - InfLLM-V2: 细粒度局部注意力，处理长上下文细节
   - Lightning Attention: 全局线性注意力，高效处理广泛上下文

2. **Transformer-to-Hybrid 持续训练**
   - 基于预训练权重架构转换
   - 训练预算减少至从头训练的 25%

3. **HALO 蒸馏方法**
   - Hybrid Attention via Layer Optimization
   - 将 Dense 注意力能力迁移到混合架构

---

## 不支持 llama.cpp 的原因

### 1. 缺少 Lightning Attention 实现

Lightning Attention 来自 [flash-linear-attention](https://github.com/fla-org/flash-linear-attention) 库，核心是 **GLA (Gated Linear Attention)** 机制。

```python
# MiniCPM-SALA 使用的算子
from fla.ops.simple_gla import chunk_simple_gla
from fla.ops.simple_gla.fused_recurrent import fused_recurrent_simple_gla
```

**llama.cpp 现状**: 无 GLA 或线性注意力实现。

### 2. 缺少 InfLLM v2 实现

InfLLM v2 是一种稀疏注意力机制，需要：
- Key 压缩 (CompressK)
- TopK 选择注意力
- 特殊的 KV Cache 管理 (InfLLMv2CacheLayer)

**llama.cpp 现状**: 无 InfLLM 支持。

### 3. 混合层架构

```json
"mixer_types": [
    "minicpm4",         // 标准注意力
    "lightning-attn",   // 线性注意力 (24层)
    ...
    "minicpm4",         // 标准注意力 (8层)
]
```

**llama.cpp 现状**: 不支持混合注意力层架构。

### 4. HyPE 位置编码

Hybrid Positional Embedding 需要特殊的 RoPE 扩展来协调不同注意力机制间的位置信息。

---

## 支持的推理框架

### 官方支持: SGLang (定制分支)

```bash
# 使用 SGLang 运行 (官方推荐)
git clone -b minicpm_sala https://github.com/OpenBMB/sglang.git
bash install_minicpm_sala.sh

python3 -m sglang.launch_server \
    --model /path/to/MiniCPM-SALA \
    --trust-remote-code \
    --attention-backend minicpm_flashinfer \
    --dense-as-sparse
```

**依赖组件**:
- `infllmv2_cuda_impl` - InfLLM v2 CUDA 内核
- `sparse_kernel` - 稀疏注意力内核
- `flash-linear-attention` - 线性注意力算子
- `tilelang` - Tile 优化编译器

### HuggingFace Transformers (支持)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "openbmb/MiniCPM-SALA",
    trust_remote_code=True,
    device_map="auto"
)
```

**缺点**: 无加速优化，长上下文推理慢。

---

## 实现方案 (供 llama.cpp 社区参考)

### 方案 1: 完整实现 (推荐)

需要添加以下组件：

#### A. Lightning Attention 算子
```cpp
// src/llama-lightning-attn.cpp
// 参考: flash-linear-attention/ops/simple_gla

struct llama_lightning_attn {
    // Gated Linear Attention 核心计算
    // chunk_simple_gla 等效实现
};
```

#### B. InfLLM v2 算子
```cpp
// src/llama-infllm.cpp
// 参考: infllm_v2 实现

struct llama_infllm_cache {
    // Key 压缩
    // TopK 稀疏选择
    // 分层缓存管理
};
```

#### C. 混合层调度
```cpp
// src/llama-layer.cpp

enum llama_attn_type {
    LLAMA_ATTN_TYPE_DENSE,      // minicpm4
    LLAMA_ATTN_TYPE_LIGHTNING,  // lightning-attn
    LLAMA_ATTN_TYPE_INFLLM,     // infllm-v2
};
```

#### D. HyPE 位置编码
```cpp
// src/llama-rope.cpp

void llama_rope_hybrid(...);  // 扩展 RoPE 支持混合架构
```

#### E. GGUF 格式扩展
```python
# gguf-py/gguf/constants.py

class MODEL_ARCH(IntEnum):
    ...
    MINICPM_SALA = auto()  # 新增架构类型
```

### 方案 2: 近似实现 (快速支持)

将混合架构近似为标准 Transformer：

1. **Lightning Attention 层** → 近似为带衰减因子的标准 Attention
2. **InfLLM 层** → 近似为 Window Attention + Sink Tokens

**缺点**: 性能和精度损失，失去长上下文优势。

### 方案 3: 社区等待 (当前状态)

等待 OpenBMB 或社区贡献官方支持。

---

## 技术挑战

| 挑战 | 难度 | 说明 |
|------|------|------|
| CUDA 内核优化 | 高 | Lightning Attention 和 InfLLM 都需要高性能 CUDA 实现 |
| KV Cache 管理 | 高 | 混合架构需要特殊的缓存策略 |
| 精度保持 | 中 | HyPE 和混合注意力的精度要求 |
| 内存优化 | 高 | 1M 上下文需要极致的内存管理 |
| GGUF 格式 | 低 | 需要扩展格式支持新架构 |

---

## 参考资源

### 论文/报告
- [MiniCPM-SALA Technical Report](https://github.com/OpenBMB/MiniCPM/blob/main/docs/MiniCPM_SALA.pdf)
- [HyPE: Hybrid Positional Embedding](https://arxiv.org/abs/2601.22156)
- [InfLLM-V2](https://arxiv.org/abs/2509.24663)

### 代码库
- [flash-linear-attention](https://github.com/fla-org/flash-linear-attention)
- [SGLang MiniCPM-SALA 分支](https://github.com/OpenBMB/sglang/tree/minicpm_sala)
- [MiniCPM-SALA Model](https://huggingface.co/openbmb/MiniCPM-SALA)

### 相关讨论
- llama.cpp Issues: 暂无 MiniCPM-SALA 相关讨论
- OpenBMB Discord: 官方讨论渠道

---

## 建议

### 对于用户

当前方案:
1. **使用 SGLang** (官方推荐，完整支持)
2. **使用 HF Transformers** (简单但不快)
3. **等待 llama.cpp 支持** (时间不确定)

### 对于开发者

如果要为 llama.cpp 添加支持，建议步骤:

1. **先实现 Lightning Attention** (通用组件，可被其他模型复用)
2. **再实现 InfLLM v2** (长上下文核心)
3. **最后整合 MiniCPM-SALA** (混合调度)

---

## 结论

MiniCPM-SALA 是一个创新的长上下文模型，但其混合架构需要大量的工程工作才能在 llama.cpp 中支持。目前官方只支持 SGLang，llama.cpp 社区尚未有相关计划。

**预计工作量**: 3-6 个月 (全职开发者)
**优先级**: 取决于社区对 1M 上下文的需求

---

*报告生成: 2026-02-18*
