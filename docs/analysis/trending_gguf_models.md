# HuggingFace Trending GGUF 模型报告

> **生成时间**: 2026-02-17
> **数据来源**: 手动整理 + ModelScope
> **说明**: API 访问受限，以下为已知热门 GGUF 模型

---

## 已测试模型

| 模型 | 大小 | 量化 | 状态 | 预填充 | 生成 | 备注 |
|------|------|------|------|--------|------|------|
| JoyAI-LLM-Flash-Q4_K_M | 28GB | Q4_K_M | ✅ | 471 t/s (16K) | 38 t/s | V100满显存 |
| GLM-4.7-Flash-REAP-23B-A3B | 13GB | IQ4_NL | ✅ | 863 t/s (8K) | 32 t/s | MoE |
| MiniCPM-o-4_5-Q4_K_M | ~8GB | Q4_K_M | ✅ | - | - | 多模态 |
| Qwen3-4B-Instruct | ~3GB | Q4_K_M | ✅ | - | - | 小模型 |
| Qwen3-VL-8B | ~8GB | Q8_0 | ✅ | - | - | 视觉 |

---

## 推荐测试列表 (V100 32GB)

### 🔥 高优先级

#### Llama 系列
- [ ] `unsloth/Meta-Llama-3.1-8B-Instruct-GGUF` (8B, Q4_K_M)
- [ ] `unsloth/Meta-Llama-3.1-70B-Instruct-GGUF` (70B, Q4_K_M) - 需要测试能否加载
- [ ] `unsloth/Llama-3.2-3B-Instruct-GGUF` (3B, Q4_K_M)
- [ ] `unsloth/Llama-3.3-70B-Instruct-GGUF` (70B, Q4_K_M)

#### Qwen 系列
- [ ] `unsloth/Qwen3-8B-Instruct-GGUF` (8B, Q4_K_M)
- [ ] `unsloth/Qwen3-30B-A3B-Instruct-GGUF` (30B, Q4_K_M) - MoE
- [ ] `Qwen/Qwen3-VL-4B-Instruct-GGUF` (4B, Q8_0)
- [ ] `Qwen/Qwen3-VL-8B-Instruct-GGUF` (8B, Q8_0)

#### DeepSeek 系列
- [ ] `mlx-community/DeepSeek-V3.1-4bit` (48B MoE)
- [ ] `mlx-community/DeepSeek-V3.1-8bit` (48B MoE)

#### GLM 系列
- [ ] `unsloth/GLM-4.7-Flash-GGUF` (47B, Q4_K_M)
- [x] `unsloth/GLM-4.7-Flash-REAP-23B-A3B-GGUF` (23B MoE, IQ4_NL) ✅ 已测试

#### Mistral 系列
- [ ] `mistralai/Mistral-7B-Instruct-v0.3-GGUF` (7B)
- [ ] `mistralai/Mixtral-8x7B-Instruct-v0.1-GGUF` (8x7B MoE)

### ⭐ 中优先级

#### 代码模型
- [ ] `Qwen/Qwen3-Coder-480B-A35B-Instruct-GGUF` (480B MoE, Q4_K_M)
- [ ] `mlx-community/Qwen3-Coder-Next-4bit` (32B)

#### 长上下文
- [ ] `mlx-community/Kimi-K2.5` (64B)
- [ ] `mlx-community/Kimi-K2-Thinking` (64B)

#### 视觉模型
- [x] `OpenBMB/MiniCPM-o-4_5-gguf` (8B) ✅ 已测试
- [ ] `prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF`

### 🔬 低优先级 (超大模型)

- [ ] `mlx-community/GLM-4.5-Air-bf16` (218GB, 需要 BF16 支持)
- [ ] `mlx-community/Kimi-K2.5` (631GB)
- [ ] `mlx-community/MiniMax-M2.1-8bit` (231GB)

---

## 模型分类速查

### 按架构
| 架构 | 代表模型 | 特点 |
|------|---------|------|
| Llama | Meta-Llama-3.x | 生态完善，英文强 |
| Qwen | Qwen3 | 中文优秀，多模态 |
| DeepSeek | DeepSeek-V3 | MoE，推理强 |
| GLM | GLM-4.7 | 中文优秀，长上下文 |
| Mistral | Mistral/Mixtral | 欧洲开源，效率高 |

### 按大小 (V100 32GB 适配)
| 大小 | 可用量化 | 典型模型 |
|------|---------|---------|
| <4B | Q4_K_M, Q8_0 | Qwen3-0.6B, Qwen3-4B |
| 4B-8B | Q4_K_M, Q8_0 | Llama-3.1-8B, Qwen3-8B |
| 14B-20B | Q4_K_M, IQ4_XS | Qwen3-30B-A3B (MoE) |
| 28B-32B | Q4_K_M | JoyAI, GLM-4.7 |
| 70B | Q4_K_M (可能OOM) | Llama-3.3-70B |

---

## 下载命令模板

```bash
# ModelScope 下载
export HF_ENDPOINT=https://hf-mirror.com
modelscope download --model <model_id> --local_dir ./models/

# HuggingFace 下载
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download <model_id> --local-dir ./models/
```

---

## 测试记录

| 日期 | 模型 | 结果 | 备注 |
|------|------|------|------|
| 2026-02-17 | JoyAI-LLM-Flash | ✅ | ctx=16K, 38t/s |
| 2026-02-17 | GLM-4.7-Flash-REAP | ✅ | ctx=8K, 32t/s |
