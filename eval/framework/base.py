#!/usr/bin/env python3
"""
评估框架基础类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TestResult:
    """单个测试用例结果"""
    name: str
    category: str
    passed: bool
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class StageResult:
    """阶段测试结果"""
    stage_name: str
    stage_number: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration_seconds: float
    test_results: List[TestResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    passed_threshold: bool = False
    threshold_percentage: float = 0.0

    @property
    def pass_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return self.passed_tests / self.total_tests


class BaseEvaluator(ABC):
    """评估器基类"""

    def __init__(self, model_url: str, model_name: str, **kwargs):
        self.model_url = model_url.rstrip('/')
        self.model_name = model_name
        self.config = kwargs
        self.results: List[TestResult] = []

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """阶段名称"""
        pass

    @property
    @abstractmethod
    def stage_number(self) -> int:
        """阶段编号 (1, 2, 3)"""
        pass

    @property
    @abstractmethod
    def threshold_percentage(self) -> float:
        """通过门槛 (0.0-1.0)"""
        pass

    @abstractmethod
    def run_tests(self) -> StageResult:
        """运行所有测试"""
        pass

    def check_prerequisites(self) -> bool:
        """检查前置条件"""
        return True

    def _make_api_request(self, endpoint: str, payload: Dict) -> Dict:
        """调用模型API"""
        import requests
        url = f"{self.model_url}{endpoint}"
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
