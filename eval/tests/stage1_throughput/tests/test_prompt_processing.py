#!/usr/bin/env python3
"""
Stage 1 - Prompt 处理速度测试

测试模型的 prompt processing (prefill) 性能，
使用不同长度的 prompt 测量处理速度 (tokens/second)。

Usage:
    python test_prompt_processing.py --backend vulkan --model-id minicpm-o-4_5
    python test_prompt_processing.py --backend cuda --model-file /path/to/model.gguf
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from runners.vulkan_runner import VulkanRunner, load_vulkan_backend_config
from runners.cuda_runner import CudaRunner, load_cuda_backend_config
from core.data_logger import DataLogger
from core.metrics import MetricsCalculator


def load_model_config(model_id: str) -> dict:
    """加载模型配置"""
    config_dir = Path(__file__).parent.parent / "config" / "models"
    config_file = config_dir / f"{model_id}.yaml"

    if not config_file.exists():
        # 使用通用配置
        config_file = config_dir / "generic.yaml"

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def find_model_file(pattern: str) -> str:
    """根据 pattern 查找模型文件"""
    import glob
    models_dir = Path("/mnt/volume3/llama_cpp/models")

    matches = list(models_dir.glob(pattern))
    if matches:
        return str(matches[0])

    raise FileNotFoundError(f"Model file not found: {pattern}")


def run_prompt_processing_test(backend: str, model_id: str, model_file: str = None,
                                iterations: int = 3, output_dir: str = None):
    """
    运行 prompt processing 测试

    Args:
        backend: 'vulkan' 或 'cuda'
        model_id: 模型标识（如 'minicpm-o-4_5'）
        model_file: 模型文件路径（可选，会自动查找）
        iterations: 每个长度测试次数
        output_dir: 结果输出目录
    """
    # 加载配置
    model_config_full = load_model_config(model_id)
    model_config = model_config_full.get('model', model_config_full)

    # 查找模型文件
    if model_file is None:
        pattern = model_config.get('gguf_pattern', f"*{model_id}*.gguf")
        model_file = find_model_file(pattern)

    print(f"Testing model: {model_file}")
    print(f"Backend: {backend}")

    # 创建运行器
    if backend == 'vulkan':
        backend_config = load_vulkan_backend_config()
        runner = VulkanRunner(backend_config, model_config)
        device = 'gfx1151'
    elif backend == 'cuda':
        backend_config = load_cuda_backend_config()
        runner = CudaRunner(backend_config, model_config)
        device = 'V100'
    else:
        raise ValueError(f"Unknown backend: {backend}")

    # 创建数据记录器
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "results" / "raw"

    logger = DataLogger(output_dir, backend, device)
    runner.set_logger(logger)

    # 启动服务器
    if not runner.setup_server(model_file):
        print("Failed to start server")
        return

    try:
        # 获取测试配置
        test_config = model_config.get('test_config', {})
        prompt_config = test_config.get('prompt_processing', {})

        # 测试长度列表
        prompt_lengths = prompt_config.get('prompt_lengths', [512, 1024, 2048, 4096])
        iters = prompt_config.get('iterations', iterations)

        print(f"\nTesting prompt lengths: {prompt_lengths}")
        print(f"Iterations per length: {iters}")
        print("-" * 60)

        for length in prompt_lengths:
            print(f"\nPrompt length: {length} tokens")

            for i in range(iters):
                result = runner.run_test("prompt_processing", {
                    "prompt_length": length,
                    "max_tokens": 1
                })

                if result.success:
                    tps = result.metrics.prompt_tokens_per_second
                    time_ms = result.metrics.prompt_processing_time_ms
                    print(f"  Iter {i+1}/{iters}: {tps:.1f} t/s ({time_ms:.0f} ms)")

                    # 记录结果
                    logger.log_result(result)
                else:
                    print(f"  Iter {i+1}/{iters}: FAILED - {result.error_message}")

        print("\n" + "=" * 60)
        print(f"Results saved to: {logger.get_current_file()}")

    finally:
        runner.teardown_server()


def main():
    parser = argparse.ArgumentParser(
        description="Stage 1 - Prompt Processing Speed Test"
    )
    parser.add_argument(
        "--backend",
        choices=['vulkan', 'cuda'],
        required=True,
        help="Backend to use (vulkan or cuda)"
    )
    parser.add_argument(
        "--model-id",
        required=True,
        help="Model identifier (e.g., 'minicpm-o-4_5', 'glm-4-9b')"
    )
    parser.add_argument(
        "--model-file",
        help="Path to GGUF model file (auto-detected if not specified)"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations per test (default: 3)"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for results"
    )

    args = parser.parse_args()

    run_prompt_processing_test(
        backend=args.backend,
        model_id=args.model_id,
        model_file=args.model_file,
        iterations=args.iterations,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
