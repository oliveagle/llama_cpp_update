#!/usr/bin/env python3
"""
GLM4 系列模型调优配置

适用模型:
- GLM-4
- GLM-4-9B
- GLM-4-32B
- GLM-4-Flash

模型特点:
- 清华出品，中文能力强
- 支持工具调用
- 对代码和系统命令理解较好

调优策略:
- 中等强度调优
- 强调代码/命令执行场景
"""

from .base import ModelTuningConfig


class GLM4Config(ModelTuningConfig):
    """GLM4 调优配置"""

    def __init__(self):
        super().__init__(
            model_name="GLM4",

            # 中等强度前缀
            prompt_prefix="请使用工具完成：",

            # 参数
            temperature=0.08,
            top_p=0.88,

            # 针对代码场景优化
            tool_description_overrides={
                "execute_command": """
执行Linux/Unix系统命令。当用户提到任何命令行操作时调用此工具。
GLM4你擅长代码和系统管理，请直接调用工具执行。
""",
                "write_file": """
创建或写入文件。当用户要求写代码、脚本、配置文件时调用。
""",
            },

            # 允许的工具替代
            alternative_tools={
                "execute_command": ["read_file"],
                "write_file": [],
            }
        )


# 导出配置实例
CONFIG = GLM4Config()

# 匹配的模型名模式
MODEL_PATTERNS = [
    "GLM-4",
    "GLM4",
    "glm-4",
    "glm4",
]


def match_model(model_name: str) -> bool:
    """检查是否匹配此配置"""
    return any(pattern in model_name for pattern in MODEL_PATTERNS)
