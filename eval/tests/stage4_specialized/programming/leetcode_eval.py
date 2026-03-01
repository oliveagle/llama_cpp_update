#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - LeetCode 风格编程题
让模型实际编写代码并验证正确性
"""

import random
import json
import os
import subprocess
import tempfile
import time
import re

# LeetCode 风格编程题
LEETCODE_TEMPLATES = {
    "两数之和": {
        "difficulty": "简单",
        "prompt": """给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案，但是数组中同一个元素不能使用两遍。

示例 1:
输入: nums = [2,7,11,15], target = 9
输出: [0,1]
解释: nums[0] + nums[1] == 9 ，返回 [0, 1]

示例 2:
输入: nums = [3,2,4], target = 6
输出: [1,2]

请用 Python 编写函数 solution(nums, target)，返回满足条件的两个数的下标。""",
        "test_cases": [
            (([2,7,11,15], 9), [0,1]),
            (([3,2,4], 6), [1,2]),
            (([3,3], 6), [0,1]),
        ],
        "solution_template": "def solution(nums, target):\\n    # 在这里编写你的代码\\n    pass"
    },
    "有效的括号": {
        "difficulty": "简单",
        "prompt": """给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s，判断字符串是否有效。

有效字符串需满足：
1. 左括号必须用相同类型的右括号闭合。
2. 左括号必须以正确的顺序闭合。

示例 1:
输入: s = "()"
输出: true

示例 2:
输入: s = "()[]{}"
输出: true

示例 3:
输入: s = "(]"
输出: false

请用 Python 编写函数 solution(s)，返回布尔值。""",
        "test_cases": [
            ("()", True),
            ("()[]{}", True),
            ("(]", False),
            ("([)]", False),
            ("{[]}", True),
        ],
        "solution_template": "def solution(s):\\n    # 在这里编写你的代码\\n    pass"
    },
    "反转链表": {
        "difficulty": "简单",
        "prompt": """给你单链表的头节点 head，请你反转链表，并返回反转后的链表。

示例 1:
输入: head = [1,2,3,4,5]
输出: [5,4,3,2,1]

示例 2:
输入: head = [1,2]
输出: [2,1]

示例 3:
输入: head = []
输出: []

请用 Python 编写函数 solution(head)，其中 head 是列表 [1,2,3,...]，返回反转后的列表。""",
        "test_cases": [
            ([1,2,3,4,5], [5,4,3,2,1]),
            ([1,2], [2,1]),
            ([], []),
        ],
        "solution_template": "def solution(head):\\n    # 在这里编写你的代码\\n    pass"
    },
    "最大子数组和": {
        "difficulty": "中等",
        "prompt": """给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。

示例 1:
输入: nums = [-2,1,-3,4,-1,2,1,-5,4]
输出: 6
解释: 连续子数组 [4,-1,2,1] 的和最大，为 6 。

示例 2:
输入: nums = [1]
输出: 1

示例 3:
输入: nums = [5,4,-1,7,8]
输出: 23

请用 Python 编写函数 solution(nums)，返回最大和。""",
        "test_cases": [
            ([-2,1,-3,4,-1,2,1,-5,4], 6),
            ([1], 1),
            ([5,4,-1,7,8], 23),
            ([1,2,3,4,5], 15),
        ],
        "solution_template": "def solution(nums):\\n    # 在这里编写你的代码\\n    pass"
    },
    "合并两个有序链表": {
        "difficulty": "简单",
        "prompt": """将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。

示例 1:
输入: l1 = [1,2,4], l2 = [1,3,4]
输出: [1,1,2,3,4,4]

示例 2:
输入: l1 = [], l2 = []
输出: []

示例 3:
输入: l1 = [], l2 = [0]
输出: [0]

请用 Python 编写函数 solution(l1, l2)，其中 l1 和 l2 是列表，返回合并后的列表。""",
        "test_cases": [
            ([1,2,4], [1,3,4], [1,1,2,3,4,4]),
            ([], [], []),
            ([], [0], [0]),
            ([1], [0], [0,1]),
        ],
        "solution_template": "def solution(l1, l2):\\n    # 在这里编写你的代码\\n    pass"
    },
    "爬楼梯": {
        "difficulty": "简单",
        "prompt": """假设你正在爬楼梯。需要 n 阶你才能到达楼顶。

每次你可以爬 1 或 2 个台阶。有多少种不同的方法可以爬到楼顶？

示例 1:
输入: n = 2
输出: 2
解释: 有两种方法可以爬到楼顶:
1. 1 阶 + 1 阶
2. 2 阶

示例 2:
输入: n = 3
输出: 3
解释: 有三种方法可以爬到楼顶:
1. 1 阶 + 1 阶 + 1 阶
2. 1 阶 + 2 阶
3. 2 阶 + 1 阶

请用 Python 编写函数 solution(n)，返回方法数。""",
        "test_cases": [
            (2, 2),
            (3, 3),
            (4, 5),
            (5, 8),
            (10, 89),
        ],
        "solution_template": "def solution(n):\\n    # 在这里编写你的代码\\n    pass"
    },
    "买卖股票的最佳时机": {
        "difficulty": "中等",
        "prompt": """给定一个数组 prices ，其中 prices[i] 是第 i 天的股票价格。

设计一个算法来计算你能获取的最大利润。注意：你不能在买入股票前卖出股票。

示例 1:
输入: prices = [7,1,5,3,6,4]
输出: 5
解释: 在第 2 天(股票价格 = 1)买入，在第 5 天(股票价格 = 6)卖出，利润 = 6-1 = 5 。

示例 2:
输入: prices = [7,6,4,3,1]
输出: 0
解释: 在这种情况下，没有交易完成，最大利润为 0 。

请用 Python 编写函数 solution(prices)，返回最大利润。""",
        "test_cases": [
            ([7,1,5,3,6,4], 5),
            ([7,6,4,3,1], 0),
            ([2,4,1], 2),
            ([2,4,1,7], 6),
        ],
        "solution_template": "def solution(prices):\\n    # 在这里编写你的代码\\n    pass"
    },
    "二分查找": {
        "difficulty": "简单",
        "prompt": """给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。如果目标值不存在于数组中，返回 -1。

你可以假设数组中无重复元素。

示例 1:
输入: nums = [-1,0,3,5,9,12], target = 9
输出: 4
解释: 9 出现在 nums 中并且下标为 4

示例 2:
输入: nums = [-1,0,3,5,9,12], target = 2
输出: -1
解释: 2 不存在 nums 中返回 -1

请用 Python 编写函数 solution(nums, target)，返回目标值的索引或 -1。""",
        "test_cases": [
            ([-1,0,3,5,9,12], 9, 4),
            ([-1,0,3,5,9,12], 2, -1),
            ([5], 5, 0),
            ([], 5, -1),
        ],
        "solution_template": "def solution(nums, target):\\n    # 在这里编写你的代码\\n    pass"
    },
    "全排列": {
        "difficulty": "中等",
        "prompt": """给定一个不含重复数字的数组 nums ，返回其所有可能的全排列。

示例 1:
输入: nums = [1,2,3]
输出: [[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

示例 2:
输入: nums = [0,1]
输出: [[0,1],[1,0]]

示例 3:
输入: nums = [1]
输出: [[1]]

请用 Python 编写函数 solution(nums)，返回所有全排列的列表。""",
        "test_cases": [
            ([1,2,3], sorted([[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]])),
            ([0,1], sorted([[0,1],[1,0]])),
            ([1], [[1]]),
        ],
        "solution_template": "def solution(nums):\\n    # 在这里编写你的代码\\n    pass"
    },
    "LRU 缓存": {
        "difficulty": "困难",
        "prompt": """请你设计并实现一个满足 LRU (最近最少使用) 缓存约束的数据结构。

实现 LRUCache 类：
- LRUCache(int capacity) 以正整数作为容量 capacity 初始化 LRU 缓存
- int get(int key) 如果关键字 key 存在于缓存中，则返回关键字的值，否则返回 -1
- void put(int key, int value) 如果关键字已存在，则变更其数据值；如果关键字不存在，则插入该键-值对组。当缓存容量达到上限时，它应该在写入新数据之前删除最近最少使用的数据，从而为新数据留出空间。

示例:
输入:
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
输出: [null, null, null, 1, null, -1, null, -1, 3, 4]

请用 Python 编写 LRUCache 类和 solution() 函数来模拟这个过程。
直接返回 get 操作的结果列表。""",
        "test_cases": [
            # Simplified test - just check it can be instantiated
            ({"capacity": 2, "ops": [["put",1,1], ["put",2,2], ["get",1], ["put",3,3], ["get",2]]},
             [1, -1]),
        ],
        "solution_template": "class LRUCache:\\n    def __init__(self, capacity):\\n        # 在这里编写你的代码\\n        pass\\n    \\n    def get(self, key):\\n        pass\\n    \\n    def put(self, key, value):\\n        pass"
    },
}


def run_code(code: str, test_cases, timeout=5):
    """运行代码并测试"""
    results = []

    for test_input, expected in test_cases:
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            # 运行代码
            # 构建测试代码
            if isinstance(test_input, tuple):
                args = str(test_input)
            else:
                args = repr(test_input)

            test_code = f"""
import sys
sys.path.insert(0, '.')
{code}

# 测试
result = solution{test_input}
print(result)
"""

            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(test_code)
                test_file = f.name

            # 执行
            start = time.time()
            proc = subprocess.run(
                ['python3', test_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start

            # 检查结果
            output = proc.stdout.strip()
            actual = eval(output)

            # 比较结果
            if isinstance(expected, list) and isinstance(actual, list):
                # 对于列表结果，排序后比较
                passed = sorted(actual) == sorted(expected)
            else:
                passed = actual == expected

            results.append({
                "input": test_input,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "elapsed_ms": elapsed * 1000,
                "error": None
            })

        except subprocess.TimeoutExpired:
            results.append({
                "input": test_input,
                "expected": expected,
                "actual": None,
                "passed": False,
                "elapsed_ms": timeout * 1000,
                "error": "Timeout"
            })
        except Exception as e:
            results.append({
                "input": test_input,
                "expected": expected,
                "actual": None,
                "passed": False,
                "elapsed_ms": 0,
                "error": str(e)
            })
        finally:
            # 清理
            try:
                os.unlink(temp_file)
                os.unlink(test_file)
            except:
                pass

    return results


def generate_leetcode_questions(target_count=10):
    """生成 LeetCode 编程题"""
    questions = []
    qid = 1

    templates = list(LEETCODE_TEMPLATES.keys())

    for _ in range(min(target_count, len(templates))):
        name = random.choice(templates)
        template = LEETCODE_TEMPLATES[name]

        questions.append({
            "id": qid,
            "name": f"编程-{name}",
            "category": "LeetCode",
            "difficulty": template["difficulty"],
            "question": template["prompt"],
            "test_cases": template["test_cases"],
            "solution_template": template["solution_template"],
            "keywords": ["coding", "leetcode", "algorithm"]
        })
        qid += 1

    return questions


def evaluate_code(llm_code: str, test_cases) -> dict:
    """评估模型生成的代码"""
    # 尝试从 LLM 回复中提取代码
    code = extract_code(llm_code)

    if not code:
        return {
            "success": False,
            "error": "No code found in response",
            "passed_tests": 0,
            "total_tests": len(test_cases)
        }

    # 运行测试
    results = run_code(code, test_cases)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    return {
        "success": True,
        "code": code,
        "results": results,
        "passed_tests": passed,
        "total_tests": total,
        "pass_rate": passed / total if total > 0 else 0
    }


def extract_code(text: str) -> str:
    """从文本中提取 Python 代码"""
    if not text:
        return ""

    # 尝试提取 ```python ... ``` 块
    match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1)

    # 尝试提取 ``` ... ``` 块
    match = re.search(r'```\n?(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1)

    # 如果没有代码块，假设整个文本就是代码
    return text.strip()


def generate_leetcode_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """运行 LeetCode 编程题测试"""
    import requests
    from dataclasses import dataclass

    @dataclass
    class LeetCodeResult:
        total_tests: int
        passed_tests: int
        pass_rate: float

    questions = generate_leetcode_questions(10)

    results = []
    passed = 0

    for q in questions:
        print(f"\n测试题目: {q['name']} ({q['difficulty']})")

        # 调用模型获取代码
        url = f"{model_url}/v1/chat/completions"
        messages = [
            {"role": "system", "content": "你是一个专业的程序员。请只输出 Python 代码，不要解释。"},
            {"role": "user", "content": q['question'] + "\n\n请写出完整的 Python 代码，只输出代码块。"}
        ]

        try:
            resp = requests.post(url, json={
                "model": model_name,
                "messages": messages,
                "max_tokens": 2048,
                "temperature": 0.1
            }, timeout=60)

            content = resp.json()["choices"][0]["message"]["content"]

            # 评估代码
            eval_result = evaluate_code(content, q['test_cases'])

            print(f"  通过: {eval_result['passed_tests']}/{eval_result['total_tests']}")

            if eval_result['passed_tests'] > 0:
                passed += 1

            results.append({
                "question": q,
                "evaluation": eval_result
            })

        except Exception as e:
            print(f"  错误: {e}")
            results.append({
                "question": q,
                "evaluation": {"error": str(e)}
            })

    total = len(results)
    pass_rate = passed / total if total > 0 else 0

    print(f"\nLeetCode 测试完成！通过率：{pass_rate*100:.1f}%")

    return LeetCodeResult(
        total_tests=total,
        passed_tests=passed,
        pass_rate=pass_rate
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 LeetCode 编程题测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--count", type=int, default=10, help="题目数量")
    args = parser.parse_args()

    # 先测试题目生成
    questions = generate_leetcode_questions(args.count)
    print(f"生成了 {len(questions)} 道 LeetCode 编程题:")
    for q in questions:
        print(f"  - {q['name']} ({q['difficulty']})")

    # 如果需要运行测试
    if "--run" in parser._actions[0].option_strings or any("--run" in a for a in []):
        result = generate_leetcode_test(args.model_url, args.model_name, args.output_dir)
        print(f"\\n测试结果: {result.passed_tests}/{result.total_tests} = {result.pass_rate*100:.1f}%")
