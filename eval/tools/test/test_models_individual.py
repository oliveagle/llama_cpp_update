#!/usr/bin/env python3
"""
逐个测试模型 - 使用单模型模式避免加载冲突
"""
import subprocess
import time
import requests
import sys

MODELS = [
    ("Qwen3-4B", "Qwen3-4B-Instruct-2507-UD-Q4_K_XL", "/mnt/volume3/modelscope_models/unsloth/Qwen3-4B-Instruct-2507-GGUF/Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf"),
    ("Qwen3VL-4B", "Qwen3VL-4B-Instruct-Q8_0", "/mnt/volume3/modelscope_models/Qwen/Qwen3-VL-4B-Instruct-GGUF/Qwen3VL-4B-Instruct-Q8_0.gguf"),
    ("GLM-4.7-Flash", "GLM-4.7-Flash-Q4_K_M", "/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf"),
]

SERVER_BIN = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"

def start_server(model_path, model_name):
    """启动单模型服务器"""
    cmd = [
        SERVER_BIN,
        "-m", model_path,
        "--host", "0.0.0.0",
        "--port", "8401",
        "-c", "131072",
        "-n", "4096",
        "-ngl", "99",
        "--chat-template", "qwen2" if "qwen" in model_name.lower() else "chatglm3" if "glm" in model_name.lower() else "chatml"
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(10)  # 等待加载
    return proc

def test_context(ctx_size):
    """测试 context"""
    prompt = "Test. " * (ctx_size // 2)
    try:
        resp = requests.post(
            "http://localhost:8401/v1/completions",
            json={"model": "test", "prompt": prompt, "max_tokens": 5},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["usage"]["prompt_tokens"]
        else:
            msg = resp.json().get("error", {}).get("message", "")
            if "exceeds" in msg:
                import re
                m = re.search(r'size \((\d+)\)', msg)
                return f"limit:{int(m.group(1))//1024}K" if m else "limit"
            return f"error:{msg[:20]}"
    except Exception as e:
        return f"exc:{str(e)[:20]}"

def main():
    print("="*70)
    print("逐个测试模型 Context 限制")
    print("="*70)

    for name, config_name, path in MODELS:
        print(f"\n{'='*70}")
        print(f"测试模型: {name}")
        print(f"{'='*70}")

        # 启动服务器
        print("  启动服务器...")
        proc = start_server(path, name)

        # 测试 8K, 16K, 24K, 32K
        for ctx in [8192, 16384, 24576, 32768]:
            result = test_context(ctx)
            if isinstance(result, int):
                print(f"  {ctx//1024}K: ✅ {result:,} tokens")
            elif isinstance(result, str) and result.startswith("limit"):
                print(f"  {ctx//1024}K: ❌ {result}")
                break
            else:
                print(f"  {ctx//1024}K: ❌ {result}")
                break

        # 停止服务器
        print("  停止服务器...")
        proc.terminate()
        proc.wait()
        time.sleep(3)

if __name__ == "__main__":
    main()
