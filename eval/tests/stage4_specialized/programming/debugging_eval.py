#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - 代码调试 (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

# 代码调试题目模板
DEBUGGING_TEMPLATES = {
    "Python 常见错误": [
        {"q": "for i in range(10): print(i) 缺少什么？", "opts": ["冒号", "分号", "括号", "逗号"], "a": "A"},
        {"q": "if x = 5: 的错误是？", "opts": ["应该用 ==", "应该用 ====", "缺少冒号", "缺少括号"], "a": "A"},
        {"q": "NameError: name 'x' is not defined 表示？", "opts": ["变量未定义", "类型错误", "索引越界", "语法错误"], "a": "A"},
        {"q": "IndexError: list index out of range 表示？", "opts": ["索引越界", "类型错误", "未定义", "语法错误"], "a": "A"},
        {"q": "TypeError: unsupported operand type(s) 表示？", "opts": ["类型不匹配", "语法错误", "未定义", "越界"], "a": "A"},
        {"q": "AttributeError: 'str' object has no attribute 'append' 表示？", "opts": ["方法不存在", "类型错误", "未定义", "越界"], "a": "A"},
        {"q": "KeyError: 'key' 通常发生在？", "opts": ["字典访问不存在的键", "列表访问不存在的索引", "字符串访问不存在的字符", "文件未找到"], "a": "A"},
        {"q": "ZeroDivisionError 表示？", "opts": ["除零错误", "类型错误", "未定义", "越界"], "a": "A"},
        {"q": "IndentationError 表示？", "opts": ["缩进错误", "语法错误", "类型错误", "未定义"], "a": "A"},
        {"q": "SyntaxError: invalid syntax 表示？", "opts": ["语法错误", "类型错误", "缩进错误", "越界"], "a": "A"},
        {"q": "list.append(x) 而不是 x = list.append(x) 因为 append 返回？", "opts": ["None", "列表", "x", "True"], "a": "A"},
        {"q": "可变对象作为默认参数的问题是？", "opts": ["只初始化一次", "不能修改", "会报错", "内存泄漏"], "a": "A"},
        {"q": "for i in list: if ...: list.remove(i) 的问题是？", "opts": ["遍历同时修改列表", "语法错误", "性能问题", "内存泄漏"], "a": "A"},
        {"q": "is 和 == 的区别是？", "opts": ["is 比较身份，== 比较值", "is 比较值，== 比较身份", "没有区别", "is 更快"], "a": "A"},
        {"q": "globals() 和 locals() 的返回值是？", "opts": ["字典", "列表", "元组", "集合"], "a": "A"},
    ],
    "逻辑错误": [
        {"q": "循环条件永远为 True 会导致？", "opts": ["无限循环", "语法错误", "类型错误", "越界"], "a": "A"},
        {"q": "return 语句位置错误可能导致？", "opts": ["提前返回", "语法错误", "类型错误", "越界"], "a": "A"},
        {"q": "变量作用域问题常见于？", "opts": ["全局变量和局部变量同名", "变量未定义", "类型错误", "语法错误"], "a": "A"},
        {"q": "浮点数比较用 == 有问题因为？", "opts": ["精度问题", "语法错误", "类型错误", "速度慢"], "a": "A"},
        {"q": "可变对象赋值 a = b 后修改 a，b 也变了因为？", "opts": ["引用同一对象", "语法错误", "类型错误", "bug"], "a": "A"},
    ],
    "性能问题": [
        {"q": "列表中间插入元素用什么数据结构更好？", "opts": ["deque", "list", "tuple", "set"], "a": "A"},
        {"q": "频繁成员测试用什么数据结构？", "opts": ["set", "list", "tuple", "dict"], "a": "A"},
        {"q": "字符串拼接用什么更高效？", "opts": ["join", "+", "format", "f-string"], "a": "A"},
        {"q": "循环中反复调用 len(list) 会？", "opts": ["没问题，len 是 O(1)", "很慢，O(n)", "会报错", "内存泄漏"], "a": "A"},
    ],
}


def generate_debugging_questions(target_count=150):
    """生成代码调试题目"""
    questions = []
    qid = 1

    easy_count = int(target_count * 0.4)
    medium_count = int(target_count * 0.4)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["Python 常见错误"]
    medium_cats = ["Python 常见错误", "逻辑错误"]
    hard_cats = ["逻辑错误", "性能问题"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in DEBUGGING_TEMPLATES and DEBUGGING_TEMPLATES[cat]:
            template = random.choice(DEBUGGING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"调试-{cat}-{qid}",
                "category": cat,
                "difficulty": "简单",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["debugging"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in DEBUGGING_TEMPLATES and DEBUGGING_TEMPLATES[cat]:
            template = random.choice(DEBUGGING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"调试-{cat}-{qid}",
                "category": cat,
                "difficulty": "中等",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["debugging"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in DEBUGGING_TEMPLATES and DEBUGGING_TEMPLATES[cat]:
            template = random.choice(DEBUGGING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"调试-{cat}-{qid}",
                "category": cat,
                "difficulty": "困难",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["debugging"]
            })
            qid += 1

    return questions


class DebuggingEvaluator:
    """代码调试评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_debugging_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "debugging")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_debugging_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = DebuggingEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 代码调试测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_debugging_questions(150)
        print(f"生成了 {len(questions)} 道调试题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "debugging_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_debugging_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
