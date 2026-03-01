"""
NANOQUANT Hybrid Quantization
Keep important layers in higher precision for better quality
"""

import torch
from pathlib import Path
from safetensors.torch import load_file
import json
from quantizer_improved import NanoQuantImproved


def quantize_hybrid(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-nanoquant-hybrid.gguf",
    base_rank: int = 128,
):
    """
    Hybrid quantization strategy:
    - Embeddings: Keep FP16 (critical for token representation)
    - LM Head: Keep FP16 (critical for output)
    - First 2 layers: Higher rank (256) - important for feature extraction
    - Last 2 layers: Higher rank (256) - important for output generation
    - Middle layers: Base rank (128)
    """
    print("=" * 60)
    print("NANOQUANT Hybrid Quantization")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")

    # Initialize quantizers with different ranks
    quantizer_high = NanoQuantImproved(rank=256, admm_iters=100, outlier_ratio=0.01)
    quantizer_base = NanoQuantImproved(rank=base_rank, admm_iters=100, outlier_ratio=0.005)

    quantized = {}
    total_params = 0
    compressed_params = 0

    for name, param in state_dict.items():
        # Always keep small tensors and non-weights
        if len(param.shape) < 2 or "weight" not in name or param.numel() < 1024:
            quantized[name] = {"type": "original", "data": param.cpu()}
            total_params += param.numel()
            compressed_params += param.numel()
            continue

        # Determine quantization strategy
        if "embed_tokens" in name or "lm_head" in name:
            # Critical layers - keep FP16
            print(f"  [FP16] {name}: {list(param.shape)}")
            quantized[name] = {"type": "original", "data": param.cpu()}
            total_params += param.numel()
            compressed_params += param.numel()

        elif "layers.0." in name or "layers.1." in name or \
             "layers.26." in name or "layers.27." in name:
            # First and last layers - high rank
            print(f"  [R256] {name}: {list(param.shape)}")
            result = quantizer_high.quantize_layer_with_calibration(param, layer_name=name)
            quantized[name] = {"type": "nanoquant_hybrid", "data": result}

            orig_params = param.numel()
            comp_params = result['B1'].numel() / 8 + result['B2'].numel() + result['scales'].numel()
            if 'outlier_values' in result:
                comp_params += result['outlier_values'].numel()
            total_params += orig_params
            compressed_params += comp_params

        else:
            # Middle layers - base rank
            print(f"  [R{base_rank}] {name}: {list(param.shape)}")
            result = quantizer_base.quantize_layer_with_calibration(param, layer_name=name)
            quantized[name] = {"type": "nanoquant_hybrid", "data": result}

            orig_params = param.numel()
            comp_params = result['B1'].numel() / 8 + result['B2'].numel() + result['scales'].numel()
            if 'outlier_values' in result:
                comp_params += result['outlier_values'].numel()
            total_params += orig_params
            compressed_params += comp_params

    print("\n" + "=" * 60)
    print("Quantization Complete")
    print("=" * 60)
    print(f"Original size: {total_params * 2 / 1024**2:.2f} MB")
    print(f"Compressed size: {compressed_params * 2 / 1024**2:.2f} MB")
    print(f"Overall compression: {total_params / compressed_params:.2f}×")

    print(f"\nSaving to {output_path}...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantized, output_path)
    print("Done!")


if __name__ == "__main__":
    quantize_hybrid()
