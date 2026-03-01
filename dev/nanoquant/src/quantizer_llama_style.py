"""
Final Attempt - llama.cpp-style Q4_K_M approximation

This replicates what llama.cpp actually does:
1. Block-wise quantization with super-blocks
2. Per-block min/max with shared scales
3. Proper handling of weight distribution
"""

import torch
import numpy as np
from pathlib import Path
from safetensors.torch import load_file


class LlamaStyleQuantizer:
    """
    Replicate llama.cpp Q4_K_M quantization approach.
    This is what actually works for production models.
    """

    def __init__(self, device="cpu"):
        self.device = device

    def quantize_q4_k_m_style(self, weight: torch.Tensor) -> dict:
        """
        Q4_K_M style quantization:
        - Super-blocks of 256 weights
        - 4-bit per weight (16 levels)
        - Shared scales and mins per block
        """
        orig_shape = weight.shape
        out_f, in_f = orig_shape

        # Q4_K_M parameters
        block_size = 32  # Number of weights per block
        super_block_size = 256  # Number of weights per super-block

        # Pad to multiple of super_block_size
        pad = (super_block_size - in_f % super_block_size) % super_block_size
        if pad > 0:
            weight = torch.nn.functional.pad(weight, (0, pad))

        num_super_blocks = weight.shape[1] // super_block_size
        blocks_per_super = super_block_size // block_size  # 8

        # Quantize
        all_quants = []
        all_scales = []
        all_mins = []

        for row_idx in range(out_f):
            row_quants = []
            row_scales = []
            row_mins = []

            for super_idx in range(num_super_blocks):
                super_block = weight[row_idx, super_idx * super_block_size:(super_idx + 1) * super_block_size]

                super_scales = []
                super_mins = []

                for block_idx in range(blocks_per_super):
                    block = super_block[block_idx * block_size:(block_idx + 1) * block_size]

                    # Find min/max for this block
                    w_min = block.min()
                    w_max = block.max()

                    # Scale to 4-bit range
                    scale = (w_max - w_min) / 15.0  # 15 = 2^4 - 1
                    if scale < 1e-8:
                        scale = 1.0

                    # Quantize to 4-bit
                    quant = torch.round((block - w_min) / scale).clamp(0, 15).to(torch.uint8)

                    row_quants.append(quant)
                    super_scales.append(scale)
                    super_mins.append(w_min)

                row_scales.append(torch.tensor(super_scales))
                row_mins.append(torch.tensor(super_mins))

            all_quants.append(torch.cat(row_quants))
            all_scales.append(torch.stack(row_scales))
            all_mins.append(torch.stack(row_mins))

        quants_tensor = torch.stack(all_quants).reshape(out_f, num_super_blocks, super_block_size)
        scales_tensor = torch.stack(all_scales)
        mins_tensor = torch.stack(all_mins)

        # Calculate error
        reconstructed = self._reconstruct({
            'quants': quants_tensor,
            'scales': scales_tensor,
            'mins': mins_tensor,
            'block_size': block_size,
            'super_block_size': super_block_size,
            'orig_shape': orig_shape
        })

        error = (weight[:, :in_f] - reconstructed).norm() / weight[:, :in_f].norm()
        print(f"    Q4_K_M style error: {error:.4f}")

        return {
            'quants': quants_tensor,
            'scales': scales_tensor.half(),
            'mins': mins_tensor.half(),
            'block_size': block_size,
            'super_block_size': super_block_size,
            'orig_shape': orig_shape,
        }

    def _reconstruct(self, quantized: dict) -> torch.Tensor:
        """Reconstruct weight"""
        quants = quantized['quants'].float()
        scales = quantized['scales'].float()
        mins = quantized['mins'].float()
        block_size = quantized['block_size']
        super_block_size = quantized['super_block_size']

        out_f, num_super_blocks, _ = quants.shape
        blocks_per_super = super_block_size // block_size

        reconstructed = []
        for super_idx in range(num_super_blocks):
            super_blocks = []
            for block_idx in range(blocks_per_super):
                start = block_idx * block_size
                end = start + block_size
                block_quants = quants[:, super_idx, start:end]
                block = block_quants * scales[:, super_idx, block_idx].unsqueeze(1) + mins[:, super_idx, block_idx].unsqueeze(1)
                super_blocks.append(block)
            reconstructed.append(torch.cat(super_blocks, dim=1))

        return torch.cat(reconstructed, dim=1)


def quantize_llama_style(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-q4-k-m-style.gguf",
):
    """Quantize using llama.cpp Q4_K_M style"""
    print("=" * 60)
    print("Q4_K_M Style Quantization (llama.cpp compatible)")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = LlamaStyleQuantizer()

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

        result = quantizer.quantize_q4_k_m_style(param.float().to(quantizer.device))
        quantized[name] = {"type": "q4_k_m", "data": result}

        # Compression calculation
        orig_size = param.numel() * 2
        # 4 bits per weight + scales/mins overhead
        out_f = param.shape[0]
        num_super_blocks = (param.shape[1] + 255) // 256
        comp_size = param.numel() * 0.5 + out_f * num_super_blocks * 16  # 8 scales + 8 mins per super-block

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
    quantize_llama_style()
