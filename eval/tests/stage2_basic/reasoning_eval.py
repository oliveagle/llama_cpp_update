#!/usr/bin/env python3
"""
逻辑推理能力测试

测试模型的逻辑推理、因果推理和模式识别能力
"""

import time
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger
from .utils_reasoning import extract_answer_letter, clean_reasoning_output


# 逻辑推理测试用例
REASONING_TEST_CASES = [
    {
        "name": "三段论推理",
        "description": "经典三段论逻辑",
        "problem": "前提1：所有人都是会死的。前提2：苏格拉底是人。结论：苏格拉底会怎样？",
        "answer": ["会死", "死亡", "mortal"],
        "category": "演绎推理"
    },
    {
        "name": "因果推理",
        "description": "识别因果关系",
        "problem": "如果明天下雨，那么地面会湿。今天地面是湿的。可以得出什么结论？A) 今天下雨了 B) 地面湿了 C) 无法确定是否下雨 D) 明天会下雨",
        "answer": "C",
        "category": "因果推理"
    },
    {
        "name": "模式识别",
        "description": "数字序列规律",
        "problem": "找出数列的下一个数字：2, 6, 12, 20, 30, ?",
        "answer": ["42"],
        "explanation": "差值依次为4,6,8,10,12，所以下一个是30+12=42",
        "category": "模式识别"
    },
    {
        "name": "逻辑排序",
        "description": "事件顺序推理",
        "problem": "A比B高，B比C高，D比A矮但比B高。谁最矮？",
        "answer": ["C", "c"],
        "category": "关系推理"
    },
    {
        "name": "条件推理",
        "description": "if-then 逻辑",
        "problem": "如果学生努力学习，那么他会通过考试。小明通过了考试。可以得出：A) 小明努力了 B) 小明没努力 C) 无法确定 D) 考试很简单",
        "answer": "C",
        "category": "条件推理"
    },
    {
        "name": "类比推理",
        "description": "关系类比",
        "problem": "医生对医院，就像教师对____？",
        "answer": ["学校", "课堂", "教室"],
        "category": "类比推理"
    },
    {
        "name": "空间推理",
        "description": "方向位置推理",
        "problem": "小明面向北方，向右转90度，再向后转。现在他面向哪个方向？",
        "answer": ["西", "西方", "west", "面向西", "朝西", "向西", "西方向"],
        "category": "空间推理"
    },
    {
        "name": "排除法推理",
        "description": "排除不可能选项",
        "problem": "有三个盒子，分别标有'苹果'、'橙子'、'混合'，但所有标签都贴错了。从标有'混合'的盒子中取出一个水果是苹果。正确的标签应该如何？",
        "answer": ["混合盒子是苹果", "混合装苹果", "mixed is apple", "标混合的是苹果", "混合标签是苹果", "混合=苹果", "第三个盒子是苹果", "标有混合的盒子装苹果", "混合盒子实际装苹果", "标混合的装苹果"],
        "category": "排除推理"
    },
    {
        "name": "概率推理",
        "description": "基础概率计算",
        "problem": "一个袋子里有3个红球和2个蓝球。随机取出一个球，是红球的概率是多少？用百分数表示。",
        "answer": ["60%", "60", "0.6", "3/5", "五分之三", "百分之六十"],
        "category": "概率推理"
    },
    {
        "name": "逻辑谜题",
        "description": "经典逻辑谜题",
        "problem": "一个岛上住着骑士（总是说真话）和无赖（总是说谎）。A说：'B是骑士'。B说：'A是无赖'。A和B各是什么？",
        "answer": ["A是骑士B是无赖", "A knight B knave", "A骑士B无赖", "A说真话B说谎", "A真B假", "A真话B谎话", "A是说真话的B是说谎的", "A骑士，B无赖"],
        "category": "逻辑谜题"
    }
]


class ReasoningEvaluator(BaseEvaluator):
    """逻辑推理能力评估器"""

    name = "reasoning"
    description = "逻辑推理能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-逻辑推理"

    @property
    def stage_number(self) -> int:
        return 2

    @property
    def threshold_percentage(self) -> float:
        return 0.5

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行逻辑推理测试"""
        test_results = []
        start_time = time.time()

        for test_case in REASONING_TEST_CASES:
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
        """测试单个推理问题"""
        import requests

        prompt = f"请回答以下逻辑推理问题，直接给出答案：\n\n{test_case['problem']}"

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个逻辑推理专家，请仔细思考后给出简洁答案。"},
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
                    category=test_case["category"],
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            if not content:
                content = message.get("reasoning_content", "")

            # 检查答案 - 修复版支持推理模型
            answer = test_case["answer"]
            # 清理推理过程
            cleaned_content = clean_reasoning_output(content)

            if isinstance(answer, list):
                # 文本答案列表 - 在清理后的内容中查找
                passed = any(str(a).lower() in cleaned_content.lower() for a in answer)
            elif answer in ["A", "B", "C", "D"]:
                # 选择题答案 - 使用字母提取
                extracted = extract_answer_letter(cleaned_content)
                passed = extracted == answer
            else:
                # 单文本答案
                passed = str(answer).lower() in cleaned_content.lower()

            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "problem": test_case["problem"],
                "expected_answer": answer,
                "generated_answer": content,
                "passed": passed,
                "raw_response": data
            }, test_type="reasoning")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "problem": test_case["problem"],
                    "expected_answer": answer,
                    "model_answer": content[:200]
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )


def run_reasoning_test(model_url: str, model_name: str) -> dict:
    """运行逻辑推理测试"""
    evaluator = ReasoningEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 逻辑推理能力测试")
    print("="*60)

    result = run_reasoning_test(
        "http://localhost:8401",
        "test-model"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
