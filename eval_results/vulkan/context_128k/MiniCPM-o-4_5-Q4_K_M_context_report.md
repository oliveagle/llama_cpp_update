# Context Window 测试报告 - MiniCPM-o-4_5-Q4_K_M

> **测试时间**: 2026-02-17T21:01:02.901290
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 41.3s | ❌ |
| 8K | ✅ | 19341 | 53.2s | ❌ |
| 12K | ✅ | 29106 | 100.0s | ❌ |
| 16K | ✅ | 38874 | 171.2s | ❌ |
| 24K | ❌ | - | - | - |

**最大成功 Context**: 16K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "MiniCPM-o-4_5-Q4_K_M",
  "timestamp": "2026-02-17T21:01:02.901290",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 41.29077506065369,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 53.16516995429993,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 99.96432495117188,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 16384,
      "actual_tokens": 38874,
      "status": "success",
      "response_time": 171.17682671546936,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 24576,
      "status": "failed",
      "error": "HTTP 400: {\"error\":{\"code\":400,\"message\":\"request (58410 tokens) exceeds the available context size (40960 tokens), try increasing it\",\"type\":\"exceed_context_size_error\",\"n_prompt_tokens\":58410,\"n_ctx\":40960}}"
    }
  ],
  "max_successful": 16384,
  "max_correct": 0
}
```
