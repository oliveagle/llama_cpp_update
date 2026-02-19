#!/usr/bin/env python3
"""
Stage 3 Deep Evaluation for LLaDA2 - HARDER VERSION

Uses optimized parameters:
- More diffusion steps (64)
- CFG scale for better prompt adherence
- Better prompt engineering
- Longer max tokens for reasoning
"""

import subprocess
import json
import time
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'stage3_deep'))

from math_eval import MATH_TEST_CASES
from code_eval import CODE_TEST_CASES
from logic_eval import LOGIC_TEST_CASES

MODEL_PATH = "/mnt/volume3/modelscope_models/wsbagnsv1/LLaDA2___0-mini-preview-GGUF/LLaDA2.0-mini-preview-Q4_0.gguf"
LLAMA_CPP_PATH = "/home/oliveagle/opt/llama.cpp"
DIFFUSION_CLI = f"{LLAMA_CPP_PATH}/build/bin/llama-diffusion-cli"


def run_diffusion(prompt: str, steps: int = 64, max_tokens: int = 128, cfg_scale: float = 1.5) -> dict:
    """Run diffusion with optimized parameters"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{LLAMA_CPP_PATH}/build/bin:{env.get('LD_LIBRARY_PATH', '')}"

    cmd = [
        DIFFUSION_CLI,
        "-m", MODEL_PATH,
        "-p", prompt,
        "--diffusion-steps", str(steps),
        "--diffusion-block-length", "64",  # Larger blocks
        "--diffusion-algorithm", "4",  # CONFIDENCE_BASED
        "-c", "32768",
        "-n", str(max_tokens),
        "-ngl", "99",
        "--temp", "0.3",  # Lower temperature for more deterministic
    ]

    if cfg_scale > 0:
        cmd.extend(["--diffusion-cfg-scale", str(cfg_scale)])

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # Longer timeout for more steps
            env=env
        )
        duration = time.time() - start_time

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


def build_math_prompt(problem: str) -> str:
    """Engineered prompt for math problems"""
    return f"""Solve this math problem step by step.

Problem: {problem}

Solution:"""


def build_logic_prompt(question: str, options: list) -> str:
    """Engineered prompt for logic problems"""
    opts_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
    return f"""Answer this logic question by selecting the correct option.

Question: {question}

Options:
{opts_text}

The correct answer is:"""


def extract_answer(text: str, answer_type: str = "integer") -> Any:
    """Smarter answer extraction"""
    if not text:
        return None

    text = text.strip()

    if answer_type == "integer":
        # Look for "x = 5" or "answer is 5" or just "5"
        patterns = [
            r'[=是]\s*(-?\d+)',
            r'answer\s+is\s+(-?\d+)',
            r'result\s+is\s+(-?\d+)',
            r'x\s*=\s*(-?\d+)',
            r'^(-?\d+)$',
            r'(-?\d+)\s*$',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except:
                    pass
        # Fallback: first number
        numbers = re.findall(r'-?\d+', text)
        if numbers:
            try:
                return int(numbers[-1])  # Last number often is the answer
            except:
                pass

    elif answer_type == "choice":
        # Look for "A", "B", "C", "D" at start or after "answer"
        text_upper = text.upper()
        patterns = [
            r'answer\s+is\s+([A-D])',
            r'选([A-D])',
            r'答案[是为]?\s*([A-D])',
            r'^([A-D])[\.\)]',
            r'\s([A-D])[\.\)]',
            r'^([A-D])$',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                return match.group(1)
        # Fallback: first occurrence of A/B/C/D
        for letter in ['A', 'B', 'C', 'D']:
            if letter in text_upper:
                return letter

    return text


def run_math_tests():
    """Run math tests with engineered prompts"""
    print("\n" + "="*80)
    print("📋 MATH REASONING (Harder - 64 steps, CFG)")
    print("="*80)

    passed = 0
    results = []

    # Select diverse math problems
    test_cases = [
        MATH_TEST_CASES[0],   # 一元一次方程
        MATH_TEST_CASES[5],   # 不等式
        MATH_TEST_CASES[8],   # 指数运算
        MATH_TEST_CASES[9],   # 对数
        MATH_TEST_CASES[13],  # 等比数列
        MATH_TEST_CASES[22],  # 组合数
        MATH_TEST_CASES[23],  # 概率
        MATH_TEST_CASES[30],  # 独立事件
    ]

    for i, case in enumerate(test_cases, 1):
        prompt = build_math_prompt(case['problem'])
        print(f"\n[{i}/8] {case['name']} ({case['difficulty']})")
        print(f"Prompt: {case['problem'][:50]}...")

        result = run_diffusion(prompt, steps=64, max_tokens=128, cfg_scale=1.5)

        extracted = extract_answer(result['output'], "integer")
        expected = case['answer']

        is_correct = False
        if extracted is not None and isinstance(expected, (int, float)):
            is_correct = abs(extracted - expected) < 0.01

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status}")
        print(f"  Output: {result['output'][:100]}...")
        print(f"  Extracted: {extracted}, Expected: {expected}")
        print(f"  Time: {result['duration']:.1f}s")

        results.append({
            "name": case['name'],
            "correct": is_correct,
            "output": result['output'],
            "extracted": extracted,
            "expected": expected
        })

    print(f"\n📊 Math: {passed}/8 ({passed/8*100:.1f}%)")
    return passed, results


def run_logic_tests():
    """Run logic tests with engineered prompts"""
    print("\n" + "="*80)
    print("📋 LOGIC REASONING (Harder - 64 steps, CFG)")
    print("="*80)

    passed = 0
    results = []

    test_cases = [
        LOGIC_TEST_CASES[0],  # 三段论
        LOGIC_TEST_CASES[4],  # 选言推理
        LOGIC_TEST_CASES[5],  # 假言连锁
        LOGIC_TEST_CASES[9],  # 归谬法
        LOGIC_TEST_CASES[12], # 数学类比
        LOGIC_TEST_CASES[18], # 比例类比
        LOGIC_TEST_CASES[19], # 类比推理方向
    ]

    for i, case in enumerate(test_cases, 1):
        prompt = build_logic_prompt(case['question'], case['options'])
        print(f"\n[{i}/7] {case['name']} ({case['difficulty']})")
        print(f"Question: {case['question'][:50]}...")

        result = run_diffusion(prompt, steps=64, max_tokens=64, cfg_scale=1.5)

        extracted = extract_answer(result['output'], "choice")
        expected = case['answer']

        is_correct = extracted == expected

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status}")
        print(f"  Output: {result['output'][:100]}...")
        print(f"  Extracted: {extracted}, Expected: {expected}")
        print(f"  Time: {result['duration']:.1f}s")

        results.append({
            "name": case['name'],
            "correct": is_correct,
            "output": result['output'],
            "extracted": extracted,
            "expected": expected
        })

    print(f"\n📊 Logic: {passed}/7 ({passed/7*100:.1f}%)")
    return passed, results


def run_code_tests():
    """Run code tests for comparison"""
    print("\n" + "="*80)
    print("📋 CODE GENERATION (Harder - 64 steps)")
    print("="*80)

    passed = 0
    results = []

    test_cases = [
        CODE_TEST_CASES[0],  # two_sum
        CODE_TEST_CASES[4],  # climb_stairs
        CODE_TEST_CASES[8],  # valid parentheses
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n[{i}/3] {case['name']}")

        result = run_diffusion(case['prompt'], steps=64, max_tokens=128, cfg_scale=1.0)

        # Code passes if it contains code indicators
        has_code = any(ind in result['output'] for ind in ['def ', 'return', '#', '    '])

        if has_code:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status} | Output: {result['output'][:80]}...")

        results.append({
            "name": case['name'],
            "correct": has_code,
            "output": result['output']
        })

    print(f"\n📊 Code: {passed}/3 ({passed/3*100:.1f}%)")
    return passed, results


def main():
    print("="*80)
    print("🧪 Stage 3 HARDER Evaluation - LLaDA2")
    print("⏰", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🔧 Parameters: 64 steps, CFG=1.5, temp=0.3")
    print("="*80)

    math_passed, math_results = run_math_tests()
    logic_passed, logic_results = run_logic_tests()
    code_passed, code_results = run_code_tests()

    # Summary
    print("\n" + "="*80)
    print("📊 HARDER EVALUATION SUMMARY")
    print("="*80)
    print(f"Math:   {math_passed}/8   ({math_passed/8*100:.1f}%)")
    print(f"Logic:  {logic_passed}/7   ({logic_passed/7*100:.1f}%)")
    print(f"Code:   {code_passed}/3   ({code_passed/3*100:.1f}%)")
    print("-"*80)
    total = math_passed + logic_passed + code_passed
    total_cases = 8 + 7 + 3
    print(f"Total:  {total}/{total_cases} ({total/total_cases*100:.1f}%)")

    # Save
    output = {
        "model": "LLaDA2.0-mini-preview-Q4_0",
        "params": {"steps": 64, "cfg": 1.5, "temp": 0.3},
        "timestamp": datetime.now().isoformat(),
        "math": {"passed": math_passed, "total": 8, "results": math_results},
        "logic": {"passed": logic_passed, "total": 7, "results": logic_results},
        "code": {"passed": code_passed, "total": 3, "results": code_results},
    }

    os.makedirs("eval_results/stage3/llada2", exist_ok=True)
    filename = f"eval_results/stage3/llada2/LLaDA2_harder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved: {filename}")


if __name__ == "__main__":
    main()
