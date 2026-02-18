# 256K Context Window 测试报告 - Qwen3-4B-Instruct-2507-UD-Q4_K_XL

> **测试时间**: 2026-02-17T22:09:45.783872
> **测试端点**: http://localhost:8401
> **超时时间**: 600s
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 32K | ⏱️ | - | 超时(600s) | - |

**最大成功 Context**: 0K tokens

**最大正确召回**: 0K tokens

## 详细结果

```json
{
  "model": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
  "timestamp": "2026-02-17T22:09:45.783872",
  "base_url": "http://localhost:8401",
  "timeout": 600,
  "tests": [
    {
      "target_tokens": 32768,
      "status": "timeout",
      "error": "Timeout after 600s"
    }
  ],
  "max_successful": 0,
  "max_correct": 0
}
```
