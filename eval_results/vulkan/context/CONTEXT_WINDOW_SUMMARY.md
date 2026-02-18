# Vulkan (8400) Context Window 测试汇总报告

> **测试时间**: 2026-02-17
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester
> **测试方法**: Needle in a Haystack (大海捞针)

---

## 测试结果总览

| 排名 | 模型 | 最大成功 Context | 最大正确召回 | 状态 |
|------|------|------------------|--------------|------|
| 🥇 | Qwen3VL-4B-Instruct-Q8_0 | **12K** | **12K** | 优秀 |
| 🥇 | Qwen3-Coder-Next-Q4_K_M | **12K** | **12K** | 优秀 |
| 🥇 | Qwen3-VL-8B-Instruct-Q8_0 | **12K** | **12K** | 优秀 |
| 4 | MiniCPM-o-4_5-Q4_K_M | **12K** | 0K | 运行良好但无法召回 |
| 5 | MiroThinker-v1.5-30B.Q8_0 | **12K** | 0K | 运行良好但无法召回 |
| 6 | GLM-4.7-Flash-Q4_K_M | **4K** | 0K | 受限 |

**关键发现**: AMD Vulkan 后端在 ~16K context 处出现硬性限制 (HTTP 400)

---

## 详细结果

### 🥇 优秀组 (12K 全召回)

#### Qwen3VL-4B-Instruct-Q8_0
```
✅ 4K context: 19.0s (答案正确)
✅ 8K context: 42.4s (答案正确)
✅ 12K context: 89.2s (答案正确)
❌ 16K context: HTTP 400
```

#### Qwen3-Coder-Next-Q4_K_M
```
✅ 4K context: 107.7s (答案正确)
✅ 8K context: 42.3s (答案正确)
✅ 12K context: 72.2s (答案正确)
❌ 16K context: HTTP 400
```

#### Qwen3-VL-8B-Instruct-Q8_0
```
✅ 4K context: 28.3s (答案正确)
✅ 8K context: 49.3s (答案正确)
✅ 12K context: 98.1s (答案正确)
❌ 16K context: HTTP 400
```

### 运行良好但无法召回组

#### MiniCPM-o-4_5-Q4_K_M
```
✅ 4K context: 38.6s (答案错误)
✅ 8K context: 54.0s (答案错误)
✅ 12K context: 101.7s (答案错误)
❌ 16K context: HTTP 400
```
**观察**: 模型可以处理长 context 但无法正确回答 needle 问题

#### MiroThinker-v1.5-30B.Q8_0
```
✅ 4K context: 51.9s (答案错误)
✅ 8K context: 53.0s (答案错误)
✅ 12K context: 106.1s (答案错误)
❌ 16K context: HTTP 400
```
**观察**: 30B 大模型同样无法正确召回 needle 信息

### 受限组

#### GLM-4.7-Flash-Q4_K_M
```
✅ 4K context: 206.4s (答案错误)
⏱️  8K context: 超时 (300s)
```
**观察**: 推理模型在长文本上响应极慢，可能生成大量推理内容

---

## 技术限制分析

### AMD Vulkan 后端限制

1. **硬性限制**: 所有模型在 16K context 处返回 HTTP 400
2. **实际有效**: 12K context 是稳定运行的上限
3. **VRAM 相关**: AMD gfx1151 (32GB 共享内存) 在 16K+ 出现分配失败

### 模型行为差异

| 模型类型 | Context 能力 | 召回能力 | 备注 |
|----------|-------------|----------|------|
| Qwen3 系列 | 12K | 优秀 | 原生支持长 context |
| 多模态模型 | 12K | 无 | 可能优化点在视觉而非文本 |
| 推理模型 | 4K | 无 | GLM-4.7 生成过长推理内容 |

---

## 推荐配置

### 生产环境建议

```ini
# presets/mypresets.ini 推荐配置
ctx-size = 12288  # 12K 是稳定上限
```

### 模型选择建议

| 场景 | 推荐模型 | 最大 Context |
|------|----------|--------------|
| 长文档处理 | Qwen3VL-4B | 12K |
| 代码分析 | Qwen3-Coder-Next | 12K |
| 通用对话 | Qwen3-VL-8B | 12K |
| 推理任务 | GLM-4.7-Flash | 4K (限制使用) |

---

## 原始数据文件

```
eval_results/vulkan/context/
├── GLM-4.7-Flash-Q4_K_M_context_report.md
├── GLM-4.7-Flash-Q4_K_M_context.json
├── MiniCPM-o-4_5-Q4_K_M_context_report.md
├── MiniCPM-o-4_5-Q4_K_M_context.json
├── MiroThinker-v1.5-30B.Q8_0_context_report.md
├── MiroThinker-v1.5-30B.Q8_0_context.json
├── Qwen3VL-4B-Instruct-Q8_0_context_report.md
├── Qwen3VL-4B-Instruct-Q8_0_context.json
├── Qwen3-Coder-Next-Q4_K_M_context_report.md
├── Qwen3-Coder-Next-Q4_K_M_context.json
├── Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0_context_report.md
├── Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0_context.json
└── CONTEXT_WINDOW_SUMMARY.md (本报告)
```

---

## 结论

**Vulkan (8400) Context Window 测试完成**

1. **最大稳定 Context**: 12K tokens (Qwen3 系列)
2. **硬性限制**: 16K 处所有模型返回 HTTP 400
3. **最佳表现**: Qwen3VL-4B, Qwen3-Coder-Next, Qwen3-VL-8B (全部 12K 正确召回)
4. **受限模型**: GLM-4.7-Flash (仅 4K，且超时)

**下一步**: 继续进行 Linux Shell 深度测试 (300 cases)

---

*报告生成时间: 2026-02-17*
*Agent: gfx1151-Tester*
