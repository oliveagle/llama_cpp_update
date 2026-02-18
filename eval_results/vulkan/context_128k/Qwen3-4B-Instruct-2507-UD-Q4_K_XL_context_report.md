# Context Window 测试报告 - Qwen3-4B-Instruct-2507-UD-Q4_K_XL

> **测试时间**: 2026-02-17T20:15:55.142512
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester

---

## 测试结果

| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |
|-------------|------|------------|----------|----------|
| 4K | ✅ | 9572 | 21.5s | ✅ |
| 8K | ✅ | 19341 | 43.5s | ✅ |
| 12K | ✅ | 29106 | 89.4s | ✅ |
| 16K | ✅ | 38874 | 157.5s | ✅ |
| 24K | ⏱️ | - | 超时 | - |

**最大成功 Context**: 16K tokens

**最大正确召回**: 16K tokens

## 详细结果

```json
{
  "model": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
  "timestamp": "2026-02-17T20:15:55.142512",
  "base_url": "http://localhost:8400",
  "tests": [
    {
      "target_tokens": 4096,
      "actual_tokens": 9572,
      "status": "success",
      "response_time": 21.507967948913574,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 8192,
      "actual_tokens": 19341,
      "status": "success",
      "response_time": 43.47406077384949,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 12288,
      "actual_tokens": 29106,
      "status": "success",
      "response_time": 89.36471819877625,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 16384,
      "actual_tokens": 38874,
      "status": "success",
      "response_time": 157.45397925376892,
      "correct": true,
      "answer": "汉内斯·阿尔文"
    },
    {
      "target_tokens": 24576,
      "status": "timeout",
      "error": "Timeout after 300s"
    }
  ],
  "max_successful": 16384,
  "max_correct": 16384
}
```
