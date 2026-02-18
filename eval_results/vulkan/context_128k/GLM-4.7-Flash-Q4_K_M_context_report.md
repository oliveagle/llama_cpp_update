# Context Window 测试报告 - GLM-4.7-Flash-Q4_K_M

> **测试时间**: 2026-02-17T21:07:18.378576
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 8644 | 221.6s | ❌ |
| 8K | ⏱️ | - | 超时 | - |

**最大成功 Context**: 4K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "GLM-4.7-Flash-Q4_K_M",
  "timestamp": "2026-02-17T21:07:18.378576",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 8644,
      "status": "success",
      "response_time": 221.64478611946106,
      "correct": false,
      "answer": ""
    },
    {
      "target_tokens": 8192,
      "status": "timeout",
      "error": "Timeout after 300s"
    }
  ],
  "max_successful": 4096,
  "max_correct": 0
}
```
