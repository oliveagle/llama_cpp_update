#!/usr/bin/env python3
"""Qwen3.5-4B Stage 3 深度能力测试
测试包含 10 个维度，每个维度 100 个测试用例，共 1000 个测试用例
"""

import sys
import os
import json
import time
import argparse
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.tests.stage3_deep.math_eval import run_math_test
from eval.tests.stage3_deep.code_eval import run_code_test
from eval.tests.stage3_deep.logic_eval import run_logic_test
from eval.tests.stage3_deep.commonsense_eval import run_commonsense_test
from eval.tests.stage3_deep.text_eval import run_text_test
from eval.tests.stage3_deep.shell_eval import run_shell_test
from eval.tests.stage3_deep.reasoning_eval import run_reasoning_test
from eval.tests.stage3_deep.knowledge_eval import run_knowledge_test
from eval.tests.stage3_deep.safety_eval import run_safety_test
from eval.tests.stage3_deep.multiturn_eval import run_multiturn_test

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"qwen35_4b_stage3_{time.strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_stage3_test(model_name, base_url="http://localhost:8401", output_dir="eval/results/stage3"):
    """运行完整的 Stage 3 测试"""

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    results = {
        "model": model_name,
        "base_url": base_url,
        "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "categories": {}
    }

    total_start_time = time.time()

    logger.info(f"=== 开始 Qwen3.5-4B Stage 3 深度能力测试 ===")
    logger.info(f"模型：{model_name}")
    logger.info(f"API 地址：{base_url}")
    logger.info(f"输出目录：{output_dir}")
    logger.info(f"测试开始时间：{results['test_time']}")

    # 运行各个维度测试
    categories = [
        ("数学能力", run_math_test),
        ("代码能力", run_code_test),
        ("逻辑推理", run_logic_test),
        ("常识问答", run_commonsense_test),
        ("文本理解", run_text_test),
        ("运维能力", run_shell_test),
        ("深度推理", run_reasoning_test),
        ("知识问答", run_knowledge_test),
        ("安全合规", run_safety_test),
        ("多轮对话", run_multiturn_test)
    ]

    for category_name, run_func in categories:
        logger.info(f"\n--- 开始测试：{category_name} ---")
        category_start_time = time.time()

        try:
            category_result = run_func(base_url, model_name)
            results["categories"][category_name] = {
                "passed": category_result["passed_tests"],
                "failed": category_result["failed_tests"],
                "total": category_result["total_tests"],
                "pass_rate": category_result["pass_rate"] * 100,
                "test_cases": category_result["tests"]
            }

            category_time = time.time() - category_start_time
            logger.info(f"{category_name} 测试完成：{category_time:.2f} 秒")
            logger.info(f"通过：{category_result['passed_tests']}, 失败：{category_result['failed_tests']}, 总题数：{category_result['total_tests']}")
            logger.info(f"通过率：{category_result['pass_rate']*100:.1f}%")
        except Exception as e:
            logger.error(f"{category_name} 测试失败：{str(e)}")
            results["categories"][category_name] = {
                "passed": 0,
                "failed": 100,
                "total": 100,
                "pass_rate": 0.0,
                "test_cases": [],
                "error": str(e)
            }

    # 计算总体统计
    total_passed = sum(cat["passed"] for cat in results["categories"].values())
    total_failed = sum(cat["failed"] for cat in results["categories"].values())
    total_count = total_passed + total_failed

    results["total"] = {
        "passed": total_passed,
        "failed": total_failed,
        "total": total_count,
        "pass_rate": (total_passed / total_count) * 100 if total_count > 0 else 0,
        "test_duration": time.time() - total_start_time
    }

    logger.info(f"\n=== 测试完成 ===")
    logger.info(f"总题数：{total_count}")
    logger.info(f"通过：{total_passed}, 失败：{total_failed}")
    logger.info(f"总通过率：{results['total']['pass_rate']:.1f}%")
    logger.info(f"总耗时：{results['total']['test_duration']:.2f} 秒")
    if total_count > 0:
        logger.info(f"平均每题耗时：{results['total']['test_duration']/total_count:.2f} 秒/题")

    # 保存结果
    output_file = os.path.join(output_dir, f"qwen3.5-4b_stage3_{time.strftime('%Y%m%d_%H%M%S')}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"结果已保存到：{output_file}")

    return results

def print_summary(results):
    """打印测试结果摘要"""
    print("\n" + "="*80)
    print("Qwen3.5-4B Stage 3 深度能力测试结果摘要")
    print("="*80)
    print(f"模型名称：{results['model']}")
    print(f"测试时间：{results['test_time']}")
    print(f"API 地址：{results['base_url']}")
    print(f"总题数：{results['total']['total']}")
    print(f"通过：{results['total']['passed']}")
    print(f"失败：{results['total']['failed']}")
    print(f"总通过率：{results['total']['pass_rate']:.1f}%")
    print(f"总耗时：{results['total']['test_duration']:.2f} 秒")
    if results['total']['total'] > 0:
        print(f"平均每题耗时：{results['total']['test_duration']/results['total']['total']:.2f} 秒/题")
    print("\n" + "-"*80)
    print("各维度测试结果:")
    print("-"*80)

    for category_name, category_result in results["categories"].items():
        print(f"{category_name:<10} | 通过：{category_result['passed']:3}/{category_result['total']:3} | 通过率：{category_result['pass_rate']:.1f}%")

    print("\n" + "="*80)

def main():
    parser = argparse.ArgumentParser(description="Qwen3.5-4B Stage 3 深度能力测试")
    parser.add_argument("--model", type=str, default="Qwen3.5-4B-UD-Q4_K_XL",
                        help="模型名称")
    parser.add_argument("--url", type=str, default="http://localhost:8401",
                        help="API 地址")
    parser.add_argument("--output", type=str, default="eval/results/stage3",
                        help="输出目录")
    parser.add_argument("--print", action="store_true", default=True,
                        help="打印结果摘要")

    args = parser.parse_args()

    try:
        results = run_stage3_test(args.model, args.url, args.output)

        if args.print:
            print_summary(results)

        return 0
    except Exception as e:
        logger.error(f"测试执行失败：{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
