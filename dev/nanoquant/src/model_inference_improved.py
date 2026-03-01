"""
Improved NANOQUANT Inference
Handles outliers and improved quantization format
"""

import torch
import torch.nn.functional as F
from pathlib import Path
from typing import Optional, Dict
from transformers import AutoTokenizer
import time


class NanoQuantLinearImproved:
    """Linear layer with improved NANOQUANT (supports outliers)"""

    def __init__(
        self,
        B1: torch.Tensor,
        B2: torch.Tensor,
        scales: torch.Tensor,
        outliers: Optional[torch.Tensor] = None,
        outlier_values: Optional[torch.Tensor] = None,
        bias: Optional[torch.Tensor] = None,
    ):
        self.B1 = B1.float()
        self.B2 = B2.float()
        self.scales = scales.float()
        self.outliers = outliers
        self.outlier_values = outlier_values.float() if outlier_values is not None and outlier_values.numel() > 0 else None
        self.bias = bias.float() if bias is not None else None
        self.out_features = B1.shape[0]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, seq, in_features]
        original_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])

        # Step 1: Project input
        x_proj = torch.matmul(x_2d, self.B2)
        output = torch.matmul(x_proj, self.B1.T)
        output = output * self.scales.unsqueeze(0)

        # Step 2: Add outlier contributions
        if self.outlier_values is not None and self.outliers is not None:
            # Sparse outlier contribution
            outlier_indices = torch.nonzero(self.outliers, as_tuple=True)
            if len(outlier_indices[0]) > 0:
                # For each output position, add outlier contribution
                # This is simplified - proper sparse matmul would be faster
                for i, (row, col) in enumerate(zip(outlier_indices[0], outlier_indices[1])):
                    output[:, row] += x_2d[:, col] * self.outlier_values[i]

        if self.bias is not None:
            output = output + self.bias

        return output.reshape(*original_shape[:-1], self.out_features)


class NanoQuantModelImproved:
    """Full transformer model with improved NANOQUANT"""

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = Path(model_path)
        self.device = device
        self.num_layers = 28
        self.hidden_size = 1024
        self.num_heads = 16
        self.num_kv_heads = 8
        self.head_dim = 128
        self.vocab_size = 151936

        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
            trust_remote_code=True
        )

        print(f"Loading NANOQUANT model from {model_path}...")
        self.quantized = torch.load(model_path, map_location=device)

        self.embed_tokens = self._get_tensor("model.embed_tokens.weight")
        self.norm_weight = self._get_tensor("model.norm.weight")
        self.lm_head = self._build_linear("lm_head")

        self.layers = []
        for i in range(self.num_layers):
            layer = self._build_layer(i)
            self.layers.append(layer)

        print(f"Model loaded: {len(self.layers)} layers")
        self._print_memory_usage()

    def _get_tensor(self, name: str) -> torch.Tensor:
        """Get tensor from quantized model"""
        if name in self.quantized:
            data = self.quantized[name]
            if data.get("type") in ["nanoquant", "nanoquant_improved"]:
                nq = data["data"]
                B1, B2, scales = nq["B1"], nq["B2"], nq["scales"]
                weight = B1.float() @ B2.float().T
                weight = weight * scales.float().unsqueeze(1)
                return weight
            else:
                return data["data"]
        raise KeyError(f"Tensor {name} not found")

    def _build_linear(self, name: str) -> NanoQuantLinearImproved:
        """Build NANOQUANT linear layer with outliers"""
        weight_name = f"{name}.weight"
        bias_name = f"{name}.bias"

        if weight_name in self.quantized:
            data = self.quantized[weight_name]
            if data.get("type") in ["nanoquant", "nanoquant_improved"]:
                nq = data["data"]
                bias = None
                if bias_name in self.quantized:
                    bias = self.quantized[bias_name]["data"]

                # Get outliers if present
                outliers = nq.get("outliers")
                outlier_values = nq.get("outlier_values")

                return NanoQuantLinearImproved(
                    nq["B1"], nq["B2"], nq["scales"],
                    outliers=outliers,
                    outlier_values=outlier_values,
                    bias=bias
                )
        raise KeyError(f"Linear layer {name} not found")

    def _build_layer(self, layer_idx: int):
        """Build transformer layer"""
        prefix = f"model.layers.{layer_idx}"

        # Import here to avoid circular dependency
        from model_inference import NanoQuantAttention, NanoQuantMLP, NanoQuantTransformerLayer

        attention = NanoQuantAttention(
            q_proj=self._build_linear(f"{prefix}.self_attn.q_proj"),
            k_proj=self._build_linear(f"{prefix}.self_attn.k_proj"),
            v_proj=self._build_linear(f"{prefix}.self_attn.v_proj"),
            o_proj=self._build_linear(f"{prefix}.self_attn.o_proj"),
            num_heads=self.num_heads,
            num_kv_heads=self.num_kv_heads,
            head_dim=self.head_dim,
        )

        mlp = NanoQuantMLP(
            gate_proj=self._build_linear(f"{prefix}.mlp.gate_proj"),
            up_proj=self._build_linear(f"{prefix}.mlp.up_proj"),
            down_proj=self._build_linear(f"{prefix}.mlp.down_proj"),
        )

        input_layernorm = self._get_tensor(f"{prefix}.input_layernorm.weight")
        post_attention_layernorm = self._get_tensor(f"{prefix}.post_attention_layernorm.weight")

        return NanoQuantTransformerLayer(
            attention=attention,
            mlp=mlp,
            input_layernorm_weight=input_layernorm,
            post_attention_layernorm_weight=post_attention_layernorm,
        )

    def _print_memory_usage(self):
        total_params = 0
        for name, data in self.quantized.items():
            if data.get("type") in ["nanoquant", "nanoquant_improved"]:
                nq = data["data"]
                total_params += nq["B1"].numel() + nq["B2"].numel() + nq["scales"].numel()
                if "outlier_values" in nq:
                    total_params += nq["outlier_values"].numel()
            else:
                total_params += data["data"].numel()

        print(f"Total parameters: {total_params / 1e6:.1f}M")
        print(f"Memory: {total_params * 4 / 1024**2:.1f} MB (float32)")

    def _create_causal_mask(self, seq_len: int) -> torch.Tensor:
        mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask.to(self.device)

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
    ) -> str:
        print(f"\nPrompt: {prompt}")
        print("Generating...")

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        batch_size, seq_len = input_ids.shape

        start_time = time.time()

        for i in range(max_new_tokens):
            hidden_states = F.embedding(input_ids, self.embed_tokens.float())
            mask = self._create_causal_mask(input_ids.shape[1])

            for layer in self.layers:
                hidden_states = layer.forward(hidden_states, mask)

            variance = hidden_states.pow(2).mean(-1, keepdim=True)
            hidden_states = hidden_states * torch.rsqrt(variance + 1e-6)
            hidden_states = hidden_states * self.norm_weight

            last_hidden = hidden_states[:, -1, :]
            logits = self.lm_head.forward(last_hidden)

            logits = logits / temperature

            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = float("-inf")

            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = False
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = float("-inf")

            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            input_ids = torch.cat([input_ids, next_token], dim=1)

            new_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
            print(new_text, end="", flush=True)

            if next_token.item() == self.tokenizer.eos_token_id:
                break

        elapsed = time.time() - start_time
        tokens_generated = input_ids.shape[1] - seq_len

        print(f"\n\nGenerated {tokens_generated} tokens in {elapsed:.2f}s")
        print(f"Speed: {tokens_generated / elapsed:.2f} tokens/sec")

        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/qwen3-0.6b-nanoquant-improved.gguf")
    parser.add_argument("--prompt", default="Hello, how are you?")
    parser.add_argument("--max-tokens", type=int, default=50)
    parser.add_argument("--temperature", type=float, default=0.7)

    args = parser.parse_args()

    model = NanoQuantModelImproved(args.model)
    output = model.generate(
        prompt=args.prompt,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    print("\n" + "=" * 60)
    print("Generated Text:")
    print("=" * 60)
    print(output)
