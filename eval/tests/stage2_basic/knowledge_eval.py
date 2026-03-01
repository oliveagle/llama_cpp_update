#!/usr/bin/env python3
"""
知识问答能力测试

测试模型的世界知识和常识推理
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger
from .utils_reasoning import extract_answer_letter


# 知识问答测试用例
KNOWLEDGE_TEST_CASES = [
    {
        "name": "历史知识",
        "description": "中国历史",
        "question": "中国历史上第一个统一的多民族封建王朝是？",
        "options": ["A. 商朝", "B. 周朝", "C. 秦朝", "D. 汉朝"],
        "answer": "C",
        "category": "历史"
    },
    {
        "name": "地理知识",
        "description": "世界地理",
        "question": "世界上面积最大的海洋是？",
        "options": ["A. 大西洋", "B. 印度洋", "C. 太平洋", "D. 北冰洋"],
        "answer": "C",
        "category": "地理"
    },
    {
        "name": "科学知识",
        "description": "基础物理",
        "question": "光在真空中的传播速度约是多少？",
        "options": ["A. 30万公里/秒", "B. 15万公里/秒", "C. 50万公里/秒", "D. 100万公里/秒"],
        "answer": "A",
        "category": "科学"
    },
    {
        "name": "生物知识",
        "description": "基础生物学",
        "question": "人类有多少对染色体？",
        "options": ["A. 22对", "B. 23对", "C. 24对", "D. 46对"],
        "answer": "B",
        "category": "生物"
    },
    {
        "name": "文学知识",
        "description": "中国文学",
        "question": "《红楼梦》的作者是？",
        "options": ["A. 罗贯中", "B. 施耐庵", "C. 吴承恩", "D. 曹雪芹"],
        "answer": "D",
        "category": "文学"
    },
    {
        "name": "艺术知识",
        "description": "世界艺术",
        "question": "《蒙娜丽莎》的作者是哪位画家？",
        "options": ["A. 米开朗基罗", "B. 达芬奇", "C. 拉斐尔", "D. 梵高"],
        "answer": "B",
        "category": "艺术"
    },
    {
        "name": "计算机知识",
        "description": "基础计算机",
        "question": "HTTP状态码404表示什么？",
        "options": ["A. 服务器错误", "B. 未授权", "C. 未找到资源", "D. 重定向"],
        "answer": "C",
        "category": "计算机"
    },
    {
        "name": "经济知识",
        "description": "基础经济",
        "question": "GDP是什么的缩写？",
        "options": ["A. 国内生产总值", "B. 国民生产总值", "C. 国内生产净值", "D. 国民收入"],
        "answer": "A",
        "category": "经济"
    },
    {
        "name": "医学常识",
        "description": "健康常识",
        "question": "人体最大的器官是？",
        "options": ["A. 肝脏", "B. 大脑", "C. 皮肤", "D. 心脏"],
        "answer": "C",
        "category": "医学"
    },
    {
        "name": "天文知识",
        "description": "基础天文",
        "question": "太阳系中最大的行星是？",
        "options": ["A. 土星", "B. 木星", "C. 天王星", "D. 海王星"],
        "answer": "B",
        "category": "天文"
    }
]


class KnowledgeEvaluator(BaseEvaluator):
    """知识问答能力评估器"""

    name = "knowledge"
    description = "知识问答能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-知识问答"

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
        """运行知识问答测试"""
        test_results = []
        start_time = time.time()

        for test_case in KNOWLEDGE_TEST_CASES:
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
        """测试单个知识问题"""
        import requests

        options = "\n".join(test_case["options"])
        prompt = f"问题：{test_case['question']}\n\n{options}\n\n请只回答选项字母（A/B/C/D）："

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个知识问答专家，请回答以下选择题。"},
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

            # 提取答案 - 使用修复版逻辑支持推理模型
            expected_answer = test_case["answer"]
            extracted_answer = extract_answer_letter(content)
            passed = extracted_answer == expected_answer.upper()

            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "question": test_case["question"],
                "expected_answer": expected_answer,
                "generated_answer": content,
                "passed": passed,
                "raw_response": data
            }, test_type="knowledge")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "question": test_case["question"],
                    "expected_answer": expected_answer,
                    "model_answer": content[:100]
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


def run_knowledge_test(model_url: str, model_name: str) -> dict:
    """运行知识问答测试"""
    evaluator = KnowledgeEvaluator(model_url, model_name)
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
    print("="*60)
    print("V100 (CUDA) 知识问答能力测试")
    print("="*60)

    result = run_knowledge_test(
        "http://localhost:8401",
        "test-model"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
