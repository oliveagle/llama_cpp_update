# Nanbeige4.1-3B 代码能力优化指南

## 概述

Nanbeige4.1-3B 是一个具有 thinking 能力的推理模型，但在代码生成任务上表现不稳定。通过优化 prompt 格式，可以显著提升代码生成质量。

## 核心问题

### Thinking 模式的影响

默认情况下，模型会对问题进行深度思考（reasoning），这在代码生成任务中会导致：
- 输出不稳定
- 生成不完整或有 bug 的代码
- 过度思考导致输出截断

### 解决策略

**核心原则**：让模型进入模式""代码补全而非"思考模式"

## 优化方案

### 1. 使用 Completion API

```bash
# ✅ 推荐：Completion API
curl -s http://localhost:8889/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Nanbeige.Nanbeige4.1-3B.Q8_0.gguf",
    "prompt": "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
    "temperature": 0.3,
    "max_tokens": 500
  }'

# ❌ 不推荐：Chat API（会触发 thinking）
curl -s http://localhost:8889/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Nanbeige.Nanbeige4.1-3B.Q8_0.gguf",
    "messages": [{"role": "user", "content": "Write a Python function for Two Sum"}],
    "temperature": 0.6
  }'
```

### 2. Prompt 以代码开头

```python
# ✅ 好格式 - 函数补全模式
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2

# ❌ 差格式 - 会触发 thinking
"Write a Python function for binary search."
```

### 3. 推荐参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| temperature | 0.3 | 较低温度更稳定 |
| top_p | 0.95 | 默认值 |
| max_tokens | 500-1000 | 根据任务调整 |

### 4. 完整示例

```python
import requests

def complete_code(prompt, model="Nanbeige.Nanbeige4.1-3B.Q8_0.gguf"):
    response = requests.post(
        "http://localhost:8889/v1/completions",
        json={
            "model": model,
            "prompt": prompt,
            "temperature": 0.3,
            "max_tokens": 1000
        }
    )
    return response.json()["choices"][0]["text"]

# 使用示例
code = complete_code("""
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
""")
print(code)
```

## llama-server 启动命令

```bash
./llama-server \
  -m /path/to/Nanbeige.Nanbeige4.1-3B.Q8_0.gguf \
  -c 4096 \
  --temp 0.3 \
  --top-p 0.95 \
  -ngl 0 \
  --port 8889
```

注意：Q8_0 版本显存要求约 4GB，建议使用 CPU 模式或足够的 GPU 显存。

## 测试结果

| 测试用例 | 优化前 | 优化后 |
|----------|--------|--------|
| Two Sum | ❌ 错误 | ✅ 正确 |
| Binary Search | ✅ 正确 | ✅ 正确 |
| Valid Parentheses | ❌ 错误 | ✅ 正确 |
| Merge Sorted Lists | ❌ 混乱 | ✅ 基本正确 |

## 注意事项

1. **量化损失**：Q8_0 量化可能影响代码能力，建议用 FP16 原始模型对比测试
2. **输入格式**：LiveCodeBench 格式（stdin/stdout）与函数补全格式不同，效果可能有差异
3. **Thinking 触发词**：避免使用 "think", "analyze", "solve" 等词汇

## 参考

- LiveCodeBench 官方 prompt 格式：`lcb_runner/prompts/code_generation.py`
- 模型信息：`docs/inbox/README.md`
