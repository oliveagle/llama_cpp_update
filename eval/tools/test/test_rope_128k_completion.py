#!/usr/bin/env python3
"""
使用 /v1/completions 端点测试 RoPE 缩放的 128K 支持
"""
import requests
import time

def test_context(ctx_size):
    """测试指定 context 大小"""
    print(f"\n{'='*60}")
    print(f"测试 Context: {ctx_size:,} tokens ({ctx_size//1024}K)")
    print(f"{'='*60}")

    # 生成 prompt (估算: 1 token ≈ 4 个英文字符)
    prompt = "This is a test sentence for long context testing. " * (ctx_size // 4)

    start = time.time()
    try:
        resp = requests.post(
            'http://localhost:8401/v1/completions',
            json={
                'model': 'Qwen3-0.6B-Q4_0.gguf',
                'prompt': prompt,
                'max_tokens': 10,
                'temperature': 0.7
            },
            timeout=300
        )
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            prompt_tokens = data['usage']['prompt_tokens']
            completion_tokens = data['usage']['completion_tokens']

            print(f"✅ 成功!")
            print(f"   Prompt tokens: {prompt_tokens:,}")
            print(f"   Completion tokens: {completion_tokens}")
            print(f"   总耗时: {elapsed:.2f}s")

            return {
                'context': ctx_size,
                'prompt_tokens': prompt_tokens,
                'time': round(elapsed, 2),
                'status': 'success'
            }
        else:
            error = resp.json().get('error', {})
            print(f"❌ 失败: {error.get('message', 'unknown')[:100]}")
            return {'context': ctx_size, 'status': 'error'}

    except Exception as e:
        print(f"❌ 错误: {e}")
        return {'context': ctx_size, 'status': 'exception'}

def main():
    print("="*60)
    print("RoPE 缩放 128K 测试 (/v1/completions)")
    print("="*60)

    # 测试梯度
    test_sizes = [32768, 49152, 65536, 98304, 131072]
    results = []

    for size in test_sizes:
        result = test_context(size)
        results.append(result)

        if result['status'] != 'success':
            print(f"\n在 {size} 停止测试")
            break

    # 汇总
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")

    success = [r for r in results if r['status'] == 'success']
    print(f"成功: {len(success)}/{len(results)}")

    if success:
        max_ctx = max(r['context'] for r in success)
        print(f"最大支持 Context: {max_ctx:,} tokens")

        if max_ctx >= 131072:
            print("🎉 成功突破 128K！")
        elif max_ctx >= 65536:
            print("✅ 达到 64K")
        elif max_ctx >= 32768:
            print("⚠️  达到 32K")

if __name__ == "__main__":
    main()
