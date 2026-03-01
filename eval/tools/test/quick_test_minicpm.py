#!/usr/bin/env python3
"""快速测试 MiniCPM-o-4.5 的 context 限制"""
import requests

def test_context(target_ctx, port=8401):
    """测试指定context大小"""
    text = "人工智能技术在自然语言处理领域取得了显著进展。" * (target_ctx // 10)
    prompt = text[:target_ctx * 3]

    try:
        resp = requests.post(
            f"http://localhost:{port}/v1/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "MiniCPM-o-4.5",
                "prompt": prompt,
                "max_tokens": 5,
                "temperature": 0.1
            },
            timeout=120
        )
        return resp.status_code == 200, resp.status_code
    except Exception as e:
        return False, str(e)

# 测试不同context大小
contexts = [8192, 16384, 32768, 65536, 98304, 131072]
print("MiniCPM-o-4.5 Context 测试:")
print("-" * 50)

for ctx in contexts:
    success, code = test_context(ctx)
    status = "✅" if success else "❌"
    print(f"  {status} Context {ctx:,}: {'成功' if success else code}")
