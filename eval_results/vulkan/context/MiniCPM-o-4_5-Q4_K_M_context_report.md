# Context Window 测试报告 - MiniCPM-o-4_5-Q4_K_M

> **测试时间**: 2026-02-17T16:59:34.718848
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 38.6s | ❌ |
| 8K | ✅ | 19341 | 54.0s | ❌ |
| 12K | ✅ | 29106 | 101.7s | ❌ |
| 16K | ❌ | - | - | - |

**最大成功 Context**: 12K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "MiniCPM-o-4_5-Q4_K_M",
  "timestamp": "2026-02-17T16:59:34.718848",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 38.583996295928955,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 53.9831383228302,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 101.71870923042297,
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
