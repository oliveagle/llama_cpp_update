# Vulkan (8400) 128K Context Window 测试汇总报告

> **测试时间**: 2026-02-17
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester
> **硬件**: AMD gfx1151 (Strix Halo, 32GB VRAM, 125GB 共享内存)
> **llama.cpp**: b8069 (Vulkan 后端)
> **配置**: ctx-size=256K (预设)
> **测试方法**: Needle in a Haystack (大海捞针)
> **超时限制**: 300s

---

## 测试结果总览

| 排名 | 模型 | 最大成功 | 最大召回 | 24K | 32K | 特点 |
|------|------|---------|---------|-----|-----|------|
| 🥇 | **Qwen3-Coder-Next-Q4_K_M** | **24K** | **24K** ✅ | ⏱️ | - | 最佳表现 |
| 🥈 | Qwen3-4B-Instruct-2507 | 16K | 16K | ⏱️ | - | Qwen3 标准 |
| 🥈 | Qwen3VL-4B-Instruct-Q8_0 | 16K | 16K | ⏱️ | - | Qwen3 标准 |
| 🥈 | Qwen3-VL-8B-Instruct | 16K | 16K | ⏱️ | - | Qwen3 标准 |
| 5 | MiniCPM-o-4_5-Q4_K_M | 16K | 0K ❌ | 400 | - | 能跑但无召回 |
| 5 | MiroThinker-v1.5-30B | 16K | 0K ❌ | ⏱️ | - | 能跑但无召回 |
| 7 | GLM-4.7-Flash-Q4_K_M | 4K | 0K ❌ | - | - | 推理模型超时 |

**测试完成度**: 7/7 模型 (100%)

---

## 详细测试结果

### 🥇 Qwen3-Coder-Next-Q4_K_M (冠军)

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 79.0s | ✅ 正确 | 通过 |
| 8K | 42.2s | ✅ 正确 | 通过 |
| 12K | 71.9s | ✅ 正确 | 通过 |
| 16K | 107.1s | ✅ 正确 | 通过 |
| 24K | 196.7s | ✅ 正确 | **最佳** |
| 32K | - | - | ⏱️ 超时 |

**结论**: 唯一突破 16K 的模型，达到 24K 且召回正确。

---

### 🥈 Qwen3-4B-Instruct-2507-UD-Q4_K_XL

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 21.5s | ✅ 正确 | 通过 |
| 8K | 43.5s | ✅ 正确 | 通过 |
| 12K | 89.4s | ✅ 正确 | 通过 |
| 16K | 157.5s | ✅ 正确 | 通过 |
| 24K | - | - | ⏱️ 超时 |

---

### 🥈 Qwen3VL-4B-Instruct-Q8_0

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 35.5s | ✅ 正确 | 通过 |
| 8K | 41.9s | ✅ 正确 | 通过 |
| 12K | 87.1s | ✅ 正确 | 通过 |
| 16K | 155.3s | ✅ 正确 | 通过 |
| 24K | - | - | ⏱️ 超时 |

---

### 🥈 Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 41.4s | ✅ 正确 | 通过 |
| 8K | 48.9s | ✅ 正确 | 通过 |
| 12K | 95.9s | ✅ 正确 | 通过 |
| 16K | 164.9s | ✅ 正确 | 通过 |
| 24K | - | - | ⏱️ 超时 |

**Qwen3 系列总结**: 4个模型全部达到 16K 且召回正确，但 24K 都超时。

---

### MiniCPM-o-4_5-Q4_K_M

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 41.3s | ❌ 错误 | 运行 |
| 8K | 53.2s | ❌ 错误 | 运行 |
| 12K | 100.0s | ❌ 错误 | 运行 |
| 16K | 171.2s | ❌ 错误 | 运行 |
| 24K | - | - | ❌ HTTP 400 |

**结论**: 能处理长 context 但无法召回 needle，24K 直接返回错误。

---

### MiroThinker-v1.5-30B.Q8_0 (30B 大模型)

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 62.7s | ❌ 错误 | 运行 |
| 8K | 53.3s | ❌ 错误 | 运行 |
| 12K | 106.8s | ❌ 错误 | 运行 |
| 16K | 176.8s | ❌ 错误 | 运行 |
| 24K | - | - | ⏱️ 超时 |

**结论**: 30B 大模型能跑 16K context，但无法正确召回信息。

---

### GLM-4.7-Flash-Q4_K_M (推理模型)

| Context | 时间 | 答案 | 状态 |
|---------|------|------|------|
| 4K | 221.6s | ❌ 错误 | 运行 |
| 8K | - | - | ⏱️ 超时 |

**结论**: 推理模型在长文本上响应极慢，4K 已超过 200s，8K 超时。

---

## 关键发现

### 1. 128K 目标未达成

| 目标 | 实际达成 | 差距 |
|------|---------|------|
| 128K context | 24K (Qwen3-Coder) | -104K |

**限制因素**:
1. **超时限制**: 300s 导致 32K+ 无法完成
2. **响应时间**: context 越大，首 token 延迟越长
3. **模型能力**: 只有 Qwen3 系列能正确召回 needle

### 2. 性能趋势

| Context | 平均响应时间 | 趋势 |
|---------|-------------|------|
| 4K | ~45s | - |
| 8K | ~45s | 持平 |
| 12K | ~90s | 2x |
| 16K | ~155s | 3.5x |
| 24K | ~197s | 4.4x (仅 Coder) |

### 3. 模型分类

| 类型 | 代表模型 | Context 能力 | 召回能力 |
|------|---------|-------------|---------|
| **Qwen3 代码** | Qwen3-Coder-Next | 24K | ✅ 优秀 |
| **Qwen3 通用** | Qwen3-4B/VL-4B/VL-8B | 16K | ✅ 优秀 |
| **多模态** | MiniCPM-o-4_5 | 16K | ❌ 无 |
| **大模型推理** | MiroThinker-30B | 16K | ❌ 无 |
| **小模型推理** | GLM-4.7-Flash | 4K | ❌ 无 |

---

## 原始数据文件

```
eval_results/vulkan/context_128k/
├── Qwen3-4B-Instruct-2507-UD-Q4_K_XL_context_report.md
├── Qwen3-4B-Instruct-2507-UD-Q4_K_XL_context.json
├── Qwen3VL-4B-Instruct-Q8_0_context_report.md
├── Qwen3VL-4B-Instruct-Q8_0_context.json
├── Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0_context_report.md
├── Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0_context.json
├── Qwen3-Coder-Next-Q4_K_M_context_report.md
├── Qwen3-Coder-Next-Q4_K_M_context.json
├── MiniCPM-o-4_5-Q4_K_M_context_report.md
├── MiniCPM-o-4_5-Q4_K_M_context.json
├── GLM-4.7-Flash-Q4_K_M_context_report.md
├── GLM-4.7-Flash-Q4_K_M_context.json
├── MiroThinker-v1.5-30B.Q8_0_context_report.md
├── MiroThinker-v1.5-30B.Q8_0_context.json
└── CONTEXT_128K_SUMMARY.md (本报告)
```

---

## 建议

### 生产环境配置

```ini
# 推荐 ctx-size 配置
[模型名]
ctx-size = 24576  # 24K (Qwen3-Coder)
# 或
ctx-size = 16384  # 16K (其他 Qwen3)
```

### 后续优化方向

1. **增加超时时间**: 将 300s 延长至 600s 或更长，测试 32K/48K
2. **优化测试方法**: 使用更小的 max_tokens 或更简单的 prompt
3. **分阶段测试**: 先确认 24K 稳定，再逐步测试 32K/48K/64K
4. **CUDA 对比**: 在 V100 (8401) 上测试相同模型对比性能

---

## 结论

**Vulkan (8400) 128K Context Window 测试结论**:

1. **目标 128K 未达成**，实际最大 **24K** (Qwen3-Coder-Next)
2. **Qwen3 系列表现最佳**，4个模型全部达到 16K 且召回正确
3. **超时限制是主要瓶颈**，24K 测试已达 197s，32K 预计需要 300s+
4. **配置已支持 256K**，但模型实际能力和响应时间限制了可用范围

**推荐生产配置**:
- **通用场景**: 16K context (所有 Qwen3 模型)
- **代码场景**: 24K context (Qwen3-Coder-Next)

---

*报告生成时间: 2026-02-17*
*Agent: gfx1151-Tester*
*状态: 128K 测试完成 (达成 24K)*
