# 机器模型性能排行榜

> **机器**: CF500-B5F1 (NVIDIA Tesla V100 32GB)
> **最后更新**: 2026-02-25
> **数据源**: Stage 1/2/3 吞吐量测试 + 综合能力评估 + Context 测试

---

## 🏆 综合性能排行榜 (V100 CUDA)

### 生成速度排名 (8K Context)

| 排名 | 模型 | 量化 | 生成 TPS | 预填充 TPS | 显存 |
|------|------|------|---------|-----------|------|
| 🥇 1 | **Qwen3.5-35B-A3B-UD** | Q4_K_XL | **69.0** | 692 | ~19GB |
| 🥈 2 | Qwen3-VL-8B-abliterated | Q8_0 | **39.1** | 4,113 | ~8GB |
| 🥉 3 | Qwen3VL-4B-Instruct | Q8_0 | **38.1** | 4,008 | ~4GB |
| 4 | GLM-4.7-Flash | Q4_K_M | **37.5** | 3,931 | ~5GB |
| 5 | JoyAI-LLM-Flash | Q4_K_M | **37.5** | 3,864 | ~28GB |
| 5 | Apsara-4B | Q8_0 | **23.2** | 19,570 | ~4GB |
| 6 | Qwen3-0.6B | Q4_0 | **10.5** | 652 | ~1GB |
| 7 | Qwen3-4B-Instruct-2507 | Q4_K_XL | **6.1** | 637 | ~3GB |
| 8 | MiniCPM-o-4_5 | Q4_K_M | **6.1** | 645 | ~5GB |

---

## 📏 Context 长度支持排名

| 排名 | 模型 | 最大 Context | 状态 | 备注 |
|------|------|-------------|------|------|
| 🥇 1 | **Qwen3.5-35B-A3B-UD** | **256K** | ✅ | 原生支持 |
| 🥈 2 | GLM-4.7-Flash-REAP | **202K** | ✅ | 原生支持 |
| 🥉 3 | MiniCPM-o-4_5 | **128K** | ✅ | RoPE 缩放 (3.2x) |
| 🥉 3 | Qwen3-0.6B | **128K** | ✅ | RoPE 缩放 |
| 5 | JoyAI-LLM-Flash | **32K** | ✅ | 显存限制 |
| 6 | Qwen3-VL-8B | **24K** | ✅ | 实测上限 |
| 7 | Qwen3VL-4B | **24K** | ✅ | 实测上限 |
| 8 | Qwen3-4B-Instruct | **24K** | ✅ | 实测上限 |
| 9 | Apsara-4B | **24K** | ✅ | 实测上限 |

---

## 🎯 Linux 工具调用能力排名 (Stage 2)

| 排名 | 模型 | 测试数 | 通过 | 准确率 |
|------|------|--------|------|--------|
| 🥇 1 | **JoyAI-LLM-Flash** | 30 | 26 | **86.7%** |
| 🥈 2 | **GLM-4.7-Flash** | 30 | 25 | **83.3%** |
| 🥈 3 | **Qwen3-VL-8B-abliterated** | 30 | 25 | **83.3%** |
| 4 | **Qwen3VL-4B-Instruct** | 30 | 23 | **76.7%** |
| 5 | **Qwen3-4B-Instruct-2507** | 30 | 23 | **76.7%** |
| 6 | **MiniCPM-o-4_5** | 30 | 0 | **0.0%** ⚠️ |

---

## 🧠 综合能力评估排名

### JoyAI-LLM-Flash-Q4_K_M 详细能力 (100% 准确率)

| 能力维度 | 测试数 | 通过数 | 准确率 | 平均 TPS |
|----------|--------|--------|--------|----------|
| 数学推理 | 5 | 5 | 100% | 22.4 |
| 逻辑推理 | 3 | 3 | 100% | 23.6 |
| 代码能力 | 3 | 3 | 100% | 21.0 |
| 中文理解 | 3 | 3 | 100% | 22.7 |
| 知识问答 | 3 | 3 | 100% | 23.2 |
| 多轮对话 | 2 | 2 | 100% | 24.5 |
| **总计** | **19** | **19** | **100%** | **22.6** |

---

## 📊 32K Context 黄金标准验证

用户指定 **32K 作为配置黄金点位**：

| 模型 | 大小 | 32K 支持 | 推荐场景 |
|------|------|----------|----------|
| MiniCPM-o-4.5 | 4.7GB | ✅ 完美支持 | 多模态理解、长文档分析 |
| GLM-4.7-Flash-REAP | 13GB | ✅ 完美支持 | 长 context 推理、MoE 架构 |
| JoyAI-LLM-Flash | 28GB | ✅ 支持 (上限) | 大模型推理、中文对话 |
| Qwen3-VL-8B | 8GB | ✅ 支持 | 多模态分析 |
| Qwen3VL-4B | 4GB | ✅ 支持 | 视觉问答 |
| Qwen3-4B-Instruct | 3GB | ✅ 支持 | 通用对话 |

---

## 🔥 显存占用分析

### 128K Context 显存需求

| 模型 | 模型大小 | KV Cache (128K) | 总计 | V100 32GB |
|------|----------|-----------------|------|-----------|
| MiniCPM-o-4.5 | ~5GB | ~7GB | ~12GB | ✅ 可行 |
| Qwen3-0.6B | ~1GB | ~7GB | ~8GB | ✅ 可行 |
| GLM-4.7-Flash-REAP | ~13GB | ~7GB | ~20GB | ✅ 可行 |
| Qwen3-VL-8B | ~8GB | ~7GB | ~15GB | ✅ 可行 |
| JoyAI-LLM-Flash | ~28GB | ~6GB | ~34GB | ❌ OOM |

---

## 📋 完整模型清单 (14 个)

| 模型名称 | 量化 | 大小 | 生成 TPS | 最大 Context | 推荐用途 |
|----------|------|------|---------|-------------|----------|
| **Qwen3.5-35B-A3B-UD** | Q4_K_XL | 19GB | **69.0** | **256K** | 快速推理、长文档 |
| JoyAI-LLM-Flash | Q4_K_M | 28GB | 37.5 | 32K | 中文对话、逻辑推理 |
| GLM-4.7-Flash | Q4_K_M | 5GB | 37.5 | 32K | 通用任务、工具调用 |
| GLM-4.7-Flash-REAP | IQ4_NL | 13GB | - | 202K | 超长 context 任务 |
| Qwen3-VL-8B-abliterated | Q8_0 | 8GB | 39.1 | 24K | 多模态分析 |
| Qwen3VL-4B-Instruct | Q8_0 | 4GB | 38.1 | 24K | 视觉问答 |
| Qwen3-4B-Instruct-2507 | Q4_K_XL | 3GB | 6.1 | 24K | 通用对话 |
| Qwen3-0.6B | Q4_0 | 1GB | 10.5 | 128K | 快速原型、测试 |
| MiniCPM-o-4_5 | Q4_K_M | 5GB | 6.1 | 128K | 多模态长文档 |
| Apsara-4B | Q8_0 | 4GB | 23.2 | 24K | 快速推理 |
| MiroThinker-v1.5-30B | Q8_0 | 31GB | - | 8K | ❌ 显存不足 |
| Qwen3-Coder-Next | Q4_K_M | - | - | 8K | 代码生成 |
| Youtu-VL-4B-Instruct | Q8_0 | - | - | 8K | 视觉问答 |
| Nanbeige4.1-3B | Q8_0 | - | - | 8K | 中文对话 |
| LLaDA2.0-mini-preview | Q4_0 | - | - | 8K | 生成任务 |
| Step3-VL-10B | Q4_K_M | - | - | 8K | 多模态 |

---

## 📁 历史报告索引

### Stage 1 - 性能测试
- `V100_ALL_MODELS_PERFORMANCE_REPORT.md` - 全模型性能基准
- `V100_CUDA_FIRST_TIER_REPORT.md` - 第一层基础测试
- `V100_CUDA_SECOND_TIER_REPORT.md` - 第二层测试
- `joyai_flash_context_gradient_report.md` - JoyAI Context 梯度测试

### Stage 2 - 基础能力
- `V100_STAGE2_32K_20260217_234034.md` - 32K Context 测试
- `*_linux_basic_eval.md` - Linux 工具调用测试 (各模型)

### Stage 3 - 深度能力
- `STAGE3_FINAL_REPORT.md` - Stage 3 最终报告

### Context 专项测试
- `ALL_GGUF_MODELS_CONTEXT_TEST_REPORT.md` - 全模型 Context 测试
- `MULTI_MODEL_128K_ROPE_SUCCESS.md` - 128K RoPE 缩放成功报告
- `QWEN3_0.6B_128K_ROPE_SUCCESS.md` - Qwen3-0.6B 128K 测试

---

## 📝 测试日志

### 2026-02-25
- Qwen3.5-35B-A3B-UD Stage 1 测试完成 ✅
  - Vulkan (gfx1151): 生成速度 69 tokens/s，预填充 692 tokens/s (8K)
  - 原生支持 256K context，文件大小 19GB
- JoyAI-LLM-Flash Stage 1 测试完成
  - CUDA (V100): 最大 16K (GPU 模式), 569K TPS (热启动)
  - CPU Offload: 支持 32K+, 56 TPS
- JoyAI-LLM-Flash 32K Context 验证成功 ✅
  - Vulkan (Tesla V100): 32K context, 96.8 tokens/s 预填充，24.5 tokens/s 生成
  - 配置：`--ctx-size 36864 --n-gpu-layers 99 --flash-attn on`

### 2026-02-17
- 全模型 Context 测试完成 (8 个模型)
- Stage 2 32K 测试完成 (7 个模型)
- 128K RoPE 缩放测试成功 (MiniCPM-o-4.5, Qwen3-0.6B)

---

## 🔧 推荐配置

### 实时应用 (低延迟)
```bash
# 8K Context, 高性能
--ctx-size 8192 --n-gpu-layers 99
```

### 长文档分析
```bash
# 32K Context, 平衡模式
--ctx-size 32768 --n-gpu-layers 99
```

### 超长 Context (128K)
```bash
# 使用 MiniCPM-o-4.5 或 Qwen3-0.6B
--ctx-size 131072 --rope-scaling yarn --rope-scale 3.2
```

---

*最后更新：2026-02-25*
*测试框架：llama.cpp 三层评估系统 v1.0*
*数据位置：tmp/2del/eval_results_20260219_223625/*
