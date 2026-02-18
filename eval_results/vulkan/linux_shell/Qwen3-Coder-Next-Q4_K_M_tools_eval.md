# Qwen3-Coder-Next-Q4_K_M 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | 27 |
| 通过数 | 25 |
| 失败数 | 2 |
| 准确率 | 92.6% |

## 分类统计

| 类别 | 测试数 | 通过 | 失败 | 准确率 |
|------|--------|------|------|--------|
| 信息查询 | 4 | 4 | 0 | 100.0% |
| 搜索查询 | 4 | 4 | 0 | 100.0% |
| 数学计算 | 5 | 4 | 1 | 80.0% |
| 文件操作 | 1 | 1 | 0 | 100.0% |
| 时间管理 | 4 | 4 | 0 | 100.0% |
| 系统 | 1 | 1 | 0 | 100.0% |
| 翻译 | 3 | 3 | 0 | 100.0% |
| 边界情况 | 4 | 3 | 1 | 75.0% |
| 通信 | 1 | 1 | 0 | 100.0% |

## 详细结果

| 测试项 | 类别 | 状态 | 调用的工具 | 参数匹配 |
|--------|------|------|-----------|---------|
| 基础计算-乘法 | 数学计算 | ❌ | None | ❌ |
| 复杂表达式 | 数学计算 | ✅ | calculator | ✅ |
| 平方根计算 | 数学计算 | ✅ | calculator | ✅ |
| 三角函数 | 数学计算 | ✅ | calculator | ✅ |
| 单位换算-长度 | 数学计算 | ✅ | unit_converter | ✅ |
| 天气查询-基础 | 信息查询 | ✅ | get_weather | ✅ |
| 天气预报 | 信息查询 | ✅ | get_weather_forecast | ✅ |
| 温度查询 | 信息查询 | ✅ | get_weather | ✅ |
| 时区查询 | 信息查询 | ✅ | get_timezone | ✅ |
| 当前日期 | 时间管理 | ✅ | get_date | ✅ |
| 当前时间 | 时间管理 | ✅ | get_time | ✅ |
| 日历事件 | 时间管理 | ✅ | create_calendar_event | ✅ |
| 倒计时 | 时间管理 | ✅ | countdown | ✅ |
| 网页搜索 | 搜索查询 | ✅ | search | ✅ |
| 新闻查询 | 搜索查询 | ✅ | search_news | ✅ |
| 股票查询 | 搜索查询 | ✅ | get_stock_price | ✅ |
| 汇率查询 | 搜索查询 | ✅ | get_exchange_rate | ✅ |
| 英译中 | 翻译 | ✅ | translate | ✅ |
| 中译英 | 翻译 | ✅ | translate | ✅ |
| 多语言翻译 | 翻译 | ✅ | translate | ✅ |
| 文件读取 | 文件操作 | ✅ | read_file | ✅ |
| 发送邮件 | 通信 | ✅ | send_email | ✅ |
| 设置提醒 | 系统 | ✅ | set_reminder | ✅ |
| 模糊意图-数学 | 边界情况 | ✅ | calculator | ✅ |
| 多工具选择 | 边界情况 | ✅ | get_weather_forecast | ✅ |
| 上下文省略 | 边界情况 | ❌ | None | ❌ |
| 复杂组合请求 | 边界情况 | ✅ | calculator | ✅ |

## 失败项详情

### 基础计算-乘法

- **错误**: HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)`

### 上下文省略

- **错误**: No tool call detected
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `请问您想了解哪个城市的天气？`


## 原始响应详情

```json
[
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)",
    "error": "HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)",
    "method": "native",
    "test_name": "基础计算-乘法",
    "test_description": "测试基础乘法计算"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"(100 + 50) * 2 / 3 - 10\\\"}\"}, \"id\": \"yUz8vEI9dG2YnaDbIVY1kNlgG37jNNBP\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "(100 + 50) * 2 / 3 - 10"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "(100 + 50) * 2 / 3 - 10"
      }
    },
    "method": "native",
    "test_name": "复杂表达式",
    "test_description": "测试复杂数学表达式"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sqrt(144)\\\"}\"}, \"id\": \"wlPBu90YFPWG43KuxgCpBiAmtfVJKQOb\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "sqrt(144)"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "sqrt(144)"
      }
    },
    "method": "native",
    "test_name": "平方根计算",
    "test_description": "测试平方根函数"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sin(30)\\\"}\"}, \"id\": \"u0yqHh1VuMwdqOUR29lPooreHq3quM7l\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "sin(30)"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "sin(30)"
      }
    },
    "method": "native",
    "test_name": "三角函数",
    "test_description": "测试三角函数"
  },
  {
    "success": true,
    "called_tool": "unit_converter",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"unit_converter\", \"arguments\": \"{\\\"value\\\":5,\\\"from_unit\\\":\\\"\\u7c73\\\",\\\"to_unit\\\":\\\"\\u5398\\u7c73\\\"}\"}, \"id\": \"5jG5aYKhnhmLtkszhhhBiTtN2xqhiUYi\"}]",
    "expected": {
      "tool": "unit_converter",
      "args": {
        "value": "5",
        "from_unit": "米",
        "to_unit": "厘米"
      }
    },
    "actual": {
      "tool": "unit_converter",
      "args": {
        "value": 5,
        "from_unit": "米",
        "to_unit": "厘米"
      }
    },
    "method": "native",
    "test_name": "单位换算-长度",
    "test_description": "测试单位换算"
  },
  {
    "success": true,
    "called_tool": "get_weather",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\u5317\\u4eac\\\"}\"}, \"id\": \"b58gZKyjljJMvGoUTiVBTYqfrgzwqQoI\"}]",
    "expected": {
      "tool": "get_weather",
      "args": {
        "location": "北京"
      }
    },
    "actual": {
      "tool": "get_weather",
      "args": {
        "location": "北京"
      }
    },
    "method": "native",
    "test_name": "天气查询-基础",
    "test_description": "测试基础天气查询"
  },
  {
    "success": true,
    "called_tool": "get_weather_forecast",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\u4e0a\\u6d77\\\",\\\"days\\\":1}\"}, \"id\": \"6W539UOZItzk7BDFEGHT2Ayypxq9hAew\"}]",
    "expected": {
      "tool": "get_weather_forecast",
      "args": {
        "location": "上海",
        "days": "1"
      }
    },
    "actual": {
      "tool": "get_weather_forecast",
      "args": {
        "location": "上海",
        "days": 1
      }
    },
    "method": "native",
    "test_name": "天气预报",
    "test_description": "测试未来天气查询"
  },
  {
    "success": true,
    "called_tool": "get_weather",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\u7ebd\\u7ea6\\\"}\"}, \"id\": \"vDBD5Af8RiAspjVaNCH2d1OJ7n37WXhO\"}]",
    "expected": {
      "tool": "get_weather",
      "args": {
        "location": "纽约"
      }
    },
    "actual": {
      "tool": "get_weather",
      "args": {
        "location": "纽约"
      }
    },
    "method": "native",
    "test_name": "温度查询",
    "test_description": "测试温度特定查询"
  },
  {
    "success": true,
    "called_tool": "get_timezone",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_timezone\", \"arguments\": \"{\\\"location\\\":\\\"\\u4e1c\\u4eac\\\"}\"}, \"id\": \"wxMqwcnyuEev9YGUwFKoYxeJzm6120jA\"}]",
    "expected": {
      "tool": "get_timezone",
      "args": {
        "location": "东京"
      }
    },
    "actual": {
      "tool": "get_timezone",
      "args": {
        "location": "东京"
      }
    },
    "method": "native",
    "test_name": "时区查询",
    "test_description": "测试时区信息"
  },
  {
    "success": true,
    "called_tool": "get_date",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_date\", \"arguments\": \"{}\"}, \"id\": \"bBBUNFloxcfpDOPPXdZ7XmT6WpsfjUW8\"}]",
    "expected": {
      "tool": "get_date",
      "args": {}
    },
    "actual": {
      "tool": "get_date",
      "args": {}
    },
    "method": "native",
    "test_name": "当前日期",
    "test_description": "测试当前日期查询"
  },
  {
    "success": true,
    "called_tool": "get_time",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_time\", \"arguments\": \"{}\"}, \"id\": \"nfskdBlgMSTNmTZF4GrdHeFcJid2748x\"}]",
    "expected": {
      "tool": "get_time",
      "args": {}
    },
    "actual": {
      "tool": "get_time",
      "args": {}
    },
    "method": "native",
    "test_name": "当前时间",
    "test_description": "测试当前时间查询"
  },
  {
    "success": true,
    "called_tool": "create_calendar_event",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"create_calendar_event\", \"arguments\": \"{\\\"title\\\":\\\"\\u4f1a\\u8bae\\\",\\\"time\\\":\\\"\\u660e\\u5929\\u4e0b\\u53483\\u70b9\\\"}\"}, \"id\": \"SbjM4afnNeUSWXLnS4tmsVMKAAfk5AgD\"}]",
    "expected": {
      "tool": "create_calendar_event",
      "args": {
        "title": "会议",
        "time": "明天下午3点"
      }
    },
    "actual": {
      "tool": "create_calendar_event",
      "args": {
        "title": "会议",
        "time": "明天下午3点"
      }
    },
    "method": "native",
    "test_name": "日历事件",
    "test_description": "测试日历事件创建"
  },
  {
    "success": true,
    "called_tool": "countdown",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"countdown\", \"arguments\": \"{\\\"target_date\\\":\\\"2026\\u5e74\\u6625\\u8282\\\"}\"}, \"id\": \"wd5NMhqD8BdtcSwT8n9PRXLIwvNvPLPO\"}]",
    "expected": {
      "tool": "countdown",
      "args": {
        "target_date": "2026年春节"
      }
    },
    "actual": {
      "tool": "countdown",
      "args": {
        "target_date": "2026年春节"
      }
    },
    "method": "native",
    "test_name": "倒计时",
    "test_description": "测试倒计时功能"
  },
  {
    "success": true,
    "called_tool": "search",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search\", \"arguments\": \"{\\\"query\\\":\\\"\\u4eba\\u5de5\\u667a\\u80fd \\u6700\\u65b0\\u8fdb\\u5c55 2024\\\"}\"}, \"id\": \"7z0fW3YcXCnEDgqZ5fpNAplcavqfq0qp\"}]",
    "expected": {
      "tool": "search",
      "args": {
        "query": "人工智能"
      }
    },
    "actual": {
      "tool": "search",
      "args": {
        "query": "人工智能 最新进展 2024"
      }
    },
    "method": "native",
    "test_name": "网页搜索",
    "test_description": "测试基础搜索功能"
  },
  {
    "success": true,
    "called_tool": "search_news",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search_news\", \"arguments\": \"{\\\"category\\\":\\\"\\u79d1\\u6280\\\"}\"}, \"id\": \"ksgB1HtSLzN5zT7caaBGEseA4d0skgrV\"}]",
    "expected": {
      "tool": "search_news",
      "args": {
        "category": "科技"
      }
    },
    "actual": {
      "tool": "search_news",
      "args": {
        "category": "科技"
      }
    },
    "method": "native",
    "test_name": "新闻查询",
    "test_description": "测试新闻搜索"
  },
  {
    "success": true,
    "called_tool": "get_stock_price",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_stock_price\", \"arguments\": \"{\\\"symbol\\\":\\\"\\u817e\\u8baf\\\"}\"}, \"id\": \"1pHwB9hF9E9AVVG1FYuCCJtb2z6izv31\"}]",
    "expected": {
      "tool": "get_stock_price",
      "args": {
        "symbol": "腾讯"
      }
    },
    "actual": {
      "tool": "get_stock_price",
      "args": {
        "symbol": "腾讯"
      }
    },
    "method": "native",
    "test_name": "股票查询",
    "test_description": "测试股票信息查询"
  },
  {
    "success": true,
    "called_tool": "get_exchange_rate",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_exchange_rate\", \"arguments\": \"{\\\"from_currency\\\":\\\"USD\\\",\\\"to_currency\\\":\\\"CNY\\\",\\\"amount\\\":100}\"}, \"id\": \"JP2pbv7UJJV6IkGdEkiBEBLKIbGf8B0E\"}]",
    "expected": {
      "tool": "get_exchange_rate",
      "args": {
        "from_currency": "USD",
        "to_currency": "CNY",
        "amount": "100"
      }
    },
    "actual": {
      "tool": "get_exchange_rate",
      "args": {
        "from_currency": "USD",
        "to_currency": "CNY",
        "amount": 100
      }
    },
    "method": "native",
    "test_name": "汇率查询",
    "test_description": "测试汇率转换"
  },
  {
    "success": true,
    "called_tool": "translate",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Machine Learning\\\",\\\"target_lang\\\":\\\"\\u4e2d\\u6587\\\"}\"}, \"id\": \"L3I2XfgxNAOBvKhMTyGC0DLobH5GcTec\"}]",
    "expected": {
      "tool": "translate",
      "args": {
        "text": "Machine Learning"
      }
    },
    "actual": {
      "tool": "translate",
      "args": {
        "text": "Machine Learning",
        "target_lang": "中文"
      }
    },
    "method": "native",
    "test_name": "英译中",
    "test_description": "测试英语到中文翻译"
  },
  {
    "success": true,
    "called_tool": "translate",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"\\u6df1\\u5ea6\\u5b66\\u4e60\\\",\\\"target_lang\\\":\\\"en\\\"}\"}, \"id\": \"citkSMfkdDwricuSoqwyvwLagXqWVAv1\"}]",
    "expected": {
      "tool": "translate",
      "args": {
        "text": "深度学习"
      }
    },
    "actual": {
      "tool": "translate",
      "args": {
        "text": "深度学习",
        "target_lang": "en"
      }
    },
    "method": "native",
    "test_name": "中译英",
    "test_description": "测试中文到英语翻译"
  },
  {
    "success": true,
    "called_tool": "translate",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Hello\\\",\\\"target_lang\\\":\\\"ja\\\"}\"}, \"id\": \"kLmBTBGovZqG61CniQqNGx4zQsPZxpoT\"}]",
    "expected": {
      "tool": "translate",
      "args": {
        "text": "Hello"
      }
    },
    "actual": {
      "tool": "translate",
      "args": {
        "text": "Hello",
        "target_lang": "ja"
      }
    },
    "method": "native",
    "test_name": "多语言翻译",
    "test_description": "测试多语言翻译"
  },
  {
    "success": true,
    "called_tool": "read_file",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"read_file\", \"arguments\": \"{\\\"filename\\\":\\\"document.txt\\\"}\"}, \"id\": \"f25p6yX3cLx2TiiblnRg56RawNXOPzSX\"}]",
    "expected": {
      "tool": "read_file",
      "args": {
        "filename": "document.txt"
      }
    },
    "actual": {
      "tool": "read_file",
      "args": {
        "filename": "document.txt"
      }
    },
    "method": "native",
    "test_name": "文件读取",
    "test_description": "测试文件读取"
  },
  {
    "success": true,
    "called_tool": "send_email",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"send_email\", \"arguments\": \"{\\\"to\\\":\\\"\\u5f20\\u4e09\\\",\\\"subject\\\":\\\"\\u4f1a\\u8bae\\u5b89\\u6392\\\"}\"}, \"id\": \"QNq6Q3CdxtVjRjq3qbmpO45KdnCztwVT\"}]",
    "expected": {
      "tool": "send_email",
      "args": {
        "to": "张三",
        "subject": "会议安排"
      }
    },
    "actual": {
      "tool": "send_email",
      "args": {
        "to": "张三",
        "subject": "会议安排"
      }
    },
    "method": "native",
    "test_name": "发送邮件",
    "test_description": "测试邮件发送"
  },
  {
    "success": true,
    "called_tool": "set_reminder",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"set_reminder\", \"arguments\": \"{\\\"time\\\":\\\"10\\u5206\\u949f\\u540e\\\",\\\"content\\\":\\\"\\u559d\\u6c34\\\"}\"}, \"id\": \"lru8oEbsP491f7o2ZRfQlxzlJhIivNLg\"}]",
    "expected": {
      "tool": "set_reminder",
      "args": {
        "time": "10分钟",
        "content": "喝水"
      }
    },
    "actual": {
      "tool": "set_reminder",
      "args": {
        "time": "10分钟后",
        "content": "喝水"
      }
    },
    "method": "native",
    "test_name": "设置提醒",
    "test_description": "测试提醒设置"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 + 456\\\"}\"}, \"id\": \"LXkwBD7nHuRFwfdJdH3Yb6863xWOBsgU\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "123 + 456"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "123 + 456"
      }
    },
    "method": "native",
    "test_name": "模糊意图-数学",
    "test_description": "测试模糊的数学意图"
  },
  {
    "success": true,
    "called_tool": "get_weather_forecast",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\u5317\\u4eac\\\",\\\"days\\\":1}\"}, \"id\": \"Jv5gj9JkFS8kVjkyNbGHoDWBKiUasRg3\"}]",
    "expected": {
      "tool": "get_weather_forecast",
      "args": {
        "location": "北京",
        "days": "1"
      }
    },
    "actual": {
      "tool": "get_weather_forecast",
      "args": {
        "location": "北京",
        "days": 1
      }
    },
    "method": "native",
    "test_name": "多工具选择",
    "test_description": "测试在多个可能工具中选择"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "请问您想了解哪个城市的天气？",
    "error": "No tool call detected",
    "method": "native",
    "test_name": "上下文省略",
    "test_description": "测试省略上下文的查询"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"pi * 5^2\\\"}\"}, \"id\": \"GWG5FDTj6Oi8LytY9kU2lAmECirSexvn\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "pi * 5^2"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "pi * 5^2"
      }
    },
    "method": "native",
    "test_name": "复杂组合请求",
    "test_description": "测试复杂组合请求"
  }
]
```
