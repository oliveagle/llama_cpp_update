#!/usr/bin/env python3
"""
快速测试多个模型的原生 context 限制
用于决定哪个模型值得做 RoPE 缩放突破
"""

import requests
import time

MODEL_URL = "http://localhost:8401"

# 要测试的模型
MODELS = [
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
    "Qwen3VL-4B-Instruct-Q8_0",
    "GLM-4.7-Flash-Q4_K_M",
    "JoyAI-LLM-Flash-Q4_K_M"
]

# 测试阶梯
TEST_CONTEXTS = [8192, 16384, 24576, 32768, 40960]

def test_model_context(model: str, ctx_size: int) -> dict:
    """测试指定模型的 context"""
    prompt = "Test sentence for context testing. " * (ctx_size // 4)

    try:
        start = time.time()
        resp = requests.post(
            f"{MODEL_URL}/v1/completions",
            json={
                "model": model,
                "prompt": prompt,
                "max_tokens": 5
            },
            timeout=60
        )
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            return {
                "model": model,
                "ctx": ctx_size,
                "status": "success",
                "tokens": data["usage"]["prompt_tokens"],
                "time": f"{elapsed:.1f}s"
            }
        else:
            error = resp.json().get("error", {})
            msg = error.get("message", "")
            if "exceeds" in msg:
                import re
                m = re.search(r'size \((\d+)\)', msg)
                limit = int(m.group(1)) if m else 0
                return {
                    "model": model,
                    "ctx": ctx_size,
                    "status": "limit",
                    "limit": limit
                }
            return {"model": model, "ctx": ctx_size, "status": "error", "error": msg[:50]}

    except requests.exceptions.Timeout:
        return {"model": model, "ctx": ctx_size, "status": "timeout"}
    except Exception as e:
        return {"model": model, "ctx": ctx_size, "status": "exception", "error": str(e)[:50]}


def main():
    print("="*70)
    print("快速 Context 限制测试 (用于选择 RoPE 突破目标)")
    print("="*70)
    print(f"服务器: {MODEL_URL}")
    print(f"测试模型: {len(MODELS)} 个")
    print(f"测试阶梯: {[f'{c//1024}K' for c in TEST_CONTEXTS]}")
    print("="*70)

    results = {}

    for model in MODELS:
        print(f"\n测试 {model}:")
        results[model] = []

        for ctx in TEST_CONTEXTS:
            result = test_model_context(model, ctx)
            results[model].append(result)

            if result["status"] == "success":
                print(f"  {ctx//1024:2d}K: ✅ {result['tokens']:,} tokens ({result['time']})")
            elif result["status"] == "limit":
                limit_k = result.get("limit", 0) // 1024
                print(f"  {ctx//1024:2d}K: ❌ 限制 ~{limit_k}K")
                break  # 遇到限制就停止这个模型
            elif result["status"] == "timeout":
                print(f"  {ctx//1024:2d}K: ⏱️  超时")
                break
            else:
                print(f"  {ctx//1024:2d}K: ❌ {result.get('error', 'unknown')[:30]}")
                break

    # 汇总
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)

    for model, model_results in results.items():
        success_tests = [r for r in model_results if r["status"] == "success"]
        if success_tests:
            max_ctx = max(r["ctx"] for r in success_tests)
            print(f"{model:35s}: ✅ 最大 {max_ctx//1024}K")
        else:
            first_result = model_results[0] if model_results else {}
            if first_result.get("status") == "limit":
                limit = first_result.get("limit", 0)
                print(f"{model:35s}: ⚠️  限制 ~{limit//1024}K")
            else:
                print(f"{model:35s}: ❌ 测试失败")

    # 推荐突破目标
    print("\n" + "="*70)
    print("RoPE 突破建议")
    print("="*70)

    for model, model_results in results.items():
        success_tests = [r for r in model_results if r["status"] == "success"]
        if success_tests:
            max_ctx = max(r["ctx"] for r in success_tests)
            if max_ctx >= 32768:
                target = min(max_ctx * 4, 131072)  # 目标 4x 或 128K
                print(f"{model:35s}: {max_ctx//1024}K → {target//1024}K (RoPE scale={target/max_ctx:.1f})")


if __name__ == "__main__":
    main()
