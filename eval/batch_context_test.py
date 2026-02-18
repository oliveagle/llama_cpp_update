#!/usr/bin/env python3
"""批量测试 Context Window"""

import requests
import json
import time

MODELS = [
    "GLM-4.7-Flash-Q4_K_M",
    "MiniCPM-o-4_5-Q4_K_M",
    "Qwen3VL-4B-Instruct-Q8_0",
    "Qwen3-Coder-Next-Q4_K_M",
    "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0",
    "MiroThinker-v1.5-30B.Q8_0"
]

URL = "http://localhost:8400"

def generate_prompt(target_k):
    filler = "这是一段用于测试长上下文能力的填充文本，包含足够的信息来模拟真实使用场景。"
    needle = "【重要：答案是小狗】"
    target_chars = target_k * 1024 * 4
    repeats = target_chars // len(filler) + 1
    context = (filler * repeats)[:target_chars]
    mid = len(context) // 2
    context = context[:mid] + needle + context[mid:]
    return f"以下是背景信息：{context}\n\n问题：答案是什么？只回答一个词。"

def test_model(model, k):
    prompt = generate_prompt(k)
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20,
        "temperature": 0.1
    }

    try:
        resp = requests.post(f"{URL}/v1/chat/completions", json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            tokens = data.get("usage", {}).get("prompt_tokens", 0)
            content = data["choices"][0]["message"].get("content", "")
            correct = "小狗" in content
            return ("OK", tokens, correct)
        else:
            return ("FAIL", 0, False)
    except Exception as e:
        return ("ERROR", 0, False)

print("=== Vulkan (8400) Context Window 批量测试 ===")
print("测试梯度: 4K, 8K")
print()
print("| 模型 | 4K 状态 | 4K Tokens | 8K 状态 | 8K Tokens | 最大可用 |")
print("|------|---------|-----------|---------|-----------|----------|")

results = {}
for model in MODELS:
    # Test 4K
    s4, t4, c4 = test_model(model, 4)
    status4 = "✅" if s4 == "OK" else "❌"

    # Test 8K if 4K passed
    if s4 == "OK":
        s8, t8, c8 = test_model(model, 8)
        status8 = "✅" if s8 == "OK" else "❌"
        max_ctx = "8K" if s8 == "OK" else "4K"
    else:
        status8 = "-"
        t8 = "-"
        max_ctx = "失败"

    print(f"| {model} | {status4} | {t4} | {status8} | {t8} | {max_ctx} |")
    results[model] = {"4K": (s4, t4), "8K": (s8, t8) if s4 == "OK" else ("-", "-")}

# Save results
with open("eval_results/vulkan/context/batch_context_results.json", "w") as f:
    json.dump(results, f, indent=2)

print()
print("结果已保存: eval_results/vulkan/context/batch_context_results.json")
