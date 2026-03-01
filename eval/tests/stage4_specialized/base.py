#!/usr/bin/env python3
"""
Stage 4 基础评估器
提供通用的测试执行、评分和报告生成功能
"""

import time
import json
import os
import re
import requests
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class TestResult:
    """单个测试结果"""
    name: str
    category: str
    difficulty: str
    passed: bool
    duration_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class StageResult:
    """Stage 测试结果"""
    stage_name: str
    stage_number: int
    category: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration_seconds: float
    test_results: List[TestResult]
    passed_threshold: bool
    threshold_percentage: float
    by_difficulty: Dict[str, Dict] = field(default_factory=dict)
    by_subcategory: Dict[str, Dict] = field(default_factory=dict)

    @property
    def pass_rate(self) -> float:
        return self.passed_tests / self.total_tests if self.total_tests > 0 else 0


class Stage4BaseEvaluator:
    """Stage 4 评估器基类"""

    name = "base"
    description = "基础评估器"

    @property
    def stage_name(self) -> str:
        return "专项能力测试"

    @property
    def stage_number(self) -> int:
        return 4

    @property
    def threshold_percentage(self) -> float:
        return 0.60  # 60% 通过门槛

    def __init__(self, model_url: str, model_name: str, output_dir: str = None, **kwargs):
        self.model_url = model_url
        self.model_name = model_name
        self.output_dir = output_dir or "eval_results/stage4"
        self.timeout = kwargs.get("timeout", 120)
        os.makedirs(self.output_dir, exist_ok=True)

    def _extract_answer(self, text: str) -> str:
        """提取选择题答案 (A/B/C/D)"""
        if not text:
            return ""

        text_upper = text.upper()

        patterns = [
            r'答案 [:：]\s*([A-D])',
            r'答案 (?:是 | 为 | 选)?[:：]?\s*([A-D])',
            r'[\(\[\{]([A-D])[\)\]\}]',
            r'\b([A-D])[\.、\)]',
            r'选项 [:：]?\s*([A-D])',
            r'^([A-D])$',
        ]

        for pattern in patterns:
            match = re.search(pattern, text_upper, re.MULTILINE)
            if match:
                return match.group(1)

        # 最后手段：找最后一个独立的 A-D
        matches = re.findall(r'\b([A-D])\b', text_upper)
        if matches:
            return matches[-1]

        return ""

    def _extract_number(self, text: str) -> Optional[float]:
        """提取数值答案"""
        if not text:
            return None

        # 找数字 (包括负数和小数)
        numbers = re.findall(r'-?\d+\.?\d*', text.replace(',', ''))
        if numbers:
            try:
                return float(numbers[0])
            except ValueError:
                pass
        return None

    def _extract_code(self, text: str) -> str:
        """提取代码块"""
        if not text:
            return ""

        # 提取 ```python ... ``` 或 ``` ... ``` 中的代码
        match = re.search(r'```(?:python)?\n(.*?)\n```', text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # 如果没有代码块，返回原文
        return text.strip()

    def _check_keywords(self, text: str, keywords: List[str]) -> bool:
        """检查是否包含所有关键词"""
        if not text or not keywords:
            return False

        text_lower = text.lower()
        matched = sum(1 for kw in keywords if kw.lower() in text_lower)
        return matched >= len(keywords) * 0.8  # 80% 关键词匹配

    def _test_multiple_choice(self, test_case: Dict) -> TestResult:
        """测试选择题"""
        start_time = time.time()

        # 构建提示
        options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case['options'])])
        prompt = f"回答以下问题，只输出选项字母 (A/B/C/D)，不要解释：\n\n{test_case['question']}\n\n选项:\n{options_str}\n\n答案："

        system_prompt = "你是专家。只回答选项字母，不要任何解释或推理过程。"

        try:
            response = self._call_model(prompt, system_prompt, max_tokens=10)
            elapsed = (time.time() - start_time) * 1000

            if not response["success"]:
                return TestResult(
                    name=test_case["name"],
                    category=test_case.get("category", ""),
                    difficulty=test_case.get("difficulty", ""),
                    passed=False,
                    duration_ms=elapsed,
                    error_message=response.get("error", "")
                )

            answer = self._extract_answer(response["content"])
            expected = test_case["answer"].upper()
            passed = answer == expected

            return TestResult(
                name=test_case["name"],
                category=test_case.get("category", ""),
                difficulty=test_case.get("difficulty", ""),
                passed=passed,
                duration_ms=elapsed,
                details={
                    "expected": expected,
                    "actual": answer,
                    "response": response["content"][:200]
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category=test_case.get("category", ""),
                difficulty=test_case.get("difficulty", ""),
                passed=False,
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

    def _test_code_generation(self, test_case: Dict) -> TestResult:
        """测试代码生成题"""
        start_time = time.time()

        prompt = test_case.get("prompt", "")
        keywords = test_case.get("keywords", [])

        system_prompt = "你是资深程序员。请按要求编写 Python 代码，代码应该简洁高效。"

        try:
            response = self._call_model(prompt, system_prompt, max_tokens=1024)
            elapsed = (time.time() - start_time) * 1000

            if not response["success"]:
                return TestResult(
                    name=test_case["name"],
                    category=test_case.get("category", ""),
                    difficulty=test_case.get("difficulty", ""),
                    passed=False,
                    duration_ms=elapsed,
                    error_message=response.get("error", "")
                )

            code = self._extract_code(response["content"])
            passed = self._check_keywords(code, keywords) if keywords else True

            return TestResult(
                name=test_case["name"],
                category=test_case.get("category", ""),
                difficulty=test_case.get("difficulty", ""),
                passed=passed,
                duration_ms=elapsed,
                details={
                    "keywords_expected": keywords,
                    "code_length": len(code),
                    "response": response["content"][:300]
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category=test_case.get("category", ""),
                difficulty=test_case.get("difficulty", ""),
                passed=False,
                duration_ms=(time.time() - start_time) * 1000,
                error_message=str(e)
            )

    def _call_model(self, prompt: str, system_prompt: str = None, max_tokens: int = 512) -> Dict:
        """调用模型 API"""
        url = f"{self.model_url}/v1/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "top_p": 0.9,
        }

        try:
            resp = requests.post(url, json=payload, timeout=self.timeout)
            if resp.status_code != 200:
                return {"success": False, "error": f"HTTP {resp.status_code}"}

            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})

            return {
                "success": True,
                "content": content,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
            }

        except requests.Timeout:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_stats(self, test_results: List[TestResult]) -> Dict:
        """计算统计数据"""
        by_difficulty = {"简单": {"total": 0, "passed": 0}, "中等": {"total": 0, "passed": 0}, "困难": {"total": 0, "passed": 0}}
        by_subcategory = {}

        for r in test_results:
            diff = r.difficulty
            cat = r.category

            if diff in by_difficulty:
                by_difficulty[diff]["total"] += 1
                if r.passed:
                    by_difficulty[diff]["passed"] += 1

            if cat not in by_subcategory:
                by_subcategory[cat] = {"total": 0, "passed": 0}
            by_subcategory[cat]["total"] += 1
            if r.passed:
                by_subcategory[cat]["passed"] += 1

        # 计算通过率
        for d in by_difficulty.values():
            if d["total"] > 0:
                d["rate"] = d["passed"] / d["total"]

        for c in by_subcategory.values():
            if c["total"] > 0:
                c["rate"] = c["passed"] / c["total"]

        return {"by_difficulty": by_difficulty, "by_subcategory": by_subcategory}

    def _log_raw_data(self, test_results: List[TestResult], test_type: str):
        """记录原始数据"""
        timestamp = datetime.now().strftime("%Y-%m-%d")
        backend = "vulkan" if "8400" in self.model_url else "v100"
        raw_dir = os.path.join(self.output_dir, "raw_data")
        os.makedirs(raw_dir, exist_ok=True)

        log_file = os.path.join(raw_dir, f"{backend}_{timestamp}.jsonl")

        with open(log_file, "a", encoding="utf-8") as f:
            for r in test_results:
                record = {
                    "timestamp": datetime.now().isoformat(),
                    "backend": backend,
                    "model": self.model_name,
                    "test_type": test_type,
                    "name": r.name,
                    "category": r.category,
                    "difficulty": r.difficulty,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "details": r.details,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def run_tests(self, test_cases: List[Dict], test_type: str = "unknown") -> StageResult:
        """运行测试"""
        test_results = []
        start_time = time.time()

        for i, test_case in enumerate(test_cases, 1):
            print(f"\r  进度：{i}/{len(test_cases)}", end="", flush=True)

            if "options" in test_case:
                result = self._test_multiple_choice(test_case)
            else:
                result = self._test_code_generation(test_case)

            test_results.append(result)

        elapsed = time.time() - start_time
        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        # 计算统计
        stats = self._calculate_stats(test_results)

        # 记录原始数据
        self._log_raw_data(test_results, test_type)

        return StageResult(
            stage_name=self.stage_name,
            stage_number=self.stage_number,
            category=test_type,
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            duration_seconds=elapsed,
            test_results=test_results,
            passed_threshold=(passed / total >= self.threshold_percentage) if total > 0 else False,
            threshold_percentage=self.threshold_percentage,
            by_difficulty=stats["by_difficulty"],
            by_subcategory=stats["by_subcategory"]
        )

    def generate_report(self, result: StageResult, output_file: str = None):
        """生成 Markdown 报告"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"{result.category}_{timestamp}_report.md")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        report = f"""# Stage 4 {result.category} 测试报告

> **模型**: {self.model_name}
> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **后端**: {"Vulkan" if "8400" in self.model_url else "CUDA V100"}

---

## 📊 总体表现

| 指标 | 数值 |
|------|------|
| 总题数 | {result.total_tests} |
| 通过数 | {result.passed_tests} |
| 失败数 | {result.failed_tests} |
| 通过率 | **{result.pass_rate*100:.1f}%** |
| 耗时 | {result.duration_seconds/60:.1f} 分钟 |
| 阈值 | {result.threshold_percentage*100:.0f}% |

**评级**: {"✅ 优秀" if result.pass_rate >= 0.8 else "✅ 良好" if result.pass_rate >= 0.6 else "⚠️ 需改进"}

---

## 📈 按难度统计

| 难度 | 题数 | 通过 | 通过率 |
|------|------|------|--------|
"""

        for diff in ["简单", "中等", "困难"]:
            d = result.by_difficulty.get(diff, {})
            rate = d.get("rate", 0) * 100 if d else 0
            report += f"| {diff} | {d.get('total', 0)} | {d.get('passed', 0)} | {rate:.1f}% |\n"

        report += f"""
---

## 📋 按子类别统计

| 类别 | 题数 | 通过 | 通过率 |
|------|------|------|--------|
"""

        for cat, data in sorted(result.by_subcategory.items(), key=lambda x: x[1].get("rate", 0), reverse=True):
            rate = data.get("rate", 0) * 100 if data else 0
            report += f"| {cat} | {data.get('total', 0)} | {data.get('passed', 0)} | {rate:.1f}% |\n"

        report += f"""
---

## 📝 错误分析

"""

        # 列出失败的测试
        failed = [r for r in result.test_results if not r.passed]
        if failed:
            report += "### 失败题目 (前 20 个)\n\n"
            report += "| 题目 | 类别 | 难度 | 期望 | 实际 |\n"
            report += "|------|------|------|------|------|\n"

            for r in failed[:20]:
                expected = r.details.get("expected", "N/A") if r.details else "N/A"
                actual = r.details.get("actual", "N/A") if r.details else "N/A"
                report += f"| {r.name} | {r.category} | {r.difficulty} | {expected} | {actual} |\n"
        else:
            report += "所有题目均通过！\n"

        report += f"""
---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 报告已保存：{output_file}")
        return output_file
