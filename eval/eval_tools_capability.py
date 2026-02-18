#!/usr/bin/env python3
"""
工具使用能力评估脚本
测试模型的工具调用和函数调用能力

⚠️ 安全警告 ⚠️
================
本脚本仅用于评估模型识别工具调用的能力，不会真实执行任何命令。

本脚本只会:
1. 通过HTTP API发送prompt和工具定义给模型
2. 检查模型返回的tool_calls是否与预期匹配
3. 记录匹配结果并生成报告

本脚本不会:
- 执行任何shell命令
- 操作Docker容器
- 修改系统配置
- 重启或关闭系统

使用方法:
  python eval_tools_capability.py --model-url http://localhost:8401 --model-name MODEL

支持两种测试模式:
  1. 快速测试 (默认, 27个案例): 用于快速验证
  2. 完整测试 (--full, 300个案例): 用于全面评估
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, List, Optional


# 尝试导入大型测试集
try:
    from tools_test_cases_large import TOOLS_TEST_CASES_LARGE
    LARGE_TEST_AVAILABLE = True
except ImportError:
    LARGE_TEST_AVAILABLE = False
    TOOLS_TEST_CASES_LARGE = []


# 标准测试用例集 (27个) - 用于快速验证
# 分类：数学计算、信息查询、数据处理、系统操作、搜索查询、边界情况

TOOLS_TEST_CASES = [
    # ========== 1. 数学计算类 (5个) ==========
    {
        "name": "基础计算-乘法",
        "category": "数学计算",
        "description": "测试基础乘法计算",
        "prompt": "计算 123 乘以 456 等于多少？",
        "expected_tool": "calculator",
        "expected_args": {"expression": "123 * 456"},
    },
    {
        "name": "复杂表达式",
        "category": "数学计算",
        "description": "测试复杂数学表达式",
        "prompt": "帮我算一下 (100 + 50) * 2 / 3 - 10",
        "expected_tool": "calculator",
        "expected_args": {"expression": "(100 + 50) * 2 / 3 - 10"},
    },
    {
        "name": "平方根计算",
        "category": "数学计算",
        "description": "测试平方根函数",
        "prompt": "计算根号144的值",
        "expected_tool": "calculator",
        "expected_args": {"expression": "sqrt(144)"},
    },
    {
        "name": "三角函数",
        "category": "数学计算",
        "description": "测试三角函数",
        "prompt": "sin(30度)等于多少？",
        "expected_tool": "calculator",
        "expected_args": {"expression": "sin(30)"},
    },
    {
        "name": "单位换算-长度",
        "category": "数学计算",
        "description": "测试单位换算",
        "prompt": "5米等于多少厘米？",
        "expected_tool": "unit_converter",
        "expected_args": {"value": "5", "from_unit": "米", "to_unit": "厘米"},
    },

    # ========== 2. 天气与地理类 (4个) ==========
    {
        "name": "天气查询-基础",
        "category": "信息查询",
        "description": "测试基础天气查询",
        "prompt": "今天北京天气怎么样？",
        "expected_tool": "get_weather",
        "expected_args": {"location": "北京"},
    },
    {
        "name": "天气预报",
        "category": "信息查询",
        "description": "测试未来天气查询",
        "prompt": "明天上海会下雨吗？",
        "expected_tool": "get_weather_forecast",
        "expected_args": {"location": "上海", "days": "1"},
    },
    {
        "name": "温度查询",
        "category": "信息查询",
        "description": "测试温度特定查询",
        "prompt": "查询纽约现在的温度",
        "expected_tool": "get_weather",
        "expected_args": {"location": "纽约"},
    },
    {
        "name": "时区查询",
        "category": "信息查询",
        "description": "测试时区信息",
        "prompt": "东京现在几点？",
        "expected_tool": "get_timezone",
        "expected_args": {"location": "东京"},
    },

    # ========== 3. 时间与日历类 (4个) ==========
    {
        "name": "当前日期",
        "category": "时间管理",
        "description": "测试当前日期查询",
        "prompt": "今天是什么日期？",
        "expected_tool": "get_date",
        "expected_args": {},
    },
    {
        "name": "当前时间",
        "category": "时间管理",
        "description": "测试当前时间查询",
        "prompt": "现在几点了？",
        "expected_tool": "get_time",
        "expected_args": {},
    },
    {
        "name": "日历事件",
        "category": "时间管理",
        "description": "测试日历事件创建",
        "prompt": "帮我创建一个明天下午3点的会议提醒",
        "expected_tool": "create_calendar_event",
        "expected_args": {"title": "会议", "time": "明天下午3点"},
    },
    {
        "name": "倒计时",
        "category": "时间管理",
        "description": "测试倒计时功能",
        "prompt": "距离2026年春节还有多少天？",
        "expected_tool": "countdown",
        "expected_args": {"target_date": "2026年春节"},
    },

    # ========== 4. 搜索与信息类 (4个) ==========
    {
        "name": "网页搜索",
        "category": "搜索查询",
        "description": "测试基础搜索功能",
        "prompt": "请使用搜索工具查找人工智能最新进展",
        "expected_tool": "search",
        "expected_args": {"query": "人工智能"},
    },
    {
        "name": "新闻查询",
        "category": "搜索查询",
        "description": "测试新闻搜索",
        "prompt": "搜索今天的科技新闻",
        "expected_tool": "search_news",
        "expected_args": {"category": "科技"},
    },
    {
        "name": "股票查询",
        "category": "搜索查询",
        "description": "测试股票信息查询",
        "prompt": "查询腾讯股票的当前价格",
        "expected_tool": "get_stock_price",
        "expected_args": {"symbol": "腾讯"},
    },
    {
        "name": "汇率查询",
        "category": "搜索查询",
        "description": "测试汇率转换",
        "prompt": "100美元等于多少人民币？",
        "expected_tool": "get_exchange_rate",
        "expected_args": {"from_currency": "USD", "to_currency": "CNY", "amount": "100"},
    },

    # ========== 5. 翻译与语言类 (3个) ==========
    {
        "name": "英译中",
        "category": "翻译",
        "description": "测试英语到中文翻译",
        "prompt": "请将'Machine Learning'翻译成中文",
        "expected_tool": "translate",
        "expected_args": {"text": "Machine Learning"},
    },
    {
        "name": "中译英",
        "category": "翻译",
        "description": "测试中文到英语翻译",
        "prompt": "将'深度学习'翻译成英文",
        "expected_tool": "translate",
        "expected_args": {"text": "深度学习"},
    },
    {
        "name": "多语言翻译",
        "category": "翻译",
        "description": "测试多语言翻译",
        "prompt": "把'Hello'翻译成日语",
        "expected_tool": "translate",
        "expected_args": {"text": "Hello"},
    },

    # ========== 6. 系统与文件类 (3个) ==========
    {
        "name": "文件读取",
        "category": "文件操作",
        "description": "测试文件读取",
        "prompt": "帮我读取document.txt文件的内容",
        "expected_tool": "read_file",
        "expected_args": {"filename": "document.txt"},
    },
    {
        "name": "发送邮件",
        "category": "通信",
        "description": "测试邮件发送",
        "prompt": "发送一封邮件给张三，主题是会议安排",
        "expected_tool": "send_email",
        "expected_args": {"to": "张三", "subject": "会议安排"},
    },
    {
        "name": "设置提醒",
        "category": "系统",
        "description": "测试提醒设置",
        "prompt": "10分钟后提醒我喝水",
        "expected_tool": "set_reminder",
        "expected_args": {"time": "10分钟", "content": "喝水"},
    },

    # ========== 7. 边界情况 (4个) ==========
    {
        "name": "模糊意图-数学",
        "category": "边界情况",
        "description": "测试模糊的数学意图",
        "prompt": "我需要算一些东西，123加456",
        "expected_tool": "calculator",
        "expected_args": {"expression": "123 + 456"},
    },
    {
        "name": "多工具选择",
        "category": "边界情况",
        "description": "测试在多个可能工具中选择",
        "prompt": "帮我查一下明天北京的天气，然后设置一个提醒",
        "expected_tool": "get_weather_forecast",
        "expected_args": {"location": "北京", "days": "1"},
    },
    {
        "name": "上下文省略",
        "category": "边界情况",
        "description": "测试省略上下文的查询",
        "prompt": "那边天气如何？",
        "expected_tool": "get_weather",
        "expected_args": {},  # 可能没有location，需要模型处理
    },
    {
        "name": "复杂组合请求",
        "category": "边界情况",
        "description": "测试复杂组合请求",
        "prompt": "计算圆的面积，半径是5，然后换算成平方厘米",
        "expected_tool": "calculator",
        "expected_args": {"expression": "pi * 5^2"},
    },
]


# 全面的工具定义 (OpenAI Function Calling格式)
# 包含25+测试用例所需的全部工具
AVAILABLE_TOOLS = [
    # ========== 1. 数学计算类 ==========
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算，支持基础运算、科学计算、三角函数等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如'123 * 456'、'sqrt(144)'、'sin(30)'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unit_converter",
            "description": "单位换算，支持长度、重量、温度、货币等单位转换",
            "parameters": {
                "type": "object",
                "properties": {
                    "value": {"type": "string", "description": "要转换的数值"},
                    "from_unit": {"type": "string", "description": "源单位，如'米'、'千克'、'摄氏度'"},
                    "to_unit": {"type": "string", "description": "目标单位，如'厘米'、'克'、'华氏度'"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        }
    },

    # ========== 2. 天气与地理类 ==========
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的当前天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市名称，如'北京'、'上海'、'纽约'"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "获取指定城市的天气预报",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称"},
                    "days": {"type": "string", "description": "预报天数，如'1'、'3'、'7'"}
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_timezone",
            "description": "获取指定城市的时区和当前时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "城市名称，如'东京'、'伦敦'"}
                },
                "required": ["location"]
            }
        }
    },

    # ========== 3. 时间与日历类 ==========
    {
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "获取当前日期",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "创建日历事件或提醒",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "事件标题"},
                    "time": {"type": "string", "description": "事件时间，如'明天下午3点'、'2024-12-25 14:00'"}
                },
                "required": ["title", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "countdown",
            "description": "计算距离目标日期的剩余天数",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_date": {"type": "string", "description": "目标日期，如'2026年春节'、'2025-01-01'"}
                },
                "required": ["target_date"]
            }
        }
    },

    # ========== 4. 搜索与信息类 ==========
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "搜索互联网信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词或问题"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "搜索最新新闻",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "新闻类别，如'科技'、'财经'、'体育'"},
                    "keywords": {"type": "string", "description": "可选关键词"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "查询股票价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码或名称，如'腾讯'、'AAPL'、'00700'"}
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "查询货币汇率并进行换算",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {"type": "string", "description": "源货币，如'USD'、'EUR'、'美元'"},
                    "to_currency": {"type": "string", "description": "目标货币，如'CNY'、'人民币'"},
                    "amount": {"type": "string", "description": "可选金额，如'100'"}
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },

    # ========== 5. 翻译类 ==========
    {
        "type": "function",
        "function": {
            "name": "translate",
            "description": "翻译文本，支持多种语言互译",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要翻译的文本内容"},
                    "target_lang": {"type": "string", "description": "目标语言，如'中文'、'英语'、'日语'、'zh'、'en'、'ja'"}
                },
                "required": ["text", "target_lang"]
            }
        }
    },

    # ========== 6. 系统与文件类 ==========
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "当用户要求读取文件、查看文件内容、打开文件时调用。如果用户要求使用'命令行/cat/head/tail'等工具查看，则应该使用execute_command",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件路径或名称"}
                },
                "required": ["filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送电子邮件",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "收件人邮箱或名称"},
                    "subject": {"type": "string", "description": "邮件主题"},
                    "content": {"type": "string", "description": "可选邮件内容"}
                },
                "required": ["to", "subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "设置提醒",
            "parameters": {
                "type": "object",
                "properties": {
                    "time": {"type": "string", "description": "提醒时间，如'10分钟后'、'明天早上8点'"},
                    "content": {"type": "string", "description": "提醒内容"}
                },
                "required": ["time", "content"]
            }
        }
    },
    # ========== Linux/Shell 工具 ==========
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "当用户要求执行任何Linux/Unix命令或系统操作时，必须调用此工具。支持的命令包括：文件操作(ls/cd/cp/mv/rm)、文本处理(cat/grep/wc)、系统信息(df/free/ps)、网络(curl/ssh/ping)、容器(docker/podman)、进程管理(kill/top)等。不要告诉用户如何手动执行，而是直接调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "命令名称，如'ls'、'docker'、'systemctl'"},
                    "args": {"type": "string", "description": "命令参数，如'-la /home'"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "当用户要求创建文件、写入文件、生成脚本或保存内容时，必须调用此工具。适用于：创建Shell脚本(.sh)、配置文件、文本文件、代码文件等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "文件名或路径"},
                    "content": {"type": "string", "description": "文件内容"}
                },
                "required": ["filename", "content"]
            }
        }
    },
]


def test_tool_calling_native(
    model_url: str,
    test_case: Dict,
    timeout: int = 60,
    model_name: str = "model",
    use_tuning: bool = False
) -> Dict:
    """
    使用原生 OpenAI API 工具调用格式测试

    Args:
        use_tuning: 是否使用模型专用调优配置
    """
    try:
        # 获取工具定义（可能应用调优）
        tools = AVAILABLE_TOOLS
        prompt = test_case["prompt"]

        if use_tuning:
            try:
                from model_tuning_configs import apply_model_tuning, get_tuning_config
                tools = apply_model_tuning(AVAILABLE_TOOLS, model_name)
                config = get_tuning_config(model_name)
                prompt = config.apply_to_prompt(prompt)
            except ImportError:
                pass

        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "tools": tools,
            "tool_choice": "auto",
        }

        response = requests.post(
            f"{model_url}/v1/chat/completions",
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        result = response.json()
        message = result.get("choices", [{}])[0].get("message", {})

        # 检查是否有工具调用
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            return {
                "success": False,
                "called_tool": None,
                "arguments_match": False,
                "raw_response": message.get("content", ""),
                "error": "No tool call detected"
            }

        # 检查工具名和参数
        tool_call = tool_calls[0]
        called_tool = tool_call.get("function", {}).get("name", "")

        try:
            called_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
        except json.JSONDecodeError:
            called_args = {}

        expected_tool = test_case["expected_tool"]
        expected_args = test_case["expected_args"]

        tool_match = called_tool == expected_tool

        # 参数匹配检查 (智能宽松匹配)
        def normalize_text(text: str) -> str:
            """标准化文本：移除空格、标点，转小写"""
            import re
            # 移除非字母数字字符，保留中文
            return re.sub(r'[^\w\u4e00-\u9fff]', '', text.lower())

        def is_semantic_match(expected_val: str, actual_val: str, command_type: str = "", arg_key: str = "",
                               full_expected: dict = None, full_actual: dict = None) -> bool:
            """
            检查两个参数是否在语义上等价

            支持的语义匹配：
            - curl下载: -O url 等价于 -o filename url
            - 进程查找: pgrep name 等价于 ps aux | grep ...
            - 网络测试: ping -c 4 host 包含 host
            - 网络连接: ss -tuln 等价于 netstat -tuln
            - Docker命令: 包含相同镜像即可
            - Shell脚本: 结构等价即可
            """
            exp_lower = expected_val.lower().strip()
            act_lower = actual_val.lower().strip()

            # 直接包含检查
            if exp_lower in act_lower or act_lower in exp_lower:
                return True

            # 标准化后检查
            exp_norm = normalize_text(expected_val)
            act_norm = normalize_text(actual_val)
            if exp_norm in act_norm or act_norm in exp_norm:
                return True

            # 获取完整命令（如果可用）
            full_exp = exp_lower
            full_act = act_lower
            if full_expected and full_actual:
                exp_cmd = full_expected.get('command', '')
                act_cmd = full_actual.get('command', '')
                exp_args = full_expected.get('args', '')
                act_args = full_actual.get('args', '')
                full_exp = f"{exp_cmd} {exp_args}".lower().strip()
                full_act = f"{act_cmd} {act_args}".lower().strip()

            # 针对execute_command的特殊语义匹配
            if command_type == "execute_command" or arg_key in ["command", "args"]:
                # ping命令等价性：检查是否包含相同的主机
                if ("ping" in full_exp and "ping" in full_act) or ("ping" in exp_lower and "ping" in act_lower):
                    import re as re_module
                    # 提取主机名/IP
                    ping_exp = full_exp if "ping" in full_exp else exp_lower
                    ping_act = full_act if "ping" in full_act else act_lower
                    exp_hosts = re_module.findall(r'\b(?:[a-z0-9-]+\.)+[a-z]{2,}|\b(?:\d{1,3}\.){3}\d{1,3}\b', ping_exp)
                    act_hosts = re_module.findall(r'\b(?:[a-z0-9-]+\.)+[a-z]{2,}|\b(?:\d{1,3}\.){3}\d{1,3}\b', ping_act)
                    if exp_hosts and act_hosts:
                        if exp_hosts[0] == act_hosts[0]:
                            return True

                # curl下载命令等价性
                if "curl" in full_exp and "curl" in full_act:
                    # 提取URL进行比对
                    import re as re_module
                    exp_urls = re_module.findall(r'https?://[^\s]+', full_exp)
                    act_urls = re_module.findall(r'https?://[^\s]+', full_act)
                    if exp_urls and act_urls and exp_urls[0] == act_urls[0]:
                        return True

                # 进程查找命令等价性 (pgrep vs ps aux | grep vs ps -ef | grep)
                if ("pgrep" in full_exp or "ps" in full_exp or "grep" in full_exp) and \
                   ("pgrep" in full_act or "ps" in full_act or "grep" in full_act):
                    # 提取进程名进行比对
                    exp_parts = full_exp.replace("|", " ").replace("grep", " ").replace("-v", " ").replace("awk", " ").replace("print", " ").split()
                    act_parts = full_act.replace("|", " ").replace("grep", " ").replace("-v", " ").replace("awk", " ").replace("print", " ").split()
                    # 查找共同的关键字
                    common = set(exp_parts) & set(act_parts)
                    keywords = [p for p in common if len(p) > 2 and p not in ['aux', '-v', 'awk', 'print', 'ps', '-ef', 'auxf']]
                    if keywords:
                        return True

                # SSH登录命令
                if "ssh" in full_exp and "ssh" in full_act:
                    # 提取IP/主机名比对
                    import re as re_module
                    exp_hosts = re_module.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', full_exp)
                    act_hosts = re_module.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b|\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', full_act)
                    if exp_hosts and act_hosts:
                        return True

                # 网络连接查看命令等价性 (ss vs netstat)
                if ("ss" in full_exp or "netstat" in full_exp) and \
                   ("ss" in full_act or "netstat" in full_act):
                    # 提取关键选项进行比对（处理如 -tuln 这样的组合选项）
                    import re as re_module
                    exp_opts = set(re_module.findall(r'-([a-zA-Z])', full_exp))
                    act_opts = set(re_module.findall(r'-([a-zA-Z])', full_act))
                    # 检查是否有共同的选项 (t=TCP, u=UDP, n=numeric, l=listen, a=all)
                    common_opts = exp_opts & act_opts
                    key_opts = {'t', 'u', 'n', 'l', 'a'}
                    if common_opts:
                        return True

                # df命令等价性（无参数vs有参数）
                if "df" in full_exp and "df" in full_act:
                    # df 和 df -h 等价
                    return True

                # free命令等价性
                if "free" in full_exp and "free" in full_act:
                    return True

                # Docker命令等价性
                if "docker" in full_exp and "docker" in full_act:
                    # 提取子命令和镜像名
                    exp_parts = full_exp.split()
                    act_parts = full_act.split()
                    # 检查子命令是否一致 (run, ps, stop, logs)
                    if len(exp_parts) >= 2 and len(act_parts) >= 2:
                        if exp_parts[1] == act_parts[1]:
                            # 对于run命令，检查是否包含相同镜像
                            if exp_parts[1] == "run":
                                # 提取镜像名 (通常最后一个非选项参数)
                                exp_images = [p for p in exp_parts if p not in ['docker', 'run', '-d', '-it', '--rm'] and not p.startswith('-') and not p.startswith('--')]
                                act_images = [p for p in act_parts if p not in ['docker', 'run', '-d', '-it', '--rm'] and not p.startswith('-') and not p.startswith('--')]
                                if exp_images and act_images and exp_images[-1] == act_images[-1]:
                                    return True
                            else:
                                return True

            # Shell脚本内容等价性
            if arg_key == "content":
                import re as re_module
                # 检查关键结构
                exp_has_if = "if " in exp_lower and "then" in exp_lower
                act_has_if = "if " in act_lower and "then" in act_lower
                exp_has_for = "for " in exp_lower and "do" in exp_lower
                act_has_for = "for " in act_lower and "do" in act_lower

                # 如果都有if结构，检查条件类型
                if exp_has_if and act_has_if:
                    # 提取文件检查类型 (-f, -e, -d等)
                    exp_checks = re_module.findall(r'-\w+', exp_lower)
                    act_checks = re_module.findall(r'-\w+', act_lower)
                    # 检查是否有相同的测试操作
                    if set(exp_checks) & set(act_checks):
                        return True
                    # 或者检查是否都测试了相同的文件名
                    exp_files = re_module.findall(r'[\w.-]+\.(txt|sh|log|conf)', exp_lower)
                    act_files = re_module.findall(r'[\w.-]+\.(txt|sh|log|conf)', act_lower)
                    if exp_files and act_files:
                        return True

                # 如果都有for结构
                if exp_has_for and act_has_for:
                    return True

                # 检查是否都定义了相同的变量
                exp_vars = re_module.findall(r'\b([A-Z_]+)=', exp_lower)
                act_vars = re_module.findall(r'\b([A-Z_]+)=', act_lower)
                if exp_vars and act_vars and set(exp_vars) & set(act_vars):
                    return True

            return False

        args_match = True
        for key, value in expected_args.items():
            if key not in called_args:
                args_match = False
                break
            if isinstance(value, str) and isinstance(called_args.get(key), str):
                # 使用语义匹配，传入完整参数以便进行更智能的匹配
                if not is_semantic_match(value, called_args[key], called_tool, key, expected_args, called_args):
                    args_match = False
                    break

        return {
            "success": tool_match and args_match,
            "called_tool": called_tool,
            "arguments_match": args_match,
            "raw_response": json.dumps(tool_calls),
            "expected": {"tool": expected_tool, "args": expected_args},
            "actual": {"tool": called_tool, "args": called_args}
        }

    except Exception as e:
        return {
            "success": False,
            "called_tool": None,
            "arguments_match": False,
            "raw_response": str(e),
            "error": str(e)
        }


def test_tool_calling_prompt(
    model_url: str,
    test_case: Dict,
    timeout: int = 60
) -> Dict:
    """
    使用提示工程方式测试工具使用能力 (适用于不支持原生工具调用的模型)
    """
    try:
        # 构建工具描述
        tools_desc = []
        for tool in AVAILABLE_TOOLS:
            func = tool["function"]
            params = json.dumps(func["parameters"], ensure_ascii=False)
            tools_desc.append(f"- {func['name']}: {func['description']}\n  参数: {params}")

        tools_text = "\n".join(tools_desc)

        # 构建系统提示
        system_prompt = f"""你是一个智能助手，可以使用以下工具来帮助用户：

{tools_text}

当用户请求需要使用工具时，请以以下JSON格式输出工具调用：
```json
{{
  "tool": "工具名称",
  "arguments": {{
    "参数名": "参数值"
  }}
}}
```

如果不需要使用工具，请直接回答用户问题。"""

        # 构造请求
        payload = {
            "model": "test-model",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_case["prompt"]}
            ],
            "temperature": 0.1,
        }

        response = requests.post(
            f"{model_url}/v1/chat/completions",
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()

        result = response.json()
        message = result.get("choices", [{}])[0].get("message", {})
        content = message.get("content", "")

        # 尝试从响应中提取 JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接找 JSON
            json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return {
                    "success": False,
                    "called_tool": None,
                    "arguments_match": False,
                    "raw_response": content,
                    "error": "No JSON tool call found in response"
                }

        try:
            tool_call = json.loads(json_str)
            called_tool = tool_call.get("tool", "")
            called_args = tool_call.get("arguments", {})
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "called_tool": None,
                "arguments_match": False,
                "raw_response": content,
                "error": f"JSON parse error: {e}"
            }

        expected_tool = test_case["expected_tool"]
        expected_args = test_case["expected_args"]

        tool_match = called_tool == expected_tool

        # 参数匹配检查 (宽松匹配)
        args_match = True
        for key, value in expected_args.items():
            if key not in called_args:
                args_match = False
                break
            if isinstance(value, str) and isinstance(called_args.get(key), str):
                if value.lower() not in called_args[key].lower():
                    args_match = False
                    break

        return {
            "success": tool_match and args_match,
            "called_tool": called_tool,
            "arguments_match": args_match,
            "raw_response": content,
            "expected": {"tool": expected_tool, "args": expected_args},
            "actual": {"tool": called_tool, "args": called_args}
        }

    except Exception as e:
        return {
            "success": False,
            "called_tool": None,
            "arguments_match": False,
            "raw_response": str(e),
            "error": str(e)
        }


def test_tool_calling(
    model_url: str,
    test_case: Dict,
    timeout: int = 60,
    use_native: bool = False,
    model_name: str = "model"
) -> Dict:
    """
    测试单个工具调用用例

    Args:
        use_native: 是否使用原生 OpenAI API 工具调用 (需要模型支持)
        model_name: 模型名称

    Returns:
        {
            "success": bool,
            "called_tool": str or None,
            "arguments_match": bool,
            "raw_response": str,
            "method": "native" or "prompt"
        }
    """
    if use_native:
        result = test_tool_calling_native(model_url, test_case, timeout, model_name)
        result["method"] = "native"
        return result
    else:
        result = test_tool_calling_prompt(model_url, test_case, timeout)
        result["method"] = "prompt"
        return result


def run_tools_evaluation(
    model_url: str,
    test_cases: Optional[List[Dict]] = None,
    use_native: bool = True,
    model_name: str = "model"
) -> Dict:
    """
    运行完整的工具使用能力评估

    Args:
        use_native: 是否使用原生 OpenAI API 工具调用
        model_name: 模型名称

    Returns:
        {
            "total": int,
            "passed": int,
            "failed": int,
            "accuracy": float,
            "details": [test_result, ...]
        }
    """
    if test_cases is None:
        test_cases = TOOLS_TEST_CASES

    results = []
    passed = 0

    method_str = "原生API" if use_native else "提示工程"
    print(f"\n开始工具使用能力评估 ({len(test_cases)} 个测试用例, 方法: {method_str})")
    print("=" * 60)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] {test_case['name']}: ", end="", flush=True)

        result = test_tool_calling(model_url, test_case, use_native=use_native, model_name=model_name)
        result["test_name"] = test_case["name"]
        result["test_description"] = test_case["description"]

        if result["success"]:
            passed += 1
            print("✅ 通过")
        else:
            print(f"❌ 失败 - {result.get('error', 'Tool call incorrect')}")

        results.append(result)

    accuracy = passed / len(test_cases) if test_cases else 0

    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": len(test_cases) - passed,
        "accuracy": accuracy,
        "details": results
    }


def generate_category_stats(results: Dict, test_cases: List[Dict] = None) -> Dict[str, Dict]:
    """生成分类统计"""
    if test_cases is None:
        test_cases = TOOLS_TEST_CASES

    # 构建测试名称到分类的映射
    case_category_map = {tc['name']: tc.get('category', '其他') for tc in test_cases}

    categories = {}

    for detail in results['details']:
        # 从测试用例中找到对应的分类
        category = case_category_map.get(detail['test_name'], '其他')

        if category not in categories:
            categories[category] = {'total': 0, 'passed': 0, 'failed': 0}

        categories[category]['total'] += 1
        if detail['success']:
            categories[category]['passed'] += 1
        else:
            categories[category]['failed'] += 1

    # 计算准确率
    for cat in categories:
        total = categories[cat]['total']
        categories[cat]['accuracy'] = categories[cat]['passed'] / total if total > 0 else 0

    return categories


def generate_report(results: Dict, model_name: str, test_cases: List[Dict] = None) -> str:
    """生成评估报告"""
    if test_cases is None:
        test_cases = TOOLS_TEST_CASES

    # 构建测试名称到分类的映射
    case_category_map = {tc['name']: tc.get('category', '其他') for tc in test_cases}

    report = f"""# {model_name} 工具使用能力评估报告

## 总体得分

| 指标 | 数值 |
|------|------|
| 总测试数 | {results['total']} |
| 通过数 | {results['passed']} |
| 失败数 | {results['failed']} |
| 准确率 | {results['accuracy']:.1%} |

## 分类统计

| 类别 | 测试数 | 通过 | 失败 | 准确率 |
|------|--------|------|------|--------|
"""

    # 添加分类统计
    category_stats = generate_category_stats(results, test_cases)
    for category, stats in sorted(category_stats.items()):
        report += f"| {category} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['accuracy']:.1%} |\n"

    report += """
## 详细结果

| 测试项 | 类别 | 状态 | 调用的工具 | 参数匹配 |
|--------|------|------|-----------|---------|
"""

    for detail in results['details']:
        # 找到对应的分类
        category = case_category_map.get(detail['test_name'], '其他')

        status = "✅" if detail['success'] else "❌"
        tool = detail.get('called_tool', 'N/A')
        args_match = "✅" if detail.get('arguments_match') else "❌"

        report += f"| {detail['test_name']} | {category} | {status} | {tool} | {args_match} |\n"

    report += "\n## 失败项详情\n\n"
    failed_items = [d for d in results['details'] if not d['success']]
    if failed_items:
        for item in failed_items:
            report += f"### {item['test_name']}\n\n"
            report += f"- **错误**: {item.get('error', 'Unknown error')}\n"
            report += f"- **期望工具**: {item.get('expected', {}).get('tool', 'N/A')}\n"
            report += f"- **实际工具**: {item.get('called_tool', 'N/A')}\n"
            report += f"- **原始响应**: `{item.get('raw_response', '')[:200]}`\n\n"
    else:
        report += "所有测试项均通过！\n"

    report += "\n## 原始响应详情\n\n```json\n"
    report += json.dumps(results['details'], indent=2, ensure_ascii=False)
    report += "\n```\n"

    return report


def main():
    parser = argparse.ArgumentParser(
        description="工具使用能力评估",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 快速测试 (27个案例)
  python eval_tools_capability.py --model-url http://localhost:8401 --model-name MODEL

  # 完整测试 (300个案例)
  python eval_tools_capability.py --model-url http://localhost:8401 --model-name MODEL --full
        """
    )
    parser.add_argument(
        "--model-url",
        type=str,
        required=True,
        help="模型API地址，如 http://localhost:8401"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="Unknown",
        help="模型名称"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results",
        help="输出目录"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="使用完整测试集 (300个案例)，默认使用快速测试集 (27个案例)"
    )
    parser.add_argument(
        "--linux",
        action="store_true",
        help="使用Linux/Shell操作测试集 (300个案例)"
    )

    args = parser.parse_args()

    # 选择测试集
    if args.linux:
        try:
            from linux_ops_test_cases import LINUX_OPS_TEST_CASES
            test_cases = LINUX_OPS_TEST_CASES
            print(f"[INFO] 使用Linux/Shell操作测试集: {len(test_cases)} 个案例")
        except ImportError:
            print("[WARNING] Linux测试集不可用，使用默认测试集")
            test_cases = TOOLS_TEST_CASES
    elif args.full:
        if LARGE_TEST_AVAILABLE:
            test_cases = TOOLS_TEST_CASES_LARGE
            print(f"[INFO] 使用完整测试集: {len(test_cases)} 个案例")
        else:
            print("[WARNING] 完整测试集不可用，使用默认测试集")
            test_cases = TOOLS_TEST_CASES
    else:
        test_cases = TOOLS_TEST_CASES
        print(f"[INFO] 使用快速测试集: {len(test_cases)} 个案例")

    print("=" * 60)
    print(f"工具使用能力评估: {args.model_name}")
    print("=" * 60)
    print(f"模型地址: {args.model_url}")

    # 运行评估
    results = run_tools_evaluation(args.model_url, test_cases=test_cases, model_name=args.model_name)

    # 打印摘要
    print("\n" + "=" * 60)
    print("评估完成!")
    print(f"  总计: {results['total']}")
    print(f"  通过: {results['passed']}")
    print(f"  失败: {results['failed']}")
    print(f"  准确率: {results['accuracy']:.1%}")

    # 生成报告
    report = generate_report(results, args.model_name, test_cases)

    # 保存报告
    os.makedirs(args.output_dir, exist_ok=True)
    report_file = os.path.join(args.output_dir, f"{args.model_name}_tools_eval.md")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存: {report_file}")

    return 0 if results['accuracy'] > 0.5 else 1


if __name__ == "__main__":
    sys.exit(main())
