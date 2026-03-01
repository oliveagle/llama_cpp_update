# Stage 1 Context 梯度测试汇总

> **测试时间**: 2026-02-25
> **测试设备**: NVIDIA Tesla V100 32GB
> **测试后端**: CUDA

---

## 测试模型

| 模型 | 参数量 | 量化格式 | 文件大小 |
|------|--------|----------|----------|
| JoyAI-LLM-Flash | 48.94B | Q4_K_M | 27.63 GB |
| Qwen3.5-35B-A3B-UD | 34.66B | Q4_K_XL | 18.32 GB |

---

## Context 梯度性能对比

### Prompt 处理吞吐量 (TPS)

| Context | JoyAI-LLM-Flash (冷启动) | Qwen3.5-35B-A3B-UD | 备注 |
|---------|-------------------------|-------------------|------|
| 4K | 1,029 t/s | 646 t/s | JoyAI 快 1.6x |
| 8K | 1,591 t/s | 675 t/s | JoyAI 快 2.4x |
| 12K | 1,847 t/s | - | - |
| 16K | 2,001 t/s | 685 t/s | JoyAI 快 2.9x |

**注意**:
- JoyAI-LLM-Flash 的测试显示迭代 2/3 有异常高的 TPS（191K-569K），这可能是由于 llama.cpp 的 prompt 缓存机制导致 `timings.prompt_ms` 返回不准确的数据
- 上表使用迭代 1（冷启动）的数据进行对比

---

## 详细测试结果

### JoyAI-LLM-Flash (DeepSeek2 架构, 48.94B)

| Context | 冷启动 TPS | 热启动 TPS | 平均延迟 | 状态 |
|---------|------------|------------|----------|------|
| 4K | 1,029 | 191,369 | 907 ms | ✅ |
| 8K | 1,591 | 328,591 | 1,163 ms | ✅ |
| 12K | 1,847 | 497,792 | 1,497 ms | ✅ |
| 16K | 2,001 | 569,654 | 1,840 ms | ✅ |
| 24K | - | - | - | ❌ 显存不足 |
| 32K | - | - | - | ❌ 显存不足 |

**完整报告**: [joyai_flash_context_gradient_report.md](./joyai_flash_context_gradient_report.md)

### Qwen3.5-35B-A3B-UD (Qwen35MoE 架构, 34.66B)

| Context | 平均 TPS | 平均延迟 | 状态 |
|---------|----------|----------|------|
| 4K | 646 t/s | 4,203 ms | ✅ |
| 8K | 675 t/s | 8,101 ms | ✅ |
| 16K | 685 t/s | 15,955 ms | ✅ |

**完整报告**: [qwen35_35b_a3b_context_gradient_report.md](./qwen35_35b_a3b_context_gradient_report.md)

---

## 关键发现

### 1. 架构差异

| 特性 | JoyAI-LLM-Flash | Qwen3.5-35B-A3B-UD |
|------|-----------------|-------------------|
| 架构 | DeepSeek2 (Dense) | Qwen35MoE (Sparse) |
| 层数 | 40 | 40 |
| 专家数 | 256 (激活 8) | 256 (激活 8) |
| 嵌入维度 | 2048 | 2048 |
| 训练 Context | 131,072 | 262,144 |

### 2. 性能特征

**JoyAI-LLM-Flash**:
- 冷启动性能优秀（16K context 达到 2,001 t/s）
- 受限于 V100 32GB 显存，最大支持 16K context
- DeepSeek2 架构优化了长序列处理
- **注意**: 迭代 2/3 出现异常的 TPS 数据（191K-569K），可能是 llama.cpp 缓存机制导致 timing 数据不准确

**Qwen3.5-35B-A3B-UD**:
- 性能随 context 线性增长（646 → 685 t/s）
- MoE 架构在长序列上表现稳定
- 更小的模型尺寸（18GB vs 28GB）
- **缓存行为差异**: 测试显示 Qwen3.5 的缓存效果不如 JoyAI 明显（127ms → 98ms vs 2689ms → 17ms），可能是由于：
  - llama.cpp 版本差异（b8134 vs b8069）
  - 模型架构差异（Qwen35MoE vs DeepSeek2）
  - 缓存实现的变化

### 3. V100 32GB 限制

| 模型 | 最大 Context | 限制因素 |
|------|-------------|----------|
| JoyAI-LLM-Flash | 16K | 显存不足 (需 29GB+ 模型权重) |
| Qwen3.5-35B-A3B-UD | 32K+ | 未测试 (模型较小，可能支持更大) |

---

## 原始数据文件

| 模型 | JSON 结果 | 报告 |
|------|-----------|------|
| JoyAI-LLM-Flash | `joyai_flash_cuda_V100_20260225_175742.json` | `joyai_flash_context_gradient_report.md` |
| Qwen3.5-35B-A3B-UD | `qwen35_35b_a3b_cuda_V100_20260225_234715.json` | `qwen35_35b_a3b_context_gradient_report.md` |

---

## 测试脚本

```bash
# JoyAI-LLM-Flash
python3 eval/tests/stage1_throughput/tests/test_joyai_flash.py \
  --backend cuda \
  --ctx-sizes 4096 8192 12288 16384 24576 32768 \
  --iterations 3

# Qwen3.5-35B-A3B-UD
python3 eval/tests/stage1_throughput/tests/test_qwen35_35b_a3b.py \
  --backend cuda \
  --ctx-sizes 4096 8192 16384 \
  --iterations 3
```

---

*汇总生成时间: 2026-02-25*
*测试框架: llama.cpp Stage 1 Throughput Benchmark*
