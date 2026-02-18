#!/usr/bin/env python3
"""
Qwen3 系列模型调优配置

适用模型:
- Qwen3 全系列 (0.6B, 4B, 8B, 32B, etc.)
- Qwen3-Instruct
- Qwen3-VL

模型特点:
- 原生支持工具调用
- 对系统提示和工具定义理解较好
- 通常不需要强提示

调优策略:
- 轻量调优，主要依靠模型原生能力
- 允许更灵活的工具选择
"""

from .base import ModelTuningConfig


class Qwen3Config(ModelTuningConfig):
    """Qwen3 调优配置"""

    def __init__(self):
        super().__init__(
            model_name="Qwen3",

            # Qwen3通常不需要强前缀
            prompt_prefix="",

            # 标准参数
            temperature=0.1,
            top_p=0.9,

            # Qwen3原生支持工具调用，描述保持简洁
            tool_description_overrides={},

            # 允许的工具替代（灵活模式）
            alternative_tools={
                "execute_command": ["read_file", "get_time", "get_date", "get_weather"],
                "write_file": ["create_file", "save_content"],
            }
        )


# 导出配置实例
CONFIG = Qwen3Config()

# 匹配的模型名模式
MODEL_PATTERNS = [
    "Qwen3",
    "qwen3",
]


def match_model(model_name: str) -> bool:
    """检查是否匹配此配置"""
    return any(pattern in model_name for pattern in MODEL_PATTERNS)
