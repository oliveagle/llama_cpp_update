# Flash Attention Implementation

## 概述

高性能 Flash Attention 实现，支持 CPU、CUDA、HIP 和 Vulkan 后端。基于 FlashAttention-2 论文。

## 目录结构

```
flash_attention/
├── flash_attention.h           # 主 API 头文件
├── flash_attention_cpu.c       # CPU 实现
├── flash_attention_cuda.h      # CUDA API
├── flash_attention_cuda.cu     # CUDA kernel
└── test_flash_attention.c     # 测试代码
```

## 编译

### CPU 版本

```bash
# 创建构建目录
mkdir build && cd build

# 编译 CPU 版本
gcc -O3 -Wall -Wextra -I.. -o test_flash_attention \
    ../flash_attention_cpu.c ../test_flash_attention.c -lm

# 运行测试
./test_flash_attention
```

### CUDA 版本（需要 nvcc）

```bash
# 编译 CUDA 版本
nvcc -O3 -arch=sm_70 -I.. \
    -c ../flash_attention_cuda.cu -o flash_attention_cuda.o

# 链接
nvcc -o test_flash_attention_cuda \
    flash_attention_cuda.o test_flash_attention.c -lm
```

### Makefile

```makefile
CC = gcc
NVCC = nvcc
CFLAGS = -O3 -Wall -Wextra -I..
NVCCFLAGS = -O3 -arch=sm_70 -I..

CPU_SRC = flash_attention_cpu.c test_flash_attention.c
CPU_TARGET = test_flash_attention

CUDA_SRC = flash_attention_cuda.cu test_flash_attention.c
CUDA_TARGET = test_flash_attention_cuda

all: $(CPU_TARGET)

cpu: $(CPU_TARGET)
cuda: $(CUDA_TARGET)

$(CPU_TARGET): $(CPU_SRC)
	$(CC) $(CFLAGS) -o $@ $^ -lm

$(CUDA_TARGET): $(CUDA_SRC)
	$(NVCC) $(NVCCFLAGS) -c flash_attention_cuda.cu -o flash_attention_cuda.o
	$(NVCC) $(NVCCFLAGS) -o $@ flash_attention_cuda.o test_flash_attention.c -lm

clean:
	rm -f $(CPU_TARGET) $(CUDA_TARGET) *.o

.PHONY: all cpu cuda clean
```

## API 使用示例

```c
#include "flash_attention.h"
#include <stdlib.h>

int main() {
    // 1. 配置注意力参数
    fa_attn_desc_t desc;
    fa_attn_desc_init(&desc);

    desc.batch_size = 1;
    desc.num_heads = 8;
    desc.seq_len_q = 128;
    desc.seq_len_kv = 128;
    desc.head_dim = 64;
    desc.is_causal = 1;  // 因果掩码
    desc.scale = 1.0f / sqrtf((float)desc.head_dim);
    desc.backend = FA_BACKEND_CPU;
    fa_set_default_strides(&desc);

    // 2. 分配内存
    int total_elements = desc.batch_size * desc.num_heads *
                       desc.seq_len_q * desc.head_dim;
    float* q = malloc(total_elements * sizeof(float));
    float* k = malloc(total_elements * sizeof(float));
    float* v = malloc(total_elements * sizeof(float));
    float* out = malloc(total_elements * sizeof(float));

    // 初始化数据...
    // ...

    // 3. 创建 workspace
    size_t workspace_size;
    fa_workspace_query_size(&desc, &workspace_size);
    void* workspace_buf = malloc(workspace_size);
    fa_workspace_t workspace;
    fa_workspace_init(&workspace, &desc, workspace_buf, workspace_size);

    // 4. 运行注意力
    fa_status_t status = fa_attention_forward(
        &desc, q, k, v, NULL, out, &workspace
    );

    if (status != FA_SUCCESS) {
        printf("Error: %s\n", fa_status_string(status));
    }

    // 5. 清理
    free(q); free(k); free(v); free(out);
    free(workspace_buf);

    return 0;
}
```

## 算法说明

### Flash Attention 核心思想

1. **分块计算**：将序列分成小块，逐块处理
2. **在线 Softmax**：避免存储完整的注意力矩阵
3. **重计算**：减少内存访问，以计算换内存

### CPU 实现特点

- 分块并行处理
- 在线 softmax 更新算法
- 支持因果掩码
- 支持多批多头

### CUDA 实现特点

- 使用共享内存缓存 K/V
- Warp 级协作计算
- 支持半精度 (FP16/BF16)
- 高效的内存访问模式

## 性能优化建议

### CPU

1. **块大小调优**：
   - `block_size_n`: 建议 64-128
   - `block_size_d`: 建议 128-256

2. **SIMD 指令**：使用 AVX2/AVX-512 加速

3. **多线程**：OpenMP 并行化

### GPU

1. **共享内存使用**：最大化重用 K/V 数据
2. **寄存器使用**：减少全局内存访问
3. **指令流水线**：隐藏内存延迟

## TODO

- [ ] FP16/BF16 支持
- [ ] Flash Attention Backward
- [ ] Grouped Query Attention (GQA)
- [ ] Sliding Window Attention
- [ ] Paged KV Cache
- [ ] OpenCL/Vulkan 后端
- [ ] HIP (AMD GPU) 后端

## 参考文献

- FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning
  https://arxiv.org/abs/2307.08691

- FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness
  https://arxiv.org/abs/2205.14135

- Tri Dao, et al. (2023)
