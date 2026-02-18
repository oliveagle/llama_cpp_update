#!/usr/bin/env python3
"""
黄金标杆定义 - 各类别基准模型及其性能指标
"""

from typing import Dict, Any

# 黄金标杆定义
# 注意: 这些值需要根据实际测试更新
GOLDEN_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    "LLM": {
        "name": "通用语言模型",
        "baseline": {
            "model": "JoyAI-LLM-Flash-Q4_K_M",
            "path": "/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf",
            "size_gb": 28,
            "quant": "Q4_K_M",
            "description": "48B MoE, 当前本地最佳模型",
        },
        "alternatives": [
            {
                "model": "GLM-4.7-Flash-Q4_K_M",
                "path": "/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf",
                "size_gb": 18,
                "quant": "Q4_K_M",
                "description": "30B dense, 性价比高",
            },
            {
                "model": "GLM-4.7-Flash-REAP-IQ4_NL",
                "path": "/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-REAP-23B-A3B-GGUF/GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL.gguf",
                "size_gb": 13,
                "quant": "IQ4_NL",
                "description": "23B MoE, 省显存",
            },
        ],
        # TODO: 需要通过lm-eval实际测试获取准确值
        "metrics": {
            "C-Eval": {"baseline": 0.72, "target": 0.70, "unit": "acc"},
            "CMMLU": {"baseline": 0.70, "target": 0.68, "unit": "acc"},
            "GSM8K": {"baseline": 0.78, "target": 0.75, "unit": "acc"},
            "HumanEval": {"baseline": 0.65, "target": 0.60, "unit": "pass@1"},
            "MMLU": {"baseline": 0.68, "target": 0.65, "unit": "acc"},
            " throughput_8k": {"baseline": 736, "target": 500, "unit": "tokens/s"},
            "generation": {"baseline": 39, "target": 30, "unit": "tokens/s"},
        },
    },

    "OCR": {
        "name": "文字识别",
        "baseline": None,  # 待确定
        "alternatives": [],
        "metrics": {
            "ICDAR2019": {"baseline": 0.95, "target": 0.90, "unit": "accuracy"},
            "DocVQA": {"baseline": 0.85, "target": 0.80, "unit": "ANLS"},
        },
    },

    "TTS": {
        "name": "语音合成",
        "baseline": None,  # 待确定
        "alternatives": [],
        "metrics": {
            "MOS": {"baseline": 4.2, "target": 4.0, "unit": "score"},
            "SIM": {"baseline": 0.85, "target": 0.80, "unit": "similarity"},
        },
    },

    "Vision": {
        "name": "视觉/多模态",
        "baseline": {
            "model": "Qwen3-VL-8B-Instruct",
            "path": "/mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf",
            "size_gb": 8,
            "quant": "Q8_0",
            "description": "8B视觉语言模型，已下载",
        },
        "alternatives": [
            {
                "model": "Qwen3-VL-4B-Instruct",
                "path": "/mnt/volume3/modelscope_models/Qwen/Qwen3-VL-4B-Instruct-GGUF/Qwen3VL-4B-Instruct-Q8_0.gguf",
                "size_gb": 4,
                "quant": "Q8_0",
                "description": "4B轻量版，已下载",
            },
        ],
        # TODO: 需要实际测试获取准确值
        "metrics": {
            "VQAv2": {"baseline": 0.80, "target": 0.75, "unit": "accuracy"},
            "TextVQA": {"baseline": 0.75, "target": 0.70, "unit": "accuracy"},
        },
    },

    "Code": {
        "name": "代码模型",
        "baseline": {
            "model": "Qwen3-Coder-Next-Q4_K_M",
            "path": "/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/",
            "files": [
                "Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf",
                "Qwen3-Coder-Next-Q4_K_M-00002-of-00004.gguf",
                "Qwen3-Coder-Next-Q4_K_M-00003-of-00004.gguf",
                "Qwen3-Coder-Next-Q4_K_M-00004-of-00004.gguf",
            ],
            "size_gb": 46,  # 4个分片合并后
            "quant": "Q4_K_M",
            "note": "分片模型，需要合并或使用支持分片的加载器",
        },
        "alternatives": [],
        "metrics": {
            "HumanEval": {"baseline": 0.75, "target": 0.70, "unit": "pass@1"},
            "MBPP": {"baseline": 0.70, "target": 0.65, "unit": "pass@1"},
        },
    },

    "Reasoning": {
        "name": "推理模型",
        "baseline": None,  # 待确定
        "alternatives": [],
        "metrics": {
            "GSM8K": {"baseline": 0.90, "target": 0.85, "unit": "acc"},
            "LogiQA": {"baseline": 0.75, "target": 0.70, "unit": "acc"},
        },
    },
}


def get_golden_benchmark(category: str) -> Dict[str, Any]:
    """获取指定类别的黄金标杆"""
    return GOLDEN_BENCHMARKS.get(category, {})


def get_all_categories() -> list:
    """获取所有类别列表"""
    return list(GOLDEN_BENCHMARKS.keys())


def get_metrics_for_category(category: str) -> Dict[str, Dict]:
    """获取指定类别的评测指标"""
    benchmark = get_golden_benchmark(category)
    return benchmark.get("metrics", {})


def compare_with_golden(category: str, model_results: Dict[str, float]) -> Dict[str, Any]:
    """
    对比模型结果与黄金标杆

    Args:
        category: 模型类别
        model_results: {metric_name: value}

    Returns:
        对比结果
    """
    golden = get_metrics_for_category(category)
    if not golden:
        return {"error": f"No golden benchmark for category: {category}"}

    comparison = {}
    for metric, golden_value in golden.items():
        if metric in model_results:
            model_value = model_results[metric]
            baseline = golden_value["baseline"]
            target = golden_value["target"]

            comparison[metric] = {
                "model_value": model_value,
                "golden_baseline": baseline,
                "golden_target": target,
                "vs_baseline": model_value - baseline,
                "vs_baseline_pct": (model_value - baseline) / baseline * 100 if baseline > 0 else 0,
                "meets_target": model_value >= target,
                "beats_baseline": model_value >= baseline,
                "unit": golden_value["unit"],
            }

    return comparison


def print_comparison(comparison: Dict[str, Any]) -> None:
    """打印对比结果"""
    print("\n" + "=" * 80)
    print("模型 vs 黄金标杆对比")
    print("=" * 80)

    for metric, result in comparison.items():
        print(f"\n{metric}:")
        print(f"  模型值:   {result['model_value']:.4f} {result['unit']}")
        print(f"  黄金标杆: {result['golden_baseline']:.4f} {result['unit']}")
        print(f"  目标值:   {result['golden_target']:.4f} {result['unit']}")

        vs_baseline = result['vs_baseline_pct']
        sign = "+" if vs_baseline >= 0 else ""
        print(f"  相对标杆: {sign}{vs_baseline:.1f}%")

        if result['beats_baseline']:
            print(f"  ✅ 超越黄金标杆")
        elif result['meets_target']:
            print(f"  ✅ 达到目标值")
        else:
            print(f"  ❌ 未达目标")


def get_recommended_eval_tasks(category: str) -> list:
    """
    获取指定类别推荐的lm-eval评测任务

    Args:
        category: 模型类别

    Returns:
        评测任务列表
    """
    TASK_MAPPING = {
        "LLM": [
            "ceval-valid",      # 中文综合
            "cmmlu",            # 中文多任务
            "mmlu",             # 英文综合
            "gsm8k",            # 数学推理
            "humaneval",        # 代码生成
        ],
        "Code": [
            "humaneval",
            "mbpp",
        ],
        "Reasoning": [
            "gsm8k",
            "mathqa",
            "logiqa",
        ],
        "Vision": [
            # Vision tasks require special handling
            "vqav2",
        ],
    }

    return TASK_MAPPING.get(category, [])


if __name__ == "__main__":
    # 测试
    print("黄金标杆定义:")
    for cat in get_all_categories():
        info = get_golden_benchmark(cat)
        baseline = info.get("baseline")
        name = info.get("name", cat)

        print(f"\n{name} ({cat}):")
        if baseline:
            print(f"  黄金标杆: {baseline['model']} ({baseline['size_gb']}GB)")
        else:
            print(f"  黄金标杆: 待确定")

        metrics = get_metrics_for_category(cat)
        for metric, config in metrics.items():
            print(f"    - {metric}: {config['baseline']} {config['unit']}")
