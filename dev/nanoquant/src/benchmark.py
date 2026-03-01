"""
NANOQUANT Inference Engine
CPU-based inference for NANOQUANT quantized models
"""

import torch
import json
from pathlib import Path
from typing import Optional, Dict
import time


class NanoQuantLinear:
    """
    Linear layer using NANOQUANT representation

    Computation: y = x @ W^T + b
    where W ≈ scales * (B1 @ B2^T)
    """

    def __init__(
        self,
        b1: torch.Tensor,  # [out_features, rank] - binary {-1, +1}
        b2: torch.Tensor,  # [in_features, rank] - binary {-1, +1}
        scales: torch.Tensor,  # [out_features] - FP16
        bias: Optional[torch.Tensor] = None,
    ):
        self.b1 = b1.float()  # Convert to float for computation
        self.b2 = b2.float()
        self.scales = scales.float()
        self.bias = bias.float() if bias is not None else None

        self.out_features = b1.shape[0]
        self.in_features = b2.shape[0]
        self.rank = b1.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass with NANOQUANT weights

        Optimized computation:
            1. x_proj = x @ B2  # [batch, rank]
            2. y = x_proj @ B1^T  # [batch, out_features]
            3. y = y * scales  # Scale each output channel
        """
        # x: [batch, seq_len, in_features] or [batch, in_features]
        original_shape = x.shape
        x_flat = x.reshape(-1, self.in_features)

        # Step 1: Project input to rank dimension
        # x @ B2: [batch*seq, in_features] @ [in_features, rank] -> [batch*seq, rank]
        x_proj = torch.matmul(x_flat, self.b2)

        # Step 2: Project to output dimension
        # x_proj @ B1^T: [batch*seq, rank] @ [rank, out_features] -> [batch*seq, out_features]
        output = torch.matmul(x_proj, self.b1.T)

        # Step 3: Apply channel-wise scales
        output = output * self.scales.unsqueeze(0)

        # Add bias if present
        if self.bias is not None:
            output = output + self.bias.unsqueeze(0)

        # Reshape back
        output = output.reshape(*original_shape[:-1], self.out_features)

        return output

    @torch.no_grad()
    def reconstruct_weight(self) -> torch.Tensor:
        """Reconstruct full weight matrix for comparison/debugging"""
        # W = scales * (B1 @ B2^T)
        weight = torch.matmul(self.b1, self.b2.T)
        weight = weight * self.scales.unsqueeze(1)
        return weight


class NanoQuantModel:
    """Wrapper for NANOQUANT quantized model"""

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.config = None
        self.state_dict = None
        self.layers = {}

        self._load_model()

    def _load_model(self):
        """Load NANOQUANT model from disk"""
        print(f"Loading NANOQUANT model from {self.model_path}...")

        # Load config
        config_path = self.model_path / "nanoquant_config.json"
        with open(config_path, "r") as f:
            self.config = json.load(f)

        # Load weights
        weights_path = self.model_path / "nanoquant_model.bin"
        self.state_dict = torch.load(weights_path, map_location="cpu")

        print(f"Model type: {self.config.get('model_type', 'unknown')}")
        print(f"Quantization config: {self.config.get('quantization_config', {})}")

    def get_linear_layer(self, name: str) -> Optional[NanoQuantLinear]:
        """Get a NANOQUANT linear layer by name"""
        assert self.state_dict is not None, "Model not loaded"

        b1_key = f"{name}.b1"
        b2_key = f"{name}.b2"
        scales_key = f"{name}.scales"

        state = self.state_dict
        if b1_key not in state:
            return None

        b1 = state[b1_key].float()
        b2 = state[b2_key].float()
        scales = state[scales_key].float()

        # Try to load bias if present
        bias = state.get(f"{name}.bias", None)

        return NanoQuantLinear(b1, b2, scales, bias)

    def benchmark_layer(
        self,
        layer_name: str,
        batch_size: int = 1,
        seq_len: int = 128,
        num_runs: int = 10,
    ) -> Dict:
        """Benchmark a specific layer's performance"""
        layer = self.get_linear_layer(layer_name)
        if layer is None:
            print(f"Layer {layer_name} not found")
            return {}

        print(f"\nBenchmarking layer: {layer_name}")
        print(f"  Shape: [{layer.out_features}, {layer.in_features}]")
        print(f"  Rank: {layer.rank}")
        print(f"  Effective compression: {layer.in_features * layer.out_features * 2 / (layer.b1.numel() + layer.b2.numel() + layer.scales.numel() * 2):.2f}×")

        # Create random input
        x = torch.randn(batch_size, seq_len, layer.in_features)

        # Warmup
        for _ in range(3):
            _ = layer.forward(x)

        # Benchmark
        start = time.time()
        for _ in range(num_runs):
            _ = layer.forward(x)
        elapsed = time.time() - start

        # Calculate metrics
        avg_time = elapsed / num_runs * 1000  # ms
        tokens_per_sec = (batch_size * seq_len) / (elapsed / num_runs)

        print(f"  Batch: {batch_size}, Seq: {seq_len}")
        print(f"  Avg time: {avg_time:.2f} ms")
        print(f"  Throughput: {tokens_per_sec:.1f} tokens/sec")

        return {
            "avg_time_ms": avg_time,
            "tokens_per_sec": tokens_per_sec,
        }

    def compare_with_original(
        self,
        original_state_dict: Dict[str, torch.Tensor],
        layer_name: str,
    ):
        """Compare NANOQUANT layer with original weights"""
        layer = self.get_linear_layer(layer_name)
        if layer is None:
            return

        if f"{layer_name}.weight" not in original_state_dict:
            print(f"Original weight for {layer_name} not found")
            return

        original = original_state_dict[f"{layer_name}.weight"].float()
        reconstructed = layer.reconstruct_weight()

        # Handle different shapes
        if original.shape != reconstructed.shape:
            original = original.reshape(reconstructed.shape)

        mse = torch.mean((original - reconstructed) ** 2).item()
        rel_error = torch.norm(original - reconstructed) / torch.norm(original)
        max_error = torch.max(torch.abs(original - reconstructed)).item()

        print(f"\nComparison for {layer_name}:")
        print(f"  MSE: {mse:.8f}")
        print(f"  Relative error: {rel_error:.6f}")
        print(f"  Max error: {max_error:.6f}")

        return {
            "mse": mse,
            "rel_error": rel_error.item(),
            "max_error": max_error,
        }


def test_qwen3_inference():
    """Test NANOQUANT inference on Qwen3-0.6B"""
    model_path = "/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant"

    print("=" * 60)
    print("NANOQUANT Inference Test - Qwen3-0.6B")
    print("=" * 60)

    # Load model
    model = NanoQuantModel(model_path)

    # Find and benchmark linear layers
    print("\n" + "=" * 60)
    print("Layer Benchmarks")
    print("=" * 60)

    # Common layer names in transformer models
    test_layers = [
        "model.layers.0.self_attn.q_proj",
        "model.layers.0.self_attn.k_proj",
        "model.layers.0.self_attn.v_proj",
        "model.layers.0.self_attn.o_proj",
        "model.layers.0.mlp.gate_proj",
        "model.layers.0.mlp.up_proj",
        "model.layers.0.mlp.down_proj",
    ]

    for layer_name in test_layers:
        model.benchmark_layer(layer_name, batch_size=1, seq_len=128)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_qwen3_inference()
