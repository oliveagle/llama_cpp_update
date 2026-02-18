# Context Window 测试报告 - Qwen3VL-4B-Instruct-Q8_0

> **测试时间**: 2026-02-17T17:02:56.502477
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 19.0s | ✅ |
| 8K | ✅ | 19341 | 42.4s | ✅ |
| 12K | ✅ | 29106 | 89.2s | ✅ |
| 16K | ❌ | - | - | - |

**最大成功 Context**: 12K tokens

**最大正确召回**: 12K tokens

## 详细结果

```json
{
  "model": "Qwen3VL-4B-Instruct-Q8_0",
  "timestamp": "2026-02-17T17:02:56.502477",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 19.03836154937744,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 42.397897481918335,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 89.21038365364075,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 16384,
      "status": "failed",
      "error": "HTTP 400: {\"error\":{\"code\":400,\"message\":\"request (38874 tokens) exceeds the available context size (32768 tokens), try increasing it\",\"type\":\"exceed_context_size_error\",\"n_prompt_tokens\":38874,\"n_ctx\":32768}}"
    }
  ],
  "max_successful": 12288,
  "max_correct": 12288
}
```
