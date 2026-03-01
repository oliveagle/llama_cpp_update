#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - Python 基础语法 (150 题生成器)
自动生成 Python 基础语法题目，包含选择题和代码生成题
"""

import random
import json
import os
import sys

# 导入通用工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

# Python 基础语法题目模板
BASE_SYNTAX_TEMPLATES = {
    "函数": [
        {"q": "Python 中定义函数的关键字是？", "opts": ["def", "function", "func", "define"], "a": "A"},
        {"q": "函数返回多个值时实际返回的是？", "opts": ["元组", "列表", "字典", "集合"], "a": "A"},
        {"q": "*args 用于？", "opts": ["接收可变位置参数", "接收可变关键字参数", "类型提示", "文档字符串"], "a": "A"},
        {"q": "**kwargs 用于？", "opts": ["接收可变关键字参数", "接收可变位置参数", "类型提示", "文档字符串"], "a": "A"},
        {"q": "lambda 函数的限制是？", "opts": ["只能有一个表达式", "可以有多个语句", "必须有名字", "不能返回值"], "a": "A"},
        {"q": "装饰器的作用是？", "opts": ["在不修改原函数的情况下增强功能", "删除函数", "重命名函数", "加速函数执行"], "a": "A"},
        {"q": "Python 函数默认参数求值时机是？", "opts": ["函数定义时", "函数调用时", "随时", "从不"], "a": "A"},
        {"q": "闭包中访问外部变量的关键字是？", "opts": ["global", "nonlocal", "self", "this"], "a": "B"},
        {"q": "yield 关键字的作用是？", "opts": ["生成器", "返回值", "抛出异常", "导入模块"], "a": "A"},
        {"q": "生成器和普通函数的区别是？", "opts": ["使用 yield 返回值", "使用 return 返回值", "必须接受参数", "不能有参数"], "a": "A"},
    ],
    "类和对象": [
        {"q": "Python 中类的定义关键字是？", "opts": ["class", "def", "struct", "object"], "a": "A"},
        {"q": "__init__ 方法是？", "opts": ["构造方法", "析构方法", "普通方法", "静态方法"], "a": "A"},
        {"q": "self 参数代表？", "opts": ["当前实例", "类本身", "父类", "模块"], "a": "A"},
        {"q": "类的私有属性使用什么前缀？", "opts": ["__", "_", "private", "protected"], "a": "A"},
        {"q": "继承时调用父类方法用？", "opts": ["super()", "parent()", "this()", "base()"], "a": "A"},
        {"q": "多态的含义是？", "opts": ["同一种行为不同实现", "多种形式", "一个类多个方法", "继承所有方法"], "a": "A"},
        {"q": "@property 装饰器用于？", "opts": ["定义属性", "定义静态方法", "定义类方法", "定义私有方法"], "a": "A"},
        {"q": "类方法第一个参数是？", "opts": ["cls", "self", "this", "class"], "a": "A"},
        {"q": "静态方法不需要哪个参数？", "opts": ["self", "cls", "args", "kwargs"], "a": "A"},
        {"q": "__str__ 方法用于？", "opts": ["字符串表示", "调试信息", "哈希值", "比较"], "a": "A"},
        {"q": "抽象基类使用哪个模块？", "opts": ["abc", "abstract", "base", "proto"], "a": "A"},
        {"q": "Mix-in 类的特点是？", "opts": ["多重继承", "单继承", "不能实例化", "必须有抽象方法"], "a": "A"},
    ],
    "装饰器": [
        {"q": "@staticmethod 装饰器用于？", "opts": ["定义静态方法", "定义类方法", "定义属性", "定义抽象方法"], "a": "A"},
        {"q": "@classmethod 装饰器用于？", "opts": ["定义类方法", "定义静态方法", "定义属性", "定义实例方法"], "a": "A"},
        {"q": "装饰器本质上是一个？", "opts": ["函数", "类", "模块", "方法"], "a": "A"},
        {"q": "多个装饰器的执行顺序是？", "opts": ["从下到上", "从上到下", "随机", "并行"], "a": "B"},
        {"q": "@functools.wraps 的作用是？", "opts": ["保留原函数元数据", "加速执行", "添加日志", "错误处理"], "a": "A"},
    ],
    "模块和包": [
        {"q": "__init__.py 文件的作用是？", "opts": ["使目录成为包", "定义初始化函数", "导入模块", "导出接口"], "a": "A"},
        {"q": "from...import * 会导入什么？", "opts": ["所有公共成员", "私有成员", "只导入函数", "只导入类"], "a": "A"},
        {"q": "__name__ == '__main__' 的用途是？", "opts": ["判断是否为主程序", "模块测试", "导入控制", "版本判断"], "a": "A"},
        {"q": "相对导入使用什么符号？", "opts": [".", "..", "/", "@"], "a": "A"},
        {"q": "sys.path 用于？", "opts": ["模块搜索路径", "系统路径", "用户路径", "临时路径"], "a": "A"},
    ],
    "异常处理": [
        {"q": "try-except-else 中 else 何时执行？", "opts": ["没有异常时", "有异常时", "总是执行", "从不执行"], "a": "A"},
        {"q": "finally 块何时执行？", "opts": ["总是执行", "有异常时执行", "没有异常时执行", "从不执行"], "a": "A"},
        {"q": "raise 关键字用于？", "opts": ["抛出异常", "捕获异常", "处理异常", "定义异常"], "a": "A"},
        {"q": "Exception 是？", "opts": ["所有内置异常的基类", "运行时异常", "系统异常", "自定义异常"], "a": "A"},
        {"q": "except Exception as e 中 e 是？", "opts": ["异常对象", "异常类", "异常消息", "异常栈"], "a": "A"},
    ],
    "数据类型": [
        {"q": "列表推导式 [x for x in range(5)] 的结果是？", "opts": ["[0,1,2,3,4]", "[1,2,3,4,5]", "[0,1,2,3]", "[1,2,3,4]"], "a": "A"},
        {"q": "字典的 get 方法默认值是？", "opts": ["None", "空字符串", "0", "False"], "a": "A"},
        {"q": "集合 set() 的特点是？", "opts": ["无序不重复", "有序可重复", "有序不重复", "无序可重复"], "a": "A"},
        {"q": "元组和列表的主要区别是？", "opts": ["元组不可变", "列表不可变", "元组有序", "列表无序"], "a": "A"},
        {"q": "f-string 中 {x!r} 的作用是？", "opts": ["使用 repr()", "使用 str()", "格式化日期", "格式化数字"], "a": "A"},
    ],
    "类型注解": [
        {"q": "int 类型注解的正确写法是？", "opts": ["x: int", "x = int", "int x", "x -> int"], "a": "A"},
        {"q": "List[int] 需要从哪个模块导入？", "opts": ["typing", "types", "collections", "list"], "a": "A"},
        {"q": "Dict[str, int] 表示？", "opts": ["键为字符串值为整数的字典", "字符串到整数的映射", "两者都对", "两者都不对"], "a": "C"},
        {"q": "Optional[int] 等价于？", "opts": ["int | None", "int or None", "int 和 None", "int + None"], "a": "A"},
        {"q": "Union[int, str] 表示？", "opts": ["int 或 str", "int 和 str", "int 转 str", "str 转 int"], "a": "A"},
    ],
    "上下文管理器": [
        {"q": "with 语句用于？", "opts": ["资源管理", "循环", "条件判断", "异常处理"], "a": "A"},
        {"q": "实现上下文管理器需要实现？", "opts": ["__enter__ 和 __exit__", "__init__ 和 __del__", "__str__ 和 __repr__", "__eq__ 和 __hash__"], "a": "A"},
        {"q": "@contextmanager 装饰器用于？", "opts": ["简化上下文管理器", "创建装饰器", "创建生成器", "创建迭代器"], "a": "A"},
    ],
    "迭代器和生成器": [
        {"q": "iter() 函数返回？", "opts": ["迭代器", "可迭代对象", "生成器", "列表"], "a": "A"},
        {"q": "next() 函数用于？", "opts": ["获取下一个元素", "重置迭代器", "检查元素", "删除元素"], "a": "A"},
        {"q": "StopIteration 异常在？", "opts": ["迭代结束时抛出", "开始时抛出", "永不抛出", "随时抛出"], "a": "A"},
        {"q": "enumerate() 的返回值是？", "opts": ["元组 (索引, 值)", "字典", "列表", "集合"], "a": "A"},
    ],
    "推导式": [
        {"q": "[x**2 for x in range(3)] 的结果是？", "opts": ["[0,1,4]", "[1,4,9]", "[0,1,2]", "[1,2,3]"], "a": "A"},
        {"q": "{x: x**2 for x in range(3)} 的结果是？", "opts": ["{0:0,1:1,2:4}", "[0,1,4]", "{0,1,4}", "0,1,4"], "a": "A"},
        {"q": "生成器表达式使用什么括号？", "opts": ["圆括号", "方括号", "花括号", "尖括号"], "a": "A"},
    ],
}


def generate_base_syntax_questions(target_count=150):
    """生成基础语法题目"""
    questions = []
    qid = 1

    # 难度分布：简单 40%, 中等 45%, 困难 15%
    easy_count = int(target_count * 0.4)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["函数", "数据类型", "迭代器和生成器", "推导式"]
    medium_cats = ["类和对象", "装饰器", "模块和包", "异常处理", "类型注解"]
    hard_cats = ["类和对象", "装饰器", "上下文管理器", "类型注解"]

    # 生成简单题
    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in BASE_SYNTAX_TEMPLATES and BASE_SYNTAX_TEMPLATES[cat]:
            template = random.choice(BASE_SYNTAX_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"基础语法-{cat}-{qid}",
                "category": cat,
                "difficulty": "简单",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["python", "syntax"]
            })
            qid += 1

    # 生成中等题
    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in BASE_SYNTAX_TEMPLATES and BASE_SYNTAX_TEMPLATES[cat]:
            template = random.choice(BASE_SYNTAX_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"基础语法-{cat}-{qid}",
                "category": cat,
                "difficulty": "中等",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["python", "syntax"]
            })
            qid += 1

    # 生成困难题
    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in BASE_SYNTAX_TEMPLATES and BASE_SYNTAX_TEMPLATES[cat]:
            template = random.choice(BASE_SYNTAX_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"基础语法-{cat}-{qid}",
                "category": cat,
                "difficulty": "困难",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["python", "syntax"]
            })
            qid += 1

    return questions


class BaseSyntaxEvaluator:
    """基础语法评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_base_syntax_questions(150)

    def run_tests(self):
        """运行基础语法测试"""
        return self.base_eval.run_tests(self.test_cases, "base_syntax")

    def generate_report(self, result):
        """生成报告"""
        return self.base_eval.generate_report(result)


def run_base_syntax_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """便捷函数运行基础语法测试"""
    evaluator = BaseSyntaxEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {
        "result": result,
        "report_file": report_file
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 基础语法测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型地址")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M", help="模型名称")
    parser.add_argument("--output-dir", default="eval_results/stage4", help="输出目录")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_base_syntax_questions(150)
        print(f"生成了 {len(questions)} 道基础语法题目:")
        easy = sum(1 for q in questions if q["difficulty"] == "简单")
        medium = sum(1 for q in questions if q["difficulty"] == "中等")
        hard = sum(1 for q in questions if q["difficulty"] == "困难")
        print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

        # 保存题目
        output_file = os.path.join(args.output_dir, "base_syntax_questions.json")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到：{output_file}")
    else:
        print(f"开始运行基础语法测试...")
        test_result = run_base_syntax_test(args.model_url, args.model_name, args.output_dir)
        print(f"\n测试完成！通过率：{test_result['result'].pass_rate*100:.1f}%")
