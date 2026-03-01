#!/usr/bin/env python3
"""
HuggingFace Trending GGUF 深度分析脚本
- 获取更多模型 (最多500个)
- 专门寻找20B-40B参数模型
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
OUTPUT_FILE = "/mnt/volume3/llama_cpp/trending_analysis_deep.md"

# V100 限制
V100_MEMORY_GB = 32
MAX_MODEL_SIZE_GB = 40  # 放宽到40B

# 已测试模型记录
TESTED_MODELS = {
    "JoyAI-LLM-Flash-Q4_K_M": {"size_gb": 28, "tested": True, "ctx": "16K"},
    "GLM-4.7-Flash-Q4_K_M": {"size_gb": 18, "tested": True, "ctx": "14K"},
    "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL": {"size_gb": 13, "tested": True, "ctx": "8K"},
}

# 架构优先级
HIGH_PRIORITY_ARCHS = ["deepseek", "qwen", "glm", "minimax", "yi", "internlm"]
LOW_PRIORITY_ARCHS = ["llama", "mistral", "gemma", "phi"]


def fetch_models_batch(limit: int = 100, offset: int = 0) -> List[Dict]:
    """获取一批模型"""
    try:
        url = f"{HF_ENDPOINT}/api/models"
        params = {
            "library": "gguf",
            "sort": "downloads",
            "limit": limit,
            "offset": offset,
            "full": "true"
        }
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching models (offset={offset}): {e}")
        return []


def fetch_all_models(total: int = 500) -> List[Dict]:
    """获取所有模型（分页）"""
    all_models = []
    batch_size = 100

    for offset in range(0, total, batch_size):
        print(f"  获取模型 {offset+1}-{min(offset+batch_size, total)}...")
        batch = fetch_models_batch(limit=batch_size, offset=offset)
        if not batch:
            break
        all_models.extend(batch)
        if len(batch) < batch_size:
            break

    return all_models


def estimate_model_size(name: str) -> Dict:
    """估算模型大小"""
    name_lower = name.lower()

    # 按大小降序，避免小数字覆盖大数字
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

    if "a3b" in name_lower or "a22b" in name_lower:
        if "480b" in name_lower or "235b" in name_lower:
            return {"size_gb": 25, "label": "MoE-Large", "params": "200B+ MoE"}
        elif "30b" in name_lower or "80b" in name_lower:
            return {"size_gb": 18, "label": "MoE-Medium", "params": "30-80B MoE"}

    return {"size_gb": 15, "label": "Unknown", "params": "Unknown"}


def detect_architecture(name: str) -> str:
    """检测模型架构"""
    arch_patterns = {
        "deepseek": "DeepSeek",
        "qwen": "Qwen",
        "qwen2": "Qwen",
        "qwen3": "Qwen",
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

    name_lower = name.lower()
    for pattern, arch in arch_patterns.items():
        if pattern in name_lower:
            return arch
    return "Other"


def is_llm_model(model: Dict) -> bool:
    """判断是否为 LLM 模型"""
    tags = [t.lower() for t in model.get("tags", [])]
    name = model.get("id", "").lower()
    pipeline = model.get("pipeline_tag", "").lower()

    if "text-generation" not in tags:
        return False

    non_llm_patterns = [
        "bert", "roberta", "electra", "minilm", "mpnet", "e5-",
        "bge-", "jina-embeddings", "clip-", "whisper", "wav2vec",
        "t5-", "bart-", "finbert", "nsfw", "xlm-roberta",
        "speaker-diarization", "text-to-speech", "image-",
        "vision-", "video-", "colbert", "chronos", "adetailer"
    ]

    for pattern in non_llm_patterns:
        if pattern in name:
            return False

    if pipeline and pipeline != "text-generation":
        return False

    return True


def calculate_priority(name: str, arch: str, model: Dict) -> int:
    """计算测试优先级"""
    priority = 5
    name_lower = name.lower()

    if not is_llm_model(model):
        return 0

    test_patterns = ["gpt2", "opt-125m", "tiny-", "test-", "small-", "mini-", "dummy-", "demo-",
                     "gpt-oss-", "gpt-oss-120b"]
    for pattern in test_patterns:
        if pattern in name_lower:
            return 0

    if arch.lower() in HIGH_PRIORITY_ARCHS:
        priority += 4
    elif arch.lower() in LOW_PRIORITY_ARCHS:
        priority -= 3

    if model.get("downloads", 0) > 1000000:
        priority += 2
    elif model.get("downloads", 0) > 100000:
        priority += 1

    if model.get("likes", 0) > 1000:
        priority += 1

    size_info = estimate_model_size(name)
    if 15 <= size_info["size_gb"] <= 30:
        priority += 2
    elif size_info["size_gb"] < 10:
        priority -= 5
    elif size_info["size_gb"] > 35:
        priority -= 3

    if "moe" in str(model.get("tags", [])).lower() or "a3b" in name.lower():
        priority += 1

    return max(0, min(10, priority))


def parse_model_info(model: Dict) -> Dict:
    """解析模型信息"""
    model_id = model.get("id", "")
    parts = model_id.split("/")
    name = parts[-1] if len(parts) > 1 else model_id
    author = parts[0] if len(parts) > 1 else "unknown"

    size_info = estimate_model_size(name)
    arch = detect_architecture(name.lower())

    return {
        "id": model_id,
        "name": name,
        "author": author,
        "downloads": model.get("downloads", 0),
        "likes": model.get("likes", 0),
        "tags": model.get("tags", []),
        "size_gb": size_info["size_gb"],
        "size_label": size_info["label"],
        "params": size_info["params"],
        "arch": arch,
        "can_test": size_info["size_gb"] <= MAX_MODEL_SIZE_GB,
        "priority": calculate_priority(name, arch, model),
    }


def generate_deep_report(models: List[Dict]) -> str:
    """生成深度分析报告"""
    # 去重：基于模型ID
    seen_ids = set()
    unique_models = []
    for m in models:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            unique_models.append(m)

    llm_models = [m for m in unique_models if m["priority"] >= 1]
    target_models = [m for m in llm_models if 15 <= m["size_gb"] <= 30]
    target_models.sort(key=lambda x: x["priority"], reverse=True)

    arch_counts = {}
    for m in llm_models:
        arch = m["arch"]
        arch_counts[arch] = arch_counts.get(arch, 0) + 1

    report = f"""# HuggingFace GGUF 深度分析报告 (20B-40B专题)

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **分析模型数**: {len(models)}
> **有效LLM模型**: {len(llm_models)}
> **20B-30B目标模型**: {len(target_models)}
> **架构分布**: {', '.join([f"{k}({v})" for k, v in sorted(arch_counts.items(), key=lambda x: -x[1])])}

---

## 20B-40B 黄金区间模型推荐

| 排名 | 模型 | 架构 | 参数量 | 预估大小 | 优先级 | 下载量 |
|------|------|------|--------|----------|--------|--------|
"""

    for idx, m in enumerate(target_models[:20], 1):
        report += f"| {idx} | {m['name'][:45]} | {m['arch']} | {m['params']} | {m['size_label']} | {m['priority']}/10 | {m['downloads']:,} |\n"

    if not target_models:
        report += "| - | 暂无符合条件的模型 | - | - | - | - | - |\n"

    report += f"""

## 模型分布统计

### 按大小分布
| 大小范围 | 模型数量 | 说明 |
|----------|----------|------|
| 20-30GB (黄金区间) | {len([m for m in llm_models if 20 <= m['size_gb'] <= 30])} | 最适合V100测试 |
| 15-20GB | {len([m for m in llm_models if 15 <= m['size_gb'] < 20])} | 可测试，性能较好 |
| 10-15GB | {len([m for m in llm_models if 10 <= m['size_gb'] < 15])} | 较小，优先级低 |
| <10GB | {len([m for m in llm_models if m['size_gb'] < 10])} | 太小，暂不关注 |
| >30GB | {len([m for m in llm_models if m['size_gb'] > 30])} | 可能OOM |

### 按架构分布
| 架构 | 数量 | 优先级 |
|------|------|--------|
"""

    for arch, count in sorted(arch_counts.items(), key=lambda x: -x[1]):
        priority = "高" if arch.lower() in HIGH_PRIORITY_ARCHS else ("低" if arch.lower() in LOW_PRIORITY_ARCHS else "中")
        report += f"| {arch} | {count} | {priority} |\n"

    report += """

## 推荐下载测试 (Top 10)

```bash
export HF_ENDPOINT=https://hf-mirror.com

"""

    for m in target_models[:10]:
        author = m['author']
        report += f"""# {m['name'][:40]} ({m['params']})
modelscope download --model {m['id']} \
  --local_dir /mnt/volume3/modelscope_models/{author}/

"""

    report += "```\n\n"

    report += f"""## 原始数据 (20B-30B模型)

```json
{json.dumps([{
    "id": m["id"],
    "params": m["params"],
    "size_gb": m["size_gb"],
    "arch": m["arch"],
    "priority": m["priority"],
    "downloads": m["downloads"],
} for m in target_models[:30]], indent=2, ensure_ascii=False)}
```
"""

    return report


def main():
    print("=" * 60)
    print("HuggingFace GGUF 深度分析 (20B-40B专题)")
    print("=" * 60)
    print()

    print("正在获取模型列表 (最多500个)...")
    raw_models = fetch_all_models(total=500)

    if not raw_models:
        print("获取失败，请检查网络或 HF_ENDPOINT 设置")
        sys.exit(1)

    print(f"获取到 {len(raw_models)} 个模型")
    print()

    print("正在分析模型...")
    models = [parse_model_info(m) for m in raw_models]

    # 去重：基于模型ID
    seen_ids = set()
    unique_models = []
    for m in models:
        if m["id"] not in seen_ids:
            seen_ids.add(m["id"])
            unique_models.append(m)
    models = unique_models

    llm_count = len([m for m in models if m["priority"] >= 1])
    target_count = len([m for m in models if 15 <= m["size_gb"] <= 30])

    print(f"有效LLM模型: {llm_count}")
    print(f"20B-30B目标模型: {target_count}")
    print()

    print("正在生成深度分析报告...")
    report = generate_deep_report(models)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存: {OUTPUT_FILE}")
    print()

    target_models = [m for m in models if 15 <= m["size_gb"] <= 30]
    target_models.sort(key=lambda x: x["priority"], reverse=True)

    print("=" * 60)
    print("分析摘要")
    print("=" * 60)
    print(f"总模型数: {len(models)}")
    print(f"有效LLM: {llm_count}")
    print(f"20B-30B目标: {target_count}")
    print()

    if target_models:
        print("20B-30B推荐模型:")
        for m in target_models[:5]:
            print(f"  [{m['priority']}/10] {m['name']} ({m['arch']}, {m['params']})")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
