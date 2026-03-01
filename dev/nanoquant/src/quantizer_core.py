"""
NANOQUANT - Simplified Implementation
Based on: "NanoQuant: Efficient Sub-1-Bit Quantization of Large Language Models"
arXiv:2602.06694v1

Core algorithm: Binary decomposition with low-rank factorization
"""

import torch
import numpy as np
from typing import Tuple, Dict


class NanoQuantConfig:
    """Configuration for NANOQUANT quantization"""
    def __init__(
        self,
        rank: int = 32,           # Low-rank decomposition rank
        block_size: int = 128,     # Block size for grouping
        num_bits_direction: int = 1,  # Bits for direction (binary)
        scale_bits: int = 8,       # Bits for scales (FP8 or INT8)
        use_admm: bool = True,     # Use ADMM optimization
        admm_iters: int = 50,      # ADMM iterations
        rho: float = 0.01,         # ADMM penalty parameter
    ):
        self.rank = rank
        self.block_size = block_size
        self.num_bits_direction = num_bits_direction
        self.scale_bits = scale_bits
        self.use_admm = use_admm
        self.admm_iters = admm_iters
        self.rho = rho


def binary_decomposition_admm(
    weight: torch.Tensor,
    rank: int,
    num_iters: int = 50,
    rho: float = 0.01,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Binary decomposition using ADMM (Alternating Direction Method of Multipliers)

    Decomposes weight matrix W into:
        W ≈ diag(scales) @ (B1 @ B2^T)

    where:
        - B1 is binary matrix [out_features, rank] with values {-1, +1}
        - B2 is continuous matrix [in_features, rank]
        - scales is vector [out_features]

    Args:
        weight: Input weight matrix [out_features, in_features]
        rank: Rank for low-rank decomposition
        num_iters: Number of ADMM iterations
        rho: ADMM penalty parameter

    Returns:
        B1: Binary matrix [out_features, rank]
        B2: Matrix [in_features, rank]
        scales: Scaling factors [out_features]
    """
    out_features, in_features = weight.shape
    device = weight.device

    # Convert to float32 for computation
    weight = weight.float()

    # Initialize B2 with SVD for better starting point
    try:
        U, S, Vh = torch.linalg.svd(weight, full_matrices=False)
        # Take top-r singular values
        U_r = U[:, :rank]  # [out_features, rank]
        S_r = S[:rank]     # [rank]
        V_r = Vh[:rank, :].T  # [in_features, rank]

        # Initialize B1 as binary from U_r, B2 from V_r scaled by singular values
        B1 = torch.sign(U_r)
        B1[B1 == 0] = 1

        # B2 gets the magnitude information
        B2 = V_r * torch.sqrt(S_r).unsqueeze(0)
    except Exception:
        # Fallback to random initialization
        B1 = torch.randint(0, 2, (out_features, rank), device=device).float() * 2 - 1
        B2 = torch.randn(in_features, rank, device=device) / np.sqrt(rank)

    # ADMM auxiliary variables
    Z1 = B1.clone()
    Y1 = torch.zeros_like(B1)

    # Precompute B2 @ B2^T
    B2_T_B2 = B2.T @ B2

    # ADMM iterations
    for _ in range(num_iters):
        # Update B1: Binary projection
        B1 = torch.sign(Z1 + Y1 / rho)
        B1[B1 == 0] = 1

        # Update Z1: Batch least squares solution
        # We want to solve: minimize ||W - Z1 @ B2^T||^2 + (rho/2)||Z1 - B1 + Y1/rho||^2
        # Batch solve: (B2 @ B2^T + rho*I) Z1^T = (W @ B2 + rho*B1 - Y1)^T
        A = B2_T_B2 + rho * torch.eye(rank, device=device)
        b_batch = weight @ B2 + rho * B1 - Y1  # [out_features, rank]

        # Solve for all rows at once using batched solve
        try:
            Z1 = torch.linalg.solve(A.unsqueeze(0).expand(out_features, -1, -1),
                                    b_batch.unsqueeze(-1)).squeeze(-1)
        except:
            # Fallback: solve individually
            for i in range(out_features):
                Z1[i] = torch.linalg.solve(A, b_batch[i])

        # Update dual variable
        Y1 = Y1 + rho * (Z1 - B1)

    # Final B1 from Z1
    B1 = torch.sign(Z1)
    B1[B1 == 0] = 1

    # Compute optimal B2 given final B1
    # Solve: B2^T = (B1^T @ B1)^{-1} @ B1^T @ W
    B1_T_B1 = B1.T @ B1  # [rank, rank]
    B1_T_W = B1.T @ weight  # [rank, in_features]

    try:
        B2_T = torch.linalg.solve(B1_T_B1 + 0.01 * torch.eye(rank, device=device), B1_T_W)
        B2 = B2_T.T  # [in_features, rank]
    except Exception:
        # Fallback to pseudoinverse
        B2 = torch.linalg.lstsq(B1, weight).solution.T

    # Compute optimal channel-wise scales
    # Reconstruct without scales first
    reconstruction = B1 @ B2.T  # [out_features, in_features]

    # Per-row least squares for scales
    # scales[i] = argmin_s ||W[i] - s * R[i]||^2 = sum(W[i] * R[i]) / sum(R[i]^2)
    numerator = (weight * reconstruction).sum(dim=1)  # [out_features]
    denominator = (reconstruction ** 2).sum(dim=1) + 1e-8  # [out_features]
    scales = numerator / denominator

    return B1, B2, scales


def quantize_tensor_nanoquant(
    tensor: torch.Tensor,
    config: NanoQuantConfig,
) -> Dict:
    """
    Quantize a weight tensor using NANOQUANT method

    Returns quantized representation with:
        - binary_directions_1: Binary matrix B1
        - binary_directions_2: Matrix B2
        - importance_scales: Channel-wise scaling factors
        - metadata: Quantization parameters
    """
    original_shape = tensor.shape

    # Handle both 2D (linear) and higher dimensional (conv) weights
    if len(original_shape) > 2:
        # Reshape to 2D for processing
        tensor_2d = tensor.view(tensor.size(0), -1)
    else:
        tensor_2d = tensor

    # Apply binary decomposition on full matrix
    B1, B2, scales = binary_decomposition_admm(
        tensor_2d,
        rank=min(config.rank, tensor_2d.size(0), tensor_2d.size(1)),
        num_iters=config.admm_iters,
        rho=config.rho,
    )

    # Prepare result
    result = {
        'binary_directions_1': B1,
        'binary_directions_2': B2,
        'importance_scales': scales,
        'original_shape': tuple(original_shape),
        'config': config,
    }

    return result


def dequantize_tensor_nanoquant(
    quantized: Dict,
) -> torch.Tensor:
    """
    Dequantize from NANOQUANT representation back to floating point

    Reconstruction: W ≈ diag(scales) @ (B1 @ B2^T)
    """
    B1 = quantized['binary_directions_1']
    B2 = quantized['binary_directions_2']
    scales = quantized['importance_scales']
    original_shape = quantized['original_shape']

    # Convert shape to tuple if it's a tensor
    if isinstance(original_shape, torch.Tensor):
        original_shape = tuple(original_shape.tolist())

    # Reconstruct: B1 @ B2^T
    reconstructed = B1 @ B2.T  # [out_features, in_features]

    # Apply channel-wise scales
    reconstructed = reconstructed * scales.unsqueeze(1)

    # Reshape to original shape
    if len(original_shape) > 2:
        reconstructed = reconstructed.view(original_shape)

    return reconstructed


def compute_compression_ratio(
    original_shape: Tuple[int, ...],
    config: NanoQuantConfig,
) -> float:
    """
    Calculate the theoretical compression ratio

    Original: FP16 = 16 bits per parameter
    Compressed: B1 (1 bit * out_f * rank) + B2 (16 bit * in_f * rank) + scales (16 bit * out_f)
    """
    if len(original_shape) == 2:
        out_f, in_f = original_shape
    else:
        out_f = original_shape[0]
        in_f = np.prod(original_shape[1:])

    # Original size (FP16)
    original_bits = out_f * in_f * 16

    # Compressed size
    # B1: out_f * rank * 1 bit (binary)
    # B2: in_f * rank * 16 bit (FP16)
    # Scales: out_f * 16 bit (FP16)
    compressed_bits = (
        out_f * config.rank * 1 +     # B1 (1-bit)
        in_f * config.rank * 16 +      # B2 (FP16)
        out_f * 16                      # Scales (FP16)
    )

    return original_bits / compressed_bits


if __name__ == "__main__":
    # Test the implementation
    print("=" * 60)
    print("NANOQUANT Core Implementation Test")
    print("=" * 60)

    # Test with a small example
    test_weight = torch.randn(256, 512)

    config = NanoQuantConfig(
        rank=32,
        block_size=128,
        admm_iters=30,
    )

    print(f"\nOriginal weight shape: {test_weight.shape}")
    print(f"Original size (FP16): {test_weight.numel() * 2 / 1024:.2f} KB")

    # Quantize
    print("\nQuantizing with NANOQUANT...")
    quantized = quantize_tensor_nanoquant(test_weight, config)

    # Dequantize
    print("Dequantizing...")
    reconstructed = dequantize_tensor_nanoquant(quantized)

    # Calculate metrics
    compression = compute_compression_ratio(test_weight.shape, config)
    mse = torch.mean((test_weight - reconstructed) ** 2).item()
    relative_error = torch.norm(test_weight - reconstructed) / torch.norm(test_weight)

    print(f"\nResults:")
    print(f"  Compression ratio: {compression:.2f}×")
    print(f"  MSE: {mse:.6f}")
    print(f"  Relative error: {relative_error:.4f}")
    print(f"  Effective bits per parameter: {16 / compression:.2f}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
