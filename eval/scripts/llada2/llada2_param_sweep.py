#!/usr/bin/env python3
"""
Parameter sweep for LLaDA2 to find optimal settings for math/logic
"""

import subprocess
import json
import time
import os
from datetime import datetime

MODEL_PATH = "/mnt/volume3/modelscope_models/wsbagnsv1/LLaDA2___0-mini-preview-GGUF/LLaDA2.0-mini-preview-Q4_0.gguf"
LLAMA_CPP_PATH = "/home/oliveagle/opt/llama.cpp"
DIFFUSION_CLI = f"{LLAMA_CPP_PATH}/build/bin/llama-diffusion-cli"

# Test prompts
MATH_PROMPT = "3x + 7 = 22, x = ?"
LOGIC_PROMPT = "If A then B. If B then C. Therefore: A. True or False?"
CODE_PROMPT = "def add(a, b):"

def run_test(prompt, params):
    """Run diffusion with given params"""
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = f"{LLAMA_CPP_PATH}/build/bin:{env.get('LD_LIBRARY_PATH', '')}"

    cmd = [
        DIFFUSION_CLI,
        "-m", MODEL_PATH,
        "-p", prompt,
        "--diffusion-steps", str(params.get('steps', 16)),
        "--diffusion-block-length", str(params.get('block', 32)),
        "--diffusion-algorithm", str(params.get('algo', 4)),
        "-c", "32768",
        "-n", str(params.get('tokens', 32)),
        "-ngl", "99",
        "--temp", str(params.get('temp', 0.8)),
    ]

    if params.get('cfg', 0) > 0:
        cmd.extend(["--diffusion-cfg-scale", str(params['cfg'])])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
        output = result.stderr + result.stdout

        # Extract generated text
        lines = output.split('\n')
        generated = ""
        found = False
        for line in lines:
            if found:
                if line.strip():
                    generated += line + "\n"
            elif line.startswith('total time:'):
                found = True

        return generated.strip()
    except Exception as e:
        return f"ERROR: {e}"

# Parameter combinations to test
param_sets = [
    {"name": "Default", "steps": 16, "block": 32, "temp": 0.8, "algo": 4, "cfg": 0, "tokens": 32},
    {"name": "High steps", "steps": 128, "block": 64, "temp": 0.8, "algo": 4, "cfg": 0, "tokens": 32},
    {"name": "Low temp", "steps": 16, "block": 32, "temp": 0.3, "algo": 4, "cfg": 0, "tokens": 32},
    {"name": "High temp", "steps": 16, "block": 32, "temp": 1.2, "algo": 4, "cfg": 0, "tokens": 32},
    {"name": "With CFG", "steps": 16, "block": 32, "temp": 0.8, "algo": 4, "cfg": 2.0, "tokens": 32},
    {"name": "Max tokens", "steps": 16, "block": 32, "temp": 0.8, "algo": 4, "cfg": 0, "tokens": 128},
    {"name": "Algorithm 0 (ORIGIN)", "steps": 16, "block": 32, "temp": 0.8, "algo": 0, "cfg": 0, "tokens": 32},
    {"name": "Algorithm 3 (RANDOM)", "steps": 16, "block": 32, "temp": 0.8, "algo": 3, "cfg": 0, "tokens": 32},
    {"name": "High steps + CFG", "steps": 64, "block": 64, "temp": 0.8, "algo": 4, "cfg": 2.0, "tokens": 64},
]

print("="*80)
print("🔬 LLaDA2 Parameter Sweep")
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

results = []

for params in param_sets:
    print(f"\n{'='*80}")
    print(f"📊 Testing: {params['name']}")
    print(f"   steps={params['steps']}, block={params['block']}, temp={params['temp']}, cfg={params['cfg']}")
    print('='*80)

    # Math test
    print(f"\n🧮 Math: '{MATH_PROMPT}'")
    math_output = run_test(MATH_PROMPT, params)
    print(f"   Output: '{math_output[:50]}...' " if len(math_output) > 50 else f"   Output: '{math_output}'")
    has_answer = '5' in math_output or 'x=5' in math_output or 'x = 5' in math_output
    print(f"   Has '5': {'✅' if has_answer else '❌'}")

    # Logic test
    print(f"\n🧠 Logic: '{LOGIC_PROMPT}'")
    logic_output = run_test(LOGIC_PROMPT, params)
    print(f"   Output: '{logic_output[:50]}...' " if len(logic_output) > 50 else f"   Output: '{logic_output}'")
    has_true = 'True' in logic_output or 'False' in logic_output
    print(f"   Has True/False: {'✅' if has_true else '❌'}")

    # Code test
    print(f"\n💻 Code: '{CODE_PROMPT}'")
    code_output = run_test(CODE_PROMPT, params)
    print(f"   Output: '{code_output[:50]}...' " if len(code_output) > 50 else f"   Output: '{code_output}'")
    has_code = 'def' in code_output or 'return' in code_output
    print(f"   Has code: {'✅' if has_code else '❌'}")

    results.append({
        "params": params,
        "math": {"output": math_output, "has_answer": has_answer},
        "logic": {"output": logic_output, "has_true": has_true},
        "code": {"output": code_output, "has_code": has_code}
    })

# Summary
print("\n" + "="*80)
print("📊 PARAMETER SWEEP SUMMARY")
print("="*80)
print(f"{'Config':<25} {'Math':<8} {'Logic':<8} {'Code':<8}")
print("-"*80)

for r in results:
    name = r['params']['name']
    math = '✅' if r['math']['has_answer'] else '❌'
    logic = '✅' if r['logic']['has_true'] else '❌'
    code = '✅' if r['code']['has_code'] else '❌'
    print(f"{name:<25} {math:<8} {logic:<8} {code:<8}")

# Save results
output_file = f"eval_results/llada2_param_sweep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
os.makedirs("eval_results", exist_ok=True)
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n💾 Results saved to: {output_file}")
