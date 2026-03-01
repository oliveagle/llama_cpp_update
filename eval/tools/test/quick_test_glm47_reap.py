#!/usr/bin/env python3
"""测试 GLM-4.7-Flash-REAP 的 context 限制 (原生202K)"""
import requests

def test_context(target_ctx, port=8401):
    """测试指定context大小"""
    text = "人工智能技术在自然语言处理领域取得了显著进展。大语言模型能够理解和生成人类语言，应用于对话系统、文本摘要、机器翻译等多个领域。"
    # 每token约3个字符（中文）
    repeat = (target_ctx * 3) // len(text) + 1
    prompt = (text * repeat)[:target_ctx * 3]

    try:
        resp = requests.post(
            f"http://localhost:{port}/v1/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "GLM-4.7-Flash-REAP",
                "prompt": prompt,
                "max_tokens": 5,
                "temperature": 0.1
            },
            timeout=300
        )
        return resp.status_code == 200, resp.status_code, len(prompt)
    except Exception as e:
        return False, str(e), 0

# 测试不同context大小
contexts = [8192, 16384, 32768, 65536, 98304, 131072]
print("GLM-4.7-Flash-REAP Context 测试 (原生202K支持):")
print("-" * 50)

for ctx in contexts:
    success, code, actual_len = test_context(ctx)
    status = "✅" if success else "❌"
    actual_tokens = actual_len // 3
    print(f"  {status} Context {ctx:,}: {'成功' if success else code} (实际: ~{actual_tokens:,} tokens)")
