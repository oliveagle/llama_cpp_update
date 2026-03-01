"""
NANOQUANT with Vector Quantization (VQ-VAE style)

Instead of scalar quantization, use learned codebooks with vector quantization.
This can capture correlations between weights better than independent quantization.
"""

import torch
from pathlib import Path
from safetensors.torch import load_file


class VectorQuantizer:
    """
    Vector quantization using learned codebooks.
    Groups weights into vectors and assigns to nearest codeword.
    """

    def __init__(self, device="cpu"):
        self.device = device

    def _vq_quantize(self, weight: torch.Tensor, vector_dim: int = 4, num_codewords: int = 256) -> dict:
        """
        Vector quantization: group weights into vectors, quantize to codebook.

        Args:
            weight: Weight matrix [out_f, in_f]
            vector_dim: Dimension of each vector (must divide in_f)
            num_codewords: Number of codewords in codebook (256 = 8 bits per vector)
        """
        orig_shape = weight.shape
        out_f, in_f = weight.shape

        # Pad if needed
        pad = (vector_dim - in_f % vector_dim) % vector_dim
        if pad > 0:
            weight = torch.nn.functional.pad(weight, (0, pad))

        num_vectors = weight.shape[1] // vector_dim

        # Reshape to vectors: [out_f, num_vectors, vector_dim]
        vectors = weight.reshape(out_f, num_vectors, vector_dim)

        # Flatten all vectors for k-means
        all_vectors = vectors.reshape(-1, vector_dim)  # [out_f * num_vectors, vector_dim]

        # K-means++ initialization
        codebook = self._kmeans_pp(all_vectors, num_codewords)

        # K-means iterations
        for _ in range(20):
            # Assign to nearest codeword
            distances = torch.cdist(all_vectors, codebook)  # [N, num_codewords]
            indices = torch.argmin(distances, dim=1).to(torch.int32)

            # Update codebook
            for c in range(num_codewords):
                mask = indices == c
                if mask.any():
                    codebook[c] = all_vectors[mask].mean(dim=0)

        # Final assignment
        distances = torch.cdist(all_vectors, codebook)
        indices = torch.argmin(distances, dim=1).to(torch.int32)

        # Reshape indices back
        indices = indices.reshape(out_f, num_vectors)

        # Calculate error
        reconstructed = codebook[indices].reshape(out_f, -1)[:, :in_f]
        error = (weight[:, :in_f] - reconstructed).norm() / weight[:, :in_f].norm()
        print(f"    VQ reconstruction error: {error:.4f}")

        return {
            'codebook': codebook.half(),  # [num_codewords, vector_dim]
            'indices': indices,  # [out_f, num_vectors]
            'vector_dim': vector_dim,
            'num_codewords': num_codewords,
            'orig_shape': orig_shape,
        }

    def _kmeans_pp(self, data: torch.Tensor, k: int) -> torch.Tensor:
        """K-means++ initialization (simplified for large n)"""
        n, d = data.shape
        codebook = torch.zeros(k, d, device=data.device)

        # First centroid: random
        codebook[0] = data[torch.randint(n, (1,))]

        # For large datasets, sample subset for distance computation
        sample_size = min(10000, n)
        sample_indices = torch.randperm(n)[:sample_size]
        sample_data = data[sample_indices]

        for i in range(1, k):
            # Compute distances on sample
            dists = torch.cdist(sample_data, codebook[:i]).min(dim=1)[0]
            # Sample from top-k farthest points
            _, top_indices = torch.topk(dists, min(10, len(dists)))
            idx = sample_indices[top_indices[torch.randint(len(top_indices), (1,))]]
            codebook[i] = data[idx]

        return codebook


def quantize_vq(
    input_path: str = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
    output_path: str = "models/qwen3-0.6b-vq.gguf",
    vector_dim: int = 4,
    num_codewords: int = 256,
):
    """Quantize using vector quantization"""
    print("=" * 60)
    print(f"Vector Quantization (vector_dim={vector_dim}, codewords={num_codewords})")
    print("=" * 60)

    state_dict = load_file(f"{input_path}/model.safetensors")
    quantizer = VectorQuantizer()

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

        result = quantizer._vq_quantize(
            param.float().to(quantizer.device),
            vector_dim=vector_dim,
            num_codewords=num_codewords
        )
        quantized[name] = {"type": "vq", "data": result}

        # Calculate compression
        orig_size = param.numel() * 2  # FP16
        # Indices: 1 byte per vector
        # Codebook: num_codewords * vector_dim * 2 bytes
        out_f, in_f = param.shape
        num_vectors = (in_f + vector_dim - 1) // vector_dim
        comp_size = out_f * num_vectors + num_codewords * vector_dim * 2

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
    quantize_vq(vector_dim=4, num_codewords=256)
