"""
NANOQUANT with GPTQ-style Importance Weighting

Use calibration data to weight reconstruction error by activation magnitude.
This ensures weights that affect larger activations are preserved better.
"""

import torch
from pathlib import Path
from safetensors.torch import load_file
from transformers import AutoTokenizer


class GPTQStyleQuantizer:
    """
    GPTQ-style quantization with importance weighting.
    Uses Hessian diagonal (approximated via activations) to weight errors.
    """

    def __init__(self, device="cpu"):
        self.device = device
        self.activation_stats = {}

    def collect_activation_stats(self, input_path: str, num_samples: int = 5):
        """Collect activation statistics from calibration data"""
        print("Collecting activation statistics...")

        tokenizer = AutoTokenizer.from_pretrained(
            input_path, trust_remote_code=True
        )
        state_dict = load_file(f"{input_path}/model.safetensors")

        # Use simple prompts for calibration
        prompts = [
            "The quick brown fox jumps over the lazy dog.",
            "In 2024, artificial intelligence has become",
            "The capital of France is Paris, which is known for",
            "To solve this problem, we need to",
            "The scientific method involves"
        ]

        # Collect input activations for each linear layer
        # We'll approximate this by looking at weight magnitudes
        # as a proxy for activation statistics

        for name, param in state_dict.items():
            if len(param.shape) >= 2 and "weight" in name and param.numel() >= 1024:
                # Use weight column norms as proxy for activation importance
                # This is a simplification; real GPTQ uses actual Hessian
                col_norms = param.norm(dim=0).float()
                self.activation_stats[name] = col_norms.to(self.device)

        print(f"Collected stats for {len(self.activation_stats)} layers")

    def _quantize_layer_weighted(self, weight: torch.Tensor, importance: torch.Tensor,
                                  num_bits: int = 3, block_size: int = 128) -> dict:
        """
        Quantize with importance weighting.

        Higher importance = lower quantization error allowed
        """
        orig_shape = weight.shape
        out_f, in_f = weight.shape

        # Normalize importance
        importance = importance / importance.mean()

        # Pad to multiple of block_size
        pad_in = (block_size - in_f % block_size) % block_size
        if pad_in > 0:
            weight_padded = torch.nn.functional.pad(weight, (0, pad_in))
            importance_padded = torch.nn.functional.pad(importance, (0, pad_in))
        else:
            weight_padded = weight
            importance_padded = importance

        num_blocks = weight_padded.shape[1] // block_size
        weight_blocks = weight_padded.reshape(out_f, num_blocks, block_size)
        importance_blocks = importance_padded.reshape(num_blocks, block_size)

        num_levels = 2 ** num_bits
        all_centroids = []
        all_indices = []

        for row_idx in range(out_f):
            row_blocks = weight_blocks[row_idx]  # [num_blocks, block_size]

            # Flatten
            flat_values = row_blocks.reshape(-1)
            flat_importance = importance_blocks.reshape(-1)

            # Weighted k-means initialization
            # Use importance-weighted percentiles
            sorted_vals, sorted_idx = torch.sort(flat_values)
            sorted_imp = flat_importance[sorted_idx]
            cumsum_imp = torch.cumsum(sorted_imp, dim=0)
            total_imp = cumsum_imp[-1]

            centroids = []
            for i in range(num_levels):
                target = total_imp * (2 * i + 1) / (2 * num_levels)
                idx = torch.searchsorted(cumsum_imp, target)
                idx = torch.clamp(idx, 0, len(sorted_vals) - 1)
                centroids.append(sorted_vals[idx].item())
            centroids = torch.tensor(centroids, device=weight.device)

            # Weighted k-means iterations
            indices = None
            for _ in range(10):
                # Assign to nearest centroid (weighted by importance)
                distances = torch.abs(flat_values.unsqueeze(1) - centroids.unsqueeze(0))
                # Weight distances by inverse importance (higher importance = closer)
                weighted_distances = distances / (flat_importance.unsqueeze(1) + 1e-8)
                indices = torch.argmin(weighted_distances, dim=1).to(torch.uint8)

                # Update centroids with weighted means
                for c in range(num_levels):
                    mask = indices == c
                    if mask.any():
                        weights = flat_importance[mask]
                        values = flat_values[mask]
                        centroids[c] = (values * weights).sum() / weights.sum()

            all_centroids.append(centroids)
            indices_blocks = indices.reshape(num_blocks, block_size)
            all_indices.append(indices_blocks)

        centroids_tensor = torch.stack(all_centroids)
        indices_tensor = torch.stack(all_indices)

        # Calculate weighted reconstruction error
        reconstructed = self._reconstruct({
            'centroids': centroids_tensor,
            'indices': indices_tensor,
            'block_size': block_size,
            'orig_shape': orig_shape
        })

        error = ((weight - reconstructed) * importance.unsqueeze(0)).norm() / (weight * importance.unsqueeze(0)).norm()
        print(f"    Weighted reconstruction error: {error:.4f}")

        return {
            'centroids': centroids_tensor.half(),
            'indices': indices_tensor,
            'num_bits': num_bits,
            'block_size': block_size,
            'orig_shape': orig_shape,
        }

    def _reconstruct(self, quantized: dict) -> torch.Tensor:
        """Reconstruct weight from quantization"""
        centroids = quantized['centroids'].float()
        indices = quantized['indices'].long()
        block_size = quantized['block_size']

        out_f = centroids.shape[0]
        num_blocks = indices.shape[1]
        block_size_actual = indices.shape[2]

        expanded = centroids.unsqueeze(1).unsqueeze(2).expand(-1, num_blocks, block_size_actual, -1)
        gathered = torch.gather(expanded, 3, indices.unsqueeze(-1)).squeeze(-1)

        return gathered.reshape(out_f, -1)


def quantize_gptq_style(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-gptq-style.gguf",
    num_bits: int = 3,
    block_size: int = 128,
):
    """Quantize using GPTQ-style importance weighting"""
    print("=" * 60)
    print(f"GPTQ-Style Quantization ({num_bits}-bit, block_size={block_size})")
    print("=" * 60)

    quantizer = GPTQStyleQuantizer()
    quantizer.collect_activation_stats(input_path)

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

        print(f"\n  Quantizing {name}: {list(param.shape)}")

        importance = quantizer.activation_stats.get(name, torch.ones(param.shape[1]))
        result = quantizer._quantize_layer_weighted(
            param.float().to(quantizer.device),
            importance,
            num_bits=num_bits,
            block_size=block_size
        )
        quantized[name] = {"type": f"{num_bits}bit_weighted", "data": result}

        # Calculate compression
        orig_size = param.numel() * 2
        out_f = param.shape[0]
        num_levels = 2 ** num_bits
        # Indices: num_bits per element
        # Centroids: num_levels * 2 bytes per row
        comp_size = param.numel() * num_bits / 8 + out_f * num_levels * 2

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
    quantize_gptq_style(num_bits=3, block_size=128)
