#!/usr/bin/env python3
"""
Stage 2 Evaluation for LLaDA2 Diffusion Model

Runs comprehensive stage2 tests using diffusion-cli since LLaDA2
does not support standard OpenAI API (it's a diffusion model).
"""

import subprocess
import json
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = "/mnt/volume3/modelscope_models/wsbagnsv1/LLaDA2___0-mini-preview-GGUF/LLaDA2.0-mini-preview-Q4_0.gguf"
LLAMA_CPP_PATH = "/home/oliveagle/opt/llama.cpp"
DIFFUSION_CLI = f"{LLAMA_CPP_PATH}/build/bin/llama-diffusion-cli"

# Import test cases from stage2 framework
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests', 'stage2_basic'))
from text_eval import TEXT_TEST_CASES
from code_eval import CODE_TEST_CASES
from math_eval import MATH_TEST_CASES
from reasoning_eval import REASONING_TEST_CASES
from knowledge_eval import KNOWLEDGE_TEST_CASES
from translation_eval import TRANSLATION_TEST_CASES
from summarization_eval import SUMMARIZATION_TEST_CASES
from safety_eval import SAFETY_TEST_CASES
from multiturn_eval import MULTITURN_TEST_CASES


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

        # Parse output - look for generated text after "total time:"
        output = result.stderr + result.stdout

        # Extract the generated text (after total time line)
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


def evaluate_response(expected_answer: str, actual_output: str, question_type: str = "text") -> bool:
    """Simple evaluation of response"""
    if not actual_output:
        return False

    output_lower = actual_output.lower()
    expected_lower = expected_answer.lower()

    # For multiple choice, check if answer letter or content is in output
    if question_type in ["text", "knowledge", "reasoning"]:
        # Check if expected answer is mentioned
        if expected_lower in output_lower:
            return True
        # Check for answer letter (A, B, C, D)
        if len(expected_answer) == 1 and expected_answer.isalpha():
            # Look for patterns like "答案是 A" or "选 A" or "A."
            import re
            patterns = [
                rf'答案[是为]?\s*{expected_answer}',
                rf'选[择]?\s*{expected_answer}',
                rf'^{expected_answer}[\.\)]',
                rf'\s{expected_answer}[\.\)]'
            ]
            for pattern in patterns:
                if re.search(pattern, output_lower):
                    return True
    elif question_type == "math":
        # For math, check if the numeric answer appears
        if expected_answer in actual_output:
            return True
    elif question_type == "code":
        # For code, check if output contains any code-like structure
        code_indicators = ['def ', 'class ', 'import ', '#', '//', '```', '{', '}']
        return any(ind in actual_output for ind in code_indicators)

    return False


def run_category_test(category_name: str, test_cases: list, question_type: str = "text") -> dict:
    """Run tests for a category"""
    print(f"\n{'='*80}")
    print(f"📋 {category_name} ({len(test_cases)} cases)")
    print('='*80)

    results = []
    passed = 0

    for i, case in enumerate(test_cases[:10], 1):  # Limit to 10 cases
        # Build prompt based on case structure
        if 'question' in case:
            if 'options' in case:
                prompt = f"{case['question']}\n" + "\n".join([f"{chr(65+j)}. {opt}" for j, opt in enumerate(case['options'])])
            else:
                prompt = case['question']
        elif 'prompt' in case:
            prompt = case['prompt']
        else:
            prompt = str(case)

        print(f"\n[{i}/10] {case.get('name', case.get('category', 'Test'))}")
        print(f"Prompt: {prompt[:60]}...")

        result = run_diffusion(prompt, steps=16, max_tokens=64)

        # Evaluate
        expected = case.get('answer', '')
        is_correct = evaluate_response(expected, result['output'], question_type) if expected else result['success']

        if is_correct:
            passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL" if expected else "⚪ SKIP"

        print(f"{status} | Output: {result['output'][:80]}...")
        if expected:
            print(f"      Expected: {expected}")

        results.append({
            "case": case.get('name', f"test_{i}"),
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
    print("🧪 Stage 2 Evaluation - LLaDA2 Diffusion Model")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Model: LLaDA2.0-mini-preview-Q4_0")
    print(f"🔧 Diffusion steps: 16, Block length: 32")
    print("="*80)

    # Run all category tests
    all_results = {
        "model": "LLaDA2.0-mini-preview-Q4_0",
        "timestamp": datetime.now().isoformat(),
        "categories": []
    }

    categories = [
        ("Text Understanding", TEXT_TEST_CASES, "text"),
        ("Code Generation", CODE_TEST_CASES, "code"),
        ("Math Reasoning", MATH_TEST_CASES, "math"),
        ("Logical Reasoning", REASONING_TEST_CASES, "reasoning"),
        ("Knowledge QA", KNOWLEDGE_TEST_CASES, "knowledge"),
        ("Translation", TRANSLATION_TEST_CASES, "text"),
        ("Summarization", SUMMARIZATION_TEST_CASES, "text"),
        ("Safety", SAFETY_TEST_CASES, "text"),
        ("Multi-turn", MULTITURN_TEST_CASES, "text"),
    ]

    total_passed = 0
    total_cases = 0

    for cat_name, cases, qtype in categories:
        try:
            result = run_category_test(cat_name, cases, qtype)
            all_results["categories"].append(result)
            total_passed += result["passed"]
            total_cases += result["total"]
        except Exception as e:
            print(f"Error running {cat_name}: {e}")
            all_results["categories"].append({
                "category": cat_name,
                "total": 0,
                "passed": 0,
                "accuracy": 0,
                "error": str(e)
            })

    # Summary
    print("\n" + "="*80)
    print("📊 STAGE 2 EVALUATION SUMMARY")
    print("="*80)

    for cat in all_results["categories"]:
        status = "✅" if cat.get("accuracy", 0) >= 60 else "⚠️" if cat.get("accuracy", 0) >= 40 else "❌"
        print(f"{status} {cat['category']:20} | {cat['passed']:2}/{cat['total']:2} | {cat['accuracy']:5.1f}%")

    overall_accuracy = (total_passed / total_cases * 100) if total_cases else 0
    print("-"*80)
    print(f"📈 Overall: {total_passed}/{total_cases} | {overall_accuracy:.1f}%")

    # Save results
    output_file = f"eval_results/stage2/llada2/LLaDA2_stage2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to: {output_file}")

    return overall_accuracy


if __name__ == "__main__":
    main()
