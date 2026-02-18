#!/usr/bin/env python3
"""
Stage 1 - Token 生成速度测试

测试模型的 token generation 性能，
测量生成速度 (tokens/second) 和延迟。

Usage:
    python test_token_generation.py --backend vulkan --model-id minicpm-o-4_5
    python test_token_generation.py --backend cuda --model-file /path/to/model.gguf
"""

import argparse
import sys
import yaml
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from runners.vulkan_runner import VulkanRunner, load_vulkan_backend_config
from runners.cuda_runner import CudaRunner, load_cuda_backend_config
from core.data_logger import DataLogger


def load_model_config(model_id: str) -> dict:
    """加载模型配置"""
    config_dir = Path(__file__).parent.parent / "config" / "models"
    config_file = config_dir / f"{model_id}.yaml"

    if not config_file.exists():
        config_file = config_dir / "generic.yaml"

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def find_model_file(pattern: str) -> str:
    """根据 pattern 查找模型文件"""
    models_dir = Path("/mnt/volume3/llama_cpp/models")

    matches = list(models_dir.glob(pattern))
    if matches:
        return str(matches[0])

    raise FileNotFoundError(f"Model file not found: {pattern}")


def run_token_generation_test(backend: str, model_id: str, model_file: str = None,
                               iterations: int = 3, output_dir: str = None):
    """
    运行 token generation 测试

    Args:
        backend: 'vulkan' 或 'cuda'
        model_id: 模型标识
        model_file: 模型文件路径（可选）
        iterations: 每个配置测试次数
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
        gen_config = test_config.get('token_generation', {})

        prompt_length = gen_config.get('prompt_length', 1024)
        max_tokens_list = gen_config.get('max_tokens_list', [128, 256, 512])
        iters = gen_config.get('iterations', iterations)

        print(f"\nPrompt length: {prompt_length}")
        print(f"Testing max_tokens: {max_tokens_list}")
        print(f"Iterations per config: {iters}")
        print("-" * 60)

        for max_tokens in max_tokens_list:
            print(f"\nMax tokens to generate: {max_tokens}")

            for i in range(iters):
                result = runner.run_test("token_generation", {
                    "prompt_length": prompt_length,
                    "max_tokens": max_tokens
                })

                if result.success:
                    gen_tps = result.metrics.generation_tokens_per_second
                    total_tps = result.metrics.total_tokens_per_second
                    ttft = result.metrics.ttft_ms
                    print(f"  Iter {i+1}/{iters}: Gen {gen_tps:.1f} t/s, Total {total_tps:.1f} t/s, TTFT {ttft:.0f}ms")

                    logger.log_result(result)
                else:
                    print(f"  Iter {i+1}/{iters}: FAILED - {result.error_message}")

        print("\n" + "=" * 60)
        print(f"Results saved to: {logger.get_current_file()}")

    finally:
        runner.teardown_server()


def main():
    parser = argparse.ArgumentParser(
        description="Stage 1 - Token Generation Speed Test"
    )
    parser.add_argument(
        "--backend",
        choices=['vulkan', 'cuda'],
        required=True,
        help="Backend to use"
    )
    parser.add_argument(
        "--model-id",
        required=True,
        help="Model identifier"
    )
    parser.add_argument(
        "--model-file",
        help="Path to GGUF model file"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of iterations per test"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for results"
    )

    args = parser.parse_args()

    run_token_generation_test(
        backend=args.backend,
        model_id=args.model_id,
        model_file=args.model_file,
        iterations=args.iterations,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
