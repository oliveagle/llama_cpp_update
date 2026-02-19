#!/usr/bin/env python3
"""
LLaDA2 Diffusion Model Test

Tests LLaDA2 using the diffusion-cli tool since it's a diffusion model,
not an autoregressive model.
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

# Simple test cases for diffusion model
TEST_CASES = [
    {
        "category": "text_completion",
        "prompt": "The quick brown fox",
        "description": "Simple text completion"
    },
    {
        "category": "qa",
        "prompt": "Q: What is the capital of France? A:",
        "description": "Question answering"
    },
    {
        "category": "code",
        "prompt": "def hello_world():",
        "description": "Code generation"
    },
    {
        "category": "math",
        "prompt": "Solve: 2 + 2 =",
        "description": "Simple math"
    },
    {
        "category": "chinese",
        "prompt": "中国的首都是",
        "description": "Chinese text"
    }
]


def run_diffusion(prompt: str, steps: int = 16, max_tokens: int = 64) -> dict:
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
            timeout=120,
            env=env
        )
        duration = time.time() - start_time

        # Parse output - look for the generated text after parameters
        output = result.stderr + result.stdout

        # Extract the generated text (after diffusion params)
        lines = output.split('\n')
        generated_text = ""
        found_output = False
        for line in lines:
            if found_output:
                generated_text += line + "\n"
            elif line.strip() and not line.startswith(('diffusion_params', 'ggml_', 'main:')):
                if 'mask_token_id' in line or 'steps' in line or 'max_length' in line:
                    continue
                if line.startswith('total time:'):
                    found_output = True

        return {
            "success": result.returncode == 0,
            "output": generated_text.strip(),
            "duration": duration,
            "error": result.stderr if result.returncode != 0 else None
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
    print("=" * 80)
    print("🧪 LLaDA2 Diffusion Model Test")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Model: LLaDA2.0-mini-preview-Q4_0")
    print(f"🔧 Steps: 16, Block length: 32")
    print("=" * 80)

    results = []
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] {test['category']}: {test['description']}")
        print(f"Prompt: {test['prompt'][:50]}...")

        result = run_diffusion(test['prompt'])
        results.append({
            **test,
            **result
        })

        if result['success']:
            print(f"✅ Success ({result['duration']:.1f}s)")
            print(f"Output: {result['output'][:100]}...")
        else:
            print(f"❌ Failed: {result['error'][:100]}...")

    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Summary")
    print("=" * 80)

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['category']:15} | {r['duration']:.1f}s | {r['description']}")

    print(f"\nTotal: {passed}/{total} passed ({passed/total*100:.0f}%)")

    # Save results
    output_file = f"eval_results/llada2_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("eval_results", exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump({
            "model": "LLaDA2.0-mini-preview-Q4_0",
            "timestamp": datetime.now().isoformat(),
            "total_tests": total,
            "passed": passed,
            "results": results
        }, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
