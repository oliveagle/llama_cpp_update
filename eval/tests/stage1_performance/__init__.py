#!/usr/bin/env python3
"""
Stage 1: 基础性能测试

测试项:
1. 吞吐量 (Throughput) - tokens/sec
2. 预填充速度 (Prompt Processing) - tokens/sec
3. 生成速度 (Generation) - tokens/sec
4. Context梯度 (4K -> 128K)
"""

from .evaluator import PerformanceEvaluator

__all__ = ["PerformanceEvaluator"]
