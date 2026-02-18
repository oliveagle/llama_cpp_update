# Context Window 测试报告 - Qwen3VL-4B-Instruct-Q8_0

> **测试时间**: 2026-02-17T20:26:12.882285
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 35.5s | ✅ |
| 8K | ✅ | 19341 | 41.9s | ✅ |
| 12K | ✅ | 29106 | 87.1s | ✅ |
| 16K | ✅ | 38874 | 155.3s | ✅ |
| 24K | ⏱️ | - | 超时 | - |

**最大成功 Context**: 16K tokens

**最大正确召回**: 16K tokens

## 详细结果

```json
{
  "model": "Qwen3VL-4B-Instruct-Q8_0",
  "timestamp": "2026-02-17T20:26:12.882285",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 35.49070930480957,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 41.885337352752686,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 87.09606218338013,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 16384,
      "actual_tokens": 38874,
      "status": "success",
      "response_time": 155.28781390190125,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 24576,
      "status": "timeout",
      "error": "Timeout after 300s"
    }
  ],
  "max_successful": 16384,
  "max_correct": 16384
}
```
