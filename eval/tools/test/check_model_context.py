#!/usr/bin/env python3
"""
检查所有可用模型的原生 context 长度
"""
import requests

def check_model_context(model_name):
    """检查模型的 context 信息"""
    try:
        # 用短请求获取模型信息
        resp = requests.post(
            'http://localhost:8401/v1/completions',
            json={
                'model': model_name,
                'prompt': 'Test',
                'max_tokens': 1
            },
            timeout=30
        )

        if resp.status_code == 200:
            # 从响应头或模型信息推断
            return "可用"
        else:
            error = resp.json().get('error', {})
            msg = error.get('message', '')
            if 'n_ctx_train' in msg:
                # 提取训练 context
                import re
                match = re.search(r'n_ctx_train\s*[=:]\s*(\d+)', msg)
                if match:
                    return f"训练限制: {match.group(1)}"
            return f"错误: {msg[:50]}"
    except Exception as e:
        return f"异常: {str(e)[:50]}"

# 所有模型
models = [
    "Qwen3-0.6B-Q4_0",
    "Alibaba-Apsara.DASD-4B-Thinking.Q8_0",
    "GLM-4.7-Flash-Q4_K_M",
    "JoyAI-LLM-Flash-Q4_K_M",
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
    "Qwen3VL-4B-Instruct-Q8_0",
    "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0",
]

print("="*60)
print("模型 Context 限制检查")
print("="*60)

# 首先测试一个大 context 来触发错误信息
for model in models:
    print(f"\n检查 {model}...")

    # 测试 50K context
    long_prompt = "Test sentence. " * 10000

    try:
        resp = requests.post(
            'http://localhost:8401/v1/completions',
            json={
                'model': model,
                'prompt': long_prompt,
                'max_tokens': 1
            },
            timeout=60
        )

        if resp.status_code == 200:
            tokens = resp.json()['usage']['prompt_tokens']
            print(f"  ✅ 支持 50K+ (实际: {tokens:,} tokens)")
        else:
            error = resp.json().get('error', {}).get('message', '')
            if 'exceeds' in error:
                import re
                # 提取限制值
                match = re.search(r'available context size \((\d+)\)', error)
                if match:
                    limit = int(match.group(1))
                    print(f"  ⚠️  限制: {limit:,} tokens (~{limit//1024}K)")
                else:
                    print(f"  ⚠️  限制: {error[:60]}")
            else:
                print(f"  ❌ 错误: {error[:60]}")
    except Exception as e:
        print(f"  ❌ 异常: {str(e)[:60]}")
