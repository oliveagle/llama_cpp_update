# Context Window 测试报告 - MiroThinker-v1.5-30B.Q8_0

> **测试时间**: 2026-02-17T17:12:25.059723
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 51.9s | ❌ |
| 8K | ✅ | 19341 | 53.0s | ❌ |
| 12K | ✅ | 29106 | 106.1s | ❌ |
| 16K | ❌ | - | - | - |

**最大成功 Context**: 12K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "MiroThinker-v1.5-30B.Q8_0",
  "timestamp": "2026-02-17T17:12:25.059723",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 51.887794971466064,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 53.047667264938354,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 106.10930109024048,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 16384,
      "status": "failed",
      "error": "HTTP 400: {\"error\":{\"code\":400,\"message\":\"request (38874 tokens) exceeds the available context size (32768 tokens), try increasing it\",\"type\":\"exceed_context_size_error\",\"n_prompt_tokens\":38874,\"n_ctx\":32768}}"
    }
  ],
  "max_successful": 12288,
  "max_correct": 0
}
```
