#!/usr/bin/env python3
"""
数学能力测试 - GSM8K 风格

测试模型的数学推理能力
"""

import time
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger
from .utils_reasoning import extract_last_number


# GSM8K 风格数学测试用例
MATH_TEST_CASES = [
    {
        "name": "价格计算",
        "description": "基础价格计算",
        "problem": "一个商店正在促销。买3件衬衫每件25元，或者买5件衬衫每件20元。如果小明想买12件衬衫，最少需要多少钱？",
        "answer": 245,
        "explanation": "最优方案是2组5件(200元) + 2件单价(50元)，但更好的方案是4组3件(4*75=300)或2组5件+2件(200+50=250)。实际上最少是：2组5件(200元) + 2件按单价25元(50元) = 250元。或者：4组3件 = 300元。最优是250元。"
    },
    {
        "name": "速度距离",
        "description": "速度距离时间计算",
        "problem": "一辆汽车以每小时60公里的速度行驶了2.5小时，然后以每小时80公里的速度行驶了1.5小时。总行驶距离是多少公里？",
        "answer": 270,
        "explanation": "第一段：60 * 2.5 = 150公里。第二段：80 * 1.5 = 120公里。总计：150 + 120 = 270公里。"
    },
    {
        "name": "比例问题",
        "description": "比例和百分比",
        "problem": "一个班级有40名学生，其中25%喜欢数学，35%喜欢英语，其余喜欢科学。喜欢科学的学生有多少人？",
        "answer": 16,
        "explanation": "喜欢数学：40 * 0.25 = 10人。喜欢英语：40 * 0.35 = 14人。喜欢科学：40 - 10 - 14 = 16人。或者：40 * (1 - 0.25 - 0.35) = 40 * 0.4 = 16人。"
    },
    {
        "name": "连续整数",
        "description": "连续整数求和",
        "problem": "三个连续整数的和是72。这三个整数中最大的是多少？",
        "answer": 25,
        "explanation": "设中间数为x，则三个数为(x-1), x, (x+1)。和为3x = 72，x = 24。最大数为25。"
    },
    {
        "name": "工作效率",
        "description": "工作效率问题",
        "problem": "A单独完成一项工作需要6天，B单独完成需要4天。如果A和B一起工作，需要多少天完成？",
        "answer": 2.4,
        "explanation": "A效率：1/6 每天。B效率：1/4 每天。合计：1/6 + 1/4 = 2/12 + 3/12 = 5/12 每天。时间：12/5 = 2.4天。"
    },
    {
        "name": "混合物问题",
        "description": "混合浓度",
        "problem": "有10%浓度的盐水200克，要配制成20%浓度的盐水，需要加入多少克盐？",
        "answer": 25,
        "explanation": "原盐水中盐：200 * 0.1 = 20克。设加入x克盐，则 (20+x)/(200+x) = 0.2。解得：20+x = 40+0.2x，0.8x = 20，x = 25克。"
    },
    {
        "name": "年龄问题",
        "description": "年龄差问题",
        "problem": "父亲现在45岁，儿子15岁。多少年后父亲的年龄是儿子年龄的2倍？",
        "answer": 15,
        "explanation": "设x年后，45+x = 2(15+x)。45+x = 30+2x，x = 15。15年后父亲60岁，儿子30岁。"
    },
    {
        "name": "利润计算",
        "description": "利润百分比",
        "problem": "一件商品成本价是80元，售价是104元。利润率是多少？",
        "answer": 30,
        "explanation": "利润：104 - 80 = 24元。利润率：24/80 * 100% = 30%。"
    },
    {
        "name": "数列求和",
        "description": "等差数列求和",
        "problem": "计算1到100所有整数的和是多少？",
        "answer": 5050,
        "explanation": "等差数列求和公式：n(n+1)/2 = 100*101/2 = 5050。或者用配对法：(1+100) + (2+99) + ... = 101 * 50 = 5050。"
    },
    {
        "name": "利息计算",
        "description": "复利计算",
        "problem": "本金10000元，年利率5%，存3年后本息共多少？（复利计算）",
        "answer": 11576.25,
        "explanation": "复利公式：A = P(1+r)^n = 10000 * (1+0.05)^3 = 10000 * 1.157625 = 11576.25元。"
    },
]


class MathEvaluator(BaseEvaluator):
    """数学能力评估器"""

    name = "math"
    description = "数学推理能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-数学"

    @property
    def stage_number(self) -> int:
        return 2

    @property
    def threshold_percentage(self) -> float:
        return 0.5  # 50% 通过门槛

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行数学能力测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in MATH_TEST_CASES:
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
        """测试单个数学问题"""
        import requests

        prompt = f"请解答以下数学题，只输出最终答案数字：\n\n{test_case['problem']}"

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个数学助手，请仔细思考后给出答案。"},
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
                    category="数学能力",
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

            # 从回答中提取数字
            extracted_answer = self._extract_number(content)
            expected = test_case["answer"]

            # 判断正确性（允许0.1的浮点误差）
            passed = abs(extracted_answer - expected) < 0.11 if extracted_answer is not None else False

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "problem": test_case["problem"],
                "expected_answer": expected,
                "generated_answer": content,
                "extracted_answer": extracted_answer,
                "passed": passed,
                "raw_response": data
            }, test_type="math")

            return TestResult(
                name=test_case["name"],
                category="数学能力",
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "description": test_case["description"],
                    "problem": test_case["problem"],
                    "expected_answer": expected,
                    "extracted_answer": extracted_answer,
                    "model_answer": content[:200]
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category="数学能力",
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _extract_number(self, text: str) -> float:
        """从文本中提取数字答案 - 修复版，支持推理模型"""
        return extract_last_number(text)


def run_math_test(model_url: str, model_name: str) -> dict:
    """运行数学测试"""
    evaluator = MathEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 数学能力测试")
    print("="*60)

    result = run_math_test(
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
            print(f"   期望: {test['details'].get('expected_answer', 'N/A')}")
            print(f"   提取: {test['details'].get('extracted_answer', 'N/A')}")
        if test["error"]:
            print(f"   错误: {test['error']}")

    with open("eval_results/v100_math_test.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n结果已保存: eval_results/v100_math_test.json")
