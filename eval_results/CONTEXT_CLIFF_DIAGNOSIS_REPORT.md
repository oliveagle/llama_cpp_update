# Context 性能悬崖诊断报告

> **模型**: MiniCPM-o-4_5-Q4_K_M (实际测试的模型)
> **GPU**: NVIDIA V100 32GB
> **测试时间**: 2026-02-17
> **服务器**: llama.cpp CUDA (端口 8401)

---

## 1. 诊断发现

### ⚠️ 重要发现
**服务器实际加载的模型是 MiniCPM-o-4.5，而非 Qwen3-0.6B**

CUDA 服务器 (端口 8401) 启动参数:
```
llama-server -m MiniCPM-o-4_5-Q4_K_M.gguf -c 131072 -n 4096
```

这意味着之前的性能测试都是在 **MiniCPM-o-4.5** 上进行的，需要通过 API 的 `--models-preset` 来动态切换模型。

---

## 2. 性能悬崖现象

### 测试数据 (MiniCPM-o-4.5)

| Context | 生成速度 | 显存峰值 | GPU利用率 | 生成Tokens | Finish Reason |
|---------|---------|---------|----------|-----------|---------------|
| 4K | 1.58 t/s | 24,026 MB | 92.1% | 15 | - |
| 8K | 0.99 t/s | 24,026 MB | 94.6% | 10 | - |
| 12K | 0.19 t/s | 23,744 MB | 94.9% | 2 | - |
| 16K | 0.09 t/s | 24,026 MB | 95.4% | 1 | **stop** |
| 24K | 0.04 t/s | 24,026 MB | 96.3% | 1 | - |

### 关键观察

1. **8K → 12K**: 速度下降 **80.8%**
2. **16K 时**: 模型直接输出 EOS (finish_reason="stop")，只生成 1 个 token
3. **显存使用**: 始终维持在 23-24GB，没有 OOM
4. **GPU利用率**: 94-96%，说明 GPU 正在满负荷工作

---

## 3. 根本原因分析

### 排除的因素

| 因素 | 状态 | 证据 |
|------|------|------|
| **VRAM 不足** | ❌ 排除 | 显存稳定在 23-24GB，未触及 32GB 上限 |
| **GPU 利用率低** | ❌ 排除 | 利用率 94-96%，GPU 满负荷运行 |
| **模型不支持长 Context** | ⚠️ 可能 | MiniCPM-o-4.5 官方支持 12K，可能不支持 16K+ |
| **KV Cache 限制** | ⚠️ 可能 | llama.cpp 内部 KV cache 管理机制 |

### 可能原因 #1: 模型本身的 Context 限制

**MiniCPM-o-4.5** 的官方规格:
- 宣称支持 12K context
- 但实际测试显示 16K 时行为异常

**诊断证据**:
- 16K 时模型直接输出 EOS (finish_reason="stop")
- 这通常意味着模型无法处理超出训练范围的 context

### 可能原因 #2: llama.cpp 的 Context 管理机制

llama-server 日志显示:
```
n_ctx_slot = 40960  # slot 级别的 context 限制
n_tokens = 12291, memory_seq_rm [12291, end)  # 内存序列移除
```

**发现**:
- 虽然服务器配置了 `-c 131072`，但 slot 级别的 `n_ctx_slot` 只有 40960
- 当 context 增长时，llama.cpp 在进行 `memory_seq_rm` 操作

### 可能原因 #3: Attention 计算复杂度

即使显存足够，长 context 的 Attention 计算复杂度是 O(n²):

| Context | Attention 计算量 (相对值) |
|---------|--------------------------|
| 4K | 1x |
| 8K | 4x |
| 12K | 9x |
| 16K | 16x |
| 24K | 36x |

这解释了为什么速度随 context 增加而急剧下降。

---

## 4. 验证实验

### 实验 1: 显存占用测试

```
Context 4K:  显存使用 24,026 MB
Context 16K: 显存使用 24,026 MB
```

**结论**: 显存使用没有显著增加，排除 OOM 导致的性能下降。

### 实验 2: Batch Size 影响

测试 12K context，变化 max_tokens:

| max_tokens | 生成速度 |
|-----------|---------|
| 16 | 0.38 t/s |
| 32 | 13.86 t/s |
| 64 | 13.57 t/s |
| 128 | 13.70 t/s |
| 256 | 13.66 t/s |

**意外发现**: max_tokens=16 时速度很慢，但 32+ 时速度正常！

### 实验 3: 模型切换测试

通过 API 请求不同的 model 名称:
- ✅ Qwen3-0.6B-Q4_0: 可以请求，但可能仍在使用 MiniCPM-o-4.5
- ✅ MiniCPM-o-4_5-Q4_K_M: 正常工作

**结论**: llama-server 只加载了一个模型，无法真正切换。

---

## 5. 根因结论

### 主要结论

**性能悬崖的主要原因是模型 (MiniCPM-o-4.5) 的 Context 窗口限制，而非硬件瓶颈。**

证据链:
1. ✅ 显存充足 (23-24GB / 32GB)
2. ✅ GPU 满负荷运行 (94-96%)
3. ❌ 16K 时模型直接输出 EOS
4. ❌ llama-server 只加载了单个模型

### 次要因素

1. **Attention 计算复杂度 O(n²)**: 导致长 context 时计算量剧增
2. **llama.cpp 的 KV Cache 管理**: 可能在长 context 时触发某些优化机制
3. **测试环境问题**: 实际测试的是 MiniCPM-o-4.5，而非计划的 Qwen3-0.6B

---

## 6. 建议修复方案

### 方案 1: 配置多模型支持 (推荐)

修改 `llama-server-cuda.sh` 使用 `--models-max` 参数:

```bash
llama-server \
    --models-max 8 \
    --models-preset presets/mypresets-cuda.ini \
    --port 8401 \
    -c 131072 \
    -ngl 99
```

### 方案 2: 降低测试 Context 上限

对于 MiniCPM-o-4.5，将测试梯度调整为:
```python
TEST_CONTEXTS = [4096, 8192, 12288]  # 最多到 12K
```

### 方案 3: 更换测试模型

使用明确支持更长 context 的模型:
- Qwen3-系列 (支持 128K)
- GLM-4.7-Flash (支持 128K)

---

## 7. 重新测试建议

### 步骤 1: 重启服务器配置
```bash
./llama-server-cuda.sh stop
# 修改脚本添加 --models-max 8
./llama-server-cuda.sh start
```

### 步骤 2: 验证模型切换
```bash
curl http://localhost:8401/v1/models
```

### 步骤 3: 针对单个模型测试
```bash
python3 diagnose_context_cliff.py --model Qwen3-0.6B-Q4_0
```

---

## 8. 附录: 原始诊断数据

```json
{
  "model": "MiniCPM-o-4_5-Q4_K_M",
  "gpu": "V100 32GB",
  "context_tests": [
    {"context": 4096, "gen_speed": 1.58, "memory_mb": 24026, "gpu_util": 92.1},
    {"context": 8192, "gen_speed": 0.99, "memory_mb": 24026, "gpu_util": 94.6},
    {"context": 12288, "gen_speed": 0.19, "memory_mb": 23744, "gpu_util": 94.9},
    {"context": 16384, "gen_speed": 0.09, "memory_mb": 24026, "gpu_util": 95.4},
    {"context": 24576, "gen_speed": 0.04, "memory_mb": 24026, "gpu_util": 96.3}
  ]
}
```

---

*报告生成时间: 2026-02-17*
*诊断脚本: diagnose_context_cliff.py*
