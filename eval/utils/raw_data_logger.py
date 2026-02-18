#!/usr/bin/env python3
"""
原始测试数据记录器
使用 JSON Lines 格式，append-only 保存所有测试原始数据

Usage:
    from utils.raw_data_logger import RawDataLogger

    logger = RawDataLogger("v100")
    logger.log_test_result({
        "test_name": "speed_test",
        "model": "Qwen3-VL-8B",
        "timestamp": "2026-02-17T10:00:00",
        "raw_response": {...}
    })
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class RawDataLogger:
    """原始数据记录器 - JSON Lines append-only"""

    def __init__(self, backend: str, base_dir: str = "eval_results/raw_data"):
        """
        初始化记录器

        Args:
            backend: 后端名称 (v100, vulkan, etc.)
            base_dir: 原始数据存储目录
        """
        self.backend = backend
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # 按日期分文件: raw_data/v100_2026-02-17.jsonl
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.file_path = self.base_dir / f"{backend}_{self.date_str}.jsonl"

    def log_test_result(self, data: Dict[str, Any], test_type: str = "unknown"):
        """
        记录单个测试结果

        Args:
            data: 测试原始数据
            test_type: 测试类型 (performance, capability, etc.)
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "backend": self.backend,
            "test_type": test_type,
            "data": data
        }

        # Append-only 写入
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_batch_results(self, results: list, test_type: str = "unknown"):
        """
        批量记录测试结果

        Args:
            results: 测试结果列表
            test_type: 测试类型
        """
        for result in results:
            self.log_test_result(result, test_type)

    def get_file_path(self) -> str:
        """获取当前日志文件路径"""
        return str(self.file_path)

    def get_all_records(self, date: Optional[str] = None) -> list:
        """
        读取所有记录

        Args:
            date: 指定日期 (YYYY-MM-DD)，默认今天

        Returns:
            记录列表
        """
        target_file = self.file_path
        if date:
            target_file = self.base_dir / f"{self.backend}_{date}.jsonl"

        records = []
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        return records

    @staticmethod
    def get_all_backends(base_dir: str = "eval_results/raw_data") -> list:
        """获取所有可用的后端列表"""
        base_path = Path(base_dir)
        if not base_path.exists():
            return []

        backends = set()
        for f in base_path.glob("*.jsonl"):
            # 文件名格式: backend_YYYY-MM-DD.jsonl
            backend = f.stem.rsplit("_", 1)[0]
            backends.add(backend)
        return sorted(list(backends))

    @staticmethod
    def get_all_dates(backend: str, base_dir: str = "eval_results/raw_data") -> list:
        """获取指定后端的所有日期"""
        base_path = Path(base_dir)
        if not base_path.exists():
            return []

        dates = []
        for f in base_path.glob(f"{backend}_*.jsonl"):
            # 文件名格式: backend_YYYY-MM-DD.jsonl
            date = f.stem.rsplit("_", 1)[1]
            dates.append(date)
        return sorted(dates)


def test_logger():
    """测试记录器功能"""
    logger = RawDataLogger("test_backend")

    # 测试单条记录
    logger.log_test_result({
        "model": "test_model",
        "result": "success",
        "metrics": {"accuracy": 0.95}
    }, test_type="performance")

    # 测试批量记录
    logger.log_batch_results([
        {"test": 1, "result": "pass"},
        {"test": 2, "result": "fail"}
    ], test_type="capability")

    # 读取记录
    records = logger.get_all_records()
    print(f"记录了 {len(records)} 条数据")
    for r in records:
        print(f"  [{r['timestamp']}] {r['test_type']}: {r['data']}")

    print(f"\n文件路径: {logger.get_file_path()}")

    # 清理测试文件
    os.remove(logger.get_file_path())
    print("测试文件已清理")


if __name__ == "__main__":
    test_logger()
