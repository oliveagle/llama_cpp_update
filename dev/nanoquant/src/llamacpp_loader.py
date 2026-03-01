"""
NANOQUANT llama.cpp Integration
Load and run NANOQUANT models with llama.cpp-compatible interface
"""

import torch
import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import numpy as np


class NanoQuantTensor:
    """Represents a NANOQUANT quantized tensor"""

    def __init__(
        self,
        B1: torch.Tensor,  # Binary directions [out_features, rank]
        B2: torch.Tensor,  # Continuous directions [in_features, rank]
        scales: torch.Tensor,  # Channel-wise scales [out_features]
        original_shape: Tuple[int, ...],
    ):
        self.B1 = B1
        self.B2 = B2
        self.scales = scales
        self.original_shape = original_shape
        self.rank = B1.shape[1]

    def reconstruct(self) -> torch.Tensor:
        """Reconstruct full weight matrix"""
        # W = diag(scales) @ B1 @ B2^T
        weight = self.B1 @ self.B2.T
        weight = weight * self.scales.unsqueeze(1)

        if len(self.original_shape) > 2:
            weight = weight.view(self.original_shape)

        return weight

    @torch.no_grad()
    def matmul(self, x: torch.Tensor) -> torch.Tensor:
        """
        Optimized matrix multiplication: y = x @ W^T

        Using the factorization:
            x @ W^T = x @ (B2 @ B1^T @ diag(scales))
                    = ((x @ B2) @ B1^T) * scales
        """
        # x: [..., in_features]
        original_shape = x.shape
        in_features = original_shape[-1]
        x_2d = x.reshape(-1, in_features)

        # Step 1: x @ B2 -> [batch, rank]
        x_proj = torch.matmul(x_2d, self.B2)

        # Step 2: x_proj @ B1^T -> [batch, out_features]
        output = torch.matmul(x_proj, self.B1.T)

        # Step 3: Apply scales
        output = output * self.scales.unsqueeze(0)

        # Reshape back
        out_shape = original_shape[:-1] + (self.B1.shape[0],)
        return output.reshape(out_shape)

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.original_shape

    @property
    def dtype(self) -> torch.dtype:
        return self.scales.dtype

    @property
    def device(self) -> torch.device:
        return self.B1.device


class NanoQuantLlamaCppModel:
    """
    llama.cpp-compatible interface for NANOQUANT models
    """

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.config: Optional[Dict] = None
        self.tokenizer = None

        # Model state
        self.tensors: Dict[str, NanoQuantTensor] = {}
        self.original_tensors: Dict[str, torch.Tensor] = {}

        self._load_model()

    def _load_model(self):
        """Load NANOQUANT model"""
        print(f"Loading NANOQUANT model from {self.model_path}...")

        # Load quantized model
        quantized = torch.load(self.model_path, map_location='cpu')

        # Process tensors
        for name, data in quantized.items():
            if data.get('type') == 'nanoquant':
                qdata = data['data']
                self.tensors[name] = NanoQuantTensor(
                    B1=qdata['B1'],
                    B2=qdata['B2'],
                    scales=qdata['scales'],
                    original_shape=tuple(qdata['shape'].tolist()),
                )
            else:
                # Original tensor (not quantized)
                self.original_tensors[name] = data['data']

        print(f"  Loaded {len(self.tensors)} NANOQUANT tensors")
        print(f"  Loaded {len(self.original_tensors)} original tensors")

    def get_tensor(self, name: str) -> Optional[torch.Tensor]:
        """Get tensor by name (reconstruct if NANOQUANT)"""
        if name in self.tensors:
            return self.tensors[name].reconstruct()
        elif name in self.original_tensors:
            return self.original_tensors[name]
        return None

    def apply_linear(self, name: str, x: torch.Tensor) -> torch.Tensor:
        """Apply linear layer using optimized matmul"""
        weight_name = f"{name}.weight"
        bias_name = f"{name}.bias"

        if weight_name in self.tensors:
            # Optimized NANOQUANT matmul
            output = self.tensors[weight_name].matmul(x)
        elif weight_name in self.original_tensors:
            # Standard matmul
            weight = self.original_tensors[weight_name]
            output = torch.matmul(x, weight.T)
        else:
            raise ValueError(f"Weight {weight_name} not found")

        # Add bias if present
        if bias_name in self.original_tensors:
            bias = self.original_tensors[bias_name]
            output = output + bias

        return output

    def benchmark_inference(
        self,
        batch_size: int = 1,
        seq_len: int = 128,
        num_runs: int = 10,
    ) -> Dict:
        """Benchmark inference performance"""
        import time

        print("\n" + "=" * 60)
        print("NANOQUANT Inference Benchmark")
        print("=" * 60)

        # Create dummy input
        hidden_size = 1024  # Qwen3 0.6B hidden size
        x = torch.randn(batch_size, seq_len, hidden_size)

        # Find all linear layers
        linear_layers = [name for name in self.tensors.keys() if "proj" in name or "head" in name]

        results = {}

        for layer_name in list(self.tensors.keys())[:5]:  # Test first 5 layers
            tensor = self.tensors[layer_name]

            # Create matching input
            in_features = tensor.B2.shape[0]
            test_x = torch.randn(batch_size, seq_len, in_features)

            # Warmup
            for _ in range(3):
                _ = tensor.matmul(test_x)

            # Benchmark
            start = time.time()
            for _ in range(num_runs):
                _ = tensor.matmul(test_x)
            elapsed = time.time() - start

            avg_time = elapsed / num_runs * 1000
            throughput = (batch_size * seq_len) / (elapsed / num_runs)

            results[layer_name] = {
                'avg_time_ms': avg_time,
                'throughput': throughput,
            }

            print(f"{layer_name}:")
            print(f"  Avg time: {avg_time:.2f} ms")
            print(f"  Throughput: {throughput:.1f} tokens/sec")

        return results

    def validate_accuracy(
        self,
        original_model_path: Optional[str] = None,
    ) -> Dict:
        """
        Validate NANOQUANT model accuracy against original
        """
        from safetensors.torch import load_file

        print("\n" + "=" * 60)
        print("NANOQUANT Accuracy Validation")
        print("=" * 60)

        if original_model_path is None:
            # Try to find original model
            original_model_path = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B"

        original_state = load_file(f"{original_model_path}/model.safetensors")

        errors = {}

        for name, nq_tensor in list(self.tensors.items())[:5]:
            if name in original_state:
                original = original_state[name].float()
                reconstructed = nq_tensor.reconstruct()

                # Handle shape mismatch
                if original.shape != reconstructed.shape:
                    original = original.view(reconstructed.shape)

                mse = torch.mean((original - reconstructed) ** 2).item()
                rel_error = torch.norm(original - reconstructed) / torch.norm(original)
                max_error = torch.max(torch.abs(original - reconstructed)).item()

                errors[name] = {
                    'mse': mse,
                    'rel_error': rel_error.item(),
                    'max_error': max_error,
                }

                print(f"{name}:")
                print(f"  MSE: {mse:.6f}")
                print(f"  Relative error: {rel_error:.4f}")
                print(f"  Max error: {max_error:.6f}")

        return errors


def export_to_gguf(
    nanoquant_path: str,
    output_path: str,
):
    """
    Export NANOQUANT model to custom GGUF-like format
    (Note: llama.cpp doesn't natively support NANOQUANT yet)
    """
    model = NanoQuantLlamaCppModel(nanoquant_path)

    print("\n" + "=" * 60)
    print("Exporting to GGUF-like format")
    print("=" * 60)

    # For now, just save reconstructed weights in standard GGUF
    # Real NANOQUANT support would need custom GGML type

    print(f"Note: llama.cpp doesn't natively support NANOQUANT yet.")
    print(f"For testing, you can reconstruct weights and use standard GGUF.")
    print(f"")
    print(f"To use with llama.cpp:")
    print(f"  1. Reconstruct weights from NANOQUANT format")
    print(f"  2. Save as FP16")
    print(f"  3. Use llama-quantize to convert to IQ1_S or TQ1_0")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant.gguf")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--export-gguf", action="store_true")

    args = parser.parse_args()

    # Load model
    model = NanoQuantLlamaCppModel(args.model)

    if args.benchmark:
        model.benchmark_inference()

    if args.validate:
        model.validate_accuracy()

    if args.export_gguf:
        export_to_gguf(args.model, args.model.replace(".gguf", "-reconstructed.gguf"))
