# Context Window 测试报告 - MiniCPM-o-4_5-Q4_K_M

> **测试时间**: 2026-02-17T16:30:25.364748
> **测试端点**: http://localhost:8401
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ❌ | - | - | - |

**最大成功 Context**: 0K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "MiniCPM-o-4_5-Q4_K_M",
  "timestamp": "2026-02-17T16:30:25.364748",
  "base_url": "http://localhost:8401",
  "tests": [
    {
      "target_tokens": 4096,
      "status": "failed",
      "error": "HTTP 400: {\"error\":{\"code\":400,\"message\":\"request (9572 tokens) exceeds the available context size (8192 tokens), try increasing it\",\"type\":\"exceed_context_size_error\",\"n_prompt_tokens\":9572,\"n_ctx\":8192}}"
    }
  ],
  "max_successful": 0,
  "max_correct": 0
}
```
