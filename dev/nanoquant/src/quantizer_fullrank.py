"""
NANOQUANT Full-Rank Approach
Use full or near-full rank with quantized components
Key insight: B1 binary + B2 int4 with full rank = good quality + compression
"""

import torch
import numpy as np
from pathlib import Path
from safetensors.torch import load_file


class FullRankBinaryQuantizer:
    """
    Use full-rank binary decomposition:
    W ≈ scales * sign(W) @ (abs(W) quantized to 4-bit)^T

    This is essentially separating sign and magnitude,
    then quantizing magnitude.
    """

    def __init__(self, device="cpu"):
        self.device = device

    def quantize_layer(self, weight: torch.Tensor, num_bits: int = 4) -> dict:
        """Quantize using sign-magnitude separation"""
        orig_shape = weight.shape

        if len(orig_shape) > 2:
            weight = weight.view(weight.size(0), -1)

        weight = weight.float().to(self.device)
        out_f, in_f = weight.shape

        # Method: W = sign(W) * |W|
        # Quantize: B1 = sign(W), B2 = quantize(|W|), scales = per-channel

        # Extract sign (binary)
        B1 = torch.sign(weight)  # {-1, +1}
        B1[B1 == 0] = 1

        # Extract magnitude
        magnitude = torch.abs(weight)

        # Quantize magnitude per-row to num_bits
        w_min = magnitude.min(dim=1, keepdim=True)[0]
        w_max = magnitude.max(dim=1, keepdim=True)[0]

        scale_mag = (w_max - w_min) / (2**num_bits - 1)
        scale_mag = torch.clamp(scale_mag, min=1e-8)

        # Quantize magnitude
        magnitude_quant = torch.round((magnitude - w_min) / scale_mag)
        magnitude_quant = torch.clamp(magnitude_quant, 0, 2**num_bits - 1).to(torch.uint8)

        # Store dequantized magnitude for reconstruction
        magnitude_dequant = magnitude_quant.float() * scale_mag + w_min

        # Compute optimal scales for final reconstruction
        # W ≈ diag(scales) * B1 * magnitude_dequant
        reconstruction = B1 * magnitude_dequant
        numerator = (weight * reconstruction).sum(dim=1)
        denominator = (reconstruction ** 2).sum(dim=1) + 1e-8
        scales = numerator / denominator

        return {
            'B1': B1.half(),  # Binary stored as FP16 (can be packed to 1-bit)
            'magnitude_quant': magnitude_quant,  # uint8, num_bits actual
            'magnitude_scale': scale_mag.squeeze().half(),
            'magnitude_zero': w_min.squeeze().half(),
            'scales': scales.half(),
            'num_bits': num_bits,
            'orig_shape': orig_shape,
        }


def quantize_sign_magnitude(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-sign-magnitude-4bit.gguf",
    num_bits: int = 4,
):
    """Quantize using sign-magnitude decomposition"""
    print("=" * 60)
    print(f"Sign-Magnitude Quantization ({num_bits}-bit magnitude)")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = FullRankBinaryQuantizer()

    quantized = {}
    total_orig = 0
    total_comp = 0

    for name, param in state_dict.items():
        if len(param.shape) < 2 or "weight" not in name or param.numel() < 1024:
            quantized[name] = {"type": "original", "data": param.cpu()}
            total_orig += param.numel() * 2
            total_comp += param.numel() * 2
            continue

        print(f"  Quantizing {name}: {list(param.shape)}")

        result = quantizer.quantize_layer(param, num_bits=num_bits)
        quantized[name] = {"type": "sign_magnitude", "data": result}

        # Calculate compression
        orig_size = param.numel() * 2  # FP16
        # B1: 1 bit per element (but stored as FP16 for now)
        # magnitude_quant: num_bits per element
        # scales: 2 bytes per row
        comp_size = param.numel() * (1 + num_bits) / 8 + param.shape[0] * 6

        total_orig += orig_size
        total_comp += comp_size

        ratio = orig_size / comp_size
        print(f"    Compression: {ratio:.2f}x")

    print("\n" + "=" * 60)
    print("Quantization Complete")
    print("=" * 60)
    print(f"Original: {total_orig / 1024**2:.2f} MB")
    print(f"Compressed: {total_comp / 1024**2:.2f} MB")
    print(f"Ratio: {total_orig / total_comp:.2f}x")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantized, output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    # Try with 4-bit magnitude
    quantize_sign_magnitude(num_bits=4)
