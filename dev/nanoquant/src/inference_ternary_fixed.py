"""
Inference for Ternary Quantized Model - Fixed Version
"""

import torch
import torch.nn.functional as F
from pathlib import Path
from transformers import AutoTokenizer
import sys
import time
sys.path.insert(0, str(Path(__file__).parent))


class TernaryLinear:
    """Linear layer with ternary weights"""

    def __init__(self, B1, B2, scales, B1_shape, bias=None):
        # B1 might be packed or unpacked
        if B1.dtype == torch.uint8:
            self.B1 = self._unpack_ternary(B1, B1_shape)
        else:
            self.B1 = B1.float()
        self.B2 = B2.float()
        self.scales = scales.float()
        self.bias = bias.float() if bias is not None else None
        self.out_features = B1_shape[0]

    def _unpack_ternary(self, packed, shape):
        """Unpack 2-bit ternary values"""
        out_f, rank = shape
        flat = torch.zeros(out_f * rank, dtype=torch.long)
        for i in range(4):
            flat[i::4] = (packed >> (2 * i)) & 0x3
        flat = flat[:out_f * rank]
        B1 = flat.float() - 1
        return B1.reshape(out_f, rank)

    def forward(self, x):
        original_shape = x.shape
        x_2d = x.reshape(-1, x.shape[-1])
        x_proj = torch.matmul(x_2d, self.B2)
        output = torch.matmul(x_proj, self.B1.T)
        output = output * self.scales.unsqueeze(0)
        if self.bias is not None:
            output = output + self.bias
        return output.reshape(*original_shape[:-1], self.out_features)


class SimpleTransformerLayer:
    """Simplified transformer layer"""

    def __init__(self, attn_layers, mlp_layers, norm_weights):
        self.q_proj, self.k_proj, self.v_proj, self.o_proj = attn_layers
        self.gate_proj, self.up_proj, self.down_proj = mlp_layers
        self.input_norm, self.post_attn_norm = norm_weights
        self.num_heads = 16
        self.head_dim = 128

    def _rms_norm(self, x, weight):
        variance = x.pow(2).mean(-1, keepdim=True)
        return x * torch.rsqrt(variance + 1e-6) * weight

    def forward(self, x, mask):
        # Self-attention
        normed = self._rms_norm(x, self.input_norm)
        q = self.q_proj.forward(normed)
        k = self.k_proj.forward(normed)
        v = self.v_proj.forward(normed)

        batch, seq, _ = q.shape
        q = q.view(batch, seq, self.num_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch, seq, 8, self.head_dim).transpose(1, 2)
        v = v.view(batch, seq, 8, self.head_dim).transpose(1, 2)

        # Repeat k, v for GQA
        k = k.repeat_interleave(2, dim=1)
        v = v.repeat_interleave(2, dim=1)

        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        if mask is not None:
            scores = scores + mask
        attn = F.softmax(scores, dim=-1)
        attn_out = torch.matmul(attn, v)
        attn_out = attn_out.transpose(1, 2).contiguous().view(batch, seq, -1)
        attn_out = self.o_proj.forward(attn_out)
        x = x + attn_out

        # MLP
        normed = self._rms_norm(x, self.post_attn_norm)
        gate = self.gate_proj.forward(normed)
        gate = F.silu(gate)
        up = self.up_proj.forward(normed)
        hidden = gate * up
        mlp_out = self.down_proj.forward(hidden)
        x = x + mlp_out

        return x


class TernaryModel:
    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.device = "cpu"
        self.num_layers = 28
        self.hidden_size = 1024

        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B",
            trust_remote_code=True
        )

        print(f"Loading ternary model from {model_path}...")
        self.quantized = torch.load(model_path, map_location=self.device)

        self.embed_tokens = self._get_tensor("model.embed_tokens.weight")
        self.norm_weight = self._get_tensor("model.norm.weight")
        self.lm_head = self._build_linear("lm_head")

        self.layers = []
        for i in range(self.num_layers):
            self.layers.append(self._build_layer(i))

        print(f"Model loaded: {len(self.layers)} layers")

    def _get_tensor(self, name):
        if name in self.quantized:
            data = self.quantized[name]
            if data.get("type") == "ternary":
                nq = data["data"]
                B1 = nq.get("B1_packed") if "B1_packed" in nq else nq.get("B1")
                B2 = nq["B2"]
                scales = nq["scales"]
                if B1.dtype == torch.uint8:
                    B1 = self._unpack_simple(B1, nq["B1_shape"])
                weight = B1.float() @ B2.float().T
                weight = weight * scales.float().unsqueeze(1)
                return weight
            else:
                return data["data"]
        raise KeyError(f"Tensor {name} not found")

    def _unpack_simple(self, packed, shape):
        out_f, rank = shape
        flat = torch.zeros(out_f * rank, dtype=torch.long)
        for i in range(4):
            flat[i::4] = (packed >> (2 * i)) & 0x3
        flat = flat[:out_f * rank]
        B1 = flat.float() - 1
        return B1.reshape(out_f, rank)

    def _build_linear(self, name):
        weight_name = f"{name}.weight"
        bias_name = f"{name}.bias"

        if weight_name in self.quantized:
            data = self.quantized[weight_name]
            if data.get("type") == "ternary":
                nq = data["data"]
                B1 = nq.get("B1_packed") if "B1_packed" in nq else nq.get("B1")
                bias = self.quantized[bias_name]["data"] if bias_name in self.quantized else None
                return TernaryLinear(B1, nq["B2"], nq["scales"], nq["B1_shape"], bias)
        raise KeyError(f"Linear layer {name} not found")

    def _build_layer(self, layer_idx):
        prefix = f"model.layers.{layer_idx}"

        attn_layers = [
            self._build_linear(f"{prefix}.self_attn.q_proj"),
            self._build_linear(f"{prefix}.self_attn.k_proj"),
            self._build_linear(f"{prefix}.self_attn.v_proj"),
            self._build_linear(f"{prefix}.self_attn.o_proj"),
        ]

        mlp_layers = [
            self._build_linear(f"{prefix}.mlp.gate_proj"),
            self._build_linear(f"{prefix}.mlp.up_proj"),
            self._build_linear(f"{prefix}.mlp.down_proj"),
        ]

        norm_weights = [
            self._get_tensor(f"{prefix}.input_layernorm.weight"),
            self._get_tensor(f"{prefix}.post_attention_layernorm.weight"),
        ]

        return SimpleTransformerLayer(attn_layers, mlp_layers, norm_weights)

    def _create_causal_mask(self, seq_len):
        mask = torch.triu(torch.ones(seq_len, seq_len), diagonal=1)
        mask = mask.masked_fill(mask == 1, float("-inf"))
        return mask.to(self.device)

    @torch.no_grad()
    def generate(self, prompt, max_new_tokens=50, temperature=0.7):
        print(f"\nPrompt: {prompt}")
        print("Generating...")

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        seq_len = input_ids.shape[1]

        start_time = time.time()

        for _ in range(max_new_tokens):
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
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            input_ids = torch.cat([input_ids, next_token], dim=1)

            new_text = self.tokenizer.decode(next_token[0], skip_special_tokens=True)
            print(new_text, end="", flush=True)

            if next_token.item() == self.tokenizer.eos_token_id:
                break

        elapsed = time.time() - start_time
        tokens_generated = input_ids.shape[1] - seq_len
        print(f"\n\nGenerated {tokens_generated} tokens in {elapsed:.2f}s ({tokens_generated / elapsed:.2f} tokens/sec)")

        return self.tokenizer.decode(input_ids[0], skip_special_tokens=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/qwen3-0.6b-ternary-r512.gguf")
    parser.add_argument("--prompt", default="Hello, my name is")
    parser.add_argument("--max-tokens", type=int, default=30)
    args = parser.parse_args()

    model = TernaryModel(args.model)
    output = model.generate(args.prompt, max_new_tokens=args.max_tokens)
    print("\n" + "=" * 60)
    print("Full output:", output)
