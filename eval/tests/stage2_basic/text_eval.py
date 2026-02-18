#!/usr/bin/env python3
"""
文本理解测试 - MMLU/CMMLU 风格

测试模型的文本理解、知识推理能力
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


# 文本理解测试用例
TEXT_TEST_CASES = [
    {
        "name": "历史知识",
        "category": "人文历史",
        "question": "中国的四大发明不包括以下哪一项？",
        "options": ["造纸术", "指南针", "火药", "地动仪"],
        "answer": "D",
        "explanation": "四大发明是造纸术、指南针、火药、印刷术。地动仪是张衡发明的地震检测仪器，不属于四大发明。"
    },
    {
        "name": "物理常识",
        "category": "自然科学",
        "question": "光在真空中的传播速度约为多少？",
        "options": ["3×10^6 m/s", "3×10^8 m/s", "3×10^10 m/s", "3×10^4 m/s"],
        "answer": "B",
        "explanation": "光速约为 3×10^8 米/秒（30万公里/秒）。"
    },
    {
        "name": "逻辑推理",
        "category": "逻辑推理",
        "question": "所有的猫都是哺乳动物。汤姆是一只猫。因此：",
        "options": ["汤姆是哺乳动物", "汤姆不是哺乳动物", "无法确定", "汤姆是狗"],
        "answer": "A",
        "explanation": "根据三段论，所有猫都是哺乳动物，汤姆是猫，所以汤姆是哺乳动物。"
    },
    {
        "name": "文学常识",
        "category": "文学艺术",
        "question": "《红楼梦》的作者是？",
        "options": ["曹雪芹", "罗贯中", "施耐庵", "吴承恩"],
        "answer": "A",
        "explanation": "《红楼梦》作者是曹雪芹。罗贯中写《三国演义》，施耐庵写《水浒传》，吴承恩写《西游记》。"
    },
    {
        "name": "化学知识",
        "category": "自然科学",
        "question": "水的化学式是？",
        "options": ["HO", "H2O", "H2O2", "CO2"],
        "answer": "B",
        "explanation": "水的化学式是 H2O，表示两个氢原子和一个氧原子组成。"
    },
    {
        "name": "地理知识",
        "category": "地理",
        "question": "世界上面积最大的国家是？",
        "options": ["中国", "美国", "俄罗斯", "加拿大"],
        "answer": "C",
        "explanation": "俄罗斯是世界上面积最大的国家，约1700万平方公里。"
    },
    {
        "name": "数学逻辑",
        "category": "数学逻辑",
        "question": "如果 A > B 且 B > C，那么：",
        "options": ["A > C", "A < C", "A = C", "无法确定"],
        "answer": "A",
        "explanation": "根据传递性，A > B 且 B > C，所以 A > C。"
    },
    {
        "name": "生物知识",
        "category": "生命科学",
        "question": "人类有多少对染色体？",
        "options": ["22对", "23对", "24对", "46对"],
        "answer": "B",
        "explanation": "人类有23对（46条）染色体，其中22对是常染色体，1对是性染色体。"
    },
    {
        "name": "天文知识",
        "category": "天文地理",
        "question": "太阳系中最大的行星是？",
        "options": ["地球", "土星", "木星", "火星"],
        "answer": "C",
        "explanation": "木星是太阳系中最大的行星，直径约为地球的11倍。"
    },
    {
        "name": "计算机基础",
        "category": "计算机科学",
        "question": "HTTP状态码404表示什么意思？",
        "options": ["服务器错误", "未找到", "重定向", "禁止访问"],
        "answer": "B",
        "explanation": "HTTP 404表示请求的资源未找到（Not Found）。"
    },
]


class TextEvaluator(BaseEvaluator):
    """文本理解评估器"""

    name = "text"
    description = "文本理解和知识推理测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-文本"

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
        """运行文本理解测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in TEXT_TEST_CASES:
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
        """测试单个文本理解问题"""
        import requests

        options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case["options"])])
        prompt = f"{test_case['question']}\n\n{options_text}\n\n请回答选项字母（A/B/C/D）："

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个知识问答助手，请直接回答选项字母。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 64,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=60)
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
            # 支持推理模型：如果 content 为空，尝试使用 reasoning_content
            if not content:
                content = message.get("reasoning_content", "")
            content = content.strip().upper()

            # 提取答案字母
            extracted_answer = self._extract_answer(content)
            expected = test_case["answer"]
            passed = extracted_answer == expected

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "category": test_case["category"],
                "question": test_case["question"],
                "expected_answer": expected,
                "generated_answer": content,
                "extracted_answer": extracted_answer,
                "passed": passed,
                "raw_response": data
            }, test_type="text")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "question": test_case["question"],
                    "expected": expected,
                    "extracted": extracted_answer,
                    "model_answer": content
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

    def _extract_answer(self, text: str) -> str:
        """从回答中提取答案字母"""
        text = text.upper()

        # 查找 A/B/C/D
        for char in ["A", "B", "C", "D"]:
            if char in text:
                return char

        return ""


def run_text_test(model_url: str, model_name: str) -> dict:
    """运行文本理解测试"""
    evaluator = TextEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 文本理解测试")
    print("="*60)

    result = run_text_test(
        "http://localhost:8401",
        "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
    print(f"耗时: {result['duration_seconds']:.1f}秒")

    print("\n分类统计:")
    categories = {}
    for test in result["tests"]:
        cat = test["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if test["passed"]:
            categories[cat]["passed"] += 1

    for cat, stats in categories.items():
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")

    print("\n详细结果:")
    for test in result["tests"]:
        status = "✅" if test["passed"] else "❌"
        print(f"{status} [{test['category']}] {test['name']}")

    with open("eval_results/v100_text_test.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n结果已保存: eval_results/v100_text_test.json")
