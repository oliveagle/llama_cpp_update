"""
Ternary Quantization (BitNet b1.58 style)
Uses {-1, 0, +1} instead of binary {-1, +1}
This is the actual "1.58-bit" quantization from the BitNet paper
"""

import torch
import numpy as np
from pathlib import Path
from safetensors.torch import load_file
from typing import Tuple


class TernaryQuantizer:
    """
    Ternary quantization: W ≈ scales * (B1 @ B2^T)
    where B1 ∈ {-1, 0, +1} (ternary)
    B2 is low-rank continuous
    """

    def __init__(
        self,
        rank: int = 512,  # Much higher rank for better quality
        num_iters: int = 100,
        device: str = "cpu",
    ):
        self.rank = rank
        self.num_iters = num_iters
        self.device = device

    def quantize_layer(self, weight: torch.Tensor) -> dict:
        """Quantize a layer using ternary decomposition"""
        orig_shape = weight.shape

        if len(orig_shape) > 2:
            weight = weight.view(weight.size(0), -1)

        weight = weight.float().to(self.device)
        out_f, in_f = weight.shape
        rank = min(self.rank, out_f, in_f)

        # Initialize with SVD
        try:
            U, S, Vh = torch.linalg.svd(weight, full_matrices=False)
            U_r = U[:, :rank]
            V_r = Vh[:rank, :].T

            # Initialize B1 as ternary (keep values with |U_r| > 0.5)
            B1 = torch.sign(U_r)
            B1[torch.abs(U_r) < 0.5] = 0

            B2 = V_r * torch.sqrt(S[:rank]).unsqueeze(0)
        except:
            B1 = (torch.randn(out_f, rank, device=self.device) > 0).float() * 2 - 1
            B1[torch.rand_like(B1) < 0.6] = 0  # 60% zeros
            B2 = torch.randn(in_f, rank, device=self.device) / np.sqrt(rank)

        # Iterative refinement
        for _ in range(self.num_iters):
            # Fix B1, optimize B2
            B2 = self._optimize_B2(weight, B1, B2)

            # Fix B2, update B1 (ternary)
            B1 = self._update_B1_ternary(weight, B1, B2)

        # Compute optimal scales
        reconstruction = B1 @ B2.T
        numerator = (weight * reconstruction).sum(dim=1)
        denominator = (reconstruction ** 2).sum(dim=1) + 1e-8
        scales = numerator / denominator

        # Pack B1 efficiently (2 bits per element: 00=-1, 01=0, 10=+1)
        B1_packed = self._pack_ternary(B1)

        return {
            'B1_packed': B1_packed,
            'B1_shape': B1.shape,
            'B2': B2.half(),  # FP16
            'scales': scales.half(),
            'orig_shape': orig_shape,
        }

    def _optimize_B2(self, W: torch.Tensor, B1: torch.Tensor, B2: torch.Tensor) -> torch.Tensor:
        """Optimize B2 given fixed B1"""
        # Solve: minimize ||W - diag(scales) @ B1 @ B2^T||^2
        # For now, simple least squares without scales
        B1_T_B1 = B1.T @ B1
        B1_T_W = B1.T @ W

        try:
            B2_T = torch.linalg.solve(B1_T_B1 + 0.01 * torch.eye(B1.shape[1], device=W.device), B1_T_W)
            return B2_T.T
        except:
            return B2

    def _update_B1_ternary(self, W: torch.Tensor, B1: torch.Tensor, B2: torch.Tensor) -> torch.Tensor:
        """Update B1 with ternary constraint"""
        # Gradient: dL/dB1 = -2 * (W - B1 @ B2^T) @ B2
        residual = W - B1 @ B2.T
        grad = -2 * residual @ B2

        # Ternary projection with threshold
        B1_new = torch.sign(grad)
        B1_new[torch.abs(grad) < 0.5] = 0  # Fixed threshold for sparsity

        # Ensure at least some non-zeros per row
        row_has_nonzero = (B1_new != 0).any(dim=1, keepdim=True)
        B1 = torch.where(row_has_nonzero, B1_new, B1)

        return B1

    def _pack_ternary(self, B1: torch.Tensor) -> torch.Tensor:
        """Pack ternary values: 2 bits per element"""
        # Map: -1 -> 0, 0 -> 1, +1 -> 2
        B1_mapped = (B1 + 1).long()  # -1->0, 0->1, +1->2

        # Pack 4 values into 1 byte
        flat = B1_mapped.flatten()
        padding = (4 - len(flat) % 4) % 4
        flat = torch.cat([flat, torch.zeros(padding, dtype=flat.dtype, device=flat.device)])

        packed = torch.zeros(len(flat) // 4, dtype=torch.uint8, device=flat.device)
        for i in range(4):
            packed |= (flat[i::4] << (2 * i)).to(torch.uint8)

        return packed.cpu()


def quantize_ternary(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-ternary-r512.gguf",
    rank: int = 512,
):
    """Quantize using ternary decomposition"""
    print("=" * 60)
    print(f"Ternary Quantization (rank={rank})")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")

    quantizer = TernaryQuantizer(rank=rank, num_iters=50)

    quantized = {}
    total_params = 0
    compressed_params = 0

    for name, param in state_dict.items():
        if len(param.shape) < 2 or "weight" not in name or param.numel() < 1024:
            quantized[name] = {"type": "original", "data": param.cpu()}
            continue

        print(f"  Quantizing {name}: {list(param.shape)}")

        result = quantizer.quantize_layer(param)
        quantized[name] = {"type": "ternary", "data": result}

        # Calculate compression
        orig_params = param.numel()
        # B1: 2 bits per element
        # B2: FP16
        # scales: FP16
        b1_bits = result['B1_packed'].numel() * 8  # In bits
        comp_params = b1_bits / 16 + result['B2'].numel() + result['scales'].numel()

        total_params += orig_params
        compressed_params += comp_params

        ratio = orig_params / comp_params
        print(f"    Compression: {ratio:.2f}×")

    print("\n" + "=" * 60)
    print("Quantization Complete")
    print("=" * 60)
    print(f"Original: {total_params * 2 / 1024**2:.2f} MB")
    print(f"Compressed: {compressed_params * 2 / 1024**2:.2f} MB")
    print(f"Ratio: {total_params / compressed_params:.2f}×")

    print(f"\nSaving to {output_path}...")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(quantized, output_path)
    print("Done!")


if __name__ == "__main__":
    quantize_ternary(rank=512)
