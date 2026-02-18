#!/usr/bin/env python3
"""
JSONL 数据记录器

标准化的测试数据记录格式，支持按后端、模型、时间分片存储。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import asdict


class DataLogger:
    """
    Stage 1 测试数据记录器

    所有测试数据以 JSONL 格式存储，便于后续分析和报告生成。

    Usage:
        logger = DataLogger("/mnt/volume3/llama_cpp/eval/tests/stage1_throughput/results/raw")
        logger.log_result(test_result)
    """

    def __init__(self, output_dir: str, backend_type: str = "unknown", device: str = "unknown"):
        """
        初始化数据记录器

        Args:
            output_dir: 原始数据输出目录
            backend_type: 后端类型 (cuda, vulkan, rocm)
            device: 设备标识 (V100, gfx1151, etc)
        """
        self.output_dir = Path(output_dir)
        self.backend_type = backend_type
        self.device = device
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名: {backend}_{device}_{timestamp}.jsonl
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f"{backend_type}_{device}_{timestamp}.jsonl"
        self.filepath = self.output_dir / self.filename

        self.record_count = 0

    def log_result(self, result: Any) -> str:
        """
        记录单个测试结果

        Args:
            result: 测试结果对象 (TestResult 或字典)

        Returns:
            记录ID (行号)
        """
        # 转换为字典
        if hasattr(result, '__dataclass_fields__'):
            data = asdict(result)
        else:
            data = dict(result)

        # 添加元数据
        data['_meta'] = {
            'record_id': self.record_count,
            'logged_at': datetime.now().isoformat(),
            'backend_type': self.backend_type,
            'device': self.device
        }

        # 追加写入 JSONL
        with open(self.filepath, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, default=str)
            f.write('\n')

        self.record_count += 1
        return f"{self.filename}#{self.record_count - 1}"

    def log_batch(self, results: list) -> list:
        """
        批量记录测试结果

        Args:
            results: 测试结果列表

        Returns:
            记录ID列表
        """
        ids = []
        for result in results:
            record_id = self.log_result(result)
            ids.append(record_id)
        return ids

    def get_current_file(self) -> str:
        """获取当前数据文件路径"""
        return str(self.filepath)

    def get_record_count(self) -> int:
        """获取已记录的数据条数"""
        return self.record_count

    @staticmethod
    def load_results(filepath: str) -> list:
        """
        加载 JSONL 文件中的所有记录

        Args:
            filepath: JSONL 文件路径

        Returns:
            记录列表
        """
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    results.append(json.loads(line))
        return results

    @staticmethod
    def filter_results(filepath: str, **kwargs) -> list:
        """
        按条件过滤记录

        Args:
            filepath: JSONL 文件路径
            **kwargs: 过滤条件，如 model_id="Qwen3-4B", test_type="token_generation"

        Returns:
            符合条件的记录列表
        """
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                data = json.loads(line)
                match = True
                for key, value in kwargs.items():
                    if key in data and data[key] != value:
                        match = False
                        break
                if match:
                    results.append(data)
        return results
