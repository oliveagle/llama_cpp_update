#!/usr/bin/env python3
"""
评估框架包

导出核心类:
- BaseEvaluator: 评估器基类
- StageResult: 阶段测试结果
- TestResult: 单个测试用例结果
- EvaluationRunner: 测试执行器
- ReportGenerator: 报告生成器
"""

from .base import BaseEvaluator, StageResult, TestResult
from .runner import EvaluationRunner
from .report import ReportGenerator

__all__ = [
    'BaseEvaluator',
    'StageResult',
    'TestResult',
    'EvaluationRunner',
    'ReportGenerator',
]
