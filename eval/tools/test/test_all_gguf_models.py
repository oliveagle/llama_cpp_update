#!/usr/bin/env python3
"""
测试所有非Qwen GGUF模型的Context限制
目标：验证每个模型能否达到32K/64K/128K context
"""
import requests
import json
import time
import subprocess
import sys
from datetime import datetime

# 测试配置
TEST_CONTEXTS = [8192, 16384, 32768, 65536, 98304, 131072]
PORT = 8401
BASE_URL = f"http://localhost:{PORT}"

# 需要测试的模型列表
MODELS_TO_TEST = [
    {
        "name": "MiniCPM-o-4.5-Q4_K_M",
        "path": "/mnt/volume3/modelscope_models/OpenBMB/MiniCPM-o-4_5-gguf/MiniCPM-o-4_5-Q4_K_M.gguf",
        "arch": "qwen3",
        "native_ctx": 40960,
        "rope_scale": 3.2,  # 40K -> 128K
        "size_gb": 4.7,
        "chat_template": "qwen2"
    },
    {
        "name": "JoyAI-LLM-Flash-Q4_K_M",
        "path": "/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf",
        "arch": "deepseek2",
        "native_ctx": 131072,
        "rope_scale": None,  # 原生支持128K
        "size_gb": 28,
        "chat_template": "chatglm3"
    }
]

def generate_prompt(token_count):
    """生成指定token数量的测试文本"""
    # 重复中文文本以达到目标长度
    base_text = "人工智能技术在自然语言处理领域取得了显著进展。大型语言模型能够理解和生成人类语言，应用于对话系统、文本摘要、机器翻译等多个领域。"
    multiplier = (token_count * 3) // len(base_text) + 1
    long_text = base_text * multiplier
    return long_text[:token_count * 3]  # 约3字节一个中文字符

def test_model_context(model_info, target_ctx):
    """测试指定模型在目标context下的表现"""
    prompt = generate_prompt(target_ctx)
    prompt_tokens = len(prompt) // 3

    try:
        response = requests.post(
            f"{BASE_URL}/v1/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": model_info["name"],
                "prompt": prompt,
                "max_tokens": 10,
                "temperature": 0.1
            },
            timeout=300
        )

        if response.status_code == 200:
            result = response.json()
            generated_tokens = len(result.get("choices", [{}])[0].get("text", ""))
            return {
                "status": "success",
                "prompt_tokens": prompt_tokens,
                "generated_tokens": generated_tokens,
                "response": result
            }
        else:
            return {
                "status": "error",
                "code": response.status_code,
                "message": response.text[:200]
            }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "message": "Request timed out"}
    except Exception as e:
        return {"status": "exception", "message": str(e)}

def main():
    print("=" * 80)
    print("非Qwen GGUF模型 Context 测试报告")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results = {}

    for model in MODELS_TO_TEST:
        print(f"\n{'='*80}")
        print(f"模型: {model['name']}")
        print(f"架构: {model['arch']}")
        print(f"原生Context: {model['native_ctx']:,}")
        print(f"RoPE Scale: {model['rope_scale'] or 'N/A (原生支持)'}")
        print(f"模型大小: {model['size_gb']} GB")
        print("=" * 80)

        model_results = []

        for ctx in TEST_CONTEXTS:
            if ctx > model['native_ctx'] * 4:
                print(f"  跳过 {ctx:,} (超过RoPE缩放上限)")
                continue

            print(f"\n  测试 Context: {ctx:,} ... ", end="", flush=True)

            result = test_model_context(model, ctx)
            model_results.append({
                "target_ctx": ctx,
                **result
            })

            if result["status"] == "success":
                print(f"✅ 成功 (Prompt: {result['prompt_tokens']:,} tokens)")
            elif result["status"] == "timeout":
                print(f"⏱️ 超时")
            else:
                print(f"❌ 失败 ({result.get('message', 'Unknown')[:50]})")

        results[model['name']] = model_results

    # 打印汇总
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)

    for model_name, model_results in results.items():
        print(f"\n{model_name}:")
        print("-" * 60)
        print(f"{'Context':<12} {'状态':<10} {'实际Tokens':<15} {'备注'}")
        print("-" * 60)

        for r in model_results:
            ctx = f"{r['target_ctx']:,}"
            status = "✅" if r['status'] == 'success' else ("⏱️" if r['status'] == 'timeout' else '❌')
            tokens = f"{r.get('prompt_tokens', 'N/A'):,}" if r.get('prompt_tokens') else "N/A"
            note = ""
            if r['status'] != 'success':
                note = r.get('message', 'Unknown')[:30]
            print(f"{ctx:<12} {status:<10} {tokens:<15} {note}")

    # 保存详细结果
    report_path = f"eval_results/ALL_GGUF_MODELS_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "models": MODELS_TO_TEST,
            "results": results
        }, f, indent=2)

    print(f"\n详细结果已保存: {report_path}")

if __name__ == "__main__":
    main()
