# 256K Context Window 测试报告 - Qwen3-Coder-Next-Q4_K_M

> **测试时间**: 2026-02-17T21:38:25.593725
> **测试端点**: http://localhost:8400
> **超时时间**: 600s
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 32K | ✅ | 77945 | 396.6s | ✅ |
| 48K | ❌ | - | - | - |

**最大成功 Context**: 32K tokens

**最大正确召回**: 32K tokens

## 详细结果

```json
{
  "model": "Qwen3-Coder-Next-Q4_K_M",
  "timestamp": "2026-02-17T21:38:25.593725",
  "base_url": "http://localhost:8400",
  "timeout": 600,
  "tests": [
    {
      "target_tokens": 32768,
      "actual_tokens": 77945,
      "status": "success",
      "response_time": 396.6403999328613,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 49152,
      "status": "failed",
      "error": "HTTP 500: proxy error: Failed to read connection"
    }
  ],
  "max_successful": 32768,
  "max_correct": 32768
}
```
