#!/usr/bin/env python3
"""
新模型第二层测试脚本
"""

import sys
import os
import json
import uuid
import re
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'eval'))
from tests.stage2_basic.code_eval import CODE_TEST_CASES
from tests.stage2_basic.math_eval import MATH_TEST_CASES
from tests.stage2_basic.text_eval import TEXT_TEST_CASES

RESULTS_DIR = "/mnt/volume3/llama_cpp/eval_results/stage2"
os.makedirs(RESULTS_DIR, exist_ok=True)


def generate_test_id(model_name: str) -> str:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    short_uuid = uuid.uuid4().hex[:8]
    safe_model = model_name.replace('/', '_').replace(' ', '_')[:40]
    return f"{safe_model}_{timestamp}_{short_uuid}"


def call_model_api(base_url: str, messages: list, max_tokens: int = 512, temperature: float = 0.7) -> dict:
    """调用模型 API"""
    payload = {
        "model": "test",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.8,
    }

    try:
        resp = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=120)
        if resp.status_code == 200:
            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "") or message.get("reasoning_content", "")
            return {"success": True, "content": content}
        else:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def test_code(base_url: str) -> dict:
    """代码能力测试"""
    passed = 0
    total = len(CODE_TEST_CASES)
    results = []

    for tc in CODE_TEST_CASES:
        result = call_model_api(
            base_url,
            messages=[
                {"role": "system", "content": "You are a coding assistant. Output only code without explanation."},
                {"role": "user", "content": tc['prompt']}
            ],
            max_tokens=512,
            temperature=0.3
        )

        if result['success']:
            content = result['content'] or ""
            # 检查是否包含关键元素
            score = 0
            checks = tc.get('checks', [])
            for check in checks:
                if check.lower() in content.lower():
                    score += 1
            score_rate = score / len(checks) if checks else 0

            test_passed = score_rate >= 0.5
            if test_passed:
                passed += 1

            results.append({
                "name": tc['name'],
                "passed": test_passed,
                "score": score_rate,
                "generated_code": content[:500]
            })
        else:
            results.append({
                "name": tc['name'],
                "passed": False,
                "error": result.get('error')
            })

    return {
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total > 0 else 0,
        "tests": results
    }


def test_math(base_url: str) -> dict:
    """数学推理测试"""
    passed = 0
    total = len(MATH_TEST_CASES)
    results = []

    for tc in MATH_TEST_CASES:
        # 跳过没有 expected 的测试用例
        if 'expected' not in tc:
            results.append({
                "name": tc.get('name', 'unknown'),
                "passed": False,
                "error": "No expected value"
            })
            continue
        problem = tc.get('problem', tc.get('question', ''))
        prompt = f"请解答以下数学题，只输出最终答案数字：\n\n{problem}"

        result = call_model_api(
            base_url,
            messages=[
                {"role": "system", "content": "你是一个数学助手，请仔细思考后给出答案。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=256,
            temperature=0.1
        )

        if result['success']:
            content = result['content'] or ""
            # 提取数字
            extracted = None
            lines = content.strip().split('\n')
            last_line = lines[-1] if lines else ""
            last_num_match = re.search(r'\b([\d.]+)\b', last_line)
            if last_num_match:
                try:
                    extracted = float(last_num_match.group(1))
                except:
                    pass

            if extracted is None:
                patterns = [
                    r'答案[是为:]+\s*([\d.]+)',
                    r'结果[是为:]+\s*([\d.]+)',
                    r'等于\s*([\d.]+)',
                    r'\b([\d.]+)\b',
                ]
                for pattern in patterns:
                    match = re.search(pattern, content)
                    if match:
                        try:
                            extracted = float(match.group(1))
                            break
                        except:
                            pass

            expected = tc.get('answer', tc.get('expected', 0))
            test_passed = False
            if extracted is not None:
                if isinstance(expected, (int, float)):
                    test_passed = abs(extracted - expected) < 0.1
                else:
                    test_passed = str(expected) in content

            if test_passed:
                passed += 1

            results.append({
                "name": tc['name'],
                "passed": test_passed,
                "expected": expected,
                "extracted": extracted,
                "model_answer": content[:200]
            })
        else:
            results.append({
                "name": tc['name'],
                "passed": False,
                "error": result.get('error')
            })

    return {
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total > 0 else 0,
        "tests": results
    }


def test_text(base_url: str) -> dict:
    """文本理解测试"""
    passed = 0
    total = len(TEXT_TEST_CASES)
    results = []

    for tc in TEXT_TEST_CASES:
        # 构建问题文本
        question = tc.get('question', '')
        options = tc.get('options', [])
        if options:
            opts_text = '\n'.join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)])
            prompt = f"{question}\n\n{opts_text}\n\n请回答选项字母(A/B/C/D)："
        else:
            prompt = question

        result = call_model_api(
            base_url,
            messages=[
                {"role": "system", "content": "你是一个知识问答助手，请直接给出答案。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=128,
            temperature=0.3
        )

        if result['success']:
            content = result['content'] or ""
            # 提取答案字母
            extracted = None
            content_upper = content.upper()

            # 查找 A/B/C/D
            answer_match = re.search(r'\b([A-D])\b', content_upper)
            if answer_match:
                extracted = answer_match.group(1)

            expected = tc.get('answer', tc.get('expected', '')).upper()
            test_passed = (extracted == expected) or (expected in content_upper)

            if test_passed:
                passed += 1

            results.append({
                "name": tc['name'],
                "category": tc.get('category', ''),
                "passed": test_passed,
                "expected": expected,
                "extracted": extracted,
                "model_answer": content[:200]
            })
        else:
            results.append({
                "name": tc['name'],
                "passed": False,
                "error": result.get('error')
            })

    return {
        "passed": passed,
        "total": total,
        "pass_rate": passed / total if total > 0 else 0,
        "tests": results
    }


def run_stage2_test(model_name: str, base_url: str, model_config: str = ""):
    """运行完整的第二层测试"""
    test_id = generate_test_id(model_name)

    print("=" * 80)
    print(f"🧪 Stage 2 测试 - {model_name}")
    print(f"🆔 测试ID: {test_id}")
    print(f"📍 测试端点: {base_url}")
    if model_config:
        print(f"⚙️  配置: {model_config}")
    print("=" * 80)

    # 检查服务
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        print("\n✅ 服务就绪")
    except:
        print("\n⚠️  服务健康检查失败，继续测试...")

    # 运行测试
    print("\n[1/3] 代码能力测试...")
    code_result = test_code(base_url)
    print(f"   结果: {code_result['passed']}/{code_result['total']} ({code_result['pass_rate']*100:.1f}%)")

    print("\n[2/3] 数学推理测试...")
    math_result = test_math(base_url)
    print(f"   结果: {math_result['passed']}/{math_result['total']} ({math_result['pass_rate']*100:.1f}%)")

    print("\n[3/3] 文本理解测试...")
    text_result = test_text(base_url)
    print(f"   结果: {text_result['passed']}/{text_result['total']} ({text_result['pass_rate']*100:.1f}%)")

    # 汇总
    total_tests = code_result['total'] + math_result['total'] + text_result['total']
    total_passed = code_result['passed'] + math_result['passed'] + text_result['passed']
    total_pass_rate = total_passed / total_tests if total_tests > 0 else 0

    result = {
        "test_id": test_id,
        "model": model_name,
        "config": model_config,
        "timestamp": datetime.now().isoformat(),
        "endpoint": base_url,
        "code": code_result,
        "math": math_result,
        "text": text_result,
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_pass_rate": total_pass_rate
        }
    }

    # 打印报告
    print("\n" + "=" * 80)
    print("📊 测试报告")
    print("=" * 80)
    print(f"\n  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别    │   通过/总计   │   通过率    │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  代码能力    │   {code_result['passed']:2d}/{code_result['total']:2d}       │   {code_result['pass_rate']*100:5.1f}%   │")
    print(f"  │  数学推理    │   {math_result['passed']:2d}/{math_result['total']:2d}       │   {math_result['pass_rate']*100:5.1f}%   │")
    print(f"  │  文本理解    │   {text_result['passed']:2d}/{text_result['total']:2d}       │   {text_result['pass_rate']*100:5.1f}%   │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  总计        │   {total_passed:2d}/{total_tests:2d}       │   {total_pass_rate*100:5.1f}%   │")
    print(f"  └─────────────────────────────────────────────────────────────┘")

    if total_pass_rate >= 0.8:
        grade = "⭐⭐⭐⭐⭐ 优秀"
    elif total_pass_rate >= 0.6:
        grade = "⭐⭐⭐⭐  良好"
    elif total_pass_rate >= 0.4:
        grade = "⭐⭐⭐    及格"
    else:
        grade = "⭐⭐      需改进"

    print(f"\n  🏆 评级: {grade}")

    # 保存结果
    output_file = os.path.join(RESULTS_DIR, f"{test_id}_result.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存: {output_file}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="新模型第二层测试")
    parser.add_argument("--model-name", required=True, help="模型名称")
    parser.add_argument("--endpoint", default="http://localhost:8401", help="API端点")
    parser.add_argument("--config", default="", help="模型配置描述")
    args = parser.parse_args()

    result = run_stage2_test(args.model_name, args.endpoint, args.config)
    sys.exit(0 if result['summary']['total_pass_rate'] >= 0.6 else 1)
