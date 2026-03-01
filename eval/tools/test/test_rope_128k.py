#!/usr/bin/env python3
"""
测试 RoPE 缩放的 128K 支持
"""
import requests
import sys

def test_context(ctx_size):
    """测试指定 context 大小"""
    print(f"\n{'='*60}")
    print(f"测试 Context: {ctx_size:,} tokens")
    print(f"{'='*60}")

    prompt = "这是一个测试长上下文能力的句子。" * (ctx_size // 10)

    try:
        resp = requests.post(
            'http://localhost:8401/v1/chat/completions',
            json={
                'model': 'Qwen3-0.6B-Q4_0',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 10
            },
            timeout=120
        )

        if resp.status_code == 200:
            data = resp.json()
            prompt_tokens = data['usage']['prompt_tokens']
            print(f"✅ 成功! Prompt tokens: {prompt_tokens:,}")
            return True
        else:
            error = resp.json().get('error', {})
            print(f"❌ 失败: {error.get('message', 'unknown')[:100]}")
            return False

    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

# 测试梯度
print("="*60)
print("RoPE 缩放 128K 测试")
print("="*60)

test_sizes = [32768, 49152, 65536, 98304, 131072]
results = []

for size in test_sizes:
    success = test_context(size)
    results.append((size, success))
    if not success:
        print(f"\n在 {size} 停止测试")
        break

# 汇总
print(f"\n{'='*60}")
print("测试结果汇总")
print(f"{'='*60}")

success_count = sum(1 for _, s in results if s)
total_count = len(results)

print(f"成功: {success_count}/{total_count}")

if success_count > 0:
    max_ctx = max(size for size, s in results if s)
    print(f"最大支持 Context: {max_ctx:,} tokens")

    if max_ctx >= 131072:
        print("🎉 成功突破 128K！")
    elif max_ctx >= 65536:
        print("✅ 达到 64K")
    elif max_ctx >= 32768:
        print("⚠️  达到 32K")
