# Context Window 测试报告 - MiroThinker-v1.5-30B.Q8_0

> **测试时间**: 2026-02-17T21:16:07.490880
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 62.7s | ❌ |
| 8K | ✅ | 19341 | 53.3s | ❌ |
| 12K | ✅ | 29106 | 106.8s | ❌ |
| 16K | ✅ | 38874 | 176.8s | ❌ |
| 24K | ⏱️ | - | 超时 | - |

**最大成功 Context**: 16K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "MiroThinker-v1.5-30B.Q8_0",
  "timestamp": "2026-02-17T21:16:07.490880",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 62.68641972541809,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 53.26569724082947,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 106.79070568084717,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 16384,
      "actual_tokens": 38874,
      "status": "success",
      "response_time": 176.81589269638062,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 24576,
      "status": "timeout",
      "error": "Timeout after 300s"
    }
  ],
  "max_successful": 16384,
  "max_correct": 0
}
```
