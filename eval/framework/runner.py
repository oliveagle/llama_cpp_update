#!/usr/bin/env python3
"""
评估执行器
"""

import time
from typing import List, Optional, Type
from .base import BaseEvaluator, StageResult


class EvaluationRunner:
    """评估执行器 - 管理三层测试流程"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "./reports"):
        self.model_url = model_url
        self.model_name = model_name
        self.output_dir = output_dir
        self.evaluators: List[Type[BaseEvaluator]] = []
        self.results: List[StageResult] = []

    def register_evaluator(self, evaluator_class: Type[BaseEvaluator]):
        """注册评估器"""
        self.evaluators.append(evaluator_class)
        # 按阶段编号排序
        self.evaluators.sort(key=lambda e: e(None, None).stage_number)

    def run_stage(self, stage_number: int, **kwargs) -> Optional[StageResult]:
        """运行指定阶段"""
        evaluator_class = None
        for ec in self.evaluators:
            if ec(None, None).stage_number == stage_number:
                evaluator_class = ec
                break

        if evaluator_class is None:
            print(f"[ERROR] 阶段 {stage_number} 未注册")
            return None

        evaluator = evaluator_class(self.model_url, self.model_name, **kwargs)

        # 检查前置条件
        if not evaluator.check_prerequisites():
            print(f"[ERROR] 阶段 {stage_number} 前置条件不满足")
            return None

        print(f"\n{'='*60}")
        print(f"阶段 {stage_number}: {evaluator.stage_name}")
        print(f"{'='*60}")

        start_time = time.time()
        result = evaluator.run_tests()
        result.duration_seconds = time.time() - start_time

        # 判断通过门槛
        result.passed_threshold = result.pass_rate >= evaluator.threshold_percentage
        result.threshold_percentage = evaluator.threshold_percentage

        self._print_stage_result(result)
        self.results.append(result)

        return result

    def run_all(self, start_stage: int = 1) -> List[StageResult]:
        """运行所有阶段"""
        print(f"\n{'='*60}")
        print(f"模型评估: {self.model_name}")
        print(f"API地址: {self.model_url}")
        print(f"{'='*60}")

        for evaluator_class in self.evaluators:
            evaluator = evaluator_class(None, None)
            stage_num = evaluator.stage_number

            if stage_num < start_stage:
                continue

            # 检查前一阶段是否通过
            if stage_num > 1:
                prev_result = self._get_stage_result(stage_num - 1)
                if prev_result and not prev_result.passed_threshold:
                    print(f"\n[SKIP] 阶段 {stage_num} 跳过 (前一阶段未通过门槛)")
                    continue

            result = self.run_stage(stage_num)
            if result is None:
                break

        return self.results

    def _get_stage_result(self, stage_number: int) -> Optional[StageResult]:
        """获取阶段结果"""
        for r in self.results:
            if r.stage_number == stage_number:
                return r
        return None

    def _print_stage_result(self, result: StageResult):
        """打印阶段结果"""
        status = "✅ 通过" if result.passed_threshold else "❌ 未通过"
        print(f"\n{'='*60}")
        print(f"{result.stage_name} 完成!")
        print(f"  总计: {result.total_tests}")
        print(f"  通过: {result.passed_tests}")
        print(f"  失败: {result.failed_tests}")
        print(f"  准确率: {result.pass_rate:.1%}")
        print(f"  门槛: {result.threshold_percentage:.0%} - {status}")
        print(f"{'='*60}")
