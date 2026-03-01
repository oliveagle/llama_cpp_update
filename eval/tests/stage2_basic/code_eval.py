#!/usr/bin/env python3
"""
代码能力测试 - HumanEval 风格

测试模型的代码生成和代码理解能力
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


# HumanEval 风格测试用例 (简化版)
CODE_TEST_CASES = [
    {
        "name": "has_close_elements",
        "description": "检查列表中是否有两个元素距离小于阈值",
        "prompt": "def has_close_elements(numbers: list[float], threshold: float) -> bool:\n    \"\"\"检查列表中是否有任意两个元素的距离小于给定阈值\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"",
        "test_cases": [
            {"input": ([1.0, 2.0, 3.0], 0.5), "expected": False},
            {"input": ([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3), "expected": True},
            {"input": ([1.0, 1.1], 0.2), "expected": True},
        ]
    },
    {
        "name": "separate_paren_groups",
        "description": "分离括号组",
        "prompt": "def separate_paren_groups(paren_string: str) -> list[str]:\n    \"\"\"将输入字符串中的括号组分离成独立字符串，括号平衡。\n    >>> separate_paren_groups('( ) (( )) (( )( ))')\n    ['()', '(())', '(()())']\n    \"\"\"",
        "test_cases": [
            {"input": ("( ) (( )) (( )( ))",), "expected": ["()", "(())", "(()())"]},
        ]
    },
    {
        "name": "truncate_number",
        "description": "截断小数",
        "prompt": "def truncate_number(number: float) -> float:\n    \"\"\"截断数字的小数部分（向零取整）\n    >>> truncate_number(3.5)\n    3\n    >>> truncate_number(-2.7)\n    -2\n    \"\"\"",
        "test_cases": [
            {"input": (3.5,), "expected": 3},
            {"input": (-2.7,), "expected": -2},
            {"input": (10.9,), "expected": 10},
        ]
    },
    {
        "name": "below_zero",
        "description": "检查余额是否曾低于零",
        "prompt": "from typing import List, Tuple\n\ndef below_zero(operations: List[Tuple[str, int]]) -> bool:\n    \"\"\"给定银行操作列表（存款/取款），检查余额是否曾低于零\n    操作格式: ('存款', 100) 或 ('取款', 50)\n    >>> below_zero([('存款', 100), ('取款', 50)])\n    False\n    >>> below_zero([('取款', 100)])\n    True\n    \"\"\"",
        "test_cases": [
            {"input": ([("存款", 100), ("取款", 50)],), "expected": False},
            {"input": ([("取款", 100)],), "expected": True},
            {"input": ([("存款", 50), ("取款", 50)],), "expected": False},
        ]
    },
    {
        "name": "mean_absolute_derivative",
        "description": "计算平均绝对导数",
        "prompt": "def mean_absolute_derivative(xs: list[int]) -> float:\n    \"\"\"计算序列的平均绝对导数（相邻元素差的绝对值的平均）\n    >>> mean_absolute_derivative([1, 2, 3, 4, 5])\n    1.0\n    >>> mean_absolute_derivative([1, 5, 3, 7])\n    3.0\n    \"\"\"",
        "test_cases": [
            {"input": ([1, 2, 3, 4, 5],), "expected": 1.0},
            {"input": ([1, 5, 3, 7],), "expected": 3.0},
        ]
    },
    {
        "name": "intersperse",
        "description": "在列表元素间插入分隔符",
        "prompt": "from typing import List\n\ndef intersperse(numbers: List[int], delimiter: int) -> List[int]:\n    \"\"\"在列表的每对连续元素之间插入分隔符\n    >>> intersperse([1, 2, 3], 0)\n    [1, 0, 2, 0, 3]\n    >>> intersperse([], 5)\n    []\n    \"\"\"",
        "test_cases": [
            {"input": ([1, 2, 3], 0), "expected": [1, 0, 2, 0, 3]},
            {"input": ([], 5), "expected": []},
            {"input": ([10], 0), "expected": [10]},
        ]
    },
    {
        "name": "count_vowels",
        "description": "统计元音字母数量",
        "prompt": "def count_vowels(s: str) -> int:\n    \"\"\"统计字符串中元音字母(a,e,i,o,u)的数量，不区分大小写\n    >>> count_vowels('Hello World')\n    3\n    >>> count_vowels('Python')\n    1\n    \"\"\"",
        "test_cases": [
            {"input": ("Hello World",), "expected": 3},
            {"input": ("Python",), "expected": 1},
            {"input": ("BCDFG",), "expected": 0},
        ]
    },
    {
        "name": "remove_duplicates",
        "description": "移除重复元素保持顺序",
        "prompt": "from typing import List\n\ndef remove_duplicates(numbers: List[int]) -> List[int]:\n    \"\"\"移除列表中的重复元素，保持第一次出现的顺序\n    >>> remove_duplicates([1, 2, 2, 3, 1, 4])\n    [1, 2, 3, 4]\n    >>> remove_duplicates([5, 5, 5])\n    [5]\n    \"\"\"",
        "test_cases": [
            {"input": ([1, 2, 2, 3, 1, 4],), "expected": [1, 2, 3, 4]},
            {"input": ([5, 5, 5],), "expected": [5]},
            {"input": ([],), "expected": []},
        ]
    },
    {
        "name": "is_palindrome",
        "description": "检查字符串是否为回文",
        "prompt": "def is_palindrome(s: str) -> bool:\n    \"\"\"检查字符串是否为回文（正读反读相同），忽略大小写和非字母数字字符\n    >>> is_palindrome('A man a plan a canal Panama')\n    True\n    >>> is_palindrome('hello')\n    False\n    \"\"\"",
        "test_cases": [
            {"input": ("A man a plan a canal Panama",), "expected": True},
            {"input": ("hello",), "expected": False},
            {"input": ("Race a car",), "expected": False},
        ]
    },
    {
        "name": "fibonacci",
        "description": "计算斐波那契数列第n项",
        "prompt": "def fibonacci(n: int) -> int:\n    \"\"\"计算斐波那契数列的第n项（从0开始）\n    >>> fibonacci(0)\n    0\n    >>> fibonacci(1)\n    1\n    >>> fibonacci(10)\n    55\n    \"\"\"",
        "test_cases": [
            {"input": (0,), "expected": 0},
            {"input": (1,), "expected": 1},
            {"input": (10,), "expected": 55},
            {"input": (7,), "expected": 13},
        ]
    },
]


class CodeEvaluator(BaseEvaluator):
    """代码能力评估器"""

    name = "code"
    description = "代码生成能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-代码"

    @property
    def stage_number(self) -> int:
        return 2

    @property
    def threshold_percentage(self) -> float:
        return 0.4  # 40% 通过门槛

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行代码能力测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in CODE_TEST_CASES:
            result = self._test_single_case(test_case)
            test_results.append(result)

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

    def _test_single_case(self, test_case: dict) -> TestResult:
        """测试单个代码用例"""
        import requests

        prompt = f"请完成以下Python函数:\n\n{test_case['prompt']}\n\n请只输出函数实现代码，不要解释。"

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个Python编程助手，请输出完整的函数实现。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=300)
            elapsed = time.time() - start

            if resp.status_code != 200:
                return TestResult(
                    name=test_case["name"],
                    category="代码能力",
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            # 支持推理模型：如果 content 为空，尝试使用 reasoning_content
            if not content:
                content = message.get("reasoning_content", "")

            # 简单评估：检查代码是否可解析且包含关键元素
            score = self._evaluate_code(content, test_case)

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "prompt": test_case["prompt"],
                "generated_code": content,
                "score": score,
                "raw_response": data
            }, test_type="code")

            return TestResult(
                name=test_case["name"],
                category="代码能力",
                passed=score >= 0.5,
                duration_ms=elapsed * 1000,
                details={
                    "description": test_case["description"],
                    "generated_code": content[:500],  # 截断保存
                    "score": score
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category="代码能力",
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _evaluate_code(self, generated_code: str, test_case: dict) -> float:
        """
        简单代码评估
        返回 0-1 的分数
        """
        score = 0.0

        # 1. 检查是否包含函数定义
        func_name = test_case["name"]
        if f"def {func_name}(" in generated_code:
            score += 0.3

        # 2. 检查是否有返回语句
        if "return" in generated_code:
            score += 0.2

        # 3. 检查是否有docstring (题目中给的)
        if '"\"\""' in generated_code or "'''" in generated_code:
            score += 0.2

        # 4. 检查语法基本正确性（简单的括号匹配）
        open_parens = generated_code.count("(")
        close_parens = generated_code.count(")")
        if open_parens == close_parens and open_parens > 0:
            score += 0.15

        open_braces = generated_code.count("[")
        close_braces = generated_code.count("]")
        if open_braces == close_braces:
            score += 0.15

        return min(score, 1.0)


def run_code_test(model_url: str, model_name: str) -> dict:
    """运行代码测试"""
    evaluator = CodeEvaluator(model_url, model_name)
    stage_result = evaluator.run_tests()

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

    print("="*60)
    print("V100 (CUDA) 代码能力测试")
    print("="*60)

    result = run_code_test(
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
            print(f"   描述: {test['details'].get('description', '')}")
            print(f"   评分: {test['details'].get('score', 0):.2f}")
        if test["error"]:
            print(f"   错误: {test['error']}")

    with open("eval_results/v100_code_test.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n结果已保存: eval_results/v100_code_test.json")
