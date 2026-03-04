#!/usr/bin/env python3
"""
评估系统配置
"""

from pathlib import Path

# 基础路径
EVAL_ROOT = Path(__file__).parent.parent
RESULTS_DIR = EVAL_ROOT / "results"
EVAL_RESULTS_DIR = EVAL_ROOT / "eval_results"

# Stage 输出目录
STAGE1_RESULTS = RESULTS_DIR / "stage1"
STAGE2_RESULTS = RESULTS_DIR / "stage2"
STAGE3_RESULTS = RESULTS_DIR / "stage3"
CAPABILITIES_RESULTS = RESULTS_DIR / "capabilities"

# 确保目录存在
for d in [RESULTS_DIR, EVAL_RESULTS_DIR, STAGE1_RESULTS, STAGE2_RESULTS, STAGE3_RESULTS, CAPABILITIES_RESULTS]:
    d.mkdir(parents=True, exist_ok=True)

# API 配置
DEFAULT_API_URL = "http://localhost:8400"
DEFAULT_TIMEOUT = 120  # 秒

# Stage 1 配置
DEFAULT_CTX_SIZE = 8192
CTX_SIZES = [4096, 8192, 16384, 32768, 65536]

# Stage 2 配置
STAGE2_THRESHOLD = 0.6  # 60% 通过率

# Stage 3 配置
STAGE3_THRESHOLD = 0.5  # 50% 通过率

# 模型配置
MODELS = {
    "Qwen3-0.6B": {
        "path": "/mnt/volume3/modelscope_models/Qwen/Qwen3-0___6B-GGUF/Qwen3-0.6B-Q4_0.gguf",
        "size_gb": 1,
    },
    "Qwen3.5-0.8B": {
        "path": "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-0___8B-GGUF/Qwen3.5-0.8B-UD-Q8_K_XL.gguf",
        "size_gb": 1,
    },
    "Qwen3-4B": {
        "path": "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-4B-GGUF/Qwen3.5-4B-UD-Q4_K_XL.gguf",
        "size_gb": 3,
    },
    "JoyAI-LLM-Flash": {
        "path": "/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf",
        "size_gb": 28,
    },
    "GLM-4.7-Flash": {
        "path": "/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf",
        "size_gb": 5,
    },
}


def get_stage_results_dir(stage: int) -> Path:
    """获取指定阶段的输出目录"""
    dirs = {
        1: STAGE1_RESULTS,
        2: STAGE2_RESULTS,
        3: STAGE3_RESULTS,
    }
    return dirs.get(stage, RESULTS_DIR)


def get_model_path(model_name: str) -> str | None:
    """获取模型路径"""
    if model_name in MODELS:
        return MODELS[model_name]["path"]
    return None
