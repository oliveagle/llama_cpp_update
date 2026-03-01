#!/usr/bin/env python3
"""
Stage 4 专项能力测试运行脚本
用于运行编程能力和运维能力测试 (各 1000 题)
"""

import argparse
import sys
import os

# 添加 eval 目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 编程能力测试模块
from programming.algorithm_eval import run_algorithm_test, generate_algorithm_questions
from programming.base_syntax_eval import run_base_syntax_test, generate_base_syntax_questions
from programming.system_design_eval import run_system_design_test, generate_system_design_questions
from programming.debugging_eval import run_debugging_test, generate_debugging_questions
from programming.engineering_eval import run_engineering_test, generate_engineering_questions
from programming.database_eval import run_database_test, generate_database_questions

# 运维能力测试模块
from devops.linux_eval import run_devops_test, generate_devops_questions
from devops.container_eval import run_container_test, generate_container_questions
from devops.network_security_eval import run_network_security_test, generate_network_security_questions
from devops.monitoring_eval import run_monitoring_test, generate_monitoring_questions
from devops.cicd_eval import run_cicd_test, generate_cicd_questions
from devops.cloud_iac_eval import run_cloud_iac_test, generate_cloud_iac_questions


def generate_all_programming_questions():
    """生成所有编程能力题目 (1000 题)"""
    questions = []
    qid = 1

    # 各模块题目数量
    modules = [
        (generate_base_syntax_questions, 150, "基础语法"),
        (generate_algorithm_questions, 250, "算法"),
        (generate_system_design_questions, 150, "系统设计"),
        (generate_debugging_questions, 150, "代码调试"),
        (generate_engineering_questions, 150, "工程实践"),
        (generate_database_questions, 150, "数据库"),
    ]

    for generator, count, name in modules:
        module_questions = generator(count)
        for q in module_questions:
            q["id"] = qid
            q["name"] = f"编程-{name}-{qid}"
            questions.append(q)
            qid += 1

    return questions


def generate_all_devops_questions():
    """生成所有运维能力题目 (1000 题)"""
    questions = []
    qid = 1

    # 各模块题目数量
    modules = [
        (generate_devops_questions, 200, "Linux 基础"),
        (generate_container_questions, 200, "容器与编排"),
        (generate_network_security_questions, 150, "网络与安全"),
        (generate_monitoring_questions, 150, "监控与日志"),
        (generate_cicd_questions, 150, "CI/CD"),
        (generate_cloud_iac_questions, 150, "云服务与 IaC"),
    ]

    for generator, count, name in modules:
        module_questions = generator(count)
        for q in module_questions:
            q["id"] = qid
            q["name"] = f"运维-{name}-{qid}"
            questions.append(q)
            qid += 1

    return questions


def run_all_programming_tests(model_url: str, model_name: str, output_dir: str):
    """运行所有编程能力测试 (1000 题)"""
    from base import Stage4BaseEvaluator

    print("正在生成 1000 道编程能力题目...")
    questions = generate_all_programming_questions()

    print(f"题目生成完成，开始测试...")
    evaluator = Stage4BaseEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests(questions, "programming")
    report_file = evaluator.generate_report(result)

    return {"result": result, "report_file": report_file}


def run_all_devops_tests(model_url: str, model_name: str, output_dir: str):
    """运行所有运维能力测试 (1000 题)"""
    from base import Stage4BaseEvaluator

    print("正在生成 1000 道运维能力题目...")
    questions = generate_all_devops_questions()

    print(f"题目生成完成，开始测试...")
    evaluator = Stage4BaseEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests(questions, "devops")
    report_file = evaluator.generate_report(result)

    return {"result": result, "report_file": report_file}


def main():
    parser = argparse.ArgumentParser(
        description="Stage 4 专项能力测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 生成题目 (不运行测试)
  python run_stage4.py --type programming --generate-only
  python run_stage4.py --type devops --generate-only
  python run_stage4.py --type all --generate-only

  # 运行测试 (完整 1000 题)
  python run_stage4.py --type programming
  python run_stage4.py --type devops

  # 指定模型
  python run_stage4.py --type programming --model-url http://localhost:8401 --model-name Qwen3-Coder-Next

  # 运行子类别测试
  python -m tests.stage4_specialized.programming.algorithm_eval --generate-only
  python -m tests.stage4_specialized.devops.container_eval
        """
    )

    parser.add_argument(
        "--type",
        choices=["programming", "devops", "algorithm", "all"],
        default="all",
        help="测试类型：programming(编程,1000题), devops(运维,1000题), algorithm(算法,250题), all(全部)"
    )
    parser.add_argument(
        "--model-url",
        default="http://localhost:8400",
        help="模型 API 地址 (默认：http://localhost:8400)"
    )
    parser.add_argument(
        "--model-name",
        default="JoyAI-LLM-Flash-Q4_K_M",
        help="模型名称 (默认：JoyAI-LLM-Flash-Q4_K_M)"
    )
    parser.add_argument(
        "--output-dir",
        default="eval_results/stage4",
        help="输出目录 (默认：eval_results/stage4)"
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="只生成题目，不运行测试"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Stage 4 专项能力测试")
    print("=" * 70)
    print(f"模型：{args.model_name}")
    print(f"地址：{args.model_url}")
    print(f"输出：{args.output_dir}")
    print("=" * 70)

    os.makedirs(args.output_dir, exist_ok=True)

    results = {}

    if args.type in ["programming", "all"]:
        if args.generate_only:
            print("\n生成编程能力测试题目... (目标 1000 题)")
            questions = generate_all_programming_questions()
            easy = sum(1 for q in questions if q["difficulty"] == "简单")
            medium = sum(1 for q in questions if q["difficulty"] == "中等")
            hard = sum(1 for q in questions if q["difficulty"] == "困难")
            print(f"生成了 {len(questions)} 道题目:")
            print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

            output_file = os.path.join(args.output_dir, "programming_questions.json")
            import json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"题目已保存到：{output_file}")
        else:
            print("\n[编程能力测试] 运行中... (1000 题)")
            result = run_all_programming_tests(args.model_url, args.model_name, args.output_dir)
            results["programming"] = result
            print(f"\n编程测试完成！通过率：{result['result'].pass_rate*100:.1f}%")

    elif args.type == "algorithm":
        if args.generate_only:
            print("\n生成算法测试题目...")
            questions = generate_algorithm_questions(250)
            easy = sum(1 for q in questions if q["difficulty"] == "简单")
            medium = sum(1 for q in questions if q["difficulty"] == "中等")
            hard = sum(1 for q in questions if q["difficulty"] == "困难")
            print(f"生成了 {len(questions)} 道题目:")
            print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

            output_file = os.path.join(args.output_dir, "algorithm_questions.json")
            import json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"题目已保存到：{output_file}")
        else:
            print("\n运行算法测试...")
            result = run_algorithm_test(args.model_url, args.model_name, args.output_dir)
            results["algorithm"] = result
            print(f"\n算法测试完成！通过率：{result['result'].pass_rate*100:.1f}%")

    if args.type in ["devops", "all"]:
        if args.generate_only:
            print("\n生成运维能力测试题目... (目标 1000 题)")
            questions = generate_all_devops_questions()
            easy = sum(1 for q in questions if q["difficulty"] == "简单")
            medium = sum(1 for q in questions if q["difficulty"] == "中等")
            hard = sum(1 for q in questions if q["difficulty"] == "困难")
            print(f"生成了 {len(questions)} 道题目:")
            print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

            output_file = os.path.join(args.output_dir, "devops_questions.json")
            import json
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            print(f"题目已保存到：{output_file}")
        else:
            print("\n[运维能力测试] 运行中... (1000 题)")
            result = run_all_devops_tests(args.model_url, args.model_name, args.output_dir)
            results["devops"] = result
            print(f"\n运维测试完成！通过率：{result['result'].pass_rate*100:.1f}%")

    # 打印汇总
    if not args.generate_only and results:
        print("\n" + "=" * 70)
        print("测试汇总")
        print("=" * 70)
        total_tests = 0
        total_passed = 0
        for test_type, result in results.items():
            r = result['result']
            total_tests += r.total_tests
            total_passed += r.passed_tests
            status = "✅" if r.pass_rate >= 0.6 else "⚠️"
            print(f"  {status} {test_type}: {r.pass_rate*100:.1f}% ({r.passed_tests}/{r.total_tests})")
        if len(results) > 1:
            overall_rate = total_passed / total_tests if total_tests > 0 else 0
            status = "✅" if overall_rate >= 0.6 else "⚠️"
            print(f"  {status} 整体: {overall_rate*100:.1f}% ({total_passed}/{total_tests})")
        print("=" * 70)


if __name__ == "__main__":
    main()
