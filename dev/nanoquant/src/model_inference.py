"""
NANOQUANT Text Generation
Full transformer inference with NANOQUANT quantized weights
"""

import torch
import torch.nn.functional as F
from pathlib import Path
from typing import List, Optional, Tuple
import json
from transformers import AutoTokenizer
import time


class NanoQuantLinear:
    """Linear layer using NANOQUANT weights"""

    def __init__(self, B1: torch.Tensor, B2: torch.Tensor, scales: torch.Tensor, bias: Optional[torch.Tensor] = None):
        self.B1 = B1.float()
        self.B2 = B2.float()
        self.scales = scales.float()
        self.bias = bias.float() if bias is not None else None
        self.out_features = B1.shape[0]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [batch, seq, in_features]
        original_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])

        # Optimized: ((x @ B2) @ B1^T) * scales
        x_proj = torch.matmul(x_2d, self.B2)
        output = torch.matmul(x_proj, self.B1.T)
        output = output * self.scales.unsqueeze(0)

        if self.bias is not None:
            output = output + self.bias

        return output.reshape(*original_shape[:-1], self.out_features)


class NanoQuantMLP:
    """MLP block with NANOQUANT weights"""

    def __init__(self, gate_proj: NanoQuantLinear, up_proj: NanoQuantLinear, down_proj: NanoQuantLinear):
        self.gate_proj = gate_proj
        self.up_proj = up_proj
        self.down_proj = down_proj

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # SwiGLU: gate = silu(x @ gate_proj^T) * (x @ up_proj^T)
        gate = self.gate_proj.forward(x)
        gate = F.silu(gate)
        up = self.up_proj.forward(x)
        hidden = gate * up
        return self.down_proj.forward(hidden)


class NanoQuantAttention:
    """Attention block with NANOQUANT weights"""

    def __init__(
        self,
        q_proj: NanoQuantLinear,
        k_proj: NanoQuantLinear,
        v_proj: NanoQuantLinear,
        o_proj: NanoQuantLinear,
        num_heads: int = 16,
        num_kv_heads: int = 16,
        head_dim: int = 64,
    ):
        self.q_proj = q_proj
        self.k_proj = k_proj
        self.v_proj = v_proj
        self.o_proj = o_proj
        self.num_heads = num_heads
        self.num_kv_heads = num_kv_heads
        self.head_dim = head_dim

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size, seq_len, hidden_size = x.shape

        # Project to Q, K, V
        q = self.q_proj.forward(x)  # [batch, seq, num_heads * head_dim]
        k = self.k_proj.forward(x)  # [batch, seq, num_kv_heads * head_dim]
        v = self.v_proj.forward(x)  # [batch, seq, num_kv_heads * head_dim]

        # Reshape for multi-head attention
        # Qwen3 uses GQA (Grouped Query Attention)
        q = q.view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch_size, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch_size, seq_len, self.num_kv_heads, self.head_dim).transpose(1, 2)

        # Repeat k, v for GQA
        if self.num_heads != self.num_kv_heads:
            repeat_factor = self.num_heads // self.num_kv_heads
            k = k.repeat_interleave(repeat_factor, dim=1)
            v = v.repeat_interleave(repeat_factor, dim=1)

        # Scaled dot-product attention
        scale = self.head_dim ** -0.5
        scores = torch.matmul(q, k.transpose(-2, -1)) * scale

        if mask is not None:
            scores = scores + mask

        attn_weights = F.softmax(scores, dim=-1)
        attn_output = torch.matmul(attn_weights, v)

        # Reshape and project output
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.view(batch_size, seq_len, self.num_heads * self.head_dim)

        return self.o_proj.forward(attn_output)


class NanoQuantTransformerLayer:
    """Single transformer layer"""

    def __init__(
        self,
        attention: NanoQuantAttention,
        mlp: NanoQuantMLP,
        input_layernorm_weight: torch.Tensor,
        post_attention_layernorm_weight: torch.Tensor,
        eps: float = 1e-6,
    ):
        self.attention = attention
        self.mlp = mlp
        self.input_layernorm_weight = input_layernorm_weight
        self.post_attention_layernorm_weight = post_attention_layernorm_weight
        self.eps = eps

    def _rms_norm(self, x: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
        """RMS normalization (used by Qwen)"""
        variance = x.pow(2).mean(-1, keepdim=True)
        x = x * torch.rsqrt(variance + self.eps)
        return x * weight

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with residual
        normed = self._rms_norm(x, self.input_layernorm_weight)
        attn_out = self.attention.forward(normed, mask)
        x = x + attn_out

        # MLP with residual
        normed = self._rms_norm(x, self.post_attention_layernorm_weight)
        mlp_out = self.mlp.forward(normed)
        x = x + mlp_out

        return x


class NanoQuantModel:
    """Full NANOQUANT transformer model"""

    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = Path(model_path)
        self.device = device
        self.num_layers = 28
        self.hidden_size = 1024
        self.num_heads = 16
        self.num_kv_heads = 8  # GQA
        self.head_dim = 128
        self.vocab_size = 151936

        # Load tokenizer
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
            trust_remote_code=True
        )

        # Load model
        print(f"Loading NANOQUANT model from {model_path}...")
        self.quantized = torch.load(model_path, map_location=device)

        # Build model components
        self.embed_tokens = self._get_tensor("model.embed_tokens.weight")
        self.norm_weight = self._get_tensor("model.norm.weight")
        self.lm_head = self._build_linear("lm_head")

        # Build layers
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
            if data.get("type") == "nanoquant":
                # Return reconstructed weight
                nq = data["data"]
                B1, B2, scales = nq["B1"], nq["B2"], nq["scales"]
                weight = B1.float() @ B2.float().T
                weight = weight * scales.float().unsqueeze(1)
                return weight
            else:
                return data["data"]
        raise KeyError(f"Tensor {name} not found")

    def _build_linear(self, name: str) -> NanoQuantLinear:
        """Build NANOQUANT linear layer"""
        weight_name = f"{name}.weight"
        bias_name = f"{name}.bias"

        if weight_name in self.quantized:
            data = self.quantized[weight_name]
            if data.get("type") == "nanoquant":
                nq = data["data"]
                bias = None
                if bias_name in self.quantized:
                    bias = self.quantized[bias_name]["data"]
                return NanoQuantLinear(nq["B1"], nq["B2"], nq["scales"], bias)
            else:
                # Original tensor - create fake NANOQUANT
                weight = data["data"].float()
                # Store as regular linear (not NANOQUANT)
                return NanoQuantLinear(
                    torch.eye(weight.shape[0], weight.shape[1]),
                    weight.T,
                    torch.ones(weight.shape[0]),
                )
        raise KeyError(f"Linear layer {name} not found")

    def _build_layer(self, layer_idx: int) -> NanoQuantTransformerLayer:
        """Build transformer layer"""
        prefix = f"model.layers.{layer_idx}"

        # Build attention
        attention = NanoQuantAttention(
            q_proj=self._build_linear(f"{prefix}.self_attn.q_proj"),
            k_proj=self._build_linear(f"{prefix}.self_attn.k_proj"),
            v_proj=self._build_linear(f"{prefix}.self_attn.v_proj"),
            o_proj=self._build_linear(f"{prefix}.self_attn.o_proj"),
            num_heads=self.num_heads,
            num_kv_heads=self.num_kv_heads,
            head_dim=self.head_dim,
        )

        # Build MLP
        mlp = NanoQuantMLP(
            gate_proj=self._build_linear(f"{prefix}.mlp.gate_proj"),
            up_proj=self._build_linear(f"{prefix}.mlp.up_proj"),
            down_proj=self._build_linear(f"{prefix}.mlp.down_proj"),
        )

        # Get norm weights
        input_layernorm = self._get_tensor(f"{prefix}.input_layernorm.weight")
        post_attention_layernorm = self._get_tensor(f"{prefix}.post_attention_layernorm.weight")

        return NanoQuantTransformerLayer(
            attention=attention,
            mlp=mlp,
            input_layernorm_weight=input_layernorm,
            post_attention_layernorm_weight=post_attention_layernorm,
        )

    def _print_memory_usage(self):
        """Print model memory usage"""
        total_params = 0
        for name, data in self.quantized.items():
            if data.get("type") == "nanoquant":
                nq = data["data"]
                total_params += nq["B1"].numel() + nq["B2"].numel() + nq["scales"].numel()
            else:
                total_params += data["data"].numel()

        print(f"Total parameters: {total_params / 1e6:.1f}M")
        print(f"Memory: {total_params * 4 / 1024**2:.1f} MB (float32)")

    def _create_causal_mask(self, seq_len: int) -> torch.Tensor:
        """Create causal attention mask"""
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
        """Generate text from prompt"""
        print(f"\nPrompt: {prompt}")
        print("Generating...")

        # Tokenize
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        batch_size, seq_len = input_ids.shape

        start_time = time.time()

        # Generate tokens
        for i in range(max_new_tokens):
            # Get embeddings
            hidden_states = F.embedding(input_ids, self.embed_tokens.float())

            # Create causal mask
            mask = self._create_causal_mask(input_ids.shape[1])

            # Forward through layers
            for layer in self.layers:
                hidden_states = layer.forward(hidden_states, mask)

            # Final norm
            variance = hidden_states.pow(2).mean(-1, keepdim=True)
            hidden_states = hidden_states * torch.rsqrt(variance + 1e-6)
            hidden_states = hidden_states * self.norm_weight

            # Get logits for last token
            last_hidden = hidden_states[:, -1, :]  # [batch, hidden]
            logits = self.lm_head.forward(last_hidden)  # [batch, vocab]

            # Sample next token
            # Temperature scaling
            logits = logits / temperature

            # Top-k filtering
            if top_k > 0:
                indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
                logits[indices_to_remove] = float("-inf")

            # Top-p (nucleus) filtering
            if top_p < 1.0:
                sorted_logits, sorted_indices = torch.sort(logits, descending=True)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = False
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
                logits[indices_to_remove] = float("-inf")

            # Sample
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            # Append to input
            input_ids = torch.cat([input_ids, next_token], dim=1)

            # Decode and print
            new_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
            print(new_text, end="", flush=True)

            # Stop on EOS
            if next_token.item() == self.tokenizer.eos_token_id:
                break

        elapsed = time.time() - start_time
        tokens_generated = input_ids.shape[1] - seq_len

        print(f"\n\nGenerated {tokens_generated} tokens in {elapsed:.2f}s")
        print(f"Speed: {tokens_generated / elapsed:.2f} tokens/sec")

        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant.gguf")
    parser.add_argument("--prompt", default="Hello, how are you today?")
    parser.add_argument("--max-tokens", type=int, default=50)
    parser.add_argument("--temperature", type=float, default=0.7)

    args = parser.parse_args()

    # Load model
    model = NanoQuantModel(args.model)

    # Generate
    output = model.generate(
        prompt=args.prompt,
        max_new_tokens=args.max_tokens,
        temperature=args.temperature,
    )

    print("\n" + "=" * 60)
    print("Full output:")
    print("=" * 60)
    print(output)


if __name__ == "__main__":
    main()
