#!/usr/bin/env python3
"""
NANOQUANT - Sub-1-bit Quantization for LLMs
Main entry point

Usage:
    python main.py quantize --model-path /path/to/hf/model --output-path ./output.gguf --rank 64
    python main.py generate --model ./output.gguf --prompt "Hello" --max-tokens 50
    python main.py benchmark --model ./output.gguf
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quantizer_fast import NanoQuantFast, quantize_qwen3_06b
from model_inference import NanoQuantModel
from llamacpp_loader import NanoQuantLlamaCppModel


def cmd_quantize(args):
    """Quantize a model"""
    print("=" * 60)
    print("NANOQUANT Model Quantization")
    print("=" * 60)

    if "qwen" in args.model_path.lower() and "0.6" in args.model_path:
        # Use optimized path for Qwen3 0.6B
        quantize_qwen3_06b(
            input_path=args.model_path,
            output_path=args.output_path,
            rank=args.rank,
        )
    else:
        # Generic quantization
        from safetensors.torch import load_file
        import json

        print(f"Loading model from {args.model_path}...")
        state_dict = load_file(f"{args.model_path}/model.safetensors")

        quantizer = NanoQuantFast(rank=args.rank, admm_iters=args.admm_iters)

        # Quantize
        quantized = {}
        for name, param in state_dict.items():
            if len(param.shape) >= 2 and "weight" in name and param.numel() >= 1024:
                print(f"  Quantizing {name}...")
                result = quantizer.quantize_layer(param, name)
                quantized[name] = {"type": "nanoquant", "data": result}
            else:
                quantized[name] = {"type": "original", "data": param}

        # Save
        print(f"Saving to {args.output_path}...")
        Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)
        import torch
        torch.save(quantized, args.output_path)
        print("Done!")


def cmd_generate(args):
    """Generate text"""
    model = NanoQuantModel(args.model)

    output = model.generate(
        prompt=args.prompt,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
    )

    print("\n" + "=" * 60)
    print("Generated Text:")
    print("=" * 60)
    print(output)


def cmd_benchmark(args):
    """Benchmark model"""
    model = NanoQuantLlamaCppModel(args.model)

    if args.validate:
        model.validate_accuracy()

    if args.inference:
        model.benchmark_inference(
            batch_size=args.batch_size,
            seq_len=args.seq_len,
            num_runs=args.num_runs,
        )


def main():
    parser = argparse.ArgumentParser(
        description="NANOQUANT - Sub-1-bit Quantization for LLMs"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Quantize command
    quantize_parser = subparsers.add_parser("quantize", help="Quantize a model")
    quantize_parser.add_argument("--model-path", required=True, help="Path to HF model")
    quantize_parser.add_argument("--output-path", required=True, help="Output path")
    quantize_parser.add_argument("--rank", type=int, default=64, help="Decomposition rank")
    quantize_parser.add_argument("--admm-iters", type=int, default=30, help="ADMM iterations")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate text")
    generate_parser.add_argument("--model", required=True, help="Path to NANOQUANT model")
    generate_parser.add_argument("--prompt", default="Hello, how are you?", help="Input prompt")
    generate_parser.add_argument("--max-tokens", type=int, default=50, help="Max new tokens")
    generate_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    generate_parser.add_argument("--top-p", type=float, default=0.9, help="Top-p sampling")

    # Benchmark command
    benchmark_parser = subparsers.add_parser("benchmark", help="Benchmark model")
    benchmark_parser.add_argument("--model", required=True, help="Path to NANOQUANT model")
    benchmark_parser.add_argument("--validate", action="store_true", help="Validate accuracy")
    benchmark_parser.add_argument("--inference", action="store_true", help="Benchmark inference")
    benchmark_parser.add_argument("--batch-size", type=int, default=1, help="Batch size")
    benchmark_parser.add_argument("--seq-len", type=int, default=128, help="Sequence length")
    benchmark_parser.add_argument("--num-runs", type=int, default=10, help="Number of runs")

    args = parser.parse_args()

    if args.command == "quantize":
        cmd_quantize(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "benchmark":
        cmd_benchmark(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
