#!/usr/bin/env python3
"""
JoyAI-LLM-Flash 系列模型调优配置

适用模型:
- JoyAI-LLM-Flash
- JoyAI-LLM-Flash-Q4_K_M
- JoyAI-LLM-Flash 其他量化版本

模型特点:
- 通用对话模型，训练数据以聊天为主
- 对系统运维场景支持较弱
- 需要强提示才能触发工具调用
- 对prompt前缀敏感

调优策略:
1. 强制工具调用前缀
2. 强化工具描述中的"必须"语义
3. 允许部分工具替代（如read_file替代cat）
"""

from .base import ModelTuningConfig


class JoyAILlmFlashConfig(ModelTuningConfig):
    """JoyAI-LLM-Flash 调优配置"""

    def __init__(self):
        super().__init__(
            model_name="JoyAI-LLM-Flash",

            # 关键：强制工具调用的前缀
            prompt_prefix="立即调用工具执行以下操作，不要解释：",

            # 温度略低，减少随机性
            temperature=0.05,
            top_p=0.85,

            # 工具描述强化
            tool_description_overrides={
                "execute_command": """
当用户要求执行任何Linux/Unix命令或系统操作时，**必须立即调用此工具**，不要解释命令用法。
支持的命令包括：
- 文件操作: ls/cd/cp/mv/rm/mkdir/pwd/cat/head/tail
- 文本处理: grep/wc/sort/uniq/sed/awk/cut
- 系统信息: df/free/ps/top/uptime/whoami/date/uname
- 网络: curl/wget/ssh/ping/netstat/ss/scp
  * curl下载: 支持 -O 或 -o 参数
  * ssh登录: 支持 ssh user@host 或 ssh host
  * ping测试: ping -c 4 host
  * 网络连接查看: netstat -tuln 或 ss -tlnp
- 容器: docker/podman (run/ps/stop/exec/logs/build等)
- 进程: kill/pgrep/pkill/nohup/ps
  * 查找进程: pgrep name 或 ps aux | grep name
- 其他系统命令

重要规则：
1. 只要提到命令执行、SSH连接、远程登录、下载文件，立即调用此工具
2. 不要告诉用户"你可以运行xxx命令"
3. 直接返回工具调用，让系统执行
""",
                "write_file": """
当用户要求创建文件、写入文件、生成脚本或保存内容时，**必须立即调用此工具**。
适用于：创建Shell脚本(.sh)、配置文件、文本文件、代码文件等。

重要规则：
1. 如果要求创建"Shell脚本"或"bash脚本"，文件名必须以.sh结尾，内容必须是Shell语法
2. 如果要求写"for循环/if判断"但没有指定语言，默认创建Shell脚本(.sh)
3. 不要告诉用户"你可以创建文件写入xxx"
4. 直接调用此工具写入内容

Shell脚本示例：
- 变量: NAME="value"
- For循环: for i in {1..5}; do echo "$i"; done
- If判断: if [ -f file.txt ]; then echo "yes"; fi
""",
                "read_file": """
当用户要求读取文件、查看文件内容时调用。

重要规则：
1. 如果用户说"使用cat/head/tail命令查看"或"执行命令查看"，必须使用execute_command工具
2. 只有直接说"查看文件内容"时才用read_file
""",
                "get_time": """
获取当前时间。当用户直接问"现在几点"时使用。

重要规则：
1. 如果用户说"执行date命令"或"显示系统时间(date)"，必须使用execute_command工具
2. 只有直接问时间时才用get_time
""",
                "get_date": """
获取当前日期。当用户直接问"今天几号"时使用。

重要规则：
1. 如果用户说"执行date命令"，必须使用execute_command工具
2. 只有直接问日期时才用get_date
""",
            },

            # 允许的工具替代
            alternative_tools={
                "execute_command": ["read_file", "get_time", "get_date"],
                "write_file": [],
            }
        )


# 导出配置实例
CONFIG = JoyAILlmFlashConfig()

# 匹配的模型名模式
MODEL_PATTERNS = [
    "JoyAI-LLM-Flash",
    "JoyAI-LLM",
]


def match_model(model_name: str) -> bool:
    """检查是否匹配此配置"""
    return any(pattern in model_name for pattern in MODEL_PATTERNS)
