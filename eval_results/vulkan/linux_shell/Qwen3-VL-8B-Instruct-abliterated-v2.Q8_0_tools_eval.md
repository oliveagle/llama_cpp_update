# Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | 27 |
| 通过数 | 23 |
| 失败数 | 4 |
| 准确率 | 85.2% |

## 分类统计

| 类别 | 测试数 | 通过 | 失败 | 准确率 |
|------|--------|------|------|--------|
| 信息查询 | 4 | 4 | 0 | 100.0% |
| 搜索查询 | 4 | 3 | 1 | 75.0% |
| 数学计算 | 5 | 5 | 0 | 100.0% |
| 文件操作 | 1 | 1 | 0 | 100.0% |
| 时间管理 | 4 | 4 | 0 | 100.0% |
| 系统 | 1 | 1 | 0 | 100.0% |
| 翻译 | 3 | 3 | 0 | 100.0% |
| 边界情况 | 4 | 2 | 2 | 50.0% |
| 通信 | 1 | 0 | 1 | 0.0% |

## 详细结果

| 测试项 | 类别 | 状态 | 调用的工具 | 参数匹配 |
|--------|------|------|-----------|---------|
| 基础计算-乘法 | 数学计算 | ✅ | calculator | ✅ |
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
| 汇率查询 | 搜索查询 | ❌ | get_exchange_rate | ❌ |
| 英译中 | 翻译 | ✅ | translate | ✅ |
| 中译英 | 翻译 | ✅ | translate | ✅ |
| 多语言翻译 | 翻译 | ✅ | translate | ✅ |
| 文件读取 | 文件操作 | ✅ | read_file | ✅ |
| 发送邮件 | 通信 | ❌ | send_email | ❌ |
| 设置提醒 | 系统 | ✅ | set_reminder | ✅ |
| 模糊意图-数学 | 边界情况 | ✅ | calculator | ✅ |
| 多工具选择 | 边界情况 | ✅ | get_weather_forecast | ✅ |
| 上下文省略 | 边界情况 | ❌ | None | ❌ |
| 复杂组合请求 | 边界情况 | ❌ | calculator | ❌ |

## 失败项详情

### 汇率查询

- **错误**: Unknown error
- **期望工具**: get_exchange_rate
- **实际工具**: get_exchange_rate
- **原始响应**: `[{"type": "function", "function": {"name": "get_exchange_rate", "arguments": "{\"from_currency\":\"\\u7f8e\\u5143\",\"to_currency\":\"\\u4eba\\u6c11\\u5e01\",\"amount\":\"100\"}"}, "id": "9mF7SohpBRUO`

### 发送邮件

- **错误**: Unknown error
- **期望工具**: send_email
- **实际工具**: send_email
- **原始响应**: `[{"type": "function", "function": {"name": "send_email", "arguments": "{\"to\":\"zhangsan@example.com\",\"subject\":\"\\u4f1a\\u8bae\\u5b89\\u6392\"}"}, "id": "8wdd1tJZ49a2Fh2stshZtFDKN7CwJ6PS"}]`

### 上下文省略

- **错误**: No tool call detected
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `请告诉我您想了解哪个城市的天气情况，我会为您查询。`

### 复杂组合请求

- **错误**: Unknown error
- **期望工具**: calculator
- **实际工具**: calculator
- **原始响应**: `[{"type": "function", "function": {"name": "calculator", "arguments": "{\"expression\":\"3.14159 * 5^2\"}"}, "id": "pTelSbqpwMXKrUjNAo2QXcjR5mBs0nRE"}]`


## 原始响应详情

```json
[
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 * 456\\\"}\"}, \"id\": \"gH0MQemnsEM18qX3i9So6BfY0TC4jHW8\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "123 * 456"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "123 * 456"
      }
    },
    "method": "native",
    "test_name": "基础计算-乘法",
    "test_description": "测试基础乘法计算"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"(100 + 50) * 2 / 3 - 10\\\"}\"}, \"id\": \"KiUnM46Xz0dZGPY8MlSFuOFGejERBVaS\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sqrt(144)\\\"}\"}, \"id\": \"gKHXvcYGcKjOPyN72uvyoGo3IUGXYfRP\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sin(30)\\\"}\"}, \"id\": \"PoDv0lt3Edmm1KOphelf3s2GxqRH13Dt\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"unit_converter\", \"arguments\": \"{\\\"value\\\":\\\"5\\\",\\\"from_unit\\\":\\\"\\\\u7c73\\\",\\\"to_unit\\\":\\\"\\\\u5398\\\\u7c73\\\"}\"}, \"id\": \"hEqB8ln0OLHzek794dVH24DBhwqpgvmx\"}]",
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
        "value": "5",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\"}\"}, \"id\": \"0w4WAHH2WCkQcnBUwjS2bU41n9QEm5XJ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e0a\\\\u6d77\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"duchkc7OLiEM5qUcXwjawLYxL5ByiRld\"}]",
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
        "days": "1"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u7ebd\\\\u7ea6\\\"}\"}, \"id\": \"PL6ZsICnr4CVQpweGGbyJzZH2kmcVBKD\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_timezone\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e1c\\\\u4eac\\\"}\"}, \"id\": \"M3TUVI1eBf74KQxDQg5fBFH8yd8CPy8E\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_date\", \"arguments\": \"{}\"}, \"id\": \"Sc11q23GlOXs4EaKD2Y2Ak3B0TOoOISb\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_time\", \"arguments\": \"{}\"}, \"id\": \"lfolzbetyynrJEHBKBkNw9xh42Pyd3sJ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"create_calendar_event\", \"arguments\": \"{\\\"title\\\":\\\"\\\\u4f1a\\\\u8bae\\\",\\\"time\\\":\\\"\\\\u660e\\\\u5929\\\\u4e0b\\\\u53483\\\\u70b9\\\"}\"}, \"id\": \"vaXhl62s5VnDiyMJdzXlgPyZNj5S42hj\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"countdown\", \"arguments\": \"{\\\"target_date\\\":\\\"2026\\\\u5e74\\\\u6625\\\\u8282\\\"}\"}, \"id\": \"3urIi1set2mDKv4UAG3UAgPBQEokkO4a\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search\", \"arguments\": \"{\\\"query\\\":\\\"\\\\u4eba\\\\u5de5\\\\u667a\\\\u80fd\\\\u6700\\\\u65b0\\\\u8fdb\\\\u5c55\\\"}\"}, \"id\": \"ckmgQajA0LQ9AubcOs06xlK5MZYTFud3\"}]",
    "expected": {
      "tool": "search",
      "args": {
        "query": "人工智能"
      }
    },
    "actual": {
      "tool": "search",
      "args": {
        "query": "人工智能最新进展"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search_news\", \"arguments\": \"{\\\"category\\\":\\\"\\\\u79d1\\\\u6280\\\"}\"}, \"id\": \"ade5lZTO7hQhGo6POyJW1o2Il5F47moC\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_stock_price\", \"arguments\": \"{\\\"symbol\\\":\\\"\\\\u817e\\\\u8baf\\\"}\"}, \"id\": \"J3ghw6aBtvJcicDZoHtDA62MOQtZQRpI\"}]",
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
    "success": false,
    "called_tool": "get_exchange_rate",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_exchange_rate\", \"arguments\": \"{\\\"from_currency\\\":\\\"\\\\u7f8e\\\\u5143\\\",\\\"to_currency\\\":\\\"\\\\u4eba\\\\u6c11\\\\u5e01\\\",\\\"amount\\\":\\\"100\\\"}\"}, \"id\": \"9mF7SohpBRUOGFeZKrMGQdFQ8s8lIXWR\"}]",
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
        "from_currency": "美元",
        "to_currency": "人民币",
        "amount": "100"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Machine Learning\\\",\\\"target_lang\\\":\\\"\\\\u4e2d\\\\u6587\\\"}\"}, \"id\": \"aTRMEz4HwrJwxFrWSeYTaCCdS1xbTXRu\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"\\\\u6df1\\\\u5ea6\\\\u5b66\\\\u4e60\\\",\\\"target_lang\\\":\\\"\\\\u82f1\\\\u8bed\\\"}\"}, \"id\": \"vpBPOIWZTL0ZnNpzaQWMAEKOaEConUnr\"}]",
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
        "target_lang": "英语"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Hello\\\",\\\"target_lang\\\":\\\"\\\\u65e5\\\\u8bed\\\"}\"}, \"id\": \"eoXOFXizZdKZOiRoE2zHdEVzE12PuCq9\"}]",
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
        "target_lang": "日语"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"read_file\", \"arguments\": \"{\\\"filename\\\":\\\"document.txt\\\"}\"}, \"id\": \"5LE0Wb4AkD14Av6ZXukrLtjWCfw4ajIB\"}]",
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
    "success": false,
    "called_tool": "send_email",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"send_email\", \"arguments\": \"{\\\"to\\\":\\\"zhangsan@example.com\\\",\\\"subject\\\":\\\"\\\\u4f1a\\\\u8bae\\\\u5b89\\\\u6392\\\"}\"}, \"id\": \"8wdd1tJZ49a2Fh2stshZtFDKN7CwJ6PS\"}]",
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
        "to": "zhangsan@example.com",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"set_reminder\", \"arguments\": \"{\\\"time\\\":\\\"10\\\\u5206\\\\u949f\\\\u540e\\\",\\\"content\\\":\\\"\\\\u559d\\\\u6c34\\\"}\"}, \"id\": \"x1QpYNGzzRBmP16dEQaznVNWCakWZXI2\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 + 456\\\"}\"}, \"id\": \"io3odQzNgVfVORFJKDPFYj6DmBmQN2J9\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"EzaqTouh3n6MSGIwcAfKAwiXxsLsBaJi\"}]",
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
        "days": "1"
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
    "raw_response": "请告诉我您想了解哪个城市的天气情况，我会为您查询。",
    "error": "No tool call detected",
    "method": "native",
    "test_name": "上下文省略",
    "test_description": "测试省略上下文的查询"
  },
  {
    "success": false,
    "called_tool": "calculator",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"3.14159 * 5^2\\\"}\"}, \"id\": \"pTelSbqpwMXKrUjNAo2QXcjR5mBs0nRE\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "pi * 5^2"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "3.14159 * 5^2"
      }
    },
    "method": "native",
    "test_name": "复杂组合请求",
    "test_description": "测试复杂组合请求"
  }
]
```
