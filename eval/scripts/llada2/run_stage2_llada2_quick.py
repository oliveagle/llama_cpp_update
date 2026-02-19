#!/usr/bin/env python3
"""
Quick Stage 2 Evaluation for LLaDA2 Diffusion Model

Runs selected stage2 tests using diffusion-cli.
Focuses on categories where diffusion models perform well.
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime

MODEL_PATH = "/mnt/volume3/modelscope_models/wsbagnsv1/LLaDA2___0-mini-preview-GGUF/LLaDA2.0-mini-preview-Q4_0.gguf"
LLAMA_CPP_PATH = "/home/oliveagle/opt/llama.cpp"
DIFFUSION_CLI = f"{LLAMA_CPP_PATH}/build/bin/llama-diffusion-cli"

# Selected test cases that work well with diffusion models
TEST_CASES = [
    # Code Generation
    {"category": "Code", "name": "Function definition", "prompt": "def greet(name):", "check": "def"},
    {"category": "Code", "name": "Loop example", "prompt": "for i in range(10):", "check": "for"},
    {"category": "Code", "name": "Import statement", "prompt": "import ", "check": "import"},
    {"category": "Code", "name": "Class definition", "prompt": "class Person:", "check": "class"},
    {"category": "Code", "name": "If statement", "prompt": "if x > 0:", "check": "if"},

    # Text Completion
    {"category": "Text", "name": "Sentence completion", "prompt": "The quick brown fox", "check": "fox"},
    {"category": "Text", "name": "Greeting", "prompt": "Hello, how are you", "check": "you"},
    {"category": "Text", "name": "Question", "prompt": "What is the weather", "check": "weather"},

    # Chinese
    {"category": "Chinese", "name": "Chinese greeting", "prompt": "你好", "check": "好"},
    {"category": "Chinese", "name": "Chinese question", "prompt": "今天", "check": "天"},

    # QA
    {"category": "QA", "name": "Capital question", "prompt": "Paris is the capital of", "check": "France"},
    {"category": "QA", "name": "Math question", "prompt": "2 + 2 equals", "check": "4"},
]


def run_diffusion(prompt: str, steps: int = 16, max_tokens: int = 32) -> dict:
    """Run diffusion generation using llama-diffusion-cli"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{LLAMA_CPP_PATH}/build/bin:{env.get('LD_LIBRARY_PATH', '')}"

    cmd = [
        DIFFUSION_CLI,
        "-m", MODEL_PATH,
        "-p", prompt,
        "--diffusion-steps", str(steps),
        "--diffusion-block-length", "32",
        "-c", "32768",
        "-n", str(max_tokens),
        "-ngl", "99"
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        duration = time.time() - start_time

        # Parse output - look for generated text after "total time:"
        output = result.stderr + result.stdout
        lines = output.split('\n')
        generated_text = ""
        found_output = False
        for line in lines:
            if found_output:
                if line.strip():
                    generated_text += line + "\n"
            elif line.startswith('total time:'):
                found_output = True

        return {
            "success": result.returncode == 0,
            "output": generated_text.strip(),
            "duration": duration,
            "error": None
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "duration": time.time() - start_time,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "duration": 0,
            "error": str(e)
        }


def main():
    print("="*80)
    print("🧪 Stage 2 Quick Evaluation - LLaDA2 Diffusion Model")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Model: LLaDA2.0-mini-preview-Q4_0")
    print("="*80)

    results = []
    categories = {}

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['category']}: {test['name']}")
        print(f"Prompt: {test['prompt']}")

        result = run_diffusion(test['prompt'])

        # Check if output contains expected pattern
        has_pattern = test['check'].lower() in result['output'].lower() if result['output'] else False

        cat = test['category']
        if cat not in categories:
            categories[cat] = {"total": 0, "success": 0, "pattern": 0}
        categories[cat]["total"] += 1
        if result['success']:
            categories[cat]["success"] += 1
        if has_pattern:
            categories[cat]["pattern"] += 1

        status = "✅" if result['success'] else "❌"
        print(f"{status} Output: {result['output'][:60]}...")

        results.append({
            **test,
            **result,
            "has_pattern": has_pattern
        })

    # Summary
    print("\n" + "="*80)
    print("📊 STAGE 2 QUICK EVALUATION SUMMARY")
    print("="*80)

    for cat, stats in categories.items():
        success_rate = stats['success'] / stats['total'] * 100
        pattern_rate = stats['pattern'] / stats['total'] * 100
        print(f"{cat:12} | Success: {stats['success']}/{stats['total']} ({success_rate:.0f}%) | Pattern: {stats['pattern']}/{stats['total']} ({pattern_rate:.0f}%)")

    total_success = sum(s['success'] for s in categories.values())
    total_tests = sum(s['total'] for s in categories.values())
    overall = total_success / total_tests * 100 if total_tests else 0

    print("-"*80)
    print(f"Overall Success Rate: {total_success}/{total_tests} ({overall:.1f}%)")

    # Save results
    output_file = f"eval_results/stage2/llada2/LLaDA2_quick_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "model": "LLaDA2.0-mini-preview-Q4_0",
            "timestamp": datetime.now().isoformat(),
            "categories": categories,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
