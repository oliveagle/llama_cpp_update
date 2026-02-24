#!/usr/bin/env python3
"""
JoyAI-LLM-Flash 模型综合能力评估
针对京东 JoyAI 大语言模型的全面评测
"""

import argparse
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, List, Optional
import statistics

# 添加 eval 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from golden_benchmarks import get_golden_benchmark, compare_with_golden, print_comparison


# ========== 评估任务定义 ==========

# 数学推理测试题 (参考 GSM8K 风格)
MATH_TESTS = [
    {
        "name": "数学 - 基础应用题",
        "prompt": "一个水池有两个进水管，单独开甲管需要 6 小时注满，单独开乙管需要 4 小时注满。如果两管同时打开，需要多少小时注满？请给出详细的计算过程。",
        "expected_answer_type": "numerical",
        "expected_value": 2.4,
        "tolerance": 0.1,
    },
    {
        "name": "数学 - 百分比计算",
        "prompt": "某商品原价 200 元，先涨价 10%，再降价 10%，最终价格是多少元？",
        "expected_answer_type": "numerical",
        "expected_value": 198,
        "tolerance": 0.1,
    },
    {
        "name": "数学 - 比例问题",
        "prompt": "甲乙两人的年龄比是 3:4，5 年后年龄比是 4:5，请问甲现在多少岁？",
        "expected_answer_type": "numerical",
        "expected_value": 15,
        "tolerance": 0.1,
    },
    {
        "name": "数学 - 行程问题",
        "prompt": "A、B 两地相距 120 公里，甲从 A 地出发以 60 公里/小时的速度向 B 地行驶，同时乙从 B 地出发以 40 公里/小时的速度向 A 地行驶。问几小时后两人相遇？",
        "expected_answer_type": "numerical",
        "expected_value": 1.2,
        "tolerance": 0.1,
    },
    {
        "name": "数学 - 数列求和",
        "prompt": "计算 1+2+3+...+100 的和是多少？",
        "expected_answer_type": "numerical",
        "expected_value": 5050,
        "tolerance": 0.1,
    },
]

# 逻辑推理测试题
LOGIC_TESTS = [
    {
        "name": "逻辑 - 三段论",
        "prompt": "如果所有的猫都会爬树，小花是一只猫，那么小花会爬树吗？请解释你的推理过程。",
        "expected_answer_type": "boolean",
        "expected_value": True,
    },
    {
        "name": "逻辑 - 条件推理",
        "prompt": "如果今天下雨，我就不去公园。现在我没有去公园，那么今天一定下雨了吗？请解释。",
        "expected_answer_type": "reasoning",
        "keywords": ["不一定", "可能", "无法确定"],
    },
    {
        "name": "逻辑 - 真假判断",
        "prompt": "有三个盒子，一个只装苹果，一个只装橘子，一个既装苹果也装橘子。三个盒子的标签都贴错了。你只能从一个盒子里拿出一个水果来判断，应该从哪个盒子拿？",
        "expected_answer_type": "choice",
        "expected_value": "既装苹果也装橘子",
    },
]

# 代码能力测试题
CODE_TESTS = [
    {
        "name": "代码 - 斐波那契",
        "prompt": "请用 Python 写一个函数计算斐波那契数列的第 n 个数。",
        "expected_language": "python",
        "keywords": ["def", "fibonacci", "return"],
    },
    {
        "name": "代码 - 字符串处理",
        "prompt": "请用 Python 写一个函数，判断一个字符串是否是回文串。",
        "expected_language": "python",
        "keywords": ["def", "palindrome", "return", "=="],
    },
    {
        "name": "代码 - 排序算法",
        "prompt": "请用 Python 实现快速排序算法。",
        "expected_language": "python",
        "keywords": ["def", "quick", "sort", "partition"],
    },
]

# 中文理解测试题
CHINESE_TESTS = [
    {
        "name": "中文 - 成语解释",
        "prompt": "请解释'塞翁失马，焉知非福'这个成语的含义，并举一个生活中的例子。",
        "keywords": ["祸福", "转化", "好坏"],
    },
    {
        "name": "中文 - 诗词理解",
        "prompt": "请解释'床前明月光，疑是地上霜'这句诗表达了诗人怎样的情感？",
        "keywords": ["思乡", "思念", "孤独"],
    },
    {
        "name": "中文 - 语境理解",
        "prompt": "小明对小红说：'你真是个大天才！'根据语境，这句话可能是什么意思？",
        "keywords": ["讽刺", "夸奖", "反语"],
    },
]

# 知识问答测试题
KNOWLEDGE_TESTS = [
    {
        "name": "知识 - 科学",
        "prompt": "什么是量子纠缠？请用通俗易懂的语言解释。",
        "keywords": ["粒子", "关联", "状态"],
    },
    {
        "name": "知识 - 历史",
        "prompt": "请简述秦始皇统一六国的历史意义。",
        "keywords": ["统一", "中央集权", "制度"],
    },
    {
        "name": "知识 - 地理",
        "prompt": "为什么青藏高原的气温比同纬度地区低？",
        "keywords": ["海拔", "高原", "气温"],
    },
]

# 多轮对话测试
MULTI_TURN_TESTS = [
    {
        "name": "多轮对话 - 上下文记忆",
        "conversation": [
            {"role": "user", "content": "我最喜欢的颜色是蓝色，我喜欢大海。"},
            {"role": "user", "content": "你还记得我喜欢什么颜色吗？"},
        ],
        "expected_answer_keywords": ["蓝色", "大海"],
    },
    {
        "name": "多轮对话 - 指代消解",
        "conversation": [
            {"role": "user", "content": "小明有一只可爱的小狗，它每天都很快乐。"},
            {"role": "user", "content": "它为什么快乐？"},
        ],
        "expected_answer_keywords": ["小狗", "陪伴", "快乐"],
    },
]


def test_single_turn(model_url: str, model_name: str, prompt: str, max_tokens: int = 512) -> Dict:
    """测试单轮对话"""
    try:
        start_time = datetime.now()

        response = requests.post(
            f"{model_url}/v1/chat/completions",
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=120
        )
        response.raise_for_status()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = response.json()
        message = result.get("choices", [{}])[0].get("message", {})
        content = message.get("content", "")
        usage = result.get("usage", {})

        return {
            "success": True,
            "content": content,
            "duration_sec": duration,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "tokens_per_sec": usage.get("completion_tokens", 0) / duration if duration > 0 else 0,
        }

    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": str(e),
            "duration_sec": 0,
        }


def test_multi_turn(model_url: str, model_name: str, conversation: List[Dict]) -> Dict:
    """测试多轮对话"""
    try:
        start_time = datetime.now()

        # 构建完整的对话历史
        messages = []
        for turn in conversation:
            messages.append({"role": turn["role"], "content": turn["content"]})

        response = requests.post(
            f"{model_url}/v1/chat/completions",
            json={
                "model": model_name,
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.7,
            },
            timeout=120
        )
        response.raise_for_status()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = response.json()
        message = result.get("choices", [{}])[0].get("message", {})
        content = message.get("content", "")
        usage = result.get("usage", {})

        return {
            "success": True,
            "content": content,
            "duration_sec": duration,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        }

    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": str(e),
            "duration_sec": 0,
        }


def check_answer_quality(content: str, test: Dict) -> bool:
    """检查回答质量"""
    if not content:
        return False

    content_lower = content.lower()

    # 数值答案检查
    if test.get("expected_answer_type") == "numerical":
        try:
            # 尝试从回答中提取数值
            import re
            numbers = re.findall(r'\d+\.?\d*', content)
            if numbers:
                # 找最接近预期值的数字
                for num_str in numbers:
                    try:
                        num = float(num_str)
                        if abs(num - test["expected_value"]) <= test.get("tolerance", 0.1):
                            return True
                    except ValueError:
                        continue
        except Exception:
            pass
        return False

    # 布尔答案检查
    if test.get("expected_answer_type") == "boolean":
        if test["expected_value"]:
            return any(kw in content for kw in ["会", "是的", "正确", "true"])
        else:
            return any(kw in content for kw in ["不会", "错误", "false"])

    # 关键词检查
    if "keywords" in test:
        return any(kw.lower() in content_lower for kw in test["keywords"])

    return True


def run_evaluation(
    model_url: str,
    model_name: str,
    output_dir: str,
) -> Dict:
    """运行完整评估"""

    results = {
        "model_name": model_name,
        "model_url": model_url,
        "timestamp": datetime.now().isoformat(),
        "categories": {},
        "summary": {},
    }

    all_tests = []

    # ========== 1. 数学推理测试 ==========
    print("\n" + "=" * 60)
    print("1. 数学推理测试")
    print("=" * 60)

    math_results = []
    for test in MATH_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_single_turn(model_url, model_name, test["prompt"])
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        math_results.append(result)
        all_tests.append(result)

    math_accuracy = sum(1 for r in math_results if r["passed"]) / len(math_results) if math_results else 0
    results["categories"]["math"] = {
        "name": "数学推理",
        "total": len(math_results),
        "passed": sum(1 for r in math_results if r["passed"]),
        "accuracy": math_accuracy,
        "details": math_results,
    }
    print(f"\n数学推理准确率：{math_accuracy:.1%}")

    # ========== 2. 逻辑推理测试 ==========
    print("\n" + "=" * 60)
    print("2. 逻辑推理测试")
    print("=" * 60)

    logic_results = []
    for test in LOGIC_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_single_turn(model_url, model_name, test["prompt"])
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        logic_results.append(result)
        all_tests.append(result)

    logic_accuracy = sum(1 for r in logic_results if r["passed"]) / len(logic_results) if logic_results else 0
    results["categories"]["logic"] = {
        "name": "逻辑推理",
        "total": len(logic_results),
        "passed": sum(1 for r in logic_results if r["passed"]),
        "accuracy": logic_accuracy,
        "details": logic_results,
    }
    print(f"\n逻辑推理准确率：{logic_accuracy:.1%}")

    # ========== 3. 代码能力测试 ==========
    print("\n" + "=" * 60)
    print("3. 代码能力测试")
    print("=" * 60)

    code_results = []
    for test in CODE_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_single_turn(model_url, model_name, test["prompt"], max_tokens=1024)
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        code_results.append(result)
        all_tests.append(result)

    code_accuracy = sum(1 for r in code_results if r["passed"]) / len(code_results) if code_results else 0
    results["categories"]["code"] = {
        "name": "代码能力",
        "total": len(code_results),
        "passed": sum(1 for r in code_results if r["passed"]),
        "accuracy": code_accuracy,
        "details": code_results,
    }
    print(f"\n代码能力准确率：{code_accuracy:.1%}")

    # ========== 4. 中文理解测试 ==========
    print("\n" + "=" * 60)
    print("4. 中文理解测试")
    print("=" * 60)

    chinese_results = []
    for test in CHINESE_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_single_turn(model_url, model_name, test["prompt"])
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        chinese_results.append(result)
        all_tests.append(result)

    chinese_accuracy = sum(1 for r in chinese_results if r["passed"]) / len(chinese_results) if chinese_results else 0
    results["categories"]["chinese"] = {
        "name": "中文理解",
        "total": len(chinese_results),
        "passed": sum(1 for r in chinese_results if r["passed"]),
        "accuracy": chinese_accuracy,
        "details": chinese_results,
    }
    print(f"\n中文理解准确率：{chinese_accuracy:.1%}")

    # ========== 5. 知识问答测试 ==========
    print("\n" + "=" * 60)
    print("5. 知识问答测试")
    print("=" * 60)

    knowledge_results = []
    for test in KNOWLEDGE_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_single_turn(model_url, model_name, test["prompt"])
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        knowledge_results.append(result)
        all_tests.append(result)

    knowledge_accuracy = sum(1 for r in knowledge_results if r["passed"]) / len(knowledge_results) if knowledge_results else 0
    results["categories"]["knowledge"] = {
        "name": "知识问答",
        "total": len(knowledge_results),
        "passed": sum(1 for r in knowledge_results if r["passed"]),
        "accuracy": knowledge_accuracy,
        "details": knowledge_results,
    }
    print(f"\n知识问答准确率：{knowledge_accuracy:.1%}")

    # ========== 6. 多轮对话测试 ==========
    print("\n" + "=" * 60)
    print("6. 多轮对话测试")
    print("=" * 60)

    multi_turn_results = []
    for test in MULTI_TURN_TESTS:
        print(f"\n测试：{test['name']}")
        result = test_multi_turn(model_url, model_name, test["conversation"])
        result["test_name"] = test["name"]
        result["passed"] = check_answer_quality(result.get("content", ""), test)

        status = "✅" if result["passed"] else "❌"
        print(f"  状态：{status}")

        multi_turn_results.append(result)
        all_tests.append(result)

    multi_turn_accuracy = sum(1 for r in multi_turn_results if r["passed"]) / len(multi_turn_results) if multi_turn_results else 0
    results["categories"]["multi_turn"] = {
        "name": "多轮对话",
        "total": len(multi_turn_results),
        "passed": sum(1 for r in multi_turn_results if r["passed"]),
        "accuracy": multi_turn_accuracy,
        "details": multi_turn_results,
    }
    print(f"\n多轮对话准确率：{multi_turn_accuracy:.1%}")

    # ========== 计算总体统计 ==========
    total_tests = len(all_tests)
    total_passed = sum(1 for r in all_tests if r.get("passed", False))
    overall_accuracy = total_passed / total_tests if total_tests > 0 else 0

    # 性能统计
    durations = [r["duration_sec"] for r in all_tests if r.get("duration_sec", 0) > 0]
    avg_duration = statistics.mean(durations) if durations else 0

    completion_tokens = [r.get("completion_tokens", 0) for r in all_tests]
    total_tokens = sum(completion_tokens)
    avg_tokens_per_sec = total_tokens / sum(durations) if durations else 0

    results["summary"] = {
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "overall_accuracy": overall_accuracy,
        "avg_response_time_sec": avg_duration,
        "avg_tokens_per_sec": avg_tokens_per_sec,
        "category_accuracies": {
            "math": math_accuracy,
            "logic": logic_accuracy,
            "code": code_accuracy,
            "chinese": chinese_accuracy,
            "knowledge": knowledge_accuracy,
            "multi_turn": multi_turn_accuracy,
        }
    }

    return results


def generate_report(results: Dict, output_dir: str) -> str:
    """生成 Markdown 报告"""

    report = f"""# JoyAI-LLM-Flash 模型综合能力评估报告

> **评测时间**: {results["timestamp"]}
> **模型名称**: {results["model_name"]}
> **评测服务**: {results["model_url"]}

---

## 📊 总体表现

| 指标 | 数值 |
|------|------|
| 总测试数 | {results["summary"]["total_tests"]} |
| 通过数 | {results["summary"]["passed"]} |
| 失败数 | {results["summary"]["failed"]} |
| 总体准确率 | {results["summary"]["overall_accuracy"]:.1%} |
| 平均响应时间 | {results["summary"]["avg_response_time_sec"]:.2f} 秒 |
| 生成速度 | {results["summary"]["avg_tokens_per_sec"]:.1f} tokens/秒 |

---

## 📈 分项能力

| 能力维度 | 测试数 | 通过数 | 准确率 |
|----------|--------|--------|--------|
"""

    for cat_key, cat_data in results["categories"].items():
        report += f"| {cat_data['name']} | {cat_data['total']} | {cat_data['passed']} | {cat_data['accuracy']:.1%} |\n"

    report += f"""
---

## 📋 详细测试结果

### 数学推理 (GSM8K 风格)

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["math"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    report += f"""
### 逻辑推理

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["logic"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    report += f"""
### 代码能力

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["code"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    report += f"""
### 中文理解

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["chinese"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    report += f"""
### 知识问答

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["knowledge"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    report += f"""
### 多轮对话

| 测试项 | 状态 | 响应时间 |
|--------|------|----------|
"""

    for r in results["categories"]["multi_turn"]["details"]:
        status = "✅" if r["passed"] else "❌"
        duration = f"{r.get('duration_sec', 0):.1f}s"
        report += f"| {r['test_name']} | {status} | {duration} |\n"

    # 添加能力雷达图数据
    report += f"""
---

## 🎯 能力雷达图数据

```json
{{
  "数学推理": {results["categories"]["math"]["accuracy"]:.2f},
  "逻辑推理": {results["categories"]["logic"]["accuracy"]:.2f},
  "代码能力": {results["categories"]["code"]["accuracy"]:.2f},
  "中文理解": {results["categories"]["chinese"]["accuracy"]:.2f},
  "知识问答": {results["categories"]["knowledge"]["accuracy"]:.2f},
  "多轮对话": {results["categories"]["multi_turn"]["accuracy"]:.2f}
}}
```

---

## 📝 示例回答

"""

    # 添加一些示例回答
    for cat_key, cat_data in list(results["categories"].items())[:3]:
        report += f"### {cat_data['name']} 示例\n\n"
        for i, r in enumerate(cat_data["details"][:1]):
            report += f"**测试**: {r['test_name']}\n\n"
            report += f"> {r.get('content', 'N/A')[:500]}...\n\n"

    report += f"""
---

## 🔍 评估说明

- 本评估基于项目自研测试框架，涵盖 6 大能力维度
- 每个测试项均采用关键词匹配或数值匹配进行自动评分
- 评测结果仅供参考，实际表现可能因使用场景而异

---

*本报告由 llama.cpp 评估框架自动生成*
"""

    return report


def main():
    parser = argparse.ArgumentParser(description="JoyAI-LLM-Flash 模型综合能力评估")
    parser.add_argument(
        "--model-url",
        type=str,
        default="http://localhost:8400",
        help="模型 API 地址",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="JoyAI-LLM-Flash-Q4_K_M",
        help="模型名称",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results/joyai_flash",
        help="输出目录",
    )

    args = parser.parse_args()

    print("=" * 60)
    print(f"JoyAI-LLM-Flash 模型综合能力评估")
    print("=" * 60)
    print(f"模型名称：{args.model_name}")
    print(f"模型地址：{args.model_url}")
    print(f"输出目录：{args.output_dir}")

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    # 运行评估
    results = run_evaluation(args.model_url, args.model_name, args.output_dir)

    # 生成报告
    report = generate_report(results, args.output_dir)

    # 保存报告
    report_file = os.path.join(args.output_dir, f"{args.model_name}_eval_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n报告已保存：{report_file}")

    # 保存 JSON 原始数据
    json_file = os.path.join(args.output_dir, f"{args.model_name}_eval_raw.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"原始数据已保存：{json_file}")

    # 打印摘要
    print("\n" + "=" * 60)
    print("评估摘要")
    print("=" * 60)
    summary = results["summary"]
    print(f"总测试数：{summary['total_tests']}")
    print(f"通过：{summary['passed']}")
    print(f"失败：{summary['failed']}")
    print(f"总体准确率：{summary['overall_accuracy']:.1%}")
    print(f"平均响应时间：{summary['avg_response_time_sec']:.2f}秒")
    print(f"生成速度：{summary['avg_tokens_per_sec']:.1f} tokens/秒")

    print("\n分项能力:")
    for cat, acc in summary["category_accuracies"].items():
        print(f"  - {cat}: {acc:.1%}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
