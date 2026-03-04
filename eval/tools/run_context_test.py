#!/usr/bin/env python3
"""
Context Window 阶梯测试 - 生成结果表格
"""

import requests
import json
import time

MODEL = "Qwen3-4B-Instruct-2507-UD-Q4_K_XL"
URL = "http://localhost:8400"
STEPS = [4, 8, 16, 32, 64, 128]

def generate_prompt(target_k):
    filler = "这是一段用于测试长上下文能力的填充文本，包含足够的信息来模拟真实使用场景。"
    needle = "【重要：答案是小狗】"
    target_chars = target_k * 1024 * 4
    repeats = target_chars // len(filler) + 1
    context = (filler * repeats)[:target_chars]
    mid = len(context) // 2
    context = context[:mid] + needle + context[mid:]
    return f"以下是背景信息：{context}\n\n问题：答案是什么？只回答一个词。"

def test_context(k):
    prompt = generate_prompt(k)
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 20,
        "temperature": 0.1
    }

    try:
        start = time.time()
        resp = requests.post(f"{URL}/v1/chat/completions", json=payload, timeout=300)
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content", "")
            tokens = data.get("usage", {}).get("prompt_tokens", 0)
            correct = "小狗" in content
            return {
                "target": f"{k}K",
                "tokens": tokens,
                "time": f"{elapsed:.1f}s",
                "correct": "✅" if correct else "❌",
                "status": "✅ 成功"
            }
        else:
            return {
                "target": f"{k}K",
                "tokens": "-",
                "time": "-",
                "correct": "-",
                "status": f"❌ HTTP {resp.status_code}"
            }
    except Exception as e:
        return {
            "target": f"{k}K",
            "tokens": "-",
            "time": "-",
            "correct": "-",
            "status": f"❌ {str(e)[:30]}"
        }

print("=== Context Window 阶梯测试 ===")
print(f"模型: {MODEL}")
print(f"测试梯度: 4K, 8K, 16K, 32K, 64K, 128K")
print("")
print("| 梯度 | Target | Actual Tokens | 响应时间 | 答案正确 | 状态 |")
print("|------|--------|---------------|----------|----------|------|")

for k in STEPS:
    result = test_context(k)
    print(f"| {result['target']} | {result['target']} | {result['tokens']} | {result['time']} | {result['correct']} | {result['status']} |")

    if "成功" not in result['status']:
        print("| ... | ... | ... | ... | ... | 停止测试 |")
        break
