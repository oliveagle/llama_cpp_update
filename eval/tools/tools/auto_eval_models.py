#!/usr/bin/env python3
"""
自动化模型评估脚本
- 扫描已下载的模型
- 自动启动 llama.cpp 服务
- 运行完整评估 (GSM8K, HumanEval, MBPP, Tools)
- 生成报告
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 配置
MODELS_DIR = "/mnt/volume3/modelscope_models"
EVAL_DIR = "/mnt/volume3/llama_cpp/eval"
LLAMA_SERVER_SCRIPT = "/mnt/volume3/llama_cpp/llama-server-cuda.sh"
LOG_FILE = "/mnt/volume3/llama_cpp/logs/auto_eval.log"

# 已测试模型记录文件
TESTED_MODELS_FILE = "/mnt/volume3/llama_cpp/eval/tested_models.json"

# 模型路径映射 (model_name -> gguf_path)
MODEL_PATHS = {
    "JoyAI-LLM-Flash-Q4_K_M": "/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf",
    "GLM-4.7-Flash-Q4_K_M": "/mnt/volume3/modelscope_models/Pro/Azure-99/GLM-4.7-Flash-Q4_K_M.gguf",
    "GLM-4.7-Flash-REAP-IQ4_NL": "/mnt/volume3/modelscope_models/Pro/Azure-99/GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL.gguf",
    "Qwen3-VL-8B-Instruct": "/mnt/volume3/modelscope_models/Qwen/Qwen3-VL-8B-Instruct-GGUF/Qwen3-VL-8B-Instruct-Q4_K_M.gguf",
    "MiniCPM-o-4_5-Q4_K_M": "/mnt/volume3/modelscope_models/openbmb/MiniCPM-o-2_6-GGUF/MiniCPM-o-4_5-Q4_K_M.gguf",
}


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)

    # 写入日志文件
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + "\n")


def load_tested_models() -> Dict:
    """加载已测试模型记录"""
    if os.path.exists(TESTED_MODELS_FILE):
        try:
            with open(TESTED_MODELS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_tested_models(record: Dict):
    """保存已测试模型记录"""
    os.makedirs(os.path.dirname(TESTED_MODELS_FILE), exist_ok=True)
    with open(TESTED_MODELS_FILE, 'w') as f:
        json.dump(record, f, indent=2, ensure_ascii=False)


def check_model_exists(model_name: str) -> Optional[str]:
    """检查模型是否存在，返回路径"""
    # 先检查预定义路径
    if model_name in MODEL_PATHS:
        path = MODEL_PATHS[model_name]
        if os.path.exists(path):
            return path

    # 扫描模型目录
    for root, dirs, files in os.walk(MODELS_DIR):
        for file in files:
            if file.endswith('.gguf') and model_name.lower() in file.lower():
                return os.path.join(root, file)

    return None


def detect_chat_template(model_path: str) -> str:
    """根据模型路径检测合适的 chat template"""
    path_lower = model_path.lower()

    if "llama-3" in path_lower or "llama3" in path_lower:
        return "llama3"
    elif "qwen2.5" in path_lower or "qwen2-5" in path_lower:
        return "qwen2.5"
    elif "qwen" in path_lower:
        return "qwen2"
    elif "glm-4" in path_lower or "glm4" in path_lower:
        return "glm4"
    elif "glm" in path_lower or "chatglm" in path_lower:
        return "chatglm3"
    elif "minicpm" in path_lower:
        return "minicpm"
    elif "phi-4" in path_lower or "phi4" in path_lower:
        return "phi4"
    elif "phi-3" in path_lower or "phi3" in path_lower:
        return "phi3"
    elif "gemma" in path_lower:
        return "gemma"
    elif "yi" in path_lower:
        return "yi"
    elif "deepseek" in path_lower:
        return "deepseek"
    else:
        return "chatml"  # 默认使用 chatml


def start_llama_server(model_path: str, port: int = 8401) -> bool:
    """启动 llama.cpp 服务"""
    log(f"启动 llama.cpp 服务: {model_path} (端口 {port})")

    # 先停止现有服务
    subprocess.run([LLAMA_SERVER_SCRIPT, "stop"], capture_output=True)
    time.sleep(2)

    # 检测 chat template
    chat_template = detect_chat_template(model_path)
    log(f"使用 chat template: {chat_template}")

    # 创建临时预设文件
    preset_name = f"temp_eval_{os.getpid()}"
    preset_content = f"""[{preset_name}]
model = {model_path}
chat_template = {chat_template}
"""
    preset_file = f"/tmp/{preset_name}.ini"
    with open(preset_file, 'w') as f:
        f.write(preset_content)

    # 启动服务
    env = os.environ.copy()
    env["PRESET"] = preset_name

    cmd = [
        LLAMA_SERVER_SCRIPT, "start"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            log(f"启动服务失败: {result.stderr}")
            return False

        # 等待服务就绪
        log("等待服务就绪...")
        for i in range(30):  # 最多等待30秒
            time.sleep(1)
            try:
                health = subprocess.run(
                    ["curl", "-s", f"http://localhost:{port}/health"],
                    capture_output=True, text=True, timeout=5
                )
                if health.returncode == 0:
                    log("服务已就绪")
                    return True
            except:
                pass

        log("服务启动超时")
        return False

    except Exception as e:
        log(f"启动服务出错: {e}")
        return False


def stop_llama_server():
    """停止 llama.cpp 服务"""
    log("停止 llama.cpp 服务")
    subprocess.run([LLAMA_SERVER_SCRIPT, "stop"], capture_output=True)


def run_evaluation(model_name: str, model_path: str, output_dir: str) -> Dict:
    """运行模型评估"""
    log(f"开始评估模型: {model_name}")

    # 启动服务
    if not start_llama_server(model_path):
        return {"error": "启动服务失败"}

    try:
        # 运行综合评估
        eval_script = os.path.join(EVAL_DIR, "eval_all_capabilities.py")

        cmd = [
            sys.executable, eval_script,
            "--model-path", model_path,
            "--model-name", model_name,
            "--model-url", "http://localhost:8401",
            "--output-dir", output_dir,
        ]

        log(f"运行评估: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200,  # 2小时超时
        )

        if result.returncode != 0:
            log(f"评估失败: {result.stderr}")
            return {"error": result.stderr}

        log("评估完成")
        return {"status": "success", "output": result.stdout}

    except subprocess.TimeoutExpired:
        log("评估超时")
        return {"error": "timeout"}
    except Exception as e:
        log(f"评估出错: {e}")
        return {"error": str(e)}
    finally:
        stop_llama_server()


def main():
    parser = argparse.ArgumentParser(description="自动化模型评估")
    parser.add_argument("--model", type=str, help="指定评估单个模型")
    parser.add_argument("--output-dir", default="./eval_results", help="输出目录")
    parser.add_argument("--limit", type=int, default=10, help="最多评估模型数")
    parser.add_argument("--force", action="store_true", help="强制重新评估")

    args = parser.parse_args()

    log("=" * 60)
    log("自动化模型评估启动")
    log("=" * 60)

    # 加载已测试记录
    tested_models = load_tested_models()

    # 确定要评估的模型列表
    if args.model:
        models_to_eval = [(args.model, check_model_exists(args.model))]
    else:
        # 获取所有预定义模型
        models_to_eval = []
        for name, path in MODEL_PATHS.items():
            if os.path.exists(path):
                models_to_eval.append((name, path))

    log(f"找到 {len(models_to_eval)} 个模型待评估")

    # 过滤已测试的模型
    if not args.force:
        models_to_eval = [
            (name, path) for name, path in models_to_eval
            if name not in tested_models or tested_models[name].get("status") != "completed"
        ]
        log(f"过滤后剩余 {len(models_to_eval)} 个模型 (排除已测试)")

    # 限制数量
    models_to_eval = models_to_eval[:args.limit]

    # 执行评估
    results = {}
    for model_name, model_path in models_to_eval:
        if not model_path:
            log(f"模型不存在，跳过: {model_name}")
            continue

        log(f"\n{'='*60}")
        log(f"评估模型: {model_name}")
        log(f"模型路径: {model_path}")
        log(f"{'='*60}")

        result = run_evaluation(model_name, model_path, args.output_dir)
        results[model_name] = result

        # 更新测试记录
        tested_models[model_name] = {
            "last_tested": datetime.now().isoformat(),
            "status": "completed" if "error" not in result else "failed",
            "path": model_path,
        }
        save_tested_models(tested_models)

        # 模型间冷却时间
        if model_name != models_to_eval[-1][0]:
            log("等待 10 秒后评估下一个模型...")
            time.sleep(10)

    # 生成汇总报告
    log("\n" + "=" * 60)
    log("评估完成汇总")
    log("=" * 60)

    success_count = sum(1 for r in results.values() if "error" not in r)
    failed_count = len(results) - success_count

    log(f"成功: {success_count}")
    log(f"失败: {failed_count}")

    for model_name, result in results.items():
        status = "✅" if "error" not in result else "❌"
        error_msg = result.get("error", "")[:50] if "error" in result else ""
        log(f"{status} {model_name}: {error_msg or 'OK'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
