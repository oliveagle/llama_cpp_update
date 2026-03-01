"""
Test NANOQUANT generation vs original model
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import sys
sys.path.insert(0, '/mnt/volume3/llama_cpp/nanoquant')
from nanoquant_generate import NanoQuantModel
import time


def test_original_model():
    """Test with original FP16 model"""
    print("=" * 60)
    print("Testing Original FP16 Model")
    print("=" * 60)

    model_name = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B"

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        trust_remote_code=True,
    )

    prompt = "Hello, my name is"
    inputs = tokenizer(prompt, return_tensors="pt")

    print(f"\nPrompt: {prompt}")
    print("Generating...")

    start = time.time()
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=20,
            do_sample=True,
            temperature=0.7,
        )
    elapsed = time.time() - start

    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\nOutput: {generated_text}")
    print(f"Time: {elapsed:.2f}s ({20 / elapsed:.2f} tokens/sec)")

    return generated_text


def test_nanoquant_model():
    """Test with NANOQUANT model"""
    print("\n" + "=" * 60)
    print("Testing NANOQUANT Model")
    print("=" * 60)

    model = NanoQuantModel("/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant.gguf")

    output = model.generate(
        prompt="Hello, my name is",
        max_new_tokens=20,
        temperature=0.7,
    )

    return output


def test_single_layer():
    """Test single layer output to verify correctness"""
    print("\n" + "=" * 60)
    print("Testing Single Layer Output")
    print("=" * 60)

    # Load both models
    model_name = "/mnt/volume3/modelscope_models/Qwen/Qwen3-0.6B"
    orig_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float32,
        trust_remote_code=True,
    )
    nq_model = NanoQuantModel("/mnt/volume3/llama_cpp/nanoquant/qwen3-0.6b-nanoquant.gguf")

    # Create test input
    test_input = torch.randn(1, 10, 1024)  # [batch, seq, hidden]

    # Test first layer
    with torch.no_grad():
        # Original model layer 0
        orig_layer = orig_model.model.layers[0]
        orig_output = orig_layer(test_input)[0]

        # NANOQUANT layer 0
        nq_layer = nq_model.layers[0]
        nq_output = nq_layer.forward(test_input)

    print(f"Original output shape: {orig_output.shape}")
    print(f"NANOQUANT output shape: {nq_output.shape}")

    # Compare
    mse = torch.mean((orig_output - nq_output) ** 2).item()
    rel_error = torch.norm(orig_output - nq_output) / torch.norm(orig_output)

    print(f"\nLayer 0 comparison:")
    print(f"  MSE: {mse:.6f}")
    print(f"  Relative error: {rel_error:.4f}")

    # Test second layer
    with torch.no_grad():
        orig_output2 = orig_model.model.layers[1](orig_output)[0]
        nq_output2 = nq_model.layers[1].forward(nq_output)

    mse2 = torch.mean((orig_output2 - nq_output2) ** 2).item()
    rel_error2 = torch.norm(orig_output2 - nq_output2) / torch.norm(orig_output2)

    print(f"\nLayer 1 comparison:")
    print(f"  MSE: {mse2:.6f}")
    print(f"  Relative error: {rel_error2:.4f}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--original":
        test_original_model()
    elif len(sys.argv) > 1 and sys.argv[1] == "--layer":
        test_single_layer()
    else:
        # Test NANOQUANT by default
        test_nanoquant_model()
