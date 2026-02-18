#!/usr/bin/env python3
"""
Stage 2: 基础能力测试

测试项 (10个类别，每个10个案例，共100个测试):
1. 代码能力 - HumanEval / MBPP (10 cases)
2. 数学能力 - GSM8K (10 cases)
3. 文本理解 - MMLU / CMMLU (10 cases)
4. 工具使用 - Function Calling / Tool Use (10 cases)
5. 逻辑推理 - 逻辑推理和因果推理 (10 cases)
6. 知识问答 - 世界知识和常识 (10 cases)
7. 翻译能力 - 多语言翻译 (10 cases)
8. 摘要总结 - 文本摘要和信息提取 (10 cases)
9. 安全合规 - 安全意识和边界 (10 cases)
10. 多轮对话 - 上下文理解和多轮交互 (10 cases)
"""

from .code_eval import CodeEvaluator
from .math_eval import MathEvaluator
from .text_eval import TextEvaluator
from .tool_eval import ToolEvaluator
from .reasoning_eval import ReasoningEvaluator
from .knowledge_eval import KnowledgeEvaluator
from .translation_eval import TranslationEvaluator
from .summarization_eval import SummarizationEvaluator
from .safety_eval import SafetyEvaluator
from .multiturn_eval import MultiTurnEvaluator

__all__ = [
    "CodeEvaluator",
    "MathEvaluator",
    "TextEvaluator",
    "ToolEvaluator",
    "ReasoningEvaluator",
    "KnowledgeEvaluator",
    "TranslationEvaluator",
    "SummarizationEvaluator",
    "SafetyEvaluator",
    "MultiTurnEvaluator"
]
