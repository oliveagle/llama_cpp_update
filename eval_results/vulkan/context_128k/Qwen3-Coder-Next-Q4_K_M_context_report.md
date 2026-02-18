# Context Window 测试报告 - Qwen3-Coder-Next-Q4_K_M

> **测试时间**: 2026-02-17T20:47:38.657285
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 79.0s | ✅ |
| 8K | ✅ | 19341 | 42.2s | ✅ |
| 12K | ✅ | 29106 | 71.9s | ✅ |
| 16K | ✅ | 38874 | 107.1s | ✅ |
| 24K | ✅ | 58410 | 196.7s | ✅ |
| 32K | ⏱️ | - | 超时 | - |

**最大成功 Context**: 24K tokens

**最大正确召回**: 24K tokens

## 详细结果

```json
{
  "model": "Qwen3-Coder-Next-Q4_K_M",
  "timestamp": "2026-02-17T20:47:38.657285",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 78.96956729888916,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 42.229743003845215,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 71.90886068344116,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 16384,
      "actual_tokens": 38874,
      "status": "success",
      "response_time": 107.08655762672424,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 24576,
      "actual_tokens": 58410,
      "status": "success",
      "response_time": 196.6548125743866,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 32768,
      "status": "timeout",
      "error": "Timeout after 300s"
    }
  ],
  "max_successful": 24576,
  "max_correct": 24576
}
```
