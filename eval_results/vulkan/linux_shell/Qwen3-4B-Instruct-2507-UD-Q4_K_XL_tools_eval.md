# Qwen3-4B-Instruct-2507-UD-Q4_K_XL 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | 27 |
| 通过数 | 26 |
| 失败数 | 1 |
| 准确率 | 96.3% |

## 分类统计

| 类别 | 测试数 | 通过 | 失败 | 准确率 |
|------|--------|------|------|--------|
| 信息查询 | 4 | 4 | 0 | 100.0% |
| 搜索查询 | 4 | 4 | 0 | 100.0% |
| 数学计算 | 5 | 5 | 0 | 100.0% |
| 文件操作 | 1 | 1 | 0 | 100.0% |
| 时间管理 | 4 | 4 | 0 | 100.0% |
| 系统 | 1 | 1 | 0 | 100.0% |
| 翻译 | 3 | 3 | 0 | 100.0% |
| 边界情况 | 4 | 3 | 1 | 75.0% |
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

### 上下文省略

- **错误**: No tool call detected
- **期望工具**: N/A
- **实际工具**: None
- **原始响应**: `为了了解天气情况，我需要知道您具体想查询哪个城市的天气。请提供城市名称，例如“北京”、“上海”或“纽约”等。`


## 原始响应详情

```json
[
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 * 456\\\"}\"}, \"id\": \"OHBIBQBI20O5I0mJhjXRUlVrcwdwthvr\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"(100 + 50) * 2 / 3 - 10\\\"}\"}, \"id\": \"L1ANP5H8zK20wgGGffFeDiFMXP75rCTE\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sqrt(144)\\\"}\"}, \"id\": \"tFhtc4S4AvMk0DqjasJTWlTyaa4iqEDE\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"sin(30)\\\"}\"}, \"id\": \"uTKlHM3XjKV7j55X1WvvaqMz1nQ9rhME\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"unit_converter\", \"arguments\": \"{\\\"value\\\":\\\"5\\\",\\\"from_unit\\\":\\\"\\\\u7c73\\\",\\\"to_unit\\\":\\\"\\\\u5398\\\\u7c73\\\"}\"}, \"id\": \"EHgaAcYhu4spZYp0qeR4gEPyxQTy54aK\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\"}\"}, \"id\": \"E7joLBQoiiQvzM4YZ4KT4bap7Hs9Af5F\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e0a\\\\u6d77\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"EtjQR9dEy9zmGAzzpYQJVgnZSRB6SOEE\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u7ebd\\\\u7ea6\\\"}\"}, \"id\": \"CLFZKfaZKw3EhGSOxTPEGNThRC58rpPz\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_timezone\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u4e1c\\\\u4eac\\\"}\"}, \"id\": \"IyLAxfOkBkil6XjaGDFFOwdidveOUZwd\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_date\", \"arguments\": \"{}\"}, \"id\": \"1pWLGpHOekiyHTtOMeJHRT2AnkHIDqZh\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_time\", \"arguments\": \"{}\"}, \"id\": \"PjiItEeI5AkR0eLf4XORqB9NXYL65Yk8\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"create_calendar_event\", \"arguments\": \"{\\\"title\\\":\\\"\\\\u4f1a\\\\u8bae\\\",\\\"time\\\":\\\"\\\\u660e\\\\u5929\\\\u4e0b\\\\u53483\\\\u70b9\\\"}\"}, \"id\": \"dS1vYhh90igzqHXrkXiiDrkUNMHOoVtk\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"countdown\", \"arguments\": \"{\\\"target_date\\\":\\\"2026\\\\u5e74\\\\u6625\\\\u8282\\\"}\"}, \"id\": \"8HX7ctVexJu4FUZYD3vtonXP8lscNsWP\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search\", \"arguments\": \"{\\\"query\\\":\\\"\\\\u4eba\\\\u5de5\\\\u667a\\\\u80fd\\\\u6700\\\\u65b0\\\\u8fdb\\\\u5c55\\\"}\"}, \"id\": \"74zNVm7Dutbd0Xh68yn43XdM3gba2bvR\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"search_news\", \"arguments\": \"{\\\"category\\\":\\\"\\\\u79d1\\\\u6280\\\"}\"}, \"id\": \"re5YJblPDObd2ocoAxPPVD4RpF9Rx5z2\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_stock_price\", \"arguments\": \"{\\\"symbol\\\":\\\"\\\\u817e\\\\u8baf\\\"}\"}, \"id\": \"5ZTYSev50oHubOW0XI6QBAiB5oslOLwk\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_exchange_rate\", \"arguments\": \"{\\\"from_currency\\\":\\\"USD\\\",\\\"to_currency\\\":\\\"CNY\\\",\\\"amount\\\":\\\"100\\\"}\"}, \"id\": \"Cfd9xkIMtAAx14UennLpi6DrCE2eXBQu\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Machine Learning\\\",\\\"target_lang\\\":\\\"zh\\\"}\"}, \"id\": \"WeRPMxSfcMjcNSKDZmlQYVzrs2Ah5QB2\"}]",
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
        "target_lang": "zh"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"\\\\u6df1\\\\u5ea6\\\\u5b66\\\\u4e60\\\",\\\"target_lang\\\":\\\"en\\\"}\"}, \"id\": \"ye5e5Ec3cwKZUvtEIzTepeyb6SVJX9vk\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"translate\", \"arguments\": \"{\\\"text\\\":\\\"Hello\\\",\\\"target_lang\\\":\\\"ja\\\"}\"}, \"id\": \"Qruj8CeskAqGE0I83Vm1dbpZEZtSbkRg\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"read_file\", \"arguments\": \"{\\\"filename\\\":\\\"document.txt\\\"}\"}, \"id\": \"HQBxXh3N7fuOLixa2NoO8lcSieYgsh4I\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"send_email\", \"arguments\": \"{\\\"to\\\":\\\"\\\\u5f20\\\\u4e09\\\",\\\"subject\\\":\\\"\\\\u4f1a\\\\u8bae\\\\u5b89\\\\u6392\\\"}\"}, \"id\": \"iVoTjPoPuTQCFFMVNr70VZGZgtORHhoc\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"set_reminder\", \"arguments\": \"{\\\"time\\\":\\\"10\\\\u5206\\\\u949f\\\\u540e\\\",\\\"content\\\":\\\"\\\\u8bb0\\\\u5f97\\\\u559d\\\\u6c34\\\"}\"}, \"id\": \"j7XHxPhKWB0OdAn9UEsJ3uqPAabbzVOI\"}]",
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
        "content": "记得喝水"
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"123 + 456\\\"}\"}, \"id\": \"7GFOztdEjnYxuVx2JTmAlmB0e3CVmz1e\"}]",
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
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"get_weather_forecast\", \"arguments\": \"{\\\"location\\\":\\\"\\\\u5317\\\\u4eac\\\",\\\"days\\\":\\\"1\\\"}\"}, \"id\": \"eIyxGc4yhYYwTX9tX8apxmbV6rI4hcH9\"}]",
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
    "raw_response": "为了了解天气情况，我需要知道您具体想查询哪个城市的天气。请提供城市名称，例如“北京”、“上海”或“纽约”等。",
    "error": "No tool call detected",
    "method": "native",
    "test_name": "上下文省略",
    "test_description": "测试省略上下文的查询"
  },
  {
    "success": true,
    "called_tool": "calculator",
    "arguments_match": true,
    "raw_response": "[{\"type\": \"function\", \"function\": {\"name\": \"calculator\", \"arguments\": \"{\\\"expression\\\":\\\"pi * 5^2\\\"}\"}, \"id\": \"uLYJHOLoJpJqKrVNlwfJLzd39nv60m8A\"}]",
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
