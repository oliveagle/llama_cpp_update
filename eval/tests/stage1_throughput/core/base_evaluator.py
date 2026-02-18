#!/usr/bin/env python3
"""
Stage 1 基础评估器 - 定义通用测试流程

多后端支持的抽象基类，所有后端特定的运行器都需要继承此类。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import requests


@dataclass
class TestMetrics:
    """测试指标数据类"""
    # 时间指标
    prompt_processing_time_ms: float = 0.0
    generation_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Token 指标
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # 速度指标
    prompt_tokens_per_second: float = 0.0
    generation_tokens_per_second: float = 0.0
    total_tokens_per_second: float = 0.0

    # 额外指标
    ttft_ms: float = 0.0  # Time To First Token
    latency_ms: float = 0.0


@dataclass
class TestResult:
    """单个测试结果"""
    timestamp: str
    backend_type: str
    device: str
    model_id: str
    model_file: str
    test_type: str
    test_params: Dict[str, Any]
    metrics: TestMetrics
    raw_response: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None


class Stage1Evaluator(ABC):
    """
    Stage 1 吞吐量测试基础评估器

    所有后端特定的运行器都需要继承此类并实现抽象方法。

    Usage:
        evaluator = VulkanEvaluator(backend_config, model_config)
        result = evaluator.run_test("token_generation", {
            "prompt_length": 1024,
            "max_tokens": 512
        })
    """

    def __init__(self, backend_config: Dict, model_config: Dict, base_url: str = "http://localhost:8400"):
        """
        初始化评估器

        Args:
            backend_config: 后端配置（包含 type, device, compute_capability 等）
            model_config: 模型配置（包含 id, gguf_file, quantization 等）
            base_url: llama-server API 端点
        """
        self.backend_config = backend_config
        self.model_config = model_config
        self.base_url = base_url.rstrip('/')
        self.logger = None  # 由子类或外部设置

        # 后端标识
        self.backend_type = backend_config.get('type', 'unknown')
        self.device = backend_config.get('device', 'unknown')

    @abstractmethod
    def setup_server(self, **kwargs) -> bool:
        """
        启动/设置后端特定的服务器

        Returns:
            bool: 是否成功启动
        """
        pass

    @abstractmethod
    def teardown_server(self) -> bool:
        """
        停止/清理服务器

        Returns:
            bool: 是否成功停止
        """
        pass

    @abstractmethod
    def get_server_params(self) -> Dict[str, Any]:
        """
        获取后端特定的服务器参数

        Returns:
            参数字典，如 {"ngl": 99, "n_ctx": 32768}
        """
        pass

    def run_test(self, test_type: str, test_params: Dict[str, Any]) -> TestResult:
        """
        运行测试（通用流程）

        Args:
            test_type: 测试类型（prompt_processing, token_generation, context_scaling）
            test_params: 测试参数

        Returns:
            TestResult 包含测试指标和原始数据
        """
        timestamp = datetime.now().isoformat()

        try:
            # 1. 准备测试环境
            self._prepare_test(test_type, test_params)

            # 2. 执行测试
            raw_result = self._execute_test(test_type, test_params)

            # 3. 计算指标
            metrics = self._calculate_metrics(raw_result)

            # 4. 构建结果
            result = TestResult(
                timestamp=timestamp,
                backend_type=self.backend_type,
                device=self.device,
                model_id=self.model_config.get('id', 'unknown'),
                model_file=self.model_config.get('gguf_file', 'unknown'),
                test_type=test_type,
                test_params=test_params,
                metrics=metrics,
                raw_response=raw_result,
                success=True
            )

            return result

        except Exception as e:
            return TestResult(
                timestamp=timestamp,
                backend_type=self.backend_type,
                device=self.device,
                model_id=self.model_config.get('id', 'unknown'),
                model_file=self.model_config.get('gguf_file', 'unknown'),
                test_type=test_type,
                test_params=test_params,
                metrics=TestMetrics(),
                raw_response={},
                success=False,
                error_message=str(e)
            )

    def _prepare_test(self, test_type: str, test_params: Dict[str, Any]):
        """测试准备 - 可以被子类覆盖"""
        pass

    def _execute_test(self, test_type: str, test_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行具体测试

        根据 test_type 调用不同的测试方法
        """
        if test_type == "prompt_processing":
            return self._test_prompt_processing(test_params)
        elif test_type == "token_generation":
            return self._test_token_generation(test_params)
        elif test_type == "context_scaling":
            return self._test_context_scaling(test_params)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    def _test_prompt_processing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试提示处理速度 (prefill)

        发送长prompt，只生成1个token，测量prompt处理时间
        """
        prompt_length = params.get('prompt_length', 4096)
        prompt = "测试 " * (prompt_length // 3)  # 简化生成prompt

        payload = {
            "model": self.model_config.get('gguf_file', 'model'),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1,
            "temperature": 0.0
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        elapsed_ms = (time.time() - start_time) * 1000

        data = response.json()
        usage = data.get('usage', {})
        timings = data.get('timings', {})

        return {
            "prompt_tokens": usage.get('prompt_tokens', prompt_length),
            "completion_tokens": 1,
            "total_tokens": usage.get('total_tokens', prompt_length + 1),
            "elapsed_ms": elapsed_ms,
            "timings": timings,
            "raw_response": data
        }

    def _test_token_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试Token生成速度 (generation)

        发送固定prompt，生成多个token，测量生成速度
        """
        prompt_length = params.get('prompt_length', 1024)
        max_tokens = params.get('max_tokens', 512)

        prompt = "测试 " * (prompt_length // 3)

        payload = {
            "model": self.model_config.get('gguf_file', 'model'),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        elapsed_ms = (time.time() - start_time) * 1000

        data = response.json()
        usage = data.get('usage', {})
        timings = data.get('timings', {})

        return {
            "prompt_tokens": usage.get('prompt_tokens', prompt_length),
            "completion_tokens": usage.get('completion_tokens', max_tokens),
            "total_tokens": usage.get('total_tokens', prompt_length + max_tokens),
            "elapsed_ms": elapsed_ms,
            "timings": timings,
            "raw_response": data
        }

    def _test_context_scaling(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试Context扩展能力

        逐步增加prompt长度直到失败或达到上限
        """
        base_context = params.get('base_context', 4096)
        max_context = params.get('max_context', 131072)
        step_multiplier = params.get('step_multiplier', 2)

        results = []
        current_context = base_context

        while current_context <= max_context:
            test_params = {"prompt_length": current_context, "max_tokens": 1}
            try:
                result = self._test_prompt_processing(test_params)
                results.append({
                    "context": current_context,
                    "success": True,
                    "tps": result.get('prompt_tokens', current_context) / (result.get('elapsed_ms', 1000) / 1000)
                })
                current_context *= step_multiplier
            except Exception as e:
                results.append({
                    "context": current_context,
                    "success": False,
                    "error": str(e)
                })
                break

        return {
            "max_successful_context": results[-1]["context"] if results and results[-1]["success"] else 0,
            "results": results
        }

    def _calculate_metrics(self, raw_result: Dict[str, Any]) -> TestMetrics:
        """
        从原始结果计算标准化指标
        """
        metrics = TestMetrics()

        # 基础指标
        metrics.prompt_tokens = raw_result.get('prompt_tokens', 0)
        metrics.completion_tokens = raw_result.get('completion_tokens', 0)
        metrics.total_tokens = raw_result.get('total_tokens', 0)

        # 时间指标
        elapsed_ms = raw_result.get('elapsed_ms', 0)
        timings = raw_result.get('timings', {})

        # 如果有详细的timings数据，使用它们
        if timings:
            prompt_ms = timings.get('prompt_ms', 0)
            predicted_ms = timings.get('predicted_ms', 0)

            metrics.prompt_processing_time_ms = prompt_ms
            metrics.generation_time_ms = predicted_ms
            metrics.total_time_ms = prompt_ms + predicted_ms
        else:
            # 否则使用总时间估算
            metrics.total_time_ms = elapsed_ms

        # 计算速度指标
        if metrics.prompt_processing_time_ms > 0:
            metrics.prompt_tokens_per_second = metrics.prompt_tokens / (metrics.prompt_processing_time_ms / 1000)

        if metrics.generation_time_ms > 0:
            metrics.generation_tokens_per_second = metrics.completion_tokens / (metrics.generation_time_ms / 1000)

        if metrics.total_time_ms > 0:
            metrics.total_tokens_per_second = metrics.total_tokens / (metrics.total_time_ms / 1000)

        return metrics
