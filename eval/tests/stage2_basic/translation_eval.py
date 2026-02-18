#!/usr/bin/env python3
"""
翻译能力测试

测试模型的多语言翻译能力
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


# 翻译测试用例
TRANSLATION_TEST_CASES = [
    {
        "name": "中英翻译",
        "description": "中文翻译成英文",
        "source": "人工智能正在改变我们的生活方式。",
        "target_language": "English",
        "expected_keywords": ["AI", "artificial intelligence", "changing", "life", "lifestyle"],
        "category": "中译英"
    },
    {
        "name": "英中翻译",
        "description": "英文翻译成中文",
        "source": "The quick brown fox jumps over the lazy dog.",
        "target_language": "Chinese",
        "expected_keywords": ["狐狸", "狗", "跳", "棕色", "敏捷"],
        "category": "英译中"
    },
    {
        "name": "技术文档翻译",
        "description": "技术术语翻译",
        "source": "Machine learning is a subset of artificial intelligence.",
        "target_language": "Chinese",
        "expected_keywords": ["机器学习", "人工智能", "子集"],
        "category": "英译中"
    },
    {
        "name": "商务邮件翻译",
        "description": "商务场景翻译",
        "source": "敬启者：关于我们上次的会议，我想跟进一下项目进度。",
        "target_language": "English",
        "expected_keywords": ["Dear", "meeting", "follow up", "project", "progress"],
        "category": "中译英"
    },
    {
        "name": "文学翻译",
        "description": "文学性文本翻译",
        "source": "To be, or not to be, that is the question.",
        "target_language": "Chinese",
        "expected_keywords": ["生存", "毁灭", "问题", "是"],
        "category": "英译中"
    },
    {
        "name": "口语翻译",
        "description": "日常口语翻译",
        "source": "Long time no see! How have you been?",
        "target_language": "Chinese",
        "expected_keywords": ["好久", "见", "最近", "怎么样"],
        "category": "英译中"
    },
    {
        "name": "成语翻译",
        "description": "中文成语翻译",
        "source": "塞翁失马，焉知非福。",
        "target_language": "English",
        "expected_keywords": ["blessing", "disguise", "loss", "fortune"],
        "category": "中译英"
    },
    {
        "name": "新闻翻译",
        "description": "新闻标题翻译",
        "source": "Global markets rally as inflation concerns ease.",
        "target_language": "Chinese",
        "expected_keywords": ["全球", "市场", "通胀", "担忧", "缓解"],
        "category": "英译中"
    },
    {
        "name": "科技术语翻译",
        "description": "专业术语",
        "source": "云计算、大数据和物联网是数字化转型的关键技术。",
        "target_language": "English",
        "expected_keywords": ["cloud computing", "big data", "IoT", "digital transformation"],
        "category": "中译英"
    },
    {
        "name": "简洁翻译",
        "description": "简洁表达",
        "source": "I love you.",
        "target_language": "Chinese",
        "expected_keywords": ["爱", "喜欢"],
        "category": "英译中"
    }
]


class TranslationEvaluator(BaseEvaluator):
    """翻译能力评估器"""

    name = "translation"
    description = "翻译能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-翻译"

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
        """运行翻译测试"""
        test_results = []
        start_time = time.time()

        for test_case in TRANSLATION_TEST_CASES:
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
        """测试单个翻译任务"""
        import requests

        prompt = f"请将以下文本翻译成{test_case['target_language']}：\n\n{test_case['source']}"

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业翻译，请准确翻译以下文本。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 256,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
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

            # 检查关键词
            keywords = test_case["expected_keywords"]
            passed = sum(1 for kw in keywords if kw.lower() in content.lower()) >= len(keywords) * 0.5

            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "source": test_case["source"],
                "target_language": test_case["target_language"],
                "expected_keywords": keywords,
                "generated_translation": content,
                "passed": passed,
                "raw_response": data
            }, test_type="translation")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "source": test_case["source"],
                    "translation": content[:200],
                    "expected_keywords": keywords
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


def run_translation_test(model_url: str, model_name: str) -> dict:
    """运行翻译测试"""
    evaluator = TranslationEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 翻译能力测试")
    print("="*60)

    result = run_translation_test(
        "http://localhost:8401",
        "test-model"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
