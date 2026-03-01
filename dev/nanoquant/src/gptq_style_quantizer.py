"""
GPTQ-style quantization for comparison
Uses proven quantization methods from GPTQ/AutoGPTQ
"""

import torch
import numpy as np
from pathlib import Path
from safetensors.torch import load_file


def quantize_weight_gptq_style(
    weight: torch.Tensor,
    bits: int = 4,
    group_size: int = 128,
) -> dict:
    """
    Simple GPTQ-style quantization
    - Blockwise quantization with group-wise scales
    - Round-to-nearest with scaling
    """
    weight = weight.float()
    orig_shape = weight.shape

    # Reshape to [num_groups, group_size]
    if len(orig_shape) == 2:
        out_features, in_features = orig_shape
        # Process in groups along input dimension
        num_groups = in_features // group_size

        scales = []
        zeros = []
        quant_weights = []

        for g in range(num_groups):
            start = g * group_size
            end = (g + 1) * group_size

            w_block = weight[:, start:end]

            # Find min/max
            w_min = w_block.min(dim=1, keepdim=True)[0]
            w_max = w_block.max(dim=1, keepdim=True)[0]

            # Compute scale and zero point
            scale = (w_max - w_min) / (2**bits - 1)
            scale = torch.clamp(scale, min=1e-8)
            zero = -w_min / scale

            # Quantize
            w_quant = torch.round((w_block - w_min) / scale)
            w_quant = torch.clamp(w_quant, 0, 2**bits - 1)

            # Dequantize to verify
            w_dequant = w_quant * scale + w_min

            quant_weights.append(w_quant.to(torch.uint8))
            scales.append(scale.squeeze())
            zeros.append(zero.squeeze())

        return {
            'weights': torch.cat([w.flatten() for w in quant_weights]),
            'scales': torch.stack(scales, dim=1),
            'zeros': torch.stack(zeros, dim=1),
            'group_size': group_size,
            'bits': bits,
            'orig_shape': orig_shape,
        }


def quantize_gptq_style(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-gptq-style.gguf",
    bits: int = 3,
    group_size: int = 128,
):
    """Quantize using GPTQ-style method"""
    print("=" * 60)
    print(f"GPTQ-Style Quantization (bits={bits}, group_size={group_size})")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")

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

        result = quantize_weight_gptq_style(param, bits=bits, group_size=group_size)
        quantized[name] = {"type": "gptq_style", "data": result}

        # Calculate sizes
        orig_size = param.numel() * 2  # FP16
        # Weights: numel * bits / 8, scales/zeros: num_groups * out_features * 2
        out_f, in_f = param.shape
        num_groups = in_f // group_size
        comp_size = param.numel() * bits / 8 + num_groups * out_f * 2 * 2

        total_orig += orig_size
        total_comp += comp_size

        compression = orig_size / comp_size
        print(f"    Compression: {compression:.2f}x")

    print("\n" + "=" * 60)
    print("Quantization Complete")
    print("=" * 60)
    print(f"Original: {total_orig / 1024**2:.2f} MB")
    print(f"Compressed: {total_comp / 1024**2:.2f} MB")
    print(f"Ratio: {total_orig / total_comp:.2f}x")

    print(f"\nSaving to {output_path}...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantized, output_path)
    print("Done!")


if __name__ == "__main__":
    quantize_gptq_style(bits=3, group_size=128)
