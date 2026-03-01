"""
NANOQUANT Multi-Bit Residual Approach

Key insight: Instead of one high-rank binary decomposition,
use multiple low-rank binary decompositions on successive residuals.

W ≈ λ₁*B₁@B₂ᵀ + λ₂*B₃@B₄ᵀ + λ₃*B₅@B₆ᵀ + ...

Each term is cheap (low-rank binary), sum gives high precision.
"""

import torch
from pathlib import Path
from safetensors.torch import load_file


class ResidualBinaryQuantizer:
    """
    Multi-bit quantization via successive binary decomposition.
    Each "bit" is actually a low-rank binary matrix pair.
    """

    def __init__(self, device="cpu"):
        self.device = device

    def _binary_decomposition(self, weight: torch.Tensor, rank: int, max_iter: int = 50) -> tuple:
        """
        Single binary decomposition using power iteration + quantization.
        Returns (B1, B2, scales) where B1, B2 are binary.
        """
        # Power iteration for initialization
        X = torch.randn(weight.shape[1], rank, device=weight.device, dtype=torch.float32)

        for _ in range(5):
            X = weight.T @ (weight @ X)
            # Gram-Schmidt orthogonalization (no LAPACK needed)
            for i in range(X.shape[1]):
                for j in range(i):
                    X[:, i] = X[:, i] - (X[:, i] @ X[:, j]) * X[:, j]
                norm = X[:, i].norm()
                if norm > 1e-8:
                    X[:, i] = X[:, i] / norm

        # Initialize B1, B2
        B1 = torch.sign(weight @ X)  # {-1, +1}
        B1[B1 == 0] = 1

        B2 = torch.sign(weight.T @ B1)  # {-1, +1}
        B2[B2 == 0] = 1

        # Simple alternating minimization (no LAPACK needed)
        for _ in range(max_iter):
            # Update B1: B1 = sign(W @ B2)
            B1 = torch.sign(weight @ B2)
            B1[B1 == 0] = 1

            # Update B2: B2 = sign(W.T @ B1)
            B2 = torch.sign(weight.T @ B1)
            B2[B2 == 0] = 1

        # Compute optimal scales per row
        reconstruction = B1 @ B2.T
        numerator = (weight * reconstruction).sum(dim=1)
        denominator = (reconstruction ** 2).sum(dim=1) + 1e-8
        scales = numerator / denominator

        return B1, B2, scales

    def quantize_layer(self, weight: torch.Tensor, num_terms: int = 3, rank: int = 64) -> dict:
        """
        Multi-bit quantization: W ≈ Σ λᵢ * B₁ᵢ @ B₂ᵢᵀ

        Args:
            weight: Weight matrix to quantize
            num_terms: Number of binary terms (effective "bits" of precision)
            rank: Rank of each binary decomposition
        """
        orig_shape = weight.shape
        if len(orig_shape) > 2:
            weight = weight.view(weight.size(0), -1)

        weight = weight.float().to(self.device)

        terms = []
        residual = weight.clone()

        for term_idx in range(num_terms):
            # Decompose residual
            B1, B2, scales = self._binary_decomposition(residual, rank)

            # Compute contribution
            contribution = scales.unsqueeze(1) * (B1 @ B2.T)

            # Store term
            terms.append({
                'B1': B1.half(),
                'B2': B2.half(),
                'scales': scales.half(),
            })

            # Update residual
            residual = residual - contribution

            # Check if residual is small enough
            residual_norm = residual.norm() / weight.norm()
            print(f"    Term {term_idx + 1}: residual norm = {residual_norm:.4f}")

            if residual_norm < 0.01:  # 1% residual, good enough
                break

        return {
            'terms': terms,
            'num_terms': len(terms),
            'rank': rank,
            'orig_shape': orig_shape,
        }


class ResidualLinear:
    """Linear layer with residual binary quantization"""

    def __init__(self, quantized_data: dict, bias=None):
        self.terms = quantized_data['terms']
        self.num_terms = quantized_data['num_terms']
        self.rank = quantized_data['rank']
        self.bias = bias.float() if bias is not None else None

        # Precompute dequantized weight
        self.weight = self._reconstruct_weight()

    def _reconstruct_weight(self):
        """Reconstruct weight from all terms"""
        weight = None
        for term in self.terms:
            B1 = term['B1'].float()
            B2 = term['B2'].float()
            scales = term['scales'].float()

            term_contrib = scales.unsqueeze(1) * (B1 @ B2.T)

            if weight is None:
                weight = term_contrib
            else:
                weight = weight + term_contrib

        if weight is None:
            raise ValueError("No terms provided for reconstruction")

        return weight

    def forward(self, x):
        if self.weight is None:
            raise ValueError("Weight not initialized")
        original_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])
        output = torch.matmul(x_2d, self.weight.T)
        if self.bias is not None:
            output = output + self.bias
        return output.reshape(*original_shape[:-1], self.weight.shape[0])


def quantize_residual(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    num_terms: int = 3,
    rank: int = 64,
    output_path: str = "models/qwen3-0.6b-residual-3term.gguf",
):
    """Quantize using residual binary decomposition"""
    print("=" * 60)
    print(f"Residual Binary Quantization ({num_terms} terms, rank {rank})")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = ResidualBinaryQuantizer()

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

        result = quantizer.quantize_layer(param, num_terms=num_terms, rank=rank)
        quantized[name] = {"type": "residual", "data": result}

        # Calculate compression
        orig_size = param.numel() * 2  # FP16
        # Each term: B1 (1 bit/elem), B2 (1 bit/elem), scales (2 bytes/row)
        actual_terms = result['num_terms']
        comp_size = param.numel() * 2 * actual_terms / 8 + param.shape[0] * 2 * actual_terms

        total_orig += orig_size
        total_comp += comp_size

        ratio = orig_size / comp_size
        print(f"    Terms used: {actual_terms}")
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
    # Try 5 terms, rank 128 for better quality
    quantize_residual(num_terms=5, rank=128, output_path="models/qwen3-0.6b-residual-5term-r128.gguf")
