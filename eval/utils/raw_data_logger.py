#!/usr/bin/env python3
"""
原始测试数据记录器 - 高性能版本
使用 JSON Lines 格式，append-only 保存所有测试原始数据
支持批量写入、异步写入和内存缓冲

Usage:
    from utils.raw_data_logger import RawDataLogger

    # 高性能模式（推荐用于大量测试）
    logger = RawDataLogger("v100", buffer_size=100, auto_flush=True)

    # 记录单条
    logger.log_test_result({
        "test_name": "speed_test",
        "model": "Qwen3-VL-8B",
        "raw_response": {...}
    }, test_type="performance")

    # 批量记录（更高效）
    logger.log_batch_results([
        {"test_name": "test1", ...},
        {"test_name": "test2", ...}
    ], test_type="capability")

    # 确保所有数据写入
    logger.flush()

    # 上下文管理器（自动 flush）
    with RawDataLogger("vulkan") as logger:
        logger.log_test_result({...})
"""

import json
import os
import threading
import atexit
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class RawDataLogger:
    """原始数据记录器 - 高性能 JSON Lines append-only

    性能优化特性：
    1. 内存缓冲：批量写入减少磁盘 I/O
    2. 异步写入：后台线程处理文件写入
    3. 自动刷新：达到缓冲大小时自动写入
    4. 优雅关闭：程序退出时自动 flush
    """

    # 类级别的锁，用于线程安全
    _file_locks: Dict[str, threading.Lock] = {}
    _global_lock = threading.Lock()

    def __init__(
        self,
        backend: str,
        base_dir: str = "eval_results/raw_data",
        buffer_size: int = 50,
        auto_flush: bool = True,
        use_threading: bool = False
    ):
        """
        初始化记录器

        Args:
            backend: 后端名称 (v100, vulkan, etc.)
            base_dir: 原始数据存储目录
            buffer_size: 内存缓冲区大小，达到此数量时自动写入
            auto_flush: 是否启用自动刷新
            use_threading: 是否使用后台线程异步写入（实验性）
        """
        self.backend = backend
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.buffer_size = buffer_size
        self.auto_flush = auto_flush
        self.use_threading = use_threading

        # 按日期分文件: raw_data/v100_2026-02-17.jsonl
        self.date_str = datetime.now().strftime("%Y-%m-%d")
        self.file_path = self.base_dir / f"{backend}_{self.date_str}.jsonl"

        # 内存缓冲区 - 使用列表而不是deque，避免maxlen限制
        self._buffer: List[Dict] = []
        self._buffer_lock = threading.Lock()
        self._flush_count = 0
        self._total_records = 0

        # 获取或创建文件锁
        with self._global_lock:
            if str(self.file_path) not in self._file_locks:
                self._file_locks[str(self.file_path)] = threading.Lock()
        self._file_lock = self._file_locks[str(self.file_path)]

        # 后台线程（可选）
        self._flush_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        if use_threading:
            self._start_flush_thread()

        # 注册退出时刷新
        atexit.register(self._cleanup)

    def _start_flush_thread(self):
        """启动后台刷新线程"""
        def flush_worker():
            while not self._stop_event.wait(timeout=5.0):  # 每5秒检查一次
                self.flush()

        self._flush_thread = threading.Thread(target=flush_worker, daemon=True)
        self._flush_thread.start()

    def _cleanup(self):
        """清理资源，确保数据写入"""
        if self.use_threading:
            self._stop_event.set()
            if self._flush_thread and self._flush_thread.is_alive():
                self._flush_thread.join(timeout=2.0)
        self.flush()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动刷新"""
        self._cleanup()
        return False

    def log_test_result(self, data: Dict[str, Any], test_type: str = "unknown") -> bool:
        """
        记录单个测试结果

        Args:
            data: 测试原始数据
            test_type: 测试类型 (performance, capability, etc.)

        Returns:
            是否成功添加到缓冲区
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "backend": self.backend,
            "test_type": test_type,
            "data": data
        }

        with self._buffer_lock:
            self._buffer.append(record)
            self._total_records += 1
            current_size = len(self._buffer)

        # 自动刷新检查
        if self.auto_flush and current_size >= self.buffer_size:
            self.flush()

        return True

    def log_batch_results(
        self,
        results: List[Dict[str, Any]],
        test_type: str = "unknown",
        auto_flush: bool = True
    ) -> int:
        """
        批量记录测试结果（比多次调用 log_test_result 更高效）

        Args:
            results: 测试结果列表
            test_type: 测试类型
            auto_flush: 是否在此调用后自动刷新

        Returns:
            成功添加的记录数
        """
        timestamp = datetime.now().isoformat()
        records = [
            {
                "timestamp": timestamp,
                "backend": self.backend,
                "test_type": test_type,
                "data": result
            }
            for result in results
        ]

        with self._buffer_lock:
            self._buffer.extend(records)
            self._total_records += len(records)
            current_size = len(self._buffer)

        # 批量写入如果缓冲区已满
        if auto_flush and current_size >= self.buffer_size:
            self.flush()

        return len(records)

    def flush(self) -> int:
        """
        将缓冲区数据写入文件

        Returns:
            写入的记录数
        """
        with self._buffer_lock:
            if not self._buffer:
                return 0
            records_to_write = list(self._buffer)
            self._buffer.clear()

        if not records_to_write:
            return 0

        # 序列化所有记录
        lines = [
            json.dumps(record, ensure_ascii=False, separators=(',', ':'))
            for record in records_to_write
        ]
        content = '\n'.join(lines) + '\n'

        # 线程安全写入
        with self._file_lock:
            try:
                with open(self.file_path, "a", encoding="utf-8", buffering=8192) as f:
                    f.write(content)
                self._flush_count += len(records_to_write)
            except IOError as e:
                # 写入失败，尝试恢复缓冲区
                with self._buffer_lock:
                    self._buffer = list(records_to_write) + self._buffer
                raise e

        return len(records_to_write)

    def get_stats(self) -> Dict[str, Any]:
        """获取记录器统计信息"""
        with self._buffer_lock:
            buffer_size = len(self._buffer)
        return {
            "backend": self.backend,
            "file_path": str(self.file_path),
            "buffer_size": buffer_size,
            "buffer_capacity": self.buffer_size,
            "total_records": self._total_records,
            "flushed_records": self._flush_count,
            "pending_records": buffer_size,
            "auto_flush": self.auto_flush,
            "use_threading": self.use_threading
        }

    def get_file_path(self) -> str:
        """获取当前日志文件路径"""
        return str(self.file_path)

    def get_all_records(self, date: Optional[str] = None, limit: Optional[int] = None) -> list:
        """
        读取所有记录

        Args:
            date: 指定日期 (YYYY-MM-DD)，默认今天
            limit: 限制返回记录数

        Returns:
            记录列表
        """
        # 先刷新确保数据完整
        self.flush()

        target_file = self.file_path
        if date:
            target_file = self.base_dir / f"{self.backend}_{date}.jsonl"

        records = []
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if limit and i >= limit:
                        break
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue  # 跳过损坏的行
        return records

    @staticmethod
    def get_all_backends(base_dir: str = "eval_results/raw_data") -> list:
        """获取所有可用的后端列表"""
        base_path = Path(base_dir)
        if not base_path.exists():
            return []

        backends = set()
        for f in base_path.glob("*.jsonl"):
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
            date = f.stem.rsplit("_", 1)[1]
            dates.append(date)
        return sorted(dates)


def benchmark_logger():
    """性能基准测试"""
    import tempfile
    import time

    print("=" * 60)
    print("RawDataLogger 性能基准测试")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试 1: 单条写入（旧方式模拟）
        print("\n测试 1: 单条即时写入（1000条）")
        logger1 = RawDataLogger(
            "test1", base_dir=tmpdir,
            buffer_size=1, auto_flush=False
        )
        start = time.time()
        for i in range(1000):
            logger1.log_test_result({"test": i, "data": "x" * 100})
            logger1.flush()  # 每条都 flush 模拟旧行为
        elapsed1 = time.time() - start
        print(f"  耗时: {elapsed1:.3f}s")
        print(f"  速度: {1000/elapsed1:.0f} 条/秒")

        # 测试 2: 批量缓冲写入
        print("\n测试 2: 批量缓冲写入（buffer_size=50, 1000条）")
        logger2 = RawDataLogger(
            "test2", base_dir=tmpdir,
            buffer_size=50, auto_flush=True
        )
        start = time.time()
        for i in range(1000):
            logger2.log_test_result({"test": i, "data": "x" * 100})
        logger2.flush()  # 确保全部写入
        elapsed2 = time.time() - start
        print(f"  耗时: {elapsed2:.3f}s")
        print(f"  速度: {1000/elapsed2:.0f} 条/秒")
        print(f"  提升: {elapsed1/elapsed2:.1f}x")

        # 测试 3: 批量记录 API
        print("\n测试 3: 批量记录 API（1000条）")
        logger3 = RawDataLogger(
            "test3", base_dir=tmpdir,
            buffer_size=100, auto_flush=True
        )
        batch = [{"test": i, "data": "x" * 100} for i in range(1000)]
        start = time.time()
        logger3.log_batch_results(batch, auto_flush=True)
        logger3.flush()
        elapsed3 = time.time() - start
        print(f"  耗时: {elapsed3:.3f}s")
        print(f"  速度: {1000/elapsed3:.0f} 条/秒")
        print(f"  提升: {elapsed1/elapsed3:.1f}x")

        # 验证数据完整性
        print("\n数据完整性验证:")
        records = logger3.get_all_records()
        print(f"  写入: 1000条")
        print(f"  读取: {len(records)}条")
        print(f"  状态: {'✓ 通过' if len(records) == 1000 else '✗ 失败'}")

    print("\n" + "=" * 60)


def test_logger():
    """测试记录器功能"""
    print("=" * 60)
    print("RawDataLogger 功能测试")
    print("=" * 60)

    with RawDataLogger("test_backend", buffer_size=5) as logger:
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

        # 显示统计
        print("\n记录器统计:")
        stats = logger.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # 读取记录
        records = logger.get_all_records()
        print(f"\n记录了 {len(records)} 条数据")

    print(f"\n文件路径: {logger.get_file_path()}")

    # 清理测试文件
    os.remove(logger.get_file_path())
    print("测试文件已清理")
    print("=" * 60)


if __name__ == "__main__":
    test_logger()
    print()
    benchmark_logger()
