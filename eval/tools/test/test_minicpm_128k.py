#!/usr/bin/env python3
"""测试 MiniCPM-o-4.5 的 128K context"""
import requests

# 生成精确的128K tokens测试文本 (约128000个中文字符)
# 使用中英文混合文本，平均每token约1个中文字符
text = "人工智能技术在自然语言处理领域取得了显著进展，大语言模型能够理解和生成人类语言，应用于对话系统、文本摘要、机器翻译等多个领域。"
# 重复足够的次数以达到128K tokens
repeat_count = 128000 // len(text) + 1
long_text = (text * repeat_count)[:128000]

print(f"测试文本长度: {len(long_text)} 字符")
print(f"目标 context: 128K (131072)")
print("-" * 50)

try:
    resp = requests.post(
        "http://localhost:8401/v1/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": "MiniCPM-o-4.5",
            "prompt": long_text,
            "max_tokens": 10,
            "temperature": 0.1
        },
        timeout=300
    )

    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ 128K 测试成功!")
        print(f"   生成tokens: {len(result.get('choices', [{}])[0].get('text', ''))}")
    else:
        print(f"❌ 失败: HTTP {resp.status_code}")
        print(f"   错误: {resp.text[:200]}")
except Exception as e:
    print(f"❌ 异常: {e}")
