# RuvLTRA 模型路由测试最终报告

## 测试信息

| 项目 | 值 |
|------|-----|
| **测试日期** | 2026-02-20 |
| **模型** | ruvltra-claude-code-0.5b-q4_k_m.gguf |
| **服务器** | llama.cpp b8069 (端口 8402) |
| **模型路径** | `/mnt/volume3/llama_cpp/models/ruvltra/ruvltra-claude-code-0.5b-q4_k_m.gguf` |
| **SHA256** | `f0a42bb979ca62b5e61f3bf924ab4b6a40aa091825ee7dcb4039949980ab81a8` |
| **文件大小** | 380MB (397,805,248 bytes) |

---

## 重要发现

### 模型真实用途

**RuvLTRA 不是一个直接路由的聊天模型！**

根据官方 README，RuvLTRA 是一个**混合路由系统**：

```
┌─────────────────────────────────────────────────────┐
│                  RuvLTRA 路由流程                    │
├─────────────────────────────────────────────────────┤
│  1. 关键词匹配 (快速)                                │
│     └─ 匹配 >=2 个关键词 → 直接返回 (78% 准确率)     │
│  2. 嵌入相似度 (精确)                                │
│     └─ 计算查询嵌入 → HNSW 搜索 → 返回最佳匹配       │
│  3. 混合策略                                         │
│     └─ 关键词 + 嵌入 = 100% 准确率                   │
└─────────────────────────────────────────────────────┘
```

### 为什么 llama.cpp 直接使用效果不好

| 问题 | 原因 |
|------|------|
| 模型输出是续写 | 模型设计用于生成嵌入，不是对话 |
| 忽略系统提示词 | 不是指令微调模型 |
| 准确率低 | 没有关键词匹配和 HNSW 搜索配合 |

### 官方使用方式

需要配合 **ruvllm** 库使用：

#### Rust
```rust
use ruvllm::prelude::*;

let model = RuvLtraModel::from_pretrained("ruv/ruvltra")?;
let routing = model.route("fix the memory leak")?;
println!("Agent: {}", routing.agent);
```

#### Python
```python
from llama_cpp import Llama
llm = Llama(model_path=model_path)
# 生成嵌入用于相似度匹配
embedding = llm.create_embedding("implement user auth")
```

#### TypeScript
```typescript
import { RuvLLM } from '@ruvector/ruvllm';
const llm = new RuvLLM({ model: 'ruv/ruvltra' });
const route = await llm.route('optimize database');
```

---

## 测试总结

### 测试过的提示词格式

| 格式 | 准确率 | 备注 |
|------|--------|------|
| "Route: {task}" | 0% | 模型直接回答问题 |
| 系统提示词 + "Assign: {task}" | 20-40% | 偏向 backend-dev |
| Few-shot 示例 | 0% | 模型续写而非推理 |
| 中文系统提示词 | 20% | 有时返回 DBA 等 |
| 英文任务 | 0% | 总是说"Sure, I can help..." |

### 最佳测试结果

**使用系统提示词时**：
- "设计数据库 Schema" → "DBA" ✓
- "评审代码安全" → "security-reviewer" ✓
- "实现用户认证 API" → "backend-dev" ✓

但总体准确率只有约 20-40%，远低于官方宣称的 100%。

---

## 正确的使用方案

### 方案 1: 使用 ruvllm Rust 库 (推荐)

```bash
cargo add ruvllm
```

```rust
use ruvllm::{RuvLtraModel, RoutingRequest};

let model = RuvLtraModel::from_pretrained("ruv/ruvltra")?;
let request = RoutingRequest {
    task: "implement user authentication".to_string(),
};
let result = model.route(request)?;
println!("Agent: {}, Confidence: {}", result.agent, result.confidence);
```

## 正确的使用方式（已验证）

### 关键词匹配 + 嵌入混合路由

项目已有的 Python 脚本 `/mnt/volume3/llama_cpp/scripts/ruvltra_router.py` 展示了正确的使用方式：

#### 测试结果

```bash
$ python3 ruvltra_router.py "实现用户认证"
推荐 Agent: coder (置信度：80%)
匹配关键词：实现

$ python3 ruvltra_router.py "修复内存泄漏问题"
推荐 Agent: debugger (置信度：90%)
匹配关键词：修复，问题

$ python3 ruvltra_router.py "添加单元测试"
推荐 Agent: tester (置信度：90%)
匹配关键词：测试，单元测试
```

#### 路由流程

1. **关键词匹配** - 统计匹配的关键词数量
2. **嵌入相似度** - 获取语义嵌入（896 维）用于精细匹配
3. **综合决策** - 基于关键词分数计算置信度

### 方案 2: 实现关键词 + 嵌入混合路由

```python
# 伪代码
KEYWORDS = {
    "architect": ["架构", "设计", "微服务", "扩展"],
    "backend-dev": ["API", "数据库", "认证", "后端"],
    "test-engineer": ["测试", "单元", "集成", "E2E"],
    ...
}

def route_task(task):
    # 1. 关键词匹配
    matches = count_keyword_matches(task, KEYWORDS)
    if matches >= 2:
        return best_match

    # 2. 嵌入相似度
    embedding = model.encode(task)
    return hnsw_search(embedding)
```

### 方案 3: 使用现有 Python 脚本

项目已有路由脚本：
```
/mnt/volume3/llama_cpp/scripts/ruvltra_router.py
```

---

## 结论

**RuvLTRA 模型本身不是一个独立的路由解决方案**。它需要：

1. **关键词匹配系统** - 用于快速初步过滤
2. **HNSW 索引** - 用于快速相似度搜索
3. **Agent 描述数据库** - 用于嵌入匹配
4. **ruvllm 库** - 整合所有组件

**单纯用 llama.cpp 运行模型文件无法达到 100% 准确率**。

### 建议

1. **使用 ruvllm Rust/Python 库** - 官方支持
2. **实现混合路由** - 关键词 + 嵌入
3. **参考现有脚本** - `/mnt/volume3/llama_cpp/scripts/ruvltra_router.py`

---

## 参考资源

| 资源 | 链接 |
|------|------|
| HuggingFace | https://huggingface.co/ruv/ruvltra |
| ModelScope | https://www.modelscope.cn/models/hf/ruv-ruvltra-claude-code |
| GitHub | https://github.com/ruvnet/ruvector |
| Crate | https://crates.io/crates/ruvllm |
| npm | https://npmjs.com/package/@ruvector/ruvllm |

---

*测试完成时间：2026-02-20 19:15*
