#!/usr/bin/env python3
"""
工具使用能力测试 - 函数调用/Tool Use

测试模型的工具理解、调用格式生成和结果处理能力
"""

import time
import json
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger
from .utils_reasoning import clean_reasoning_output


# 工具使用测试用例 (10个)
TOOL_TEST_CASES = [
    {
        "name": "天气查询工具",
        "category": "工具理解",
        "description": "理解天气查询工具参数",
        "prompt": "用户问：'北京明天天气怎么样？'\n\n可用工具：\n{\"name\": \"get_weather\", \"parameters\": {\"city\": \"城市名\", \"date\": \"YYYY-MM-DD\"}}\n\n请输出应该调用的工具参数（JSON格式）：",
        "check_keywords": ["get_weather", "北京", "city"],
        "require_json": True
    },
    {
        "name": "计算器工具",
        "category": "工具调用",
        "description": "生成计算器工具调用",
        "prompt": "计算：158 × 67 + 234 = ?\n\n可用工具：\n{\"name\": \"calculator\", \"parameters\": {\"expression\": \"数学表达式\"}}\n\n请输出工具调用：",
        "check_keywords": ["calculator", "expression", "158", "67", "234"],
        "require_json": True
    },
    {
        "name": "搜索引擎工具",
        "category": "工具理解",
        "description": "理解搜索工具参数",
        "prompt": "用户想了解：'最新的iPhone发布日期'\n\n可用工具：\n{\"name\": \"web_search\", \"parameters\": {\"query\": \"搜索关键词\", \"num_results\": \"结果数量\"}}\n\n请输出工具调用参数：",
        "check_keywords": ["web_search", "query", "iPhone"],
        "require_json": True
    },
    {
        "name": "数据库查询工具",
        "category": "工具调用",
        "description": "生成SQL查询工具调用",
        "prompt": "查询：获取所有年龄大于25岁的用户\n\n可用工具：\n{\"name\": \"execute_sql\", \"parameters\": {\"sql\": \"SQL语句\"}}\n\n请输出工具调用：",
        "check_keywords": ["execute_sql", "sql", "SELECT", "age", ">", "25"],
        "require_json": True
    },
    {
        "name": "发送邮件工具",
        "category": "工具理解",
        "description": "理解邮件工具参数",
        "prompt": "发送邮件给：zhangsan@example.com，主题是：'会议通知'，内容是：'明天下午2点开会'\n\n可用工具：\n{\"name\": \"send_email\", \"parameters\": {\"to\": \"收件人\", \"subject\": \"主题\", \"body\": \"内容\"}}\n\n请输出工具调用：",
        "check_keywords": ["send_email", "zhangsan@example.com", "会议通知"],
        "require_json": True
    },
    {
        "name": "文件读取工具",
        "category": "工具调用",
        "description": "生成文件读取调用",
        "prompt": "读取文件：/home/user/data.txt\n\n可用工具：\n{\"name\": \"read_file\", \"parameters\": {\"path\": \"文件路径\"}}\n\n请输出工具调用：",
        "check_keywords": ["read_file", "path", "/home/user/data.txt"],
        "require_json": True
    },
    {
        "name": "日期时间工具",
        "category": "工具理解",
        "description": "理解时间工具参数",
        "prompt": "获取当前北京时间\n\n可用工具：\n{\"name\": \"get_datetime\", \"parameters\": {\"timezone\": \"时区\", \"format\": \"格式\"}}\n\n请输出工具调用：",
        "check_keywords": ["get_datetime", "timezone", "Beijing", "Asia/Shanghai"],
        "require_json": True
    },
    {
        "name": "翻译工具",
        "category": "工具调用",
        "description": "生成翻译工具调用",
        "prompt": "将'Hello World'翻译成中文\n\n可用工具：\n{\"name\": \"translate\", \"parameters\": {\"text\": \"待翻译文本\", \"target_lang\": \"目标语言\"}}\n\n请输出工具调用：",
        "check_keywords": ["translate", "text", "Hello World", "zh", "中文"],
        "require_json": True
    },
    {
        "name": "地图定位工具",
        "category": "工具理解",
        "description": "理解地图工具参数",
        "prompt": "查找：天安门广场的坐标\n\n可用工具：\n{\"name\": \"geocode\", \"parameters\": {\"address\": \"地址\", \"city\": \"城市\"}}\n\n请输出工具调用：",
        "check_keywords": ["geocode", "address", "天安门"],
        "require_json": True
    },
    {
        "name": "单位换算工具",
        "category": "工具调用",
        "description": "生成单位换算调用",
        "prompt": "将100英里换算成公里\n\n可用工具：\n{\"name\": \"unit_convert\", \"parameters\": {\"value\": \"数值\", \"from_unit\": \"原单位\", \"to_unit\": \"目标单位\"}}\n\n请输出工具调用：",
        "check_keywords": ["unit_convert", "value", "100", "mile", "km"],
        "require_json": True
    },
]


class ToolEvaluator(BaseEvaluator):
    """工具使用能力评估器"""

    name = "tool"
    description = "工具使用能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-工具使用"

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
        """运行工具使用测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in TOOL_TEST_CASES:
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
        """测试单个工具使用用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个智能助手，可以使用各种工具帮助用户。请根据用户需求输出正确的工具调用参数。"},
                {"role": "user", "content": test_case["prompt"]}
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
            # 支持推理模型：如果 content 为空，尝试使用 reasoning_content
            if not content:
                content = message.get("reasoning_content", "")

            # 评估回答质量
            score = self._evaluate_tool_response(content, test_case)
            passed = score >= 0.6  # 60% 分数视为通过

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "prompt": test_case["prompt"],
                "expected_keywords": test_case["check_keywords"],
                "generated_response": content,
                "score": score,
                "passed": passed,
                "raw_response": data
            }, test_type="tool")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "description": test_case["description"],
                    "expected_keywords": test_case["check_keywords"],
                    "model_response": content[:300],
                    "score": score
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

    def _evaluate_tool_response(self, content: str, test_case: dict) -> float:
        """
        评估工具使用回答质量
        返回 0-1 的分数
        """
        # 使用清理后的内容（支持推理模型）
        cleaned_content = clean_reasoning_output(content)
        content_lower = cleaned_content.lower()
        score = 0.0

        # 1. 检查必须包含的关键词
        keywords = test_case.get("check_keywords", [])
        matched_keywords = [kw for kw in keywords if kw.lower() in content_lower]
        keyword_score = len(matched_keywords) / len(keywords) if keywords else 0
        score += keyword_score * 0.6  # 关键词匹配占60%

        # 2. 检查是否为JSON格式（如果要求）
        if test_case.get("require_json"):
            try:
                # 尝试提取JSON内容
                json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    json.loads(json_str)  # 验证JSON有效性
                    score += 0.3  # 有效JSON占30%
            except:
                pass

            # 3. 检查工具名称格式
            tool_name_match = re.search(r'"name"\s*:\s*"([^"]+)"', content)
            if tool_name_match:
                score += 0.1  # 正确的工具名称格式占10%

        return min(score, 1.0)  # 最高1.0


def run_tool_test(model_url: str, model_name: str) -> dict:
    """运行工具使用测试"""
    evaluator = ToolEvaluator(model_url, model_name)
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
    print("V100 (CUDA) 工具使用能力测试")
    print("="*60)

    result = run_tool_test(
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
        rate = stats["passed"] / stats["total"] * 100
        print(f"  {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
