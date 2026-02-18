#!/usr/bin/env python3
"""
Context Window 性能预测器
基于采样数据线性预测 300s 实用阈值

Usage:
    from context_predictor import ContextPredictor

    predictor = ContextPredictor()
    predictor.add_sample(4096, 45.0)  # context, time
    predictor.add_sample(8192, 89.0)

    max_ctx = predictor.predict_max_context(timeout=300)
    print(f"300s 内最大支持: {max_ctx//1024}K")
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ContextSample:
    """Context 测试样本"""
    tokens: int
    time_seconds: float
    correct: bool = False


class ContextPredictor:
    """Context 性能预测器"""

    def __init__(self):
        self.samples: List[ContextSample] = []
        self._coeffs: Optional[np.ndarray] = None
        self._fitted = False

    def add_sample(self, tokens: int, time_seconds: float, correct: bool = False):
        """添加测试样本"""
        self.samples.append(ContextSample(tokens, time_seconds, correct))
        self._fitted = False  # 标记需要重新拟合

    def add_samples(self, samples: List[Tuple[int, float]]):
        """批量添加样本"""
        for tokens, time in samples:
            self.add_sample(tokens, time)

    def _fit(self) -> bool:
        """拟合线性模型"""
        if len(self.samples) < 2:
            return False

        # 排除异常点 (如 4K 可能因缓存等原因异常快)
        sorted_samples = sorted(self.samples, key=lambda x: x.tokens)
        contexts = np.array([s.tokens for s in sorted_samples])
        times = np.array([s.time_seconds for s in sorted_samples])

        # 如果第一个点是异常点 (比第二个点快很多)，排除它
        if len(contexts) >= 3 and times[0] < times[1] * 0.5:
            contexts = contexts[1:]
            times = times[1:]

        try:
            self._coeffs = np.polyfit(contexts, times, 1)
            self._fitted = True
            return True
        except (np.RankWarning, ValueError):
            return False

    def predict_time(self, tokens: int) -> Optional[float]:
        """预测指定 context 所需时间"""
        if not self._fitted:
            if not self._fit():
                return None

        return self._coeffs[0] * tokens + self._coeffs[1]

    def predict_max_context(self, timeout: float = 300.0) -> Optional[int]:
        """预测指定超时时间内支持的最大 context"""
        if not self._fitted:
            if not self._fit():
                return None

        slope, intercept = self._coeffs

        if slope <= 0:
            # 斜率异常，使用简单比例估算
            if not self.samples:
                return None
            max_sample = max(self.samples, key=lambda x: x.tokens)
            ratio = timeout / max_sample.time_seconds
            return int(max_sample.tokens * ratio)

        # 线性模型: timeout = slope * context + intercept
        max_context = (timeout - intercept) / slope
        return int(max_context)

    def get_recommendation(self, timeout: float = 300.0,
                          alignment: int = 4096) -> Optional[int]:
        """获取推荐的 context 配置 (对齐到指定粒度)"""
        max_ctx = self.predict_max_context(timeout)
        if max_ctx is None:
            return None

        # 向下对齐，并留出余量
        recommend = (int(max_ctx) // alignment) * alignment

        # 确保不超过任何已测试成功的 context
        successful = [s.tokens for s in self.samples if s.time_seconds < timeout]
        if successful:
            recommend = min(recommend, max(successful))

        return recommend

    def get_stats(self) -> dict:
        """获取统计信息"""
        if not self.samples:
            return {}

        if not self._fitted:
            self._fit()

        stats = {
            "samples": len(self.samples),
            "tested_contexts": [s.tokens for s in self.samples],
            "tested_times": [s.time_seconds for s in self.samples],
        }

        if self._fitted:
            stats["slope_per_1k"] = float(self._coeffs[0] * 1024)
            stats["intercept"] = float(self._coeffs[1])
            stats["predicted_max_300s"] = self.predict_max_context(300)
            stats["recommended_config"] = self.get_recommendation(300)

        return stats

    def print_report(self, timeout: float = 300.0):
        """打印预测报告"""
        print("=" * 60)
        print("Context Window 性能预测报告")
        print("=" * 60)

        if len(self.samples) < 2:
            print(f"\n样本不足 ({len(self.samples)} 个)，无法预测")
            return

        stats = self.get_stats()

        print(f"\n测试样本: {stats['samples']} 个")
        print(f"\n实测数据:")
        for s in sorted(self.samples, key=lambda x: x.tokens):
            status = "✅" if s.time_seconds < timeout else "❌"
            print(f"  {s.tokens//1024:3d}K: {s.time_seconds:6.1f}s  {status}")

        if self._fitted:
            print(f"\n线性模型: time = {stats['slope_per_1k']:.2f}s/K * context + {stats['intercept']:.1f}s")

            max_300s = stats['predicted_max_300s']
            recommend = stats['recommended_config']

            print(f"\n预测结果:")
            print(f"  300s 最大支持: {max_300s//1024 if max_300s else 'N/A'}K tokens")
            print(f"  推荐配置: ctx-size = {recommend if recommend else 'N/A'}")

            # 预测各 context 时间
            print(f"\n各 context 预测时间:")
            for ctx_k in [4, 8, 12, 16, 20, 24, 28, 32, 48, 64, 96, 128]:
                t = self.predict_time(ctx_k * 1024)
                if t:
                    status = "✅" if t < timeout else "❌"
                    print(f"  {ctx_k:3d}K: {t:6.1f}s  {status}")

        print("=" * 60)


def predict_from_results(results: dict, timeout: float = 300.0) -> ContextPredictor:
    """从测试结果字典创建预测器"""
    predictor = ContextPredictor()

    for test in results.get("tests", []):
        if test.get("status") == "success":
            predictor.add_sample(
                tokens=test.get("actual_tokens", test.get("target_tokens", 0)),
                time_seconds=test.get("response_time", 0),
                correct=test.get("correct", False)
            )

    return predictor


if __name__ == "__main__":
    # 示例：Qwen3-Coder-Next 数据
    predictor = ContextPredictor()
    predictor.add_samples([
        (4096, 79.0),
        (8192, 42.2),
        (12288, 71.9),
        (16384, 107.1),
        (24576, 196.7),
        (32768, 396.6),
    ])
    predictor.print_report()
