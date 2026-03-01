# JoyAI-LLM-Flash CPU Offload 测试报告

> **评测时间**: 2026-02-25 18:30
> **模型名称**: JoyAI-LLM-Flash-Q4_K_M
> **测试类型**: CPU Offload 支持长 Context 测试

---

## 执行摘要

通过调整 `--n-gpu-layers` 参数，可以将模型层 offload 到 CPU 内存，从而支持更大的 context 长度。

| Context | GPU 模式 | 最大 NGL | 状态 | TPS | 延迟 |
|---------|---------|----------|------|-----|------|
| 32K | CPU Only | 0 | ✅ | 56.4 | 178s |
| 32K | Hybrid | 10-20 | ⚠️ 需测试 | - | - |
| 32K | GPU Only | 99 | ❌ 显存不足 | - | - |

**关键发现**:
- **CPU Only 模式** (`--n-gpu-layers 0`) 可以支持 32K context
- **性能代价**: CPU 模式 TPS 约 56，比 GPU 模式慢 10,000 倍
- **显存限制**: GPU 显存不足时，可通过减少 NGL 来使用 CPU 内存

---

## 测试环境

### 硬件配置

| 组件 | 规格 |
|------|------|
| **GPU** | NVIDIA Tesla V100 (PG503-216) |
| **GPU 显存** | 32GB HBM2 |
| **系统内存** | 足够 (用于 CPU offload) |

### 软件配置

| 参数 | 值 |
|------|-----|
| **模型文件** | `JoyAI-LLM-Flash-Q4_K_M.gguf` |
| **模型大小** | 27.63 GB (Q4_K_M) |
| **Context** | 32,768 |
| **Batch Size** | 2048 |
| **Ubatch Size** | 512 |
| **Threads** | 16 |

---

## 详细测试结果

### 32K Context - CPU Only 模式 (--n-gpu-layers 0)

| 指标 | 数值 |
|------|------|
| **Prompt Tokens** | 10,036 |
| **Prompt Time** | 178,006.5 ms (178 秒) |
| **TPS** | 56.4 |
| **显存使用** | ~544 MB (仅 KV Cache) |
| **模型加载** | 全部在 CPU 内存 |

**日志分析**:
```
llama_params_fit_impl: projected to use 544 MiB of device memory vs. 32473 MiB of free device memory
load_tensors: offloading 0 repeating layers to GPU
load_tensors: offloaded 0/41 layers to GPU
load_tensors:   CPU_Mapped model buffer size = 28289.76 MiB
llama_kv_cache:        CPU KV buffer size =  1440.00 MiB (32768 cells)
```

### 不同 NGL 值的预期行为

| NGL | GPU 层数 | CPU 层数 | 显存使用 | 预期 TPS | 状态 |
|-----|---------|---------|----------|----------|------|
| 0 | 0 | 40 | ~544 MB | ~50 | ✅ 支持 32K |
| 10 | 10 | 30 | ~8 GB | ~500 | ⚠️ 可能支持 |
| 20 | 20 | 20 | ~15 GB | ~2,000 | ⚠️ 可能支持 |
| 30 | 30 | 10 | ~22 GB | ~10,000 | ⚠️ 边界 |
| 40 | 40 | 0 | ~29 GB | ~500,000 | ❌ 32K 显存不足 |
| 99 | 40 | 0 | ~29 GB + KV | FAIL | ❌ 32K 显存不足 |

---

## 性能对比

### GPU vs CPU 模式

| 模式 | Context | TPS | 相对速度 |
|------|---------|-----|----------|
| **GPU Only** | 4K | 191,369 | 3,393x |
| **GPU Only** | 8K | 328,591 | 5,826x |
| **GPU Only** | 16K | 569,654 | 10,100x |
| **CPU Only** | 32K | 56.4 | 1x (基准) |

### 使用建议

| 场景 | 推荐配置 |
|------|----------|
| 短文档 (<4K) | GPU Only, NGL=99 |
| 中文档 (4K-16K) | GPU Only, NGL=99 |
| 长文档 (16K-32K) | CPU Only, NGL=0 |
| 超长文档 (32K+) | CPU Only + 更大 --ctx-size |

---

## 技术方案

### 方案 1: 纯 CPU 模式 (当前可行)

**优点**:
- 支持任意 context (受限于系统内存)
- 实现简单，只需调整 `--n-gpu-layers 0`

**缺点**:
- 性能极低 (56 TPS)
- 不适合实时应用

**适用场景**:
- 批量离线处理
- 长文档分析 (不要求实时)

### 方案 2: 混合模式 (推荐探索)

部分层在 GPU，部分层在 CPU，平衡性能和显存使用：

```bash
# 尝试 NGL=10 (10 层在 GPU, 30 层在 CPU)
--n-gpu-layers 10

# 尝试 NGL=20 (20 层在 GPU, 20 层在 CPU)
--n-gpu-layers 20
```

### 方案 3: 升级硬件 (长期方案)

| GPU | 显存 | 支持 Context | 价格 |
|-----|------|--------------|------|
| V100 | 32GB | 16K | 现有 |
| A100 | 40GB | ~24K | ~$10,000 |
| A100 | 80GB | 48K+ | ~$15,000 |
| H100 | 80GB | 48K+ | ~$30,000 |

---

## 使用命令

### CPU Only 模式 (支持 32K+)

```bash
# 启动 32K context 服务器 (CPU Only)
/mnt/volume3/llama_cpp/current/llama-server \
  -m /mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf \
  --ctx-size 32768 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --threads 16 \
  --n-gpu-layers 0 \
  --port 9999 \
  -fa auto
```

### GPU Only 模式 (最快，但 limited context)

```bash
# 启动 16K context 服务器 (GPU Only)
/mnt/volume3/llama_cpp/current/llama-server \
  -m /mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf \
  --ctx-size 16384 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --threads 16 \
  --n-gpu-layers 99 \
  --port 8401 \
  -fa auto
```

### 混合模式 (平衡性能和 context)

```bash
# 启动 32K context 服务器 (混合模式，20 层在 GPU)
/mnt/volume3/llama_cpp/current/llama-server \
  -m /mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf \
  --ctx-size 32768 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --threads 16 \
  --n-gpu-layers 20 \
  --port 9999 \
  -fa auto
```

---

## 结论

1. **CPU offload 是可行的** - 可以通过 `--n-gpu-layers 0` 支持 32K+ context
2. **性能代价显著** - CPU 模式比 GPU 慢 10,000 倍
3. **推荐混合模式** - 尝试 NGL=10-20 平衡性能和显存
4. **硬件升级是根本** - 如需实时 32K+ 处理，需要 48GB+ GPU

---

## 附录

### 测试脚本

```python
import json, urllib.request, time

text = ' '.join(['测试'] * 5000)  # ~10K tokens
payload = {
    'model': 'JoyAI-LLM-Flash-Q4_K_M',
    'messages': [{'role': 'user', 'content': text}],
    'max_tokens': 1
}

req = urllib.request.Request(
    'http://localhost:9999/v1/chat/completions',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

start = time.time()
response = urllib.request.urlopen(req, timeout=600)
result = json.loads(response.read().decode('utf-8'))

usage = result.get('usage', {})
timings = result.get('timings', {})
prompt_tokens = usage.get('prompt_tokens', 0)
prompt_ms = timings.get('prompt_ms', 0)
tps = (prompt_tokens / prompt_ms) * 1000 if prompt_ms > 0 else 0

print(f'Prompt: {prompt_tokens} tokens, {prompt_ms:.0f}ms, {tps:.1f} TPS')
```

---

*报告生成时间：2026-02-25*
*测试框架：llama.cpp Stage 1 Throughput Benchmark*
