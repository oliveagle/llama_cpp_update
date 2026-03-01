# RuvLTRA Agent 路由测试报告

## 测试概述

- **测试日期**: 2026-02-20 17:17
- **服务器**: http://localhost:8402
- **模型**: ruvltra-claude-code-0.5b-q4_k_m.gguf
- **系统提示词**: `Assign tasks to agents. Output only agent name.`
- **测试方法**: 每个 Agent 5 个任务，共 135 个测试样本

## 测试结果汇总

| Agent | 任务数 | 成功 | 准确率 |
|-------|--------|------|--------|
| backend-dev | 5 | 5 | **100%** |
| architect | 5 | 0 | 0% |
| frontend-dev | 5 | 0 | 0% |
| fullstack-dev | 5 | 0 | 0% |
| mobile-dev | 5 | 0 | 0% |
| devops-engineer | 5 | 0 | 0% |
| sre | 5 | 0 | 0% |
| dba | 5 | 0 | 0% |
| data-engineer | 5 | 0 | 0% |
| ml-engineer | 5 | 0 | 0% |
| test-engineer | 5 | 0 | 0% |
| ui-test-engineer | 5 | 0 | 0% |
| code-reviewer | 5 | 0 | 0% |
| security-reviewer | 5 | 0 | 0% |
| performance-expert | 5 | 0 | 0% |
| product-manager | 5 | 0 | 0% |
| scrum-master | 5 | 0 | 0% |
| tech-lead | 5 | 0 | 0% |
| technical-writer | 5 | 0 | 0% |
| researcher | 5 | 0 | 0% |
| ux-designer | 5 | 0 | 0% |
| prompt-engineer | 5 | 0 | 0% |
| quant-researcher | 5 | 0 | 0% |
| crypto-trader | 5 | 0 | 0% |
| financial-analyst | 5 | 0 | 0% |
| market-monitor | 5 | 0 | 0% |
| skeptic | 5 | 0 | 0% |

**总体准确率**: 5/135 (3.7%)

## 问题分析

### 1. 模型行为偏差

测试发现模型有严重的**响应偏差**：
- 93% 的响应都是 "backend-dev"
- 模型倾向于将几乎所有任务都分配给 backend-dev
- 只有明确与"实现用户认证 API"相关的任务才能正确路由

### 2. 非 Agent 名称响应

模型有时会返回非 Agent 名称的内容：
- "UI 组件库" (期望：frontend-dev)
- "产品路线图" (期望：product-manager)
- "API 文档" (期望：technical-writer)
- "Architect" (首字母大写，期望：architect)
- "UI-UX" (期望：ux-designer)
- "UI-test-engine" (期望：ui-test-engineer)

### 3. 可能的原因

1. **模型训练数据不足**: ruvltra-claude-code-0.5b 可能没有经过专门的路由训练
2. **提示词不够清晰**: 系统提示词可能没有正确引导模型行为
3. **模型容量限制**: 0.5B 参数可能不足以理解复杂的路由逻辑
4. **Agent 名称不在模型词汇表中**: 像"devops-engineer"、"fullstack-dev"等复合词可能不在模型的原始训练数据中

## 建议改进方案

### 方案 1: 使用更简单的 Agent 名称

使用单个单词的 Agent 名称：
```
architect -> architect
backend-dev -> backend
frontend-dev -> frontend
fullstack-dev -> fullstack
test-engineer -> tester
security-reviewer -> security
```

### 方案 2: 使用关键词匹配路由

不依赖模型路由，改用关键词匹配：
```python
KEYWORDS = {
    "architect": ["架构", "设计", "扩展", "微服务", "技术选型"],
    "backend": ["API", "数据库", "后端", "认证", "事务"],
    "frontend": ["UI", "组件", "页面", "表单", "响应式"],
    ...
}
```

### 方案 3: 使用专门的嵌入模型

使用嵌入模型计算任务与 Agent 描述之间的相似度：
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
# 计算任务嵌入与 Agent 描述嵌入的余弦相似度
```

### 方案 4: 微调路由模型

使用专门的路由数据集微调模型，使其学会：
1. 理解任务描述
2. 匹配 Agent 能力
3. 输出正确的 Agent 名称

## 结论

当前 ruvltra-claude-code-0.5b 模型**不适合**直接用于 Agent 路由任务。建议采用以下方案之一：

1. **关键词匹配** (最简单，准确率高)
2. **嵌入相似度** (准确率高，支持语义理解)
3. **微调专用模型** (需要训练数据和计算资源)

## 测试结果文件

- 任务文件：`agent_routing_test_results/*_tasks.jsonl`
- 结果文件：`agent_routing_test_results/*_results.jsonl`
- 汇总数据：`agent_routing_test_results/summary.jsonl`

---
*测试完成时间：2026-02-20 17:17*
