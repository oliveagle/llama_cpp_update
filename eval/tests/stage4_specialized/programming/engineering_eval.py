#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - 工程实践 (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

ENGINEERING_TEMPLATES = {
    "设计模式": [
        {"q": "单例模式确保？", "opts": ["只有一个实例", "多个实例", "无实例", "临时实例"], "a": "A"},
        {"q": "工厂模式用于？", "opts": ["创建对象", "删除对象", "修改对象", "查询对象"], "a": "A"},
        {"q": "观察者模式适合？", "opts": ["事件通知", "数据查询", "对象创建", "算法替换"], "a": "A"},
        {"q": "策略模式的特点是？", "opts": ["算法可互换", "对象创建", "结构组合", "事件通知"], "a": "A"},
        {"q": "装饰器模式用于？", "opts": ["动态添加功能", "对象创建", "结构组合", "算法替换"], "a": "A"},
        {"q": "适配器模式的作用是？", "opts": ["接口转换", "对象创建", "动态功能", "算法替换"], "a": "A"},
        {"q": "代理模式用于？", "opts": ["控制访问", "对象创建", "结构组合", "算法替换"], "a": "A"},
        {"q": "建造者模式适合？", "opts": ["复杂对象创建", "简单对象", "对象池", "对象克隆"], "a": "A"},
        {"q": "原型模式用于？", "opts": ["复制对象", "创建新对象", "删除对象", "修改对象"], "a": "A"},
        {"q": "责任链模式的特点是？", "opts": ["多个对象处理请求", "单个对象处理", "集中处理", "随机处理"], "a": "A"},
    ],
    "测试": [
        {"q": "单元测试测试的是？", "opts": ["最小可测试单元", "整个系统", "用户界面", "数据库"], "a": "A"},
        {"q": "pytest 中测试函数命名前缀是？", "opts": ["test_", "check_", "assert_", "verify_"], "a": "A"},
        {"q": "assert 语句用于？", "opts": ["断言", "异常", "循环", "条件"], "a": "A"},
        {"q": "mock 对象用于？", "opts": ["模拟依赖", "真实调用", "性能测试", "压力测试"], "a": "A"},
        {"q": "测试覆盖率衡量？", "opts": ["代码执行比例", "测试数量", "bug 数量", "测试速度"], "a": "A"},
        {"q": "TDD 的含义是？", "opts": ["测试驱动开发", "传统驱动开发", "工具驱动开发", "时间驱动开发"], "a": "A"},
        {"q": "集成测试测试的是？", "opts": ["模块间交互", "单个函数", "用户界面", "性能"], "a": "A"},
        {"q": "回归测试用于？", "opts": ["确保修改未破坏功能", "新功能测试", "性能测试", "压力测试"], "a": "A"},
        {"q": "fixture 在 pytest 中用于？", "opts": ["测试准备和清理", "断言", "模拟", "覆盖率"], "a": "A"},
        {"q": "parametrize 用于？", "opts": ["参数化测试", "固定参数", "随机参数", "无参数"], "a": "A"},
    ],
    "版本控制": [
        {"q": "Git 中提交代码用？", "opts": ["git commit", "git push", "git pull", "git add"], "a": "A"},
        {"q": "git merge 用于？", "opts": ["合并分支", "创建分支", "删除分支", "切换分支"], "a": "A"},
        {"q": "git rebase 用于？", "opts": ["变基", "合并", "回滚", "撤销"], "a": "A"},
        {"q": "Git 冲突发生在？", "opts": ["合并时", "提交时", "推送时", "拉取时"], "a": "A"},
        {"q": "git stash 用于？", "opts": ["暂存修改", "提交修改", "删除修改", "恢复修改"], "a": "A"},
        {"q": "git cherry-pick 用于？", "opts": ["选择特定提交", "合并分支", "回滚提交", "删除提交"], "a": "A"},
        {"q": "HEAD 在 Git 中表示？", "opts": ["当前分支指向", "主分支", "远程分支", "标签"], "a": "A"},
        {"q": "git reset 用于？", "opts": ["重置状态", "提交代码", "合并代码", "推送代码"], "a": "A"},
    ],
    "CI/CD": [
        {"q": "CI 的含义是？", "opts": ["持续集成", "持续部署", "持续交付", "持续开发"], "a": "A"},
        {"q": "CD 的含义是？", "opts": ["持续部署/交付", "持续开发", "持续集成", "持续测试"], "a": "A"},
        {"q": "Jenkins 是？", "opts": ["CI/CD 工具", "代码编辑器", "数据库", "操作系统"], "a": "A"},
        {"q": "GitHub Actions 用于？", "opts": ["自动化工作流", "代码编辑", "数据存储", "用户管理"], "a": "A"},
        {"q": "流水线 (Pipeline) 包括？", "opts": ["构建、测试、部署", "只构建", "只测试", "只部署"], "a": "A"},
        {"q": "蓝绿部署的特点是？", "opts": ["两套环境切换", "灰度发布", "滚动更新", "回滚"], "a": "A"},
        {"q": "金丝雀发布是？", "opts": ["逐步发布给部分用户", "全量发布", "回滚", "测试"], "a": "A"},
    ],
    "代码质量": [
        {"q": "PEP 8 是？", "opts": ["Python 编码规范", "测试框架", "打包工具", "调试工具"], "a": "A"},
        {"q": "flake8 用于？", "opts": ["代码检查", "代码格式化", "代码打包", "代码测试"], "a": "A"},
        {"q": "black 是？", "opts": ["代码格式化器", "代码检查器", "测试框架", "打包工具"], "a": "A"},
        {"q": "mypy 用于？", "opts": ["类型检查", "代码格式化", "代码测试", "代码打包"], "a": "A"},
        {"q": "重构的目的是？", "opts": ["改善代码结构", "添加新功能", "修复 bug", "提高性能"], "a": "A"},
        {"q": "代码审查 (Code Review) 用于？", "opts": ["保证代码质量", "测试代码", "部署代码", "编写文档"], "a": "A"},
        {"q": "技术债务是指？", "opts": ["为快速交付牺牲质量", "欠债不还", "贷款编程", "代码太多"], "a": "A"},
    ],
}


def generate_engineering_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["版本控制", "测试"]
    medium_cats = ["设计模式", "CI/CD", "代码质量"]
    hard_cats = ["设计模式", "CI/CD", "代码质量"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in ENGINEERING_TEMPLATES and ENGINEERING_TEMPLATES[cat]:
            template = random.choice(ENGINEERING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"工程实践-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["engineering"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in ENGINEERING_TEMPLATES and ENGINEERING_TEMPLATES[cat]:
            template = random.choice(ENGINEERING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"工程实践-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["engineering"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in ENGINEERING_TEMPLATES and ENGINEERING_TEMPLATES[cat]:
            template = random.choice(ENGINEERING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"工程实践-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["engineering"]
            })
            qid += 1

    return questions


class EngineeringEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_engineering_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "engineering")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_engineering_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = EngineeringEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 工程实践测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_engineering_questions(150)
        print(f"生成了 {len(questions)} 道工程实践题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "engineering_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_engineering_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
