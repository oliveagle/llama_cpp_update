"""
NANOQUANT Selective Quantization

Keep first and last layers in FP16, quantize middle layers.
This prevents error accumulation at the input and output.
"""

import torch
from pathlib import Path
from safetensors.torch import load_file


class SelectiveQuantizer:
    """Quantize only selected layers, keep others in FP16"""

    def __init__(self, device="cpu"):
        self.device = device

    def _quantize_2bit(self, weight: torch.Tensor, block_size: int = 128) -> dict:
        """Block-wise 2-bit quantization"""
        orig_shape = weight.shape
        out_f, in_f = weight.shape

        pad_in = (block_size - in_f % block_size) % block_size
        if pad_in > 0:
            weight_padded = torch.nn.functional.pad(weight, (0, pad_in))
        else:
            weight_padded = weight

        num_blocks = weight_padded.shape[1] // block_size
        weight_blocks = weight_padded.reshape(out_f, num_blocks, block_size)

        all_centroids = []
        all_indices = []

        for row_idx in range(out_f):
            row_blocks = weight_blocks[row_idx]
            flat_values = row_blocks.reshape(-1)

            sorted_vals = torch.sort(flat_values)[0]
            n = len(sorted_vals)
            centroids = torch.tensor([
                sorted_vals[n // 8].item(),
                sorted_vals[3 * n // 8].item(),
                sorted_vals[5 * n // 8].item(),
                sorted_vals[7 * n // 8].item(),
            ], device=weight.device)

            distances = torch.abs(flat_values.unsqueeze(1) - centroids.unsqueeze(0))
            indices = torch.argmin(distances, dim=1).to(torch.uint8)

            for _ in range(5):
                for c in range(4):
                    mask = indices == c
                    if mask.any():
                        centroids[c] = flat_values[mask].mean()
                distances = torch.abs(flat_values.unsqueeze(1) - centroids.unsqueeze(0))
                indices = torch.argmin(distances, dim=1).to(torch.uint8)

            all_centroids.append(centroids)
            indices_blocks = indices.reshape(num_blocks, block_size)
            all_indices.append(indices_blocks)

        centroids_tensor = torch.stack(all_centroids)
        indices_tensor = torch.stack(all_indices)

        return {
            'centroids': centroids_tensor.half(),
            'indices': indices_tensor,
            'block_size': block_size,
            'orig_shape': orig_shape,
        }

    def should_quantize(self, name: str, keep_first_n: int = 4, keep_last_n: int = 4) -> bool:
        """Determine if a layer should be quantized based on its position"""
        # Extract layer number if it's a transformer layer
        if "model.layers." in name:
            parts = name.split(".")
            try:
                layer_idx = int(parts[2])
                # Don't quantize first N and last N layers
                if layer_idx < keep_first_n or layer_idx >= (28 - keep_last_n):
                    return False
            except (ValueError, IndexError):
                pass

        # Always keep embeddings and LM head in FP16
        if "embed_tokens" in name or "lm_head" in name:
            return False

        return True


def quantize_selective(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-selective.gguf",
    block_size: int = 128,
    keep_first_n: int = 4,
    keep_last_n: int = 4,
):
    """Quantize with selective layer preservation"""
    print("=" * 60)
    print(f"Selective Quantization (keep first {keep_first_n}, last {keep_last_n} in FP16)")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = SelectiveQuantizer()

    quantized = {}
    total_orig = 0
    total_comp = 0
    num_quantized = 0
    num_fp16 = 0

    for name, param in state_dict.items():
        if len(param.shape) < 2 or "weight" not in name or param.numel() < 1024:
            quantized[name] = {"type": "original", "data": param.cpu()}
            total_orig += param.numel() * 2
            total_comp += param.numel() * 2
            continue

        should_q = quantizer.should_quantize(name, keep_first_n, keep_last_n)

        if should_q:
            print(f"  [Q] Quantizing {name}: {list(param.shape)}")
            result = quantizer._quantize_2bit(param.float().to(quantizer.device), block_size)
            quantized[name] = {"type": "2bit", "data": result}

            orig_size = param.numel() * 2
            out_f = param.shape[0]
            comp_size = param.numel() * 0.25 + out_f * 8

            total_orig += orig_size
            total_comp += comp_size
            num_quantized += 1
            print(f"      Compressed: {orig_size / comp_size:.2f}x")
        else:
            print(f"  [F] Keeping FP16 {name}: {list(param.shape)}")
            quantized[name] = {"type": "original", "data": param.cpu()}
            total_orig += param.numel() * 2
            total_comp += param.numel() * 2
            num_fp16 += 1

    print("\n" + "=" * 60)
    print("Quantization Complete")
    print("=" * 60)
    print(f"Layers quantized: {num_quantized}")
    print(f"Layers FP16: {num_fp16}")
    print(f"Original: {total_orig / 1024**2:.2f} MB")
    print(f"Compressed: {total_comp / 1024**2:.2f} MB")
    print(f"Ratio: {total_orig / total_comp:.2f}x")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantized, output_path)
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    quantize_selective(keep_first_n=4, keep_last_n=4)
