#!/usr/bin/env python3
"""
Stage 3 Deep Evaluation for LLaDA2 Diffusion Model

Runs selected Stage 3 deep tests using diffusion-cli.
Adapts the 1000 test cases from stage3_deep for diffusion models.
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

# Import test cases
from math_eval import MATH_TEST_CASES
from code_eval import CODE_TEST_CASES
from logic_eval import LOGIC_TEST_CASES
from commonsense_eval import COMMONSENSE_TEST_CASES
from text_eval import TEXT_TEST_CASES
from reasoning_eval import REASONING_TEST_CASES
from knowledge_eval import KNOWLEDGE_TEST_CASES

MODEL_PATH = "/mnt/volume3/modelscope_models/wsbagnsv1/LLaDA2___0-mini-preview-GGUF/LLaDA2.0-mini-preview-Q4_0.gguf"
LLAMA_CPP_PATH = "/home/oliveagle/opt/llama.cpp"
DIFFUSION_CLI = f"{LLAMA_CPP_PATH}/build/bin/llama-diffusion-cli"


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


def extract_number(text: str) -> int:
    """Extract the first integer from text"""
    if not text:
        return None
    # Look for numbers in the text
    numbers = re.findall(r'-?\d+', text)
    if numbers:
        try:
            return int(numbers[0])
        except:
            return None
    return None


def check_answer(expected: Any, actual: str, check_type: str = "exact") -> bool:
    """Check if answer is correct"""
    if not actual:
        return False

    actual_lower = actual.lower()

    if check_type == "integer":
        # For math problems, extract number
        extracted = extract_number(actual)
        if extracted is not None and isinstance(expected, (int, float)):
            return abs(extracted - expected) < 0.01
        return str(expected) in actual

    elif check_type == "contains":
        # Check if expected string is in output
        return str(expected).lower() in actual_lower

    elif check_type == "exact":
        # For exact match
        return str(expected).lower() == actual_lower.strip()

    elif check_type == "code":
        # For code, check if it looks like code
        code_indicators = ['def ', 'class ', 'import ', 'return', '#', 'for ', 'if ', 'while ']
        return any(ind in actual for ind in code_indicators)

    elif check_type == "multiple_choice":
        # For multiple choice, check if answer letter is in output
        if isinstance(expected, str) and len(expected) == 1:
            patterns = [
                rf'答案[是为]?\s*{expected}',
                rf'选[择]?\s*{expected}',
                rf'^{expected}[\.\)]',
                rf'\s{expected}[\.\)]',
                rf'answer is {expected}',
                rf'option {expected}'
            ]
            for pattern in patterns:
                if re.search(pattern, actual_lower):
                    return True
            # Also check if answer content is mentioned
            return expected.lower() in actual_lower

    return False


def run_category_tests(category_name: str, test_cases: List[Dict], check_type: str = "exact", limit: int = 20) -> Dict:
    """Run tests for a category"""
    print(f"\n{'='*80}")
    print(f"📋 {category_name} (max {limit} cases)")
    print('='*80)

    results = []
    passed = 0

    # Select diverse test cases
    selected = test_cases[:limit] if len(test_cases) <= limit else (
        test_cases[:10] +  # First 10
        test_cases[len(test_cases)//2-5:len(test_cases)//2+5] +  # Middle 10
        test_cases[-10:]  # Last 10
    )[:limit]

    for i, case in enumerate(selected, 1):
        # Build prompt
        if 'problem' in case:
            prompt = case['problem']
        elif 'question' in case:
            prompt = case['question']
            if 'options' in case:
                prompt += "\n" + "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(case['options'])])
        elif 'prompt' in case:
            prompt = case['prompt']
        else:
            prompt = str(case)

        print(f"\n[{i}/{len(selected)}] {case.get('name', 'Test')} ({case.get('difficulty', 'Unknown')})")
        print(f"Prompt: {prompt[:80]}...")

        result = run_diffusion(prompt, steps=16, max_tokens=64)

        # Evaluate
        expected = case.get('answer', '')
        is_correct = check_answer(expected, result['output'], check_type) if expected else result['success']

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        print(f"{status} | Output: {result['output'][:60]}...")
        if expected:
            print(f"      Expected: {expected}")

        results.append({
            "id": case.get('id', i),
            "name": case.get('name', f"test_{i}"),
            "category": case.get('category', 'Unknown'),
            "difficulty": case.get('difficulty', 'Unknown'),
            "prompt": prompt,
            "expected": expected,
            "output": result['output'],
            "correct": is_correct,
            "duration": result['duration'],
            "success": result['success']
        })

    accuracy = (passed / len(results) * 100) if results else 0

    return {
        "category": category_name,
        "total": len(results),
        "passed": passed,
        "accuracy": round(accuracy, 1),
        "results": results
    }


def main():
    print("="*80)
    print("🧪 Stage 3 Deep Evaluation - LLaDA2 Diffusion Model")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Model: LLaDA2.0-mini-preview-Q4_0")
    print(f"🔧 Diffusion steps: 16, Block length: 32")
    print("="*80)

    all_results = {
        "model": "LLaDA2.0-mini-preview-Q4_0",
        "timestamp": datetime.now().isoformat(),
        "stage": 3,
        "categories": []
    }

    # Define test categories with appropriate check types
    categories = [
        ("Math Reasoning", MATH_TEST_CASES, "integer"),
        ("Code Generation", CODE_TEST_CASES, "code"),
        ("Logic Reasoning", LOGIC_TEST_CASES, "multiple_choice"),
        ("Commonsense QA", COMMONSENSE_TEST_CASES, "multiple_choice"),
        ("Text Understanding", TEXT_TEST_CASES, "contains"),
        ("Reasoning", REASONING_TEST_CASES, "multiple_choice"),
        ("Knowledge QA", KNOWLEDGE_TEST_CASES, "multiple_choice"),
    ]

    total_passed = 0
    total_cases = 0

    for cat_name, cases, check_type in categories:
        try:
            result = run_category_tests(cat_name, cases, check_type, limit=20)
            all_results["categories"].append(result)
            total_passed += result["passed"]
            total_cases += result["total"]
        except Exception as e:
            print(f"Error running {cat_name}: {e}")
            import traceback
            traceback.print_exc()
            all_results["categories"].append({
                "category": cat_name,
                "total": 0,
                "passed": 0,
                "accuracy": 0,
                "error": str(e)
            })

    # Summary
    print("\n" + "="*80)
    print("📊 STAGE 3 DEEP EVALUATION SUMMARY")
    print("="*80)

    for cat in all_results["categories"]:
        status = "✅" if cat.get("accuracy", 0) >= 60 else "⚠️" if cat.get("accuracy", 0) >= 40 else "❌"
        print(f"{status} {cat['category']:25} | {cat['passed']:2}/{cat['total']:2} | {cat['accuracy']:5.1f}%")

    overall_accuracy = (total_passed / total_cases * 100) if total_cases else 0
    print("-"*80)
    print(f"📈 Overall: {total_passed}/{total_cases} | {overall_accuracy:.1f}%")

    # Grade
    if overall_accuracy >= 80:
        grade = "A (Excellent)"
    elif overall_accuracy >= 60:
        grade = "B (Good)"
    elif overall_accuracy >= 40:
        grade = "C (Fair)"
    else:
        grade = "D (Poor)"
    print(f"🎯 Grade: {grade}")

    # Save results
    output_dir = f"eval_results/stage3/llada2"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/LLaDA2_stage3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to: {output_file}")

    return overall_accuracy


if __name__ == "__main__":
    main()
