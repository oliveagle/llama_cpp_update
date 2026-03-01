"""
NANOQUANT 2-bit Approach

Instead of binary {-1, +1}, use 2-bit with 4 levels.
This gives more representational power while still having good compression.

Levels: {-1.5, -0.5, +0.5, +1.5} or learned via k-means
"""

import torch
from pathlib import Path
from safetensors.torch import load_file


class TwoBitQuantizer:
    """
    2-bit quantization with 4 levels.
    Uses similar structure to NANOQUANT but with more precision.
    """

    def __init__(self, device="cpu"):
        self.device = device

    def _quantize_2bit(self, weight: torch.Tensor, block_size: int = 128) -> dict:
        """
        Block-wise 2-bit quantization with learned scales.

        For each block:
        - Find 4 optimal centroids (k-means style)
        - Quantize to nearest centroid
        - Store indices (2 bits each) + centroids
        """
        orig_shape = weight.shape
        out_f, in_f = weight.shape

        # Pad to multiple of block_size
        pad_in = (block_size - in_f % block_size) % block_size
        if pad_in > 0:
            weight_padded = torch.nn.functional.pad(weight, (0, pad_in))
        else:
            weight_padded = weight

        num_blocks = weight_padded.shape[1] // block_size

        # Reshape to [out_f, num_blocks, block_size]
        weight_blocks = weight_padded.reshape(out_f, num_blocks, block_size)

        # For each row, find optimal 4 centroids using k-means
        all_centroids = []
        all_indices = []

        for row_idx in range(out_f):
            row_blocks = weight_blocks[row_idx]  # [num_blocks, block_size]

            # Flatten all values in this row
            flat_values = row_blocks.reshape(-1)

            # K-means with 4 centroids (simplified: use percentiles)
            sorted_vals = torch.sort(flat_values)[0]
            n = len(sorted_vals)
            centroids = torch.tensor([
                sorted_vals[n // 8].item(),      # 12.5th percentile
                sorted_vals[3 * n // 8].item(),  # 37.5th percentile
                sorted_vals[5 * n // 8].item(),  # 62.5th percentile
                sorted_vals[7 * n // 8].item(),  # 87.5th percentile
            ], device=weight.device)

            # Find nearest centroid for each value
            distances = torch.abs(flat_values.unsqueeze(1) - centroids.unsqueeze(0))
            indices = torch.argmin(distances, dim=1).to(torch.uint8)  # 0, 1, 2, 3

            # Refine centroids based on assignments
            for _ in range(5):  # 5 iterations
                for c in range(4):
                    mask = indices == c
                    if mask.any():
                        centroids[c] = flat_values[mask].mean()

                # Reassign
                distances = torch.abs(flat_values.unsqueeze(1) - centroids.unsqueeze(0))
                indices = torch.argmin(distances, dim=1).to(torch.uint8)

            all_centroids.append(centroids)

            # Reshape indices back to blocks
            indices_blocks = indices.reshape(num_blocks, block_size)
            all_indices.append(indices_blocks)

        centroids_tensor = torch.stack(all_centroids)  # [out_f, 4]
        indices_tensor = torch.stack(all_indices)  # [out_f, num_blocks, block_size]

        return {
            'centroids': centroids_tensor.half(),
            'indices': indices_tensor,  # uint8, but only uses 2 bits per value
            'block_size': block_size,
            'orig_shape': orig_shape,
        }

    def quantize_layer(self, weight: torch.Tensor, block_size: int = 128) -> dict:
        """Quantize layer with 2-bit precision"""
        orig_shape = weight.shape

        if len(orig_shape) > 2:
            weight = weight.view(weight.size(0), -1)

        weight = weight.float().to(self.device)

        result = self._quantize_2bit(weight, block_size)
        result['orig_shape'] = orig_shape

        # Calculate reconstruction error
        reconstructed = self._reconstruct(result)
        error = (weight - reconstructed).norm() / weight.norm()
        print(f"    Reconstruction error: {error:.4f}")

        return result

    def _reconstruct(self, quantized: dict) -> torch.Tensor:
        """Reconstruct weight from 2-bit quantization"""
        centroids = quantized['centroids'].float()
        indices = quantized['indices'].long()
        block_size = quantized['block_size']

        out_f = centroids.shape[0]
        num_blocks, block_size_actual = indices.shape[1], indices.shape[2]

        # Gather centroids based on indices
        # indices: [out_f, num_blocks, block_size]
        # centroids: [out_f, 4]
        reconstructed = torch.gather(
            centroids.unsqueeze(1).unsqueeze(2).expand(-1, num_blocks, block_size_actual, -1),
            3,
            indices.unsqueeze(-1)
        ).squeeze(-1)

        return reconstructed.reshape(out_f, -1)


class TwoBitLinear:
    """Linear layer with 2-bit weights"""

    def __init__(self, quantized_data: dict, bias=None):
        self.quantized = quantized_data
        self.bias = bias.float() if bias is not None else None
        self.out_features = quantized_data['centroids'].shape[0]

        # Precompute full weight
        self.weight = self._reconstruct_weight()

    def _reconstruct_weight(self):
        """Reconstruct weight from 2-bit quantization"""
        centroids = self.quantized['centroids'].float()
        indices = self.quantized['indices'].long()

        out_f = centroids.shape[0]
        num_blocks = indices.shape[0] // out_f if len(indices.shape) == 2 else indices.shape[1]
        block_size = indices.shape[-1]

        # Handle different index shapes
        if len(indices.shape) == 3:
            # indices: [out_f, num_blocks, block_size]
            reconstructed = torch.gather(
                centroids.unsqueeze(1).unsqueeze(2).expand(-1, num_blocks, block_size, -1),
                3,
                indices.unsqueeze(-1)
            ).squeeze(-1)
            return reconstructed.reshape(out_f, -1)
        else:
            # Flattened indices
            indices_flat = indices.reshape(-1)
            reconstructed = centroids.reshape(-1, 4)[torch.arange(len(centroids)).repeat_interleave(len(indices_flat) // len(centroids)), indices_flat]
            return reconstructed.reshape(out_f, -1)

    def forward(self, x):
        original_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])
        output = torch.matmul(x_2d, self.weight.T)
        if self.bias is not None:
            output = output + self.bias
        return output.reshape(*original_shape[:-1], self.out_features)


def quantize_2bit(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-2bit.gguf",
    block_size: int = 128,
):
    """Quantize using 2-bit block-wise quantization"""
    print("=" * 60)
    print(f"2-bit Block-wise Quantization (block_size={block_size})")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = TwoBitQuantizer()

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

        result = quantizer.quantize_layer(param, block_size=block_size)
        quantized[name] = {"type": "2bit", "data": result}

        # Calculate compression
        orig_size = param.numel() * 2  # FP16
        # Indices: 2 bits per element = 0.25 bytes per element
        # Centroids: 4 floats per row = 8 bytes per row
        out_f = param.shape[0]
        comp_size = param.numel() * 0.25 + out_f * 8

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
    quantize_2bit()
