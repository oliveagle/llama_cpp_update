"""
NANOQUANT Model Converter
Converts HuggingFace models to NANOQUANT format

Target: Qwen3-0.6B model
"""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from safetensors.torch import load_file
import json
from tqdm import tqdm

from nanoquant_core import (
    NanoQuantConfig,
    quantize_tensor_nanoquant,
    dequantize_tensor_nanoquant,
    compute_compression_ratio,
)


class NanoQuantConverter:
    """Converter for transforming HF models to NANOQUANT format"""

    def __init__(self, config: Optional[NanoQuantConfig] = None):
        self.config = config or NanoQuantConfig()
        self.quantized_state_dict = {}
        self.original_sizes = {}
        self.compression_ratios = {}

    def quantize_linear_layer(
        self,
        weight: torch.Tensor,
        layer_name: str,
    ) -> Dict[str, torch.Tensor]:
        """Quantize a single linear layer"""
        print(f"  Quantizing {layer_name}: {weight.shape}")

        # Store original size
        self.original_sizes[layer_name] = weight.numel() * 2  # FP16 bytes

        # Quantize (convert to float32 for processing)
        weight_f32 = weight.float()
        quantized = quantize_tensor_nanoquant(weight_f32, self.config)

        # Calculate compression ratio
        ratio = compute_compression_ratio(weight.shape, self.config)
        self.compression_ratios[layer_name] = ratio

        # Prepare storage format
        result = {
            f"{layer_name}.b1": quantized['binary_directions_1'].to(torch.int8),
            f"{layer_name}.b2": quantized['binary_directions_2'].to(torch.int8),
            f"{layer_name}.scales": quantized['importance_scales'].to(torch.float16),
            f"{layer_name}.shape": torch.tensor(quantized['original_shape']),
        }

        return result

    def convert_model(
        self,
        model_path: str,
        output_path: str,
        device: str = "cpu",
    ) -> Dict:
        """
        Convert a full model to NANOQUANT format

        Args:
            model_path: Path to HF model directory (with model.safetensors)
            output_path: Path to save NANOQUANT model
            device: Device to use for processing
        """
        model_path = Path(model_path)
        output_path = Path(output_path)

        print(f"Loading model from {model_path}...")

        # Load safetensors
        safetensors_path = model_path / "model.safetensors"
        if not safetensors_path.exists():
            raise FileNotFoundError(f"Model file not found: {safetensors_path}")

        state_dict = load_file(safetensors_path, device=device)

        # Load config
        config_path = model_path / "config.json"
        with open(config_path, "r") as f:
            model_config = json.load(f)

        print(f"Model config: {model_config.get('model_type', 'unknown')}")
        print(f"Parameters: {sum(p.numel() for p in state_dict.values()) / 1e6:.1f}M")

        # Quantize each layer
        print("\n" + "=" * 60)
        print("Starting quantization...")
        print("=" * 60)

        self.quantized_state_dict = {}
        total_original_size = 0
        total_compressed_size = 0

        for name, param in tqdm(state_dict.items(), desc="Quantizing"):
            # Only quantize weight matrices, not biases or norms
            if len(param.shape) >= 2 and "weight" in name and param.numel() > 1024:
                quantized_layer = self.quantize_linear_layer(param, name)
                self.quantized_state_dict.update(quantized_layer)

                # Estimate compressed size
                b1_size = quantized_layer[f"{name}.b1"].numel() / 8  # 1 bit -> bytes
                b2_size = quantized_layer[f"{name}.b2"].numel() / 8
                scales_size = quantized_layer[f"{name}.scales"].numel() * 2  # FP16

                compressed_size = b1_size + b2_size + scales_size
                total_original_size += self.original_sizes[name]
                total_compressed_size += compressed_size
            else:
                # Keep small tensors and non-weights as-is (FP16)
                self.quantized_state_dict[name] = param.to(torch.float16)
                total_original_size += param.numel() * 2
                total_compressed_size += param.numel() * 2

        # Calculate overall compression
        overall_compression = total_original_size / total_compressed_size

        print("\n" + "=" * 60)
        print("Quantization Summary")
        print("=" * 60)
        print(f"Original model size: {total_original_size / 1024**2:.2f} MB")
        print(f"Compressed size: {total_compressed_size / 1024**2:.2f} MB")
        print(f"Overall compression ratio: {overall_compression:.2f}×")
        print(f"Effective bits per parameter: {16 / overall_compression:.2f}")

        # Save quantized model
        output_path.mkdir(parents=True, exist_ok=True)
        self.save_model(output_path, model_config)

        return {
            "original_size_mb": total_original_size / 1024**2,
            "compressed_size_mb": total_compressed_size / 1024**2,
            "compression_ratio": overall_compression,
            "bits_per_param": 16 / overall_compression,
        }

    def save_model(self, output_path: Path, model_config: Dict):
        """Save NANOQUANT model to disk"""
        print(f"\nSaving NANOQUANT model to {output_path}...")

        # Save quantized weights
        weights_path = output_path / "nanoquant_model.bin"
        torch.save(self.quantized_state_dict, weights_path)

        # Save metadata
        metadata = {
            "model_type": "nanoquant",
            "base_config": model_config,
            "quantization_config": {
                "rank": self.config.rank,
                "block_size": self.config.block_size,
                "admm_iters": self.config.admm_iters,
                "rho": self.config.rho,
            },
            "original_sizes": {k: int(v) for k, v in self.original_sizes.items()},
            "compression_ratios": {k: float(v) for k, v in self.compression_ratios.items()},
        }

        metadata_path = output_path / "nanoquant_config.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Model saved: {weights_path}")
        print(f"Config saved: {metadata_path}")

    def validate_model(
        self,
        model_path: str,
        num_samples: int = 5,
    ) -> Dict[str, float]:
        """
        Validate NANOQUANT model by comparing with original

        Returns validation metrics (MSE, relative error per layer)
        """
        model_path = Path(model_path)

        # Load original
        original_state = load_file(model_path / "model.safetensors")

        # Load quantized
        quantized_path = model_path / "nanoquant"
        with open(quantized_path / "nanoquant_config.json", "r") as f:
            metadata = json.load(f)

        quantized_state = torch.load(
            quantized_path / "nanoquant_model.bin",
            map_location="cpu",
        )

        print("\n" + "=" * 60)
        print("Validation Results")
        print("=" * 60)

        errors = {}
        for name in list(self.original_sizes.keys())[:num_samples]:
            if name in original_state:
                original = original_state[name]

                # Reconstruct from NANOQUANT
                b1 = quantized_state[f"{name}.b1"].float()
                b2 = quantized_state[f"{name}.b2"].float()
                scales = quantized_state[f"{name}.scales"]

                # Reconstruct
                reconstructed = (b1 @ b2.T) * scales.unsqueeze(1)

                # Calculate error
                mse = torch.mean((original - reconstructed) ** 2).item()
                rel_error = (torch.norm(original - reconstructed) / torch.norm(original)).item()

                errors[name] = {"mse": mse, "rel_error": rel_error}
                print(f"{name}:")
                print(f"  MSE: {mse:.6f}")
                print(f"  Relative error: {rel_error:.4f}")

        return errors


def main():
    """Main conversion script for Qwen3-0.6B"""
    import argparse

    parser = argparse.ArgumentParser(description="Convert models to NANOQUANT format")
    parser.add_argument(
        "--model-path",
        type=str,
        default="/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
        help="Path to HF model directory",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant",
        help="Output path for NANOQUANT model",
    )
    parser.add_argument("--rank", type=int, default=32, help="Decomposition rank")
    parser.add_argument("--block-size", type=int, default=128, help="Block size")
    parser.add_argument("--admm-iters", type=int, default=30, help="ADMM iterations")
    parser.add_argument("--validate", action="store_true", help="Run validation")

    args = parser.parse_args()

    # Create config
    config = NanoQuantConfig(
        rank=args.rank,
        block_size=args.block_size,
        admm_iters=args.admm_iters,
    )

    # Convert
    converter = NanoQuantConverter(config)
    stats = converter.convert_model(
        model_path=args.model_path,
        output_path=args.output_path,
    )

    # Validate if requested
    if args.validate:
        converter.validate_model(args.model_path)

    print("\n" + "=" * 60)
    print("Conversion complete!")
    print(f"Output: {args.output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
