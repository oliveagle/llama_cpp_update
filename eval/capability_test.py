#!/usr/bin/env python3
"""
第二层测试 - 模型入门能力测试
测试维度：基础对话、代码能力、逻辑推理、角色扮演、长文本理解
"""

import requests
import json
import time
import sys
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8400/v1/chat/completions"
TIMEOUT = 120  # 8K context 预期响应时间

# 测试模型列表
MODELS = [
    "MiniCPM-o-4_5-Q4_K_M",
    "Qwen3-Coder-Next-Q4_K_M",
    "Qwen3VL-4B-Instruct-Q8_0",
    "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0",
    "GLM-4.7-Flash-Q4_K_M",
    "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL",
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
    "MiroThinker-v1.5-30B.Q8_0",
]

# 测试用例
TEST_CASES = [
    {
        "name": "基础对话-中文",
        "category": "basic_conversation",
        "messages": [{"role": "user", "content": "你好，请介绍一下你自己。"}],
        "check_keywords": ["助手", "AI", "帮助"],
    },
    {
        "name": "基础对话-英文",
        "category": "basic_conversation",
        "messages": [{"role": "user", "content": "Hello! Please introduce yourself."}],
        "check_keywords": ["assistant", "AI", "help"],
    },
    {
        "name": "代码能力-Python",
        "category": "coding",
        "messages": [{"role": "user", "content": "Write a Python function to calculate Fibonacci numbers. Include error handling for negative inputs."}],
        "check_keywords": ["def", "fibonacci", "return"],
    },
    {
        "name": "逻辑推理-数学题",
        "category": "reasoning",
        "messages": [{"role": "user", "content": "如果3个工人3天可以建3座房子，那么6个工人建6座房子需要多少天？请解释你的推理过程。"}],
        "check_keywords": ["3", "天", "房子"],
    },
    {
        "name": "角色扮演-翻译官",
        "category": "roleplay",
        "messages": [
            {"role": "user", "content": "请扮演一位专业的中英翻译官，将以下句子翻译成英文：人工智能正在改变世界。"}
        ],
        "check_keywords": ["artificial intelligence", "changing", "world"],
    },
]

def call_model(model, messages, max_tokens=512):
    """调用模型 API"""
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.8,
    }

    start_time = time.time()
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=TIMEOUT)
        elapsed = time.time() - start_time

        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}", "time": elapsed}

        data = resp.json()
        content = data["choices"][0]["message"].get("content", "")
        return {"success": True, "content": content, "time": elapsed}
    except requests.Timeout:
        return {"success": False, "error": "Timeout", "time": TIMEOUT}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start_time}

def check_response(content, keywords):
    """检查响应是否包含关键词"""
    content_lower = content.lower()
    matched = [kw for kw in keywords if kw.lower() in content_lower]
    return len(matched) >= len(keywords) // 2  # 至少匹配一半关键词

def run_test(model, test_case):
    """运行单个测试用例"""
    print(f"  📝 {test_case['name']}...", end=" ", flush=True)

    result = call_model(model, test_case["messages"])

    if not result["success"]:
        print(f"❌ FAIL ({result['error']}, {result['time']:.1f}s)")
        return {"passed": False, "error": result["error"], "time": result["time"]}

    # 检查关键词
    passed = check_response(result["content"], test_case["check_keywords"])
    status = "✅ PASS" if passed else "⚠️ WEAK"
    print(f"{status} ({result['time']:.1f}s)")

    return {
        "passed": passed,
        "time": result["time"],
        "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
    }

def test_model(model):
    """测试单个模型的所有用例"""
    print(f"\n{'='*60}")
    print(f"🤖 测试模型: {model}")
    print(f"{'='*60}")

    results = {}
    for test_case in TEST_CASES:
        results[test_case["name"]] = run_test(model, test_case)
        time.sleep(0.5)  # 避免请求过快

    # 统计
    passed = sum(1 for r in results.values() if r.get("passed"))
    total = len(TEST_CASES)
    avg_time = sum(r["time"] for r in results.values()) / total

    print(f"\n  📊 结果: {passed}/{total} 通过 | 平均响应: {avg_time:.1f}s")

    return {
        "model": model,
        "passed": passed,
        "total": total,
        "pass_rate": passed / total,
        "avg_time": avg_time,
        "details": results
    }

def main():
    print("=" * 70)
    print("🧪 llama.cpp Vulkan 第二层测试 - 入门能力测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 服务端点: {BASE_URL}")
    print(f"⏱️  超时设置: {TIMEOUT}s")
    print("=" * 70)

    all_results = []

    for model in MODELS:
        try:
            result = test_model(model)
            all_results.append(result)
        except KeyboardInterrupt:
            print("\n\n用户中断测试")
            break
        except Exception as e:
            print(f"\n  ❌ 测试异常: {e}")
            all_results.append({"model": model, "error": str(e)})

    # 汇总报告
    print("\n" + "=" * 70)
    print("📋 测试汇总")
    print("=" * 70)

    for r in all_results:
        if "error" in r:
            print(f"  ❌ {r['model']}: 异常 - {r['error']}")
        else:
            status = "✅" if r["pass_rate"] >= 0.8 else "⚠️" if r["pass_rate"] >= 0.5 else "❌"
            print(f"  {status} {r['model']}: {r['passed']}/{r['total']} ({r['pass_rate']*100:.0f}%) | 平均 {r['avg_time']:.1f}s")

    # 保存详细报告
    report_file = f"/mnt/volume3/llama_cpp/eval_results/capability_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "endpoint": BASE_URL,
            "timeout": TIMEOUT,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 详细报告已保存: {report_file}")

if __name__ == "__main__":
    main()
