# MiroThinker-v1.5-30B.Q8_0 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | 27 |
| 通过数 | 22 |
| 失败数 | 5 |
| 准确率 | 81.5% |

## 分类统计

| 类别 | 测试数 | 通过 | 失败 | 准确率 |
|------|--------|------|------|--------|
| 信息查询 | 4 | 4 | 0 | 100.0% |
| 搜索查询 | 4 | 3 | 1 | 75.0% |
| 数学计算 | 5 | 5 | 0 | 100.0% |
| 文件操作 | 1 | 1 | 0 | 100.0% |
| 时间管理 | 4 | 2 | 2 | 50.0% |
| 系统 | 1 | 1 | 0 | 100.0% |
| 翻译 | 3 | 3 | 0 | 100.0% |
| 边界情况 | 4 | 2 | 2 | 50.0% |
| 通信 | 1 | 1 | 0 | 100.0% |

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
| 日历事件 | 时间管理 | ❌ | set_reminder | ❌ |
| 倒计时 | 时间管理 | ❌ | countdown | ❌ |
| 网页搜索 | 搜索查询 | ✅ | search | ✅ |
| 新闻查询 | 搜索查询 | ✅ | search_news | ✅ |
| 股票查询 | 搜索查询 | ❌ | get_stock_price | ❌ |
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
| 复杂组合请求 | 边界情况 | ❌ | None | ❌ |

## 失败项详情

### 日历事件

- **错误**: Unknown error
- **期望工具**: create_calendar_event
- **实际工具**: set_reminder
- **原始响应**: `[{"type": "function", "function": {"name": "set_reminder", "arguments": "{\"time\":\"\\u660e\\u5929\\u4e0b\\u53483\\u70b9\",\"content\":\"\\u660e\\u5929\\u4e0b\\u53483\\u70b9\\u7684\\u4f1a\\u8bae\\u63`

### 倒计时

- **错误**: Unknown error
- **期望工具**: countdown
- **实际工具**: countdown
- **原始响应**: `[{"type": "function", "function": {"name": "countdown", "arguments": "{\"target_date\":\"2026-02-17\"}"}, "id": "VLDn6ygYRLAVf2VHYSVYaRqHweVDlGPF"}]`

### 股票查询

- **错误**: Unknown error
- **期望工具**: get_stock_price
- **实际工具**: get_stock_price
- **原始响应**: `[{"type": "function", "function": {"name": "get_stock_price", "arguments": "{\"symbol\":\"00700\"}"}, "id": "brNaRhAkCHnUqptu8pcIrbrHJrTRsN2J"}]`

### 上下文省略

- **错误**: No tool call detected
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `请告诉我您想查询哪个城市的天气？例如：北京、上海、纽约等。`

### 复杂组合请求

- **错误**: HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)`


## 原始响应详情

```json
[
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 * 456\\\"}\"}, \"id\": \"vJfD5R23wo9Cx6csWSmIVJ2nsg5MTQBp\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"(100 + 50) * 2 / 3 - 10\\\"}\"}, \"id\": \"Wx0d54JKixe5X9ADk7lcPFfkG1eGNOHZ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sqrt(144)\\\"}\"}, \"id\": \"twIUpPs60meRVKZucX3Et79NMhSAYb3z\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sin(30*\\\\u03c0/180)\\\"}\"}, \"id\": \"53pHIHWn4gxMr5aLyb22xBPuxSDbzls3\"}]",
    "expected": {
      "tool": "calculator",
      "args": {
        "expression": "sin(30)"
      }
    },
    "actual": {
      "tool": "calculator",
      "args": {
        "expression": "sin(30*π/180)"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"unit_converter\", \"arguments\": \"{\\\"value\\\":\\\"5\\\",\\\"from_unit\\\":\\\"\\\\u7c73\\\",\\\"to_unit\\\":\\\"\\\\u5398\\\\u7c73\\\"}\"}, \"id\": \"NG40byARXCD426Rx6WFv9Zyk3aQMhZkC\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\"}\"}, \"id\": \"JQxtlXt5dgiYm6EoSQcgfjLvigCe6N5h\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e0a\\\\u6d77\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"SA1G05algRB8ugj71P8grsjm3P7b58Cb\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u7ebd\\\\u7ea6\\\"}\"}, \"id\": \"FePkXa45IMUXrIcBuiH3csSJEPEy5Xj0\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_timezone\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e1c\\\\u4eac\\\"}\"}, \"id\": \"0d24NbcXnwApwIfFZw8V4ML4kcbhqeG1\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_date\", \"arguments\": \"{}\"}, \"id\": \"y3yep0D7K68duVRnUD8XQAdGpAPcpoeJ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_time\", \"arguments\": \"{}\"}, \"id\": \"izugk1ae3PK7I99kcop8fcdCXQ7Pn0Uz\"}]",
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
    "success": false,
    "called_tool": "set_reminder",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"set_reminder\", \"arguments\": \"{\\\"time\\\":\\\"\\\\u660e\\\\u5929\\\\u4e0b\\\\u53483\\\\u70b9\\\",\\\"content\\\":\\\"\\\\u660e\\\\u5929\\\\u4e0b\\\\u53483\\\\u70b9\\\\u7684\\\\u4f1a\\\\u8bae\\\\u63d0\\\\u9192\\\"}\"}, \"id\": \"Gg4Bv761sec8Nb7cUeeyNKD0X4YTZkly\"}]",
    "expected": {
      "tool": "create_calendar_event",
      "args": {
        "title": "会议",
        "time": "明天下午3点"
      }
    },
    "actual": {
      "tool": "set_reminder",
      "args": {
        "time": "明天下午3点",
        "content": "明天下午3点的会议提醒"
      }
    },
    "method": "native",
    "test_name": "日历事件",
    "test_description": "测试日历事件创建"
  },
  {
    "success": false,
    "called_tool": "countdown",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"countdown\", \"arguments\": \"{\\\"target_date\\\":\\\"2026-02-17\\\"}\"}, \"id\": \"VLDn6ygYRLAVf2VHYSVYaRqHweVDlGPF\"}]",
    "expected": {
      "tool": "countdown",
      "args": {
        "target_date": "2026年春节"
      }
    },
    "actual": {
      "tool": "countdown",
      "args": {
        "target_date": "2026-02-17"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search\", \"arguments\": \"{\\\"query\\\":\\\"\\\\u4eba\\\\u5de5\\\\u667a\\\\u80fd\\\\u6700\\\\u65b0\\\\u8fdb\\\\u5c55\\\"}\"}, \"id\": \"nRwESeS8socBSUL4g2XuDieZ6LNsx1p4\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search_news\", \"arguments\": \"{\\\"category\\\":\\\"\\\\u79d1\\\\u6280\\\"}\"}, \"id\": \"KZAZbtcWdB2UQqk3D5tuXvBQII3lPEmD\"}]",
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
    "success": false,
    "called_tool": "get_stock_price",
    "arguments_match": false,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_stock_price\", \"arguments\": \"{\\\"symbol\\\":\\\"00700\\\"}\"}, \"id\": \"brNaRhAkCHnUqptu8pcIrbrHJrTRsN2J\"}]",
    "expected": {
      "tool": "get_stock_price",
      "args": {
        "symbol": "腾讯"
      }
    },
    "actual": {
      "tool": "get_stock_price",
      "args": {
        "symbol": "00700"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_exchange_rate\", \"arguments\": \"{\\\"from_currency\\\":\\\"USD\\\",\\\"to_currency\\\":\\\"CNY\\\",\\\"amount\\\":\\\"100\\\"}\"}, \"id\": \"H5pfxI1ufs61k1tXsRH9KvI0t8o26QGQ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Machine Learning\\\",\\\"target_lang\\\":\\\"\\\\u4e2d\\\\u6587\\\"}\"}, \"id\": \"mxwd6EI4cxCxuZUvbb9LP5irRUs7hG2G\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"\\\\u6df1\\\\u5ea6\\\\u5b66\\\\u4e60\\\",\\\"target_lang\\\":\\\"en\\\"}\"}, \"id\": \"il4MEGPUH7cg1R9lf7r8K01YYEozFaax\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Hello\\\",\\\"target_lang\\\":\\\"\\\\u65e5\\\\u8bed\\\"}\"}, \"id\": \"jopeIg3Osc1I07tBVdkgxlfbgbdeRFTv\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"read_file\", \"arguments\": \"{\\\"filename\\\":\\\"document.txt\\\"}\"}, \"id\": \"tClU9Y3bjV1397QN1oitigLwXRk0xsvw\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"send_email\", \"arguments\": \"{\\\"to\\\":\\\"\\\\u5f20\\\\u4e09\\\",\\\"subject\\\":\\\"\\\\u4f1a\\\\u8bae\\\\u5b89\\\\u6392\\\"}\"}, \"id\": \"JkwHQ6z8BwvWcWkXkIY4vRK2bL9vjvlv\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"set_reminder\", \"arguments\": \"{\\\"time\\\":\\\"10\\\\u5206\\\\u949f\\\\u540e\\\",\\\"content\\\":\\\"\\\\u559d\\\\u6c34\\\"}\"}, \"id\": \"a6QDSApHN58Veebjx0esObEJstIgjdYM\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 + 456\\\"}\"}, \"id\": \"a8L1QY3FqV5jN0orGxoeJIvgaxTpA8oQ\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"Apv6UnuBI22NZ9MNbIIXYksITgOLE5Cg\"}]",
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
    "raw_response": "请告诉我您想查询哪个城市的天气？例如：北京、上海、纽约等。",
    "error": "No tool call detected",
    "method": "native",
    "test_name": "上下文省略",
    "test_description": "测试省略上下文的查询"
  },
  {
    "success": false,
    "called_tool": null,
    "arguments_match": false,
    "raw_response": "HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)",
    "error": "HTTPConnectionPool(host='localhost', port=8400): Read timed out. (read timeout=60)",
    "method": "native",
    "test_name": "复杂组合请求",
    "test_description": "测试复杂组合请求"
  }
]
```
