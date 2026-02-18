# Context Window 测试报告 - Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0

> **测试时间**: 2026-02-17T17:09:22.318428
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 28.3s | ✅ |
| 8K | ✅ | 19341 | 49.3s | ✅ |
| 12K | ✅ | 29106 | 98.1s | ✅ |
| 16K | ❌ | - | - | - |

**最大成功 Context**: 12K tokens

**最大正确召回**: 12K tokens

## 详细结果

```json
{
  "model": "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0",
  "timestamp": "2026-02-17T17:09:22.318428",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 28.280627250671387,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 49.345271587371826,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 98.06648826599121,
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
