# JoyAI-LLM-Flash-Q4_K_M 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | 5 |
| 通过数 | 0 |
| 失败数 | 5 |
| 准确率 | 0.0% |

## 详细结果

| 测试项 | 状态 | 调用的工具 | 参数匹配 |
|--------|------|-----------|---------|
| 天气查询 | ❌ | None | ❌ |
| 计算器 | ❌ | None | ❌ |
| 搜索 | ❌ | None | ❌ |
| 日历 | ❌ | None | ❌ |
| 翻译 | ❌ | None | ❌ |

## 原始响应详情

```json
[
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "error": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "test_name": "天气查询",
    "test_description": "测试模型是否能正确调用天气查询工具"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "error": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "test_name": "计算器",
    "test_description": "测试模型是否能正确调用计算器工具"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "error": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "test_name": "搜索",
    "test_description": "测试模型是否能正确调用搜索工具"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "error": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "test_name": "日历",
    "test_description": "测试模型是否能正确调用日历工具"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "error": "400 Client Error: Bad Request for url: http://localhost:8401/v1/chat/completions",
    "test_name": "翻译",
    "test_description": "测试模型是否能正确调用翻译工具"
  }
]
```
