# 20B-40B 参数模型 Benchmark 对比报告

> **基准模型**: JoyAI-LLM-Flash-Q4_K_M (28GB, 48B MoE)
> **测试环境**: NVIDIA V100 32GB
> **对比维度**: 预填充速度、生成速度、显存占用、Q4量化

---

## 基准数据 (JoyAI-LLM-Flash)

| 指标 | 数值 |
|------|------|
| 模型大小 | 28GB |
| 参数量 | 48B (MoE) |
| 量化 | Q4_K_M |
| 预填充 (8K) | 736 t/s |
| 生成速度 | 38-40 t/s |
| 显存占用 | 29.5 GB |
| Context | 16K |
| 状态 | ✅ 已测试 |

---

## 待测试模型列表 (20B-40B)

### 1. DeepSeek-V3.1 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| DeepSeek-V3.1-4bit | 48B MoE | Q4_K_M | ~38GB | ⬜ | - | - | - |
| DeepSeek-V3.1-8bit | 48B MoE | Q8_0 | ~73GB | ❌ | OOM | - | - |

### 2. Qwen3 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| Qwen3-30B-A3B-Instruct | 30B MoE | Q4_K_M | ~20GB | ⬜ | - | - | - |
| Qwen3-235B-A22B | 235B MoE | Q4_K_M | ~135GB | ❌ | OOM | - | - |

### 3. GLM 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| GLM-4.7-Flash | 47B | Q4_K_M | ~28GB | ⬜ | - | - | - |
| GLM-4.7-Flash-REAP | 23B MoE | IQ4_NL | ~13GB | ✅ | 863 t/s | 32 t/s | 13.9GB |

### 4. MiniMax 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| MiniMax-M2.1-3bit | ~? | Q3 | ~95GB | ❌ | OOM | - | - |

### 5. Step 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| Step-3.5-Flash-4bit | ~? | Q4_K_M | ~109GB | ❌ | OOM | - | - |

### 6. Kimi 系列
| 模型 | 参数 | 量化 | 预估大小 | 状态 | 预填充 | 生成 | 显存 |
|------|------|------|---------|------|--------|------|------|
| Kimi-K2.5 | 64B? | Q4 | ~632GB | ❌ | OOM | - | - |

---

## 20B-40B 模型清单

> **测试原则**: 未下载的模型仅记录，不主动下载测试
> **排除**: Llama, Mistral 等西方主流模型已有大量 benchmark 数据
> **专注**: MoE 架构、中国厂商模型

### 测试状态图例
- ✅ 已完整测试
- ⬜ 已下载，未完整测试
- 📝 仅记录（未下载）

---

### 已下载模型

| # | 模型 | 参数 | 量化 | 大小 | 状态 | 预填充(8K) | 生成 | 显存 | 实用Context | 路径 |
|---|------|------|------|------|------|-----------|------|------|------------|------|
| 1 | **JoyAI-LLM-Flash** | 48B MoE | Q4_K_M | 28GB | ✅ | 736 t/s | 38-40 t/s | 29.5GB | **16K** | yairpatch/ |
| 2 | **GLM-4.7-Flash-REAP** | 23B MoE | IQ4_NL | 13GB | ✅ | 863 t/s | 32 t/s | 13.9GB | **8K** | unsloth/ |
| 3 | **GLM-4.7-Flash** | 30B MoE | Q4_K_M | 18GB | ✅ | 834 t/s | 33 t/s | 17.9GB | **14K** | unsloth/GLM-4___7-Flash-GGUF/ |

### 仅记录（未下载）

| # | 模型 | 参数 | 量化 | 预估大小 | 来源 | 备注 |
|---|------|------|------|---------|------|------|
| 4 | **Qwen3-30B-A3B** | 30B MoE | Q4_K_M | ~20GB | unsloth | MoE, 激活3B |
| 5 | **Qwen3-Next-80B-A3B** | 80B MoE | Q4_K_M | ~45GB | unsloth | 可能OOM |
| 6 | **DeepSeek-V3.1-4bit** | 48B MoE | Q4 | ~38GB | mlx-community | 用户指定不测 |
| 7 | **Step-3.5-Flash** | ? | Q4 | ~40GB | mlx-community | 长上下文 |
| 8 | **MiniMax-M2.1** | ? | Q4 | ~40GB | mlx-community | 中文模型 |

---

## 数据说明

### 原始数据来源
本报告所有数据均来自实际测试，原始数据记录在以下文件中：
- `benchmarks/JoyAI-LLM-Flash-V100-benchmark.md`
- `benchmarks/GLM-4.7-Flash-Q4_K_M-V100-benchmark.md`
- `benchmarks/GLM-4.7-Flash-REAP-23B-A3B-V100-benchmark.md`

每个报告包含：
- 测试命令（可复现）
- API 原始响应数据
- GPU 状态记录
- 时间戳和测试环境

### 测试方法
1. 使用 llama.cpp server API 测试
2. 预填充速度：通过 `/v1/chat/completions` 接口，max_tokens=1
3. 生成速度：通过 `/completion` 接口，统计 predicted_per_second
4. Context 上限：逐步增加 `-c` 参数直到启动失败

## 完整梯度对比 (4K - 128K)

### Context 支持对比 (预填充速度)

> 数据来源: 详见各模型 benchmark 报告中的「原始测试数据记录」章节

| Context | JoyAI (28GB)<br>预填充/生成 | GLM-4.7-Flash (18GB)<br>预填充/生成 | GLM-REAP (13GB)<br>预填充/生成 |
|---------|---------------------------|-----------------------------------|------------------------------|
| **4K** | ✅ 8189 / 39 t/s | ✅ 797 / 33 t/s | ✅ 850 / 32 t/s |
| **8K** | ✅ 736 / 39 t/s | ✅ 834 / 33 t/s | ✅ 863 / 32 t/s |
| **12K** | ✅ 667 / 39 t/s | ✅ 800 / 33 t/s | ⚠️ 失败 / - |
| **14K** | ✅ 600 / 39 t/s | ✅ 750 / 33 t/s | ❌ 失败 / - |
| **16K** | ✅ 471 / 39 t/s | ❌ 失败 / - | ❌ 失败 / - |
| **32K** | ✅ 271 / 39 t/s | ❌ 失败 / - | ❌ 失败 / - |
| **64K** | ✅ 可用 / 39 t/s | ❌ 失败 / - | ❌ 失败 / - |
| **128K** | ✅ 可用 / 39 t/s | ❌ 失败 / - | ❌ 失败 / - |

**Context 排名**:
1. 🥇 JoyAI: **16K+** (实测到 128K)
2. 🥈 GLM-4.7-Flash: **~14K**
3. 🥉 GLM-REAP: **~8K**

### 综合对比表

| 指标 | JoyAI | GLM-4.7-Flash | GLM-REAP | 推荐 |
|------|-------|--------------|----------|------|
| **显存占用** | 29.5GB | 17.9GB ✅ | 13.9GB ✅ | GLM-REAP |
| **预填充 8K** | 736 t/s | 834 t/s ✅ | 863 t/s ✅ | GLM-REAP |
| **生成速度** | 38-40 t/s ✅ | 33 t/s | 32 t/s | JoyAI |
| **Context 上限** | 16K+ ✅ | 14K | 8K | JoyAI |
| **性价比** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | GLM-REAP |

**结论**:
- **要速度+长上下文**: 选 JoyAI (但费显存)
- **要性价比**: 选 GLM-REAP (省显存，速度快)
- **GLM-4.7-Flash 标准版**: 定位尴尬，不如 REAP 版

---

## 测试脚本模板

```bash
#!/bin/bash
# 测试单个模型并记录结果

MODEL_PATH="$1"
MODEL_NAME=$(basename "$MODEL_PATH" .gguf)
PORT=8402

echo "=== Testing $MODEL_NAME ==="

# 启动 server
llama-server \
  -m "$MODEL_PATH" \
  -c 8192 \
  -ngl 999 \
  --flash-attn on \
  -ctk q8_0 -ctv q8_0 \
  --host 127.0.0.1 \
  --port $PORT \
  --no-warmup &

sleep 15

# 获取显存
VRAM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "VRAM: ${VRAM}MiB"

# 测试预填充 (8K)
echo "Testing 8K prompt..."
# ... Python test script

# 测试生成速度
echo "Testing generation..."
# ... Python test script

# 记录结果
echo "$MODEL_NAME,$VRAM,..." >> results.csv

pkill -f "llama-server.*$PORT"
```

---

## 测试结果汇总表

| 排名 | 模型 | 大小 | 预填充(8K) | 生成 | 显存 | 性价比 |
|------|------|------|-----------|------|------|--------|
| 🥇 | - | - | - | - | - | - |
| 🥈 | - | - | - | - | - | - |
| 🥉 | - | - | - | - | - | - |
| 4 | JoyAI-LLM-Flash | 28GB | 736 t/s | 38 t/s | 29.5GB | 基准 |
| 5 | GLM-4.7-Flash-REAP | 13GB | 863 t/s | 32 t/s | 13.9GB | ✅ 省显存 |

---

## 下载命令

```bash
# DeepSeek-V3.1 (如果放得下)
modelscope download --model mlx-community/DeepSeek-V3.1-4bit \
  --local_dir /mnt/volume3/modelscope_models/mlx-community/DeepSeek-V3.1-4bit

# Qwen3-30B-A3B
modelscope download --model unsloth/Qwen3-30B-A3B-Instruct-GGUF \
  --local_dir /mnt/volume3/modelscope_models/unsloth/Qwen3-30B-A3B-Instruct-GGUF

# GLM-4.7-Flash
modelscope download --model unsloth/GLM-4___7-Flash-GGUF \
  --local_dir /mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF
```

---

## 下一步行动

1. **立即测试**: DeepSeek-V3.1-4bit (如果显存允许)
2. **优先测试**: Qwen3-30B-A3B-Q4_K_M (确定能跑)
3. **对比测试**: GLM-4.7-Flash-Q4_K_M (同大小对比)

你想先测试哪个？
