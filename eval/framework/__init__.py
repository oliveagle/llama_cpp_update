#!/usr/bin/env python3
"""
llama.cpp 模型能力评估框架

三层架构:
    Stage 1: 基础性能测试 (Performance)
    Stage 2: 基础能力测试 (Capabilities)
    Stage 3: 深度能力测试 (Deep Evaluation)
"""

from .base import BaseEvaluator, TestResult, StageResult
from .runner import EvaluationRunner
from .report import ReportGenerator

__version__ = "1.0.0"
__all__ = ["BaseEvaluator", "TestResult", "StageResult", "EvaluationRunner", "ReportGenerator"]