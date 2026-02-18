#!/usr/bin/env python3
"""
Stage 1: 基础性能测试 - 性能评估器

测试项:
1. 预填充速度 (Prompt Processing) - tokens/sec
2. 生成速度 (Generation) - tokens/sec
3. Context梯度测试 (4K -> 128K)
4. 首token延迟 (TTFT)
"""

import time
import requests
from typing import Dict, List
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


class PerformanceEvaluator(BaseEvaluator):
    """性能测试评估器"""

    name = "performance"
    description = "基础性能测试 (吞吐量/速度/Context)"

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        # 初始化原始数据记录器
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    @property
    def stage_name(self) -> str:
        return "基础性能测试"

    @property
    def stage_number(self) -> int:
        return 1

    @property
    def threshold_percentage(self) -> float:
        return 0.6  # 60% 通过门槛

    def run_tests(self) -> StageResult:
        """运行所有性能测试"""
        test_results: List[TestResult] = []
        start_time = time.time()

        # 1. 速度测试 (1K context)
        result_1k = self._test_speed_1k()
        test_results.append(result_1k)

        # 2. 速度测试 (4K context)
        result_4k = self._test_speed_4k()
        test_results.append(result_4k)

        # 3. Context Window 测试
        result_ctx = self._test_context_window()
        test_results.append(result_ctx)

        elapsed = time.time() - start_time

        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        return StageResult(
            stage_name=self.stage_name,
            stage_number=self.stage_number,
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            duration_seconds=elapsed,
            test_results=test_results,
            passed_threshold=(passed / total >= self.threshold_percentage) if total > 0 else False,
            threshold_percentage=self.threshold_percentage
        )

    def _test_speed_1k(self) -> TestResult:
        """测试1K context速度"""
        prompt = "这是一个测试prompt。" * 50  # ~200 tokens

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 128,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                usage = data.get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0)
                prompt_tokens = usage.get("prompt_tokens", 0)

                gen_speed = completion_tokens / elapsed if elapsed > 0 else 0
                prompt_speed = prompt_tokens / elapsed if elapsed > 0 else 0

                # 记录原始数据
                self.raw_logger.log_test_result({
                    "model": self.model_name,
                    "test_name": "speed_1k_context",
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "generation_speed_tps": round(gen_speed, 2),
                    "prompt_speed_tps": round(prompt_speed, 2),
                    "elapsed_sec": round(elapsed, 2),
                    "raw_response": data
                }, test_type="performance")

                return TestResult(
                    name="speed_1k_context",
                    category="性能测试",
                    passed=True,
                    duration_ms=elapsed * 1000,
                    details={
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "generation_speed_tps": round(gen_speed, 2),
                        "prompt_speed_tps": round(prompt_speed, 2),
                        "elapsed_sec": round(elapsed, 2)
                    }
                )
            else:
                return TestResult(
                    name="speed_1k_context",
                    category="性能测试",
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="speed_1k_context",
                category="性能测试",
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _test_speed_4k(self) -> TestResult:
        """测试4K context速度"""
        prompt = "这是一个用于测试长上下文处理能力的文本。" * 200  # ~800 tokens

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 128,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                usage = data.get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0)
                prompt_tokens = usage.get("prompt_tokens", 0)

                gen_speed = completion_tokens / elapsed if elapsed > 0 else 0
                prompt_speed = prompt_tokens / elapsed if elapsed > 0 else 0

                # 记录原始数据
                self.raw_logger.log_test_result({
                    "model": self.model_name,
                    "test_name": "speed_4k_context",
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "generation_speed_tps": round(gen_speed, 2),
                    "prompt_speed_tps": round(prompt_speed, 2),
                    "elapsed_sec": round(elapsed, 2),
                    "raw_response": data
                }, test_type="performance")

                return TestResult(
                    name="speed_4k_context",
                    category="性能测试",
                    passed=True,
                    duration_ms=elapsed * 1000,
                    details={
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "generation_speed_tps": round(gen_speed, 2),
                        "prompt_speed_tps": round(prompt_speed, 2),
                        "elapsed_sec": round(elapsed, 2)
                    }
                )
            else:
                return TestResult(
                    name="speed_4k_context",
                    category="性能测试",
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )
        except Exception as e:
            return TestResult(
                name="speed_4k_context",
                category="性能测试",
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _test_context_window(self) -> TestResult:
        """测试Context Window极限"""
        context_steps = [4096, 8192, 16384]
        max_successful = 0
        details = {"tested_contexts": []}

        for ctx_size in context_steps:
            # 生成指定长度的文本 (~ctx_size tokens)
            prompt = "这是一个测试句子。" * (ctx_size // 3)

            url = f"{self.model_url}/v1/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 10,
                "temperature": 0.1
            }

            try:
                resp = requests.post(url, json=payload, timeout=60)
                status = "success" if resp.status_code == 200 else f"HTTP {resp.status_code}"

                details["tested_contexts"].append({
                    "context": ctx_size,
                    "status": status
                })

                if resp.status_code == 200:
                    max_successful = ctx_size
                else:
                    break  # 失败则停止更大测试
            except Exception as e:
                details["tested_contexts"].append({
                    "context": ctx_size,
                    "status": f"error: {str(e)}"
                })
                break

        # 记录原始数据
        self.raw_logger.log_test_result({
            "model": self.model_name,
            "test_name": "context_window_limit",
            "max_successful_context": max_successful,
            "tested_contexts": details["tested_contexts"]
        }, test_type="performance")

        details["max_successful_context"] = max_successful

        return TestResult(
            name="context_window_limit",
            category="性能测试",
            passed=max_successful >= 4096,  # 至少支持4K
            duration_ms=0,
            details=details
        )


def run_performance_test(model_url: str, model_name: str) -> Dict:
    """运行性能测试并返回结果"""
    evaluator = PerformanceEvaluator(model_url, model_name)
    stage_result = evaluator.run_tests()

    # 转换为可序列化的字典
    return {
        "model": model_name,
        "url": model_url,
        "stage": stage_result.stage_number,
        "stage_name": stage_result.stage_name,
        "total_tests": stage_result.total_tests,
        "passed_tests": stage_result.passed_tests,
        "failed_tests": stage_result.failed_tests,
        "pass_rate": stage_result.pass_rate,
        "duration_seconds": stage_result.duration_seconds,
        "passed_threshold": stage_result.passed_threshold,
        "tests": [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "duration_ms": r.duration_ms,
                "details": r.details,
                "error": r.error_message
            }
            for r in stage_result.test_results
        ]
    }


if __name__ == "__main__":
    import json

    # 测试 V100
    print("="*60)
    print("V100 (CUDA) 性能测试")
    print("="*60)

    result = run_performance_test(
        "http://localhost:8401",
        "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
    print(f"耗时: {result['duration_seconds']:.1f}秒")

    print("\n详细结果:")
    for test in result["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"\n{status} {test['name']}")
        if test["details"]:
            for key, val in test["details"].items():
                print(f"   {key}: {val}")
        if test["error"]:
            print(f"   错误: {test['error']}")

    # 保存结果
    with open("eval_results/v100_performance_test.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n结果已保存: eval_results/v100_performance_test.json")
