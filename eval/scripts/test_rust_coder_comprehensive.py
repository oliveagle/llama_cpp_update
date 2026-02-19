#!/usr/bin/env python3
"""
Comprehensive Rust Coder testing vs Qwen3-Coder-Next
"""

import json
import subprocess
import time
import concurrent.futures

# Test cases
RUST_TESTS = [
    {
        "name": "traits",
        "prompt": "Write a Rust trait `Drawable` with a method `draw(&self)`, then implement it for a struct `Circle`. Include main.",
        "checks": ["trait Drawable", "fn draw", "impl Drawable", "struct Circle"]
    },
    {
        "name": "closures_iterators",
        "prompt": "Write Rust code: create vector, filter evens, map double, collect. Use closures.",
        "checks": ["filter", "map", "collect", "|", "closure"]
    },
    {
        "name": "smart_pointers",
        "prompt": "Write Rust code with Rc<RefCell<T>> for a shared cons list.",
        "checks": ["Rc", "RefCell", "cons", "shared"]
    },
    {
        "name": "concurrency",
        "prompt": "Write Rust code using std::thread and channels. Spawn thread, send 5 numbers.",
        "checks": ["thread::spawn", "channel", "mpsc", "send", "recv"]
    },
    {
        "name": "custom_error",
        "prompt": "Write Rust custom error type ParseError implementing std::error::Error.",
        "checks": ["struct ParseError", "impl Error", "fmt::Display", "Result"]
    },
    {
        "name": "generics_bounds",
        "prompt": "Write generic Rust function find_max<T: Ord> for slice. Examples with i32 and String.",
        "checks": ["fn find_max", "T: Ord", "slice", "String"]
    },
    {
        "name": "option_result",
        "prompt": "Write Rust combining Option and Result. Parse string to Option<i32>.",
        "checks": ["Option", "Result", "parse", "match"]
    },
    {
        "name": "reverse_words",
        "prompt": "Write Rust function taking string, returns Vec of words in reverse order. Use iterators.",
        "checks": ["split", "rev", "collect", "Vec"]
    },
    {
        "name": "macro",
        "prompt": "Write Rust macro vec_of_strings! creating Vec<String>. Example: vec_of_strings![\"a\"].",
        "checks": ["macro_rules!", "vec_of_strings", "$", "vec!"]
    },
    {
        "name": "bank_account",
        "prompt": "Write Rust struct BankAccount with private balance. Methods: new, deposit, withdraw (Result), get_balance.",
        "checks": ["struct BankAccount", "fn new", "fn deposit", "fn withdraw", "Result"]
    },
    {
        "name": "fibonacci",
        "prompt": "Write efficient Rust fibonacci function. Handle large n with u128.",
        "checks": ["fn fibonacci", "u128", "iterative", "loop"]
    },
    {
        "name": "vec_reverse",
        "prompt": "Write Rust function reverse_vector in-place using swap.",
        "checks": ["fn reverse_vector", "swap", "len()/2"]
    }
]


def query_model(prompt, port, model=None, temperature=0.2):
    """Query a model on specified port"""
    data = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 1024
    }
    if model:
        data["model"] = model

    cmd = [
        "curl", "-s", f"http://localhost:{port}/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(data)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        resp = json.loads(result.stdout)
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"ERROR: {e}"


def check_response(content, checks):
    """Check if response contains expected elements"""
    content_lower = content.lower()
    passed = 0
    for check in checks:
        if check.lower() in content_lower:
            passed += 1
    return passed, len(checks)


def test_model(tests, port, model_name, model_file=None):
    """Test a model and return results"""
    print(f"\n{'='*60}")
    print(f"Testing {model_name} (port {port})")
    print(f"{'='*60}")

    results = []
    for test in tests:
        print(f"\n  [{test['name']}] ", end="", flush=True)

        start = time.time()
        content = query_model(test['prompt'], port, model_file)
        elapsed = time.time() - start

        passed, total = check_response(content, test['checks'])
        score = passed / total if total > 0 else 0

        status = "✅" if score >= 0.7 else "⚠️" if score >= 0.4 else "❌"
        print(f"{status} ({elapsed:.1f}s) - Score: {passed}/{total}")

        results.append({
            "name": test['name'],
            "score": score,
            "passed": passed,
            "total": total,
            "time": elapsed,
            "content": content[:500] + "..." if len(content) > 500 else content
        })

    avg_score = sum(r['score'] for r in results) / len(results)
    avg_time = sum(r['time'] for r in results) / len(results)

    print(f"\n{'-'*40}")
    print(f"Overall: {avg_score*100:.1f}% | Avg time: {avg_time:.1f}s")

    return {
        "model": model_name,
        "avg_score": avg_score,
        "avg_time": avg_time,
        "results": results
    }


def main():
    print("=" * 70)
    print("RUST CODER COMPREHENSIVE TEST")
    print("=" * 70)

    # Test Rust Coder
    rust_coder = test_model(
        RUST_TESTS,
        port=8502,
        model_name="Fortytwo-Strand-Rust-Coder-14B",
        model_file="Fortytwo_Strand-Rust-Coder-14B-v1-Q4_K_M.gguf"
    )

    # Test Qwen3-Coder-Next
    print(f"\n{'='*60}")
    print("Testing Qwen3-Coder-Next (port 8400)")
    print(f"{'='*60}")
    print("  (Note: Testing on general Vulkan instance)")

    qwen_results = test_model(
        RUST_TESTS,
        port=8400,
        model_name="Qwen3-Coder-Next",
        model_file="Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
    )

    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Test':<25} {'Rust Coder':<15} {'Qwen3-Coder':<15}")
    print("-" * 55)

    for r1, r2 in zip(rust_coder['results'], qwen_results['results']):
        name = r1['name'][:23]
        s1 = f"{r1['score']*100:.0f}%"
        s2 = f"{r2['score']*100:.0f}%"
        winner = "RC" if r1['score'] > r2['score'] else "QC" if r2['score'] > r1['score'] else "="
        print(f"{name:<25} {s1:<15} {s2:<15} {winner}")

    print("-" * 55)
    print(f"{'OVERALL':<25} {rust_coder['avg_score']*100:.1f}%          {qwen_results['avg_score']*100:.1f}%")
    print(f"{'AVG TIME':<25} {rust_coder['avg_time']:.1f}s           {qwen_results['avg_time']:.1f}s")

    # Save results
    with open("/mnt/volume3/llama_cpp/docs/analysis/RUST_CODER_TEST_RESULTS.json", "w") as f:
        json.dump({
            "rust_coder": rust_coder,
            "qwen3_coder": qwen_results
        }, f, indent=2)

    print(f"\nResults saved to docs/analysis/RUST_CODER_TEST_RESULTS.json")


if __name__ == "__main__":
    main()
