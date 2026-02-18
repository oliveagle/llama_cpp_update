#!/usr/bin/env python3
"""
多轮对话能力测试

测试模型的上下文理解和多轮交互能力
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


# 多轮对话测试用例
MULTITURN_TEST_CASES = [
    {
        "name": "指代消解",
        "description": "理解代词指代",
        "turns": [
            {"role": "user", "content": "张三和李四是好朋友。"},
            {"role": "assistant", "content": "明白了，他们是好朋友。"},
            {"role": "user", "content": "他昨天结婚了。"}
        ],
        "question": "谁结婚了？",
        "expected_answer": ["张三"],
        "category": "指代消解"
    },
    {
        "name": "信息追踪",
        "description": "跟踪对话中的信息",
        "turns": [
            {"role": "user", "content": "我要订一张明天北京到上海的机票。"},
            {"role": "assistant", "content": "好的，已记录您的需求。"},
            {"role": "user", "content": "改成后天的吧。"},
            {"role": "assistant", "content": "好的，改到后天。"},
            {"role": "user", "content": "还是明天吧。"}
        ],
        "question": "最终订的是哪天的机票？",
        "expected_answer": ["明天"],
        "category": "信息追踪"
    },
    {
        "name": "意图变化",
        "description": "理解意图变化",
        "turns": [
            {"role": "user", "content": "我想吃意大利面。"},
            {"role": "assistant", "content": "好的，意大利面是不错的选择。"},
            {"role": "user", "content": "算了，还是吃寿司吧。"}
        ],
        "question": "用户最终想吃什么？",
        "expected_answer": ["寿司"],
        "category": "意图变化"
    },
    {
        "name": "上下文计算",
        "description": "基于上下文的计算",
        "turns": [
            {"role": "user", "content": "我有100元钱。"},
            {"role": "assistant", "content": "好的，您有100元。"},
            {"role": "user", "content": "花了30元买了本书。"},
            {"role": "assistant", "content": "还剩70元。"},
            {"role": "user", "content": "又花了25元吃午饭。"}
        ],
        "question": "现在还剩多少钱？",
        "expected_answer": ["45", "45元"],
        "category": "上下文计算"
    },
    {
        "name": "角色一致性",
        "description": "保持角色设定",
        "turns": [
            {"role": "user", "content": "假设你是一位历史老师，请用老师的身份和我对话。"},
            {"role": "assistant", "content": "好的同学，我是你的历史老师。"},
            {"role": "user", "content": "老师，请介绍一下秦始皇。"}
        ],
        "check_keywords": ["同学", "我们", "学习", "历史"],
        "category": "角色一致"
    },
    {
        "name": "多条件约束",
        "description": "处理多个条件",
        "turns": [
            {"role": "user", "content": "我要找一家餐厅。"},
            {"role": "assistant", "content": "好的，有什么要求吗？"},
            {"role": "user", "content": "要便宜的。"},
            {"role": "assistant", "content": "好的，经济实惠的。"},
            {"role": "user", "content": "还要在市中心。"},
            {"role": "assistant", "content": "好的，市中心的位置。"},
            {"role": "user", "content": "最好有包间。"}
        ],
        "question": "用户有哪些要求？",
        "expected_answer": ["便宜", "市中心", "包间"],
        "category": "多条件约束"
    },
    {
        "name": "否定理解",
        "description": "理解否定和转折",
        "turns": [
            {"role": "user", "content": "我喜欢红色。"},
            {"role": "assistant", "content": "红色很热情。"},
            {"role": "user", "content": "但我不喜欢穿红色的衣服。"}
        ],
        "question": "用户喜欢穿红色衣服吗？",
        "expected_answer": ["不喜欢", "不"],
        "category": "否定理解"
    },
    {
        "name": "时间顺序",
        "description": "理解时间线",
        "turns": [
            {"role": "user", "content": "早上8点我吃了早餐。"},
            {"role": "assistant", "content": "好的，早餐在8点。"},
            {"role": "user", "content": "中午12点吃了午饭。"},
            {"role": "assistant", "content": "午餐在12点。"},
            {"role": "user", "content": "晚餐比午餐晚6个小时。"}
        ],
        "question": "晚餐是几点？",
        "expected_answer": ["18", "18点", "6点", "下午6点"],
        "category": "时间顺序"
    },
    {
        "name": "隐含信息",
        "description": "理解隐含意图",
        "turns": [
            {"role": "user", "content": "这件衣服多少钱？"},
            {"role": "assistant", "content": "这件衣服售价500元。"},
            {"role": "user", "content": "好贵啊，我预算只有300。"}
        ],
        "question": "用户的意思是什么？",
        "expected_answer": ["买不起", "超预算", "太贵", "不想买"],
        "category": "隐含信息"
    },
    {
        "name": "任务恢复",
        "description": "从打断中恢复",
        "turns": [
            {"role": "user", "content": "帮我订明天上午的机票。"},
            {"role": "assistant", "content": "好的，请问从哪里出发？"},
            {"role": "user", "content": "对了，今天天气怎么样？"},
            {"role": "assistant", "content": "今天天气晴朗。"},
            {"role": "user", "content": "继续说机票的事。"}
        ],
        "check_keywords": ["出发", "哪里", "目的地", "城市"],
        "category": "任务恢复"
    }
]


class MultiTurnEvaluator(BaseEvaluator):
    """多轮对话能力评估器"""

    name = "multiturn"
    description = "多轮对话能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-多轮对话"

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
        """运行多轮对话测试"""
        test_results = []
        start_time = time.time()

        for test_case in MULTITURN_TEST_CASES:
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
        """测试单个多轮对话场景"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"

        # 构建消息历史
        messages = [{"role": "system", "content": "你是一个 helpful 助手。"}]

        # 执行多轮对话
        for turn in test_case["turns"]:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # 最终问题
        if "question" in test_case:
            messages.append({"role": "user", "content": test_case["question"]})

        payload = {
            "model": self.model_name,
            "messages": messages,
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

            # 检查答案
            if "expected_answer" in test_case:
                answers = test_case["expected_answer"]
                if isinstance(answers, str):
                    answers = [answers]
                passed = any(ans in content for ans in answers)
            elif "check_keywords" in test_case:
                keywords = test_case["check_keywords"]
                passed = sum(1 for kw in keywords if kw in content) >= len(keywords) * 0.5
            else:
                passed = False

            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "conversation": test_case["turns"],
                "expected_answer": test_case.get("expected_answer") or test_case.get("check_keywords"),
                "generated_response": content,
                "passed": passed,
                "raw_response": data
            }, test_type="multiturn")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "response": content[:200]
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


def run_multiturn_test(model_url: str, model_name: str) -> dict:
    """运行多轮对话测试"""
    evaluator = MultiTurnEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 多轮对话能力测试")
    print("="*60)

    result = run_multiturn_test(
        "http://localhost:8401",
        "test-model"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
