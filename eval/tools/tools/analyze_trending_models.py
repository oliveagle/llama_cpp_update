#!/usr/bin/env python3
"""
HuggingFace Trending GGUF 模型自动分析脚本
- 获取 trending 模型
- 分析是否值得测试
- 生成推荐列表
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import requests

# 配置
HF_ENDPOINT = os.getenv("HF_ENDPOINT", "https://hf-mirror.com")
BENCHMARK_DIR = "/mnt/volume3/llama_cpp/benchmarks"
PRESETS_FILE = "/mnt/volume3/llama_cpp/presets/mypresets-cuda.ini"
OUTPUT_FILE = "/mnt/volume3/llama_cpp/trending_analysis.md"

# V100 限制
V100_MEMORY_GB = 32
MAX_MODEL_SIZE_GB = 40  # 放宽到40B，包含32B和40B模型

# 模型类别定义
MODEL_CATEGORIES = {
    "LLM": {
        "keywords": ["llm", "chat", "instruct", "text-generation", "dialog"],
        "exclude": ["ocr", "tts", "vision", "image", "audio", "speech"]
    },
    "OCR": {
        "keywords": ["ocr", "text-recognition", "document", "layout", "parse"],
    },
    "TTS": {
        "keywords": ["tts", "text-to-speech", "speech", "voice", "audio", "kokoro", "xtts"],
    },
    "Vision": {
        "keywords": ["vision", "image", "vl", "multimodal", "clip"],
    },
    "Embedding": {
        "keywords": ["embedding", "embeddings", "e5-", "bge-", "sentence-transformers"],
    },
    "Code": {
        "keywords": ["code", "coder", "programming", "dev"],
    },
    "Reasoning": {
        "keywords": ["reasoning", "think", "r1", "deepseek-r1"],
    },
    "Tools": {
        "keywords": ["tool", "function", "agent"],
    }
}

# 已测试模型记录（从 benchmark 报告读取）
TESTED_MODELS = {
    "JoyAI-LLM-Flash-Q4_K_M": {"size_gb": 28, "tested": True, "ctx": "16K"},
    "GLM-4.7-Flash-Q4_K_M": {"size_gb": 18, "tested": True, "ctx": "14K"},
    "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL": {"size_gb": 13, "tested": True, "ctx": "8K"},
}

# 高优先级厂商/架构
HIGH_PRIORITY_ARCHS = ["deepseek", "qwen", "glm", "minimax", "yi", "internlm"]
LOW_PRIORITY_ARCHS = ["llama", "mistral", "gemma", "phi"]  # 已有大量数据

# 模型版本系列定义 (用于过滤旧版本)
# 顺序很重要：前面的版本号更高（更新）
MODEL_VERSIONS = {
    # Qwen 系列 - Qwen3 > Qwen2.5 > Qwen2
    "qwen": ["qwen3", "qwen2.5", "qwen2", "qwen1.5", "qwen"],
    # GLM 系列
    "glm": ["glm-4.5", "glm-4", "glm-3", "chatglm3", "chatglm2", "chatglm"],
    # Llama 系列
    "llama": ["llama-3.3", "llama-3.2", "llama-3.1", "llama-3", "llama-2"],
    # Mistral 系列
    "mistral": ["mistral-large", "mistral-medium", "mistral-small", "mistral-7b", "mistral"],
    # DeepSeek 系列
    "deepseek": ["deepseek-v3", "deepseek-v2.5", "deepseek-v2", "deepseek-coder-v2", "deepseek-coder", "deepseek"],
    # Yi 系列
    "yi": ["yi-1.5", "yi"],
    # InternLM 系列
    "internlm": ["internlm3", "internlm2.5", "internlm2", "internlm"],
    # Phi 系列
    "phi": ["phi-4", "phi-3.5", "phi-3", "phi-2", "phi"],
    # Gemma 系列
    "gemma": ["gemma-3", "gemma-2", "gemma"],
    # MiniMax 系列
    "minimax": ["minimax-text-01", "minimax"],
}

# 版本号映射表（用于正确比较版本号）
VERSION_ORDER = {
    # Qwen 系列
    "qwen3": 30, "qwen2.5": 25, "qwen2": 20, "qwen1.5": 15, "qwen": 10,
    # GLM 系列
    "glm-4.5": 45, "glm-4": 40, "glm-3": 30, "chatglm3": 30, "chatglm2": 20, "chatglm": 10,
    # Llama 系列
    "llama-3.3": 33, "llama-3.2": 32, "llama-3.1": 31, "llama-3": 30, "llama-2": 20,
    # Mistral 系列
    "mistral-large": 40, "mistral-medium": 30, "mistral-small": 20, "mistral-7b": 15, "mistral": 10,
    # DeepSeek 系列
    "deepseek-v3": 30, "deepseek-v2.5": 25, "deepseek-v2": 20, "deepseek-coder-v2": 22, "deepseek-coder": 15, "deepseek": 10,
    # Yi 系列
    "yi-1.5": 15, "yi": 10,
    # InternLM 系列
    "internlm3": 30, "internlm2.5": 25, "internlm2": 20, "internlm": 10,
    # Phi 系列
    "phi-4": 40, "phi-3.5": 35, "phi-3": 30, "phi-2": 20, "phi": 10,
    # Gemma 系列
    "gemma-3": 30, "gemma-2": 20, "gemma": 10,
    # MiniMax 系列
    "minimax-text-01": 20, "minimax": 10,
}


def fetch_trending_gguf(limit: int = 100) -> List[Dict]:
    """获取 trending GGUF 模型"""
    try:
        url = f"{HF_ENDPOINT}/api/models"
        params = {
            "library": "gguf",
            "sort": "downloads",  # hf-mirror 支持 downloads
            "limit": limit,
            "full": "true"
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []


def parse_model_info(model: Dict) -> Dict:
    """解析模型信息"""
    model_id = model.get("id", "")
    parts = model_id.split("/")
    name = parts[-1] if len(parts) > 1 else model_id
    author = parts[0] if len(parts) > 1 else "unknown"

    # 估算模型大小
    size_info = estimate_model_size(name)

    # 检测架构
    arch = detect_architecture(name.lower())

    # 检测量化
    quant = detect_quantization(name)

    # 检测类别
    category = detect_category(name, model.get("tags", []), model.get("pipeline_tag", ""))

    return {
        "id": model_id,
        "name": name,
        "author": author,
        "downloads": model.get("downloads", 0),
        "likes": model.get("likes", 0),
        "tags": model.get("tags", []),
        "size_gb": size_info["size_gb"],
        "size_label": size_info["label"],
        "arch": arch,
        "quant": quant,
        "category": category,
        "can_test": size_info["size_gb"] <= MAX_MODEL_SIZE_GB,
        "priority": calculate_priority(name, arch, model),
    }


def estimate_model_size(name: str) -> Dict:
    """估算模型大小 - 优先匹配大数字"""
    name_lower = name.lower()

    # 从文件名提取参数信息 - 按大小降序，避免小数字覆盖大数字
    if "480b" in name_lower or "472b" in name_lower:
        return {"size_gb": 260, "label": "480B MoE", "params": "480B MoE"}
    elif "235b" in name_lower or "256b" in name_lower:
        return {"size_gb": 135, "label": "235B MoE", "params": "235B MoE"}
    elif "120b" in name_lower:
        return {"size_gb": 70, "label": "120B", "params": "120B"}
    elif "110b" in name_lower:
        return {"size_gb": 65, "label": "110B", "params": "110B"}
    elif "72b" in name_lower or "70b" in name_lower:
        return {"size_gb": 40, "label": "70B", "params": "70B"}
    elif "64b" in name_lower:
        return {"size_gb": 36, "label": "64B", "params": "64B"}
    elif "47b" in name_lower or "47.1b" in name_lower:
        return {"size_gb": 28, "label": "47B", "params": "47B"}
    elif "34b" in name_lower:
        return {"size_gb": 20, "label": "34B", "params": "34B"}
    elif "32b" in name_lower:
        return {"size_gb": 20, "label": "32B", "params": "32B"}
    elif "30b" in name_lower:
        return {"size_gb": 18, "label": "30B", "params": "30B"}
    elif "27b" in name_lower:
        return {"size_gb": 17, "label": "27B", "params": "27B"}
    elif "23b" in name_lower:
        return {"size_gb": 14, "label": "23B", "params": "23B"}
    elif "20b" in name_lower:
        return {"size_gb": 12, "label": "20B", "params": "20B"}
    elif "14b" in name_lower:
        return {"size_gb": 9, "label": "14B", "params": "14B"}
    elif "9b" in name_lower:
        return {"size_gb": 5.5, "label": "9B", "params": "9B"}
    elif "8b" in name_lower:
        return {"size_gb": 5, "label": "8B", "params": "8B"}
    elif "7b" in name_lower:
        return {"size_gb": 4.5, "label": "7B", "params": "7B"}
    elif "4b" in name_lower:
        return {"size_gb": 2.5, "label": "4B", "params": "4B"}
    elif "3b" in name_lower:
        return {"size_gb": 2, "label": "3B", "params": "3B"}
    elif "1.7b" in name_lower:
        return {"size_gb": 1.1, "label": "1.7B", "params": "1.7B"}
    elif "1.5b" in name_lower:
        return {"size_gb": 1, "label": "1.5B", "params": "1.5B"}
    elif "1b" in name_lower:
        return {"size_gb": 0.7, "label": "1B", "params": "1B"}
    elif "0.6b" in name_lower:
        return {"size_gb": 0.4, "label": "0.6B", "params": "0.6B"}
    elif "0.5b" in name_lower:
        return {"size_gb": 0.35, "label": "0.5B", "params": "0.5B"}

    # MoE 模型估算 (激活参数)
    if "a3b" in name_lower or "a22b" in name_lower:
        if "480b" in name_lower or "235b" in name_lower:
            return {"size_gb": 25, "label": "MoE-Large", "params": "200B+ MoE"}
        elif "30b" in name_lower or "80b" in name_lower:
            return {"size_gb": 18, "label": "MoE-Medium", "params": "30-80B MoE"}

    return {"size_gb": 15, "label": "Unknown", "params": "Unknown"}


def detect_category(name: str, tags: List[str], pipeline: str = "") -> str:
    """检测模型类别"""
    name_lower = name.lower()
    tags_lower = [t.lower() for t in tags]
    pipeline_lower = pipeline.lower()

    # 检查每个类别
    for category, config in MODEL_CATEGORIES.items():
        keywords = config.get("keywords", [])
        exclude = config.get("exclude", [])

        # 检查排除词
        should_exclude = False
        for exc in exclude:
            if exc in name_lower or exc in pipeline_lower:
                should_exclude = True
                break
        if should_exclude:
            continue

        # 检查关键词
        for kw in keywords:
            if kw in name_lower or kw in pipeline_lower:
                return category
            for tag in tags_lower:
                if kw in tag:
                    return category

    return "Other"


def detect_architecture(name: str) -> str:
    """检测模型架构"""
    arch_patterns = {
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "qwen2": "Qwen2",
        "qwen3": "Qwen3",
        "glm": "GLM",
        "chatglm": "GLM",
        "minimax": "MiniMax",
        "yi": "Yi",
        "internlm": "InternLM",
        "llama": "Llama",
        "mistral": "Mistral",
        "mixtral": "Mixtral",
        "gemma": "Gemma",
        "phi": "Phi",
    }

    for pattern, arch in arch_patterns.items():
        if pattern in name:
            return arch
    return "Other"


def detect_quantization(name: str) -> str:
    """检测量化类型"""
    name_lower = name.lower()

    if "q4_k_m" in name_lower:
        return "Q4_K_M"
    elif "q4_k_s" in name_lower:
        return "Q4_K_S"
    elif "q5_k_m" in name_lower:
        return "Q5_K_M"
    elif "q8_0" in name_lower:
        return "Q8_0"
    elif "q2_k" in name_lower:
        return "Q2_K"
    elif "iq4_nl" in name_lower or "iq4_xs" in name_lower:
        return "IQ4"
    elif "fp16" in name_lower:
        return "FP16"
    elif "bf16" in name_lower:
        return "BF16"
    elif "4bit" in name_lower:
        return "4bit"
    elif "8bit" in name_lower:
        return "8bit"

    return "Unknown"


def is_llm_model(model: Dict) -> bool:
    """判断是否为 LLM 模型（非 embedding/vision/audio）"""
    tags = [t.lower() for t in model.get("tags", [])]
    name = model.get("id", "").lower()
    pipeline = model.get("pipeline_tag", "").lower()

    # 必须有 text-generation 标签
    if "text-generation" not in tags:
        return False

    # 排除非 LLM 架构
    non_llm_patterns = [
        "bert", "roberta", "electra", "minilm", "mpnet", "e5-",
        "bge-", "jina-embeddings", "clip-", "whisper", "wav2vec",
        "t5-", "bart-", "finbert", "nsfw", "xlm-roberta",
        "speaker-diarization", "text-to-speech", "image-",
        "vision-", "video-", "colbert"
    ]

    for pattern in non_llm_patterns:
        if pattern in name:
            return False

    # pipeline 必须是 text-generation
    if pipeline and pipeline != "text-generation":
        return False

    return True


def calculate_priority(name: str, arch: str, model: Dict) -> int:
    """计算测试优先级 (1-10, 10最高)"""
    priority = 5
    name_lower = name.lower()

    # 非 LLM 模型直接返回 0
    if not is_llm_model(model):
        return 0

    # 排除测试/非生产模型
    test_patterns = ["gpt2", "opt-125m", "tiny-", "test-", "small-", "mini-", "dummy-", "demo-",
                     "gpt-oss-", "gpt-oss-120b"]
    for pattern in test_patterns:
        if pattern in name_lower:
            return 0

    # 高优先级架构 +4 (中国厂商 - 用户指定优先)
    if arch.lower() in HIGH_PRIORITY_ARCHS:
        priority += 4
    # 低优先级架构 -3 (西方主流架构，已有大量数据)
    elif arch.lower() in LOW_PRIORITY_ARCHS:
        priority -= 3

    # 下载量高 +2
    if model.get("downloads", 0) > 1000000:
        priority += 2
    elif model.get("downloads", 0) > 100000:
        priority += 1

    # Likes 高 +1
    if model.get("likes", 0) > 1000:
        priority += 1

    # 大小合适 (15B-30B) +2，这是最佳测试范围
    size_info = estimate_model_size(name)
    if 15 <= size_info["size_gb"] <= 30:
        priority += 2
    # 太小 (<10B) -5，不值得测试
    elif size_info["size_gb"] < 10:
        priority -= 5
    # 太大 (>35B) -3，可能OOM
    elif size_info["size_gb"] > 35:
        priority -= 3

    # MoE 模型 +1 (值得测试)
    if "moe" in str(model.get("tags", [])).lower() or "a3b" in name.lower():
        priority += 1

    return max(0, min(10, priority))


def check_already_tested(model_id: str) -> bool:
    """检查是否已经测试过"""
    # 检查 benchmark 目录
    for tested_id in TESTED_MODELS:
        if tested_id.lower() in model_id.lower():
            return True

    # 检查 presets 文件
    try:
        with open(PRESETS_FILE, 'r') as f:
            content = f.read()
            if model_id.split('/')[-1] in content:
                return True
    except:
        pass

    return False


def extract_model_version(name: str) -> tuple:
    """
    提取模型系列和版本信息
    返回: (series, version_str, version_num)
    例如: "Qwen2.5-32B" -> ("qwen", "2.5", 25)
           "Qwen3-8B" -> ("qwen", "3", 30)
           "llama-3.1-70b" -> ("llama", "3.1", 31)
    """
    name_lower = name.lower()

    for series, versions in MODEL_VERSIONS.items():
        # 检查是否属于这个系列
        series_in_name = series.replace("-", "") in name_lower or series in name_lower
        if not series_in_name:
            continue

        # 查找具体版本 (按顺序，先匹配高版本)
        for version_str in versions:
            version_normalized = version_str.lower().replace("-", "")

            # 检查完整版本字符串是否在模型名中
            if version_str in name_lower:
                # 使用预定义的版本顺序值
                version_num = VERSION_ORDER.get(version_str, 0)
                version_clean = version_str.replace(series, "").strip("-.") or version_str
                return series, version_clean, version_num

            # 检查简化版本名 (如 qwen3, glm4 等)
            if version_normalized in name_lower.replace("-", ""):
                version_num = VERSION_ORDER.get(version_str, 0)
                version_clean = version_str.replace(series, "").strip("-.") or version_str
                return series, version_clean, version_num

        # 属于系列但未找到具体版本，返回基础版本
        return series, "base", VERSION_ORDER.get(series, 0)

    return None, None, 0


def extract_model_size_tier(size_gb: float) -> str:
    """
    将模型大小分组为规模等级
    用于同规模版本比较
    """
    if size_gb >= 20:
        return "large"    # 20B+ 大模型
    elif size_gb >= 10:
        return "medium"   # 10-20B 中等模型
    elif size_gb >= 5:
        return "small"    # 5-10B 小模型
    else:
        return "tiny"     # <5B 微型模型


def filter_latest_versions(models: List[Dict]) -> List[Dict]:
    """
    过滤模型列表，按规模分组只保留每个系列的最新版本
    例如: Qwen3-8B 和 Qwen2.5-32B 都保留 (不同规模)
          Qwen3-8B 优先于 Qwen2.5-7B (同规模，新版本优先)
    """
    # 按系列和规模分组
    series_size_groups = {}

    for model in models:
        name = model.get("name", "")
        size_gb = model.get("size_gb", 15)
        series, version_str, version_num = extract_model_version(name)

        if series is None:
            # 无法识别版本，保留
            continue

        # 按规模等级分组
        size_tier = extract_model_size_tier(size_gb)
        group_key = f"{series}_{size_tier}"

        if group_key not in series_size_groups:
            series_size_groups[group_key] = []

        series_size_groups[group_key].append({
            "model": model,
            "version_str": version_str,
            "version_num": version_num,
            "series": series,
            "size_tier": size_tier,
        })

    # 需要过滤掉的旧版本模型ID
    filtered_out_ids = set()

    for group_key, versions in series_size_groups.items():
        if len(versions) <= 1:
            continue

        # 按版本号排序
        versions.sort(key=lambda x: x["version_num"], reverse=True)

        # 保留最新版本，标记旧版本
        latest_version = versions[0]["version_num"]
        series = versions[0]["series"]
        size_tier = versions[0]["size_tier"]

        for v in versions[1:]:
            # 如果版本差距 >= 5 (如 Qwen3 vs Qwen2.5)，过滤旧版本
            if latest_version - v["version_num"] >= 5:
                filtered_out_ids.add(v["model"]["id"])
                print(f"  [版本过滤] {series} ({size_tier}): 跳过 {v['model']['name']} ({v['version_str']}), 保留 {versions[0]['model']['name']} ({versions[0]['version_str']})")

    # 返回未被过滤的模型
    filtered_models = [m for m in models if m["id"] not in filtered_out_ids]

    return filtered_models


def generate_analysis_report(models: List[Dict]) -> str:
    """生成分析报告 - 按类别分组"""

    # 分类
    can_test = [m for m in models if m["can_test"] and not check_already_tested(m["id"])]
    too_large = [m for m in models if not m["can_test"]]
    already_tested = [m for m in models if check_already_tested(m["id"])]

    # 按优先级排序
    can_test.sort(key=lambda x: x["priority"], reverse=True)

    # 只保留真正的模型 (priority >= 1)
    valid_models = [m for m in can_test if m["priority"] >= 1]

    # 按类别分组
    categories = {}
    for m in valid_models:
        cat = m.get("category", "Other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)

    # 统计各架构数量
    arch_counts = {}
    for m in valid_models:
        arch = m["arch"]
        arch_counts[arch] = arch_counts.get(arch, 0) + 1

    report = f"""# HuggingFace Trending GGUF 模型分析报告 (按类别分类)

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **数据来源**: {HF_ENDPOINT}/models?library=gguf
> **分析模型数**: {len(models)}
> **有效模型**: {len(valid_models)}
> **大小限制**: <=40GB (V100 32GB)
> **架构分布**: {', '.join([f"{k}({v})" for k, v in sorted(arch_counts.items(), key=lambda x: -x[1])])}

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 有效模型总数 | {len(valid_models)} |
| 显存过大无法测试 (>40GB) | {len(too_large)} |
| 已测试/已记录 | {len(already_tested)} |

### 类别分布
| 类别 | 数量 | 说明 |
|------|------|------|
"""

    for cat in ["LLM", "OCR", "TTS", "Vision", "Code", "Reasoning", "Tools", "Embedding", "Other"]:
        count = len(categories.get(cat, []))
        if count > 0:
            report += f"| {cat} | {count} | - |\n"

    # 按类别生成详细表格
    category_order = ["LLM", "Vision", "Code", "Reasoning", "Tools", "OCR", "TTS", "Embedding", "Other"]

    for cat in category_order:
        if cat not in categories or not categories[cat]:
            continue

        cat_models = categories[cat]
        report += f"""

---

## {cat} 类别

| 优先级 | 模型 | 架构 | 大小 | 下载量 | 说明 |
|--------|------|------|------|--------|------|
"""

        for m in cat_models[:15]:  # 每类最多显示15个
            note = ""
            if m["arch"] in HIGH_PRIORITY_ARCHS:
                note += "中国厂商 "
            if 20 <= m["size_gb"] <= 40:
                note += "20-40B "
            elif m["size_gb"] < 10:
                note += "小模型 "

            report += f"| {m['priority']}/10 | {m['name'][:40]} | {m['arch']} | {m['size_label']} | {m['downloads']:,} | {note or '-'} |\n"

    report += f"""

## 显存过大无法测试

| 模型 | 预估大小 | 原因 |
|------|---------|------|
"""

    for m in too_large[:10]:
        report += f"| {m['name'][:40]} | {m['size_gb']}GB | 超过V100 32GB限制 |\n"

    report += f"""

## 已测试/已记录模型

| 模型 | 状态 |
|------|------|
"""

    for m in already_tested[:10]:
        status = "✅ 已测试" if m["name"] in TESTED_MODELS else "📝 已记录"
        report += f"| {m['name'][:40]} | {status} |\n"

    report += """

## 推荐下载命令 (Top 10)

```bash
# 设置镜像
export HF_ENDPOINT=https://hf-mirror.com

"""

    # 从所有类别中选取高优先级模型
    top_models = sorted(valid_models, key=lambda x: x["priority"], reverse=True)[:10]
    for m in top_models:
        author = m['id'].split('/')[0]
        report += f"""# {m['name'][:40]} ({m['size_label']}, {m['category']})
modelscope download --model {m['id']} \\
  --local_dir /mnt/volume3/modelscope_models/{author}/

"""

    report += f"""```

---

## 详细数据

### 测试决策矩阵

对于每个候选模型，评估维度：

| 维度 | 权重 | 说明 |
|------|------|------|
| 架构新颖性 | 30% | 是否为中国厂商/新架构 |
| 大小合适 | 25% | 20B-40B 最佳 |
| 下载热度 | 20% | >100K 下载量 |
| 社区认可 | 15% | >1000 likes |
| 量化效率 | 10% | Q4_K_M 优于 Q8_0 |

### 自动判定规则

**立即测试** (优先级 >= 8):
- 中国厂商 + 20B-40B + Q4量化 + 热门

**值得测试** (优先级 6-7):
- 满足上述部分条件

**暂不测试** (优先级 < 6):
- 西方主流架构 (Llama/Mistral 已有大量数据)
- 太小 (<10B) 或太大 (>35B)

**无法测试**:
- 显存需求 > 30GB

---

## 执行建议

```bash
# 下载高优先级模型 (示例)
export HF_ENDPOINT=https://hf-mirror.com

# Top 1 推荐
modelscope download --model <作者>/<模型名> \
  --local_dir /mnt/volume3/modelscope_models/<作者>/

# 然后运行 benchmark
/mnt/volume3/llama_cpp/benchmark_single.sh <模型路径>
```

---

## 原始数据

"""

    # 添加原始数据
    report += "\n### 所有候选模型 (JSON)\n\n```json\n"
    report += json.dumps([{
        "id": m["id"],
        "size_gb": m["size_gb"],
        "arch": m["arch"],
        "quant": m["quant"],
        "priority": m["priority"],
        "can_test": m["can_test"],
    } for m in can_test[:30]], indent=2, ensure_ascii=False)
    report += "\n```\n"

    return report


def main():
    print("=" * 60)
    print("HuggingFace Trending GGUF 模型自动分析")
    print("=" * 60)
    print()

    # 获取模型
    print("正在获取 trending 模型...")
    raw_models = fetch_trending_gguf(limit=100)

    if not raw_models:
        print("获取失败，请检查网络或 HF_ENDPOINT 设置")
        sys.exit(1)

    print(f"获取到 {len(raw_models)} 个模型")
    print()

    # 解析模型信息
    print("正在分析模型...")
    models = [parse_model_info(m) for m in raw_models]

    # 版本过滤: 只保留各系列的最新版本
    print("\n应用版本过滤 (只保留最新版本)...")
    original_count = len(models)
    models = filter_latest_versions(models)
    filtered_count = original_count - len(models)
    if filtered_count > 0:
        print(f"已过滤 {filtered_count} 个旧版本模型")

    # 生成报告
    print("正在生成分析报告...")
    report = generate_analysis_report(models)

    # 保存报告
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存: {OUTPUT_FILE}")
    print()

    # 输出摘要
    can_test = [m for m in models if m["can_test"] and not check_already_tested(m["id"])]
    high_priority = [m for m in can_test if m["priority"] >= 8]

    print("=" * 60)
    print("分析摘要")
    print("=" * 60)
    print(f"总模型数: {len(models)}")
    print(f"可测试: {len(can_test)}")
    print(f"高优先级 (>=8): {len(high_priority)}")
    print()

    if high_priority:
        print("立即推荐测试:")
        for m in high_priority[:5]:
            print(f"  [{m['priority']}/10] {m['name']} ({m['arch']}, {m['size_label']}, {m['quant']})")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
