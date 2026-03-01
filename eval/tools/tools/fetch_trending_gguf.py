#!/usr/bin/env python3
"""
抓取 HuggingFace Trending GGUF 模型并归类
输出到 topic 文档
"""

import requests
import json
from datetime import datetime

# 使用 HuggingFace API 获取 trending GGUF 模型
def fetch_trending_gguf(limit=100):
    """获取 trending GGUF 模型列表"""

    # HF API endpoint
    url = "https://huggingface.co/api/models"
    params = {
        "library": "gguf",
        "sort": "trending",
        "limit": limit,
        "full": "true"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def categorize_model(model):
    """根据模型名称和标签归类"""
    model_id = model.get('id', '').lower()
    tags = [t.lower() for t in model.get('tags', [])]

    categories = []

    # 架构分类
    if any(x in model_id for x in ['llama', 'meta-llama']):
        categories.append('Llama 系列')
    if any(x in model_id for x in ['qwen', 'qwen2', 'qwen3']):
        categories.append('Qwen 系列')
    if any(x in model_id for x in ['mistral']):
        categories.append('Mistral 系列')
    if any(x in model_id for x in ['deepseek']):
        categories.append('DeepSeek 系列')
    if any(x in model_id for x in ['gemma', 'google']):
        categories.append('Gemma 系列')
    if any(x in model_id for x in ['phi', 'microsoft']):
        categories.append('Phi 系列')
    if any(x in model_id for x in ['glm', 'chatglm']):
        categories.append('GLM 系列')
    if any(x in model_id for x in ['yi']):
        categories.append('Yi 系列')
    if any(x in model_id for x in ['internlm']):
        categories.append('InternLM 系列')

    # 功能分类
    if any(x in model_id for x in ['vision', 'vl', 'multimodal']):
        categories.append('多模态')
    if any(x in model_id for x in ['instruct', 'chat']):
        categories.append('对话模型')
    if any(x in model_id for x in ['coder', 'code']):
        categories.append('代码模型')
    if any(x in model_id for x in ['math', 'reasoning']):
        categories.append('推理模型')

    # 量化级别
    quant = '未知'
    if 'q4_k_m' in model_id or 'q4km' in model_id:
        quant = 'Q4_K_M'
    elif 'q4_k_s' in model_id or 'q4ks' in model_id:
        quant = 'Q4_K_S'
    elif 'q5_k_m' in model_id:
        quant = 'Q5_K_M'
    elif 'q8_0' in model_id:
        quant = 'Q8_0'
    elif 'q2_k' in model_id:
        quant = 'Q2_K'
    elif 'iq4' in model_id or 'iq4_xs' in model_id:
        quant = 'IQ4_XS'
    elif 'fp16' in model_id:
        quant = 'FP16'
    elif 'bf16' in model_id:
        quant = 'BF16'

    # 模型大小估算
    size = '未知'
    if '0.5b' in model_id or '1b' in model_id or '1.5b' in model_id:
        size = '<2B'
    elif '3b' in model_id or '4b' in model_id or '7b' in model_id:
        size = '3B-7B'
    elif '8b' in model_id or '9b' in model_id:
        size = '8B-9B'
    elif '14b' in model_id:
        size = '14B'
    elif '27b' in model_id or '32b' in model_id:
        size = '27B-32B'
    elif '70b' in model_id or '72b' in model_id:
        size = '70B+'

    if not categories:
        categories.append('其他')

    return {
        'name': model.get('id', ''),
        'likes': model.get('likes', 0),
        'downloads': model.get('downloads', 0),
        'description': model.get('description', '')[:100] + '...' if model.get('description') else 'N/A',
        'tags': tags[:5],  # 前5个标签
        'categories': categories,
        'quant': quant,
        'size': size,
        'pipeline_tag': model.get('pipeline_tag', 'unknown')
    }

def generate_report(models):
    """生成 topic 文档"""

    # 按类别分组
    by_category = {}
    by_size = {}

    for model in models:
        cat = categorize_model(model)

        # 按主要类别分组
        primary_cat = cat['categories'][0] if cat['categories'] else '其他'
        if primary_cat not in by_category:
            by_category[primary_cat] = []
        by_category[primary_cat].append(cat)

        # 按大小分组
        size = cat['size']
        if size not in by_size:
            by_size[size] = []
        by_size[size].append(cat)

    # 生成 Markdown 报告
    report = f"""# HuggingFace Trending GGUF 模型报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **数据来源**: https://huggingface.co/models?library=gguf&sort=trending
> **模型总数**: {len(models)}

---

## 按架构分类

"""

    for category, items in sorted(by_category.items()):
        report += f"\n### {category} ({len(items)} 个)\n\n"
        report += "| 模型名称 | 大小 | 量化 | 下载量 | Likes | 备注 |\n"
        report += "|---------|------|------|--------|-------|------|\n"

        # 按下载量排序
        items_sorted = sorted(items, key=lambda x: x['downloads'], reverse=True)[:15]  # 取前15

        for item in items_sorted:
            name = item['name'].split('/')[-1][:40]  # 截短名称
            report += f"| {name} | {item['size']} | {item['quant']} | {item['downloads']:,} | {item['likes']} | |\n"

    report += """

## 按模型大小分类

"""

    size_order = ['<2B', '3B-7B', '8B-9B', '14B', '27B-32B', '70B+', '未知']
    for size in size_order:
        if size in by_size:
            items = by_size[size]
            report += f"\n### {size} 参数模型 ({len(items)} 个)\n\n"

            items_sorted = sorted(items, key=lambda x: x['downloads'], reverse=True)[:10]
            for item in items_sorted:
                name = item['name'].split('/')[-1][:50]
                report += f"- **{name}** ({item['quant']}) - {item['downloads']:,} 下载\n"

    report += """

## 推荐测试列表

基于 V100 32GB 显存限制，以下模型适合测试：

### 高优先级 (已下载或热门)
"""

    # 找出值得测试的模型
    test_candidates = []
    for item in [categorize_model(m) for m in models]:
        if item['size'] in ['3B-7B', '8B-9B', '14B'] and item['quant'] in ['Q4_K_M', 'Q4_K_S', 'IQ4_XS']:
            test_candidates.append(item)

    test_candidates.sort(key=lambda x: x['downloads'], reverse=True)

    for item in test_candidates[:20]:
        name = item['name']
        report += f"- [ ] `{name}` ({item['size']}, {item['quant']})\n"

    report += """

### 中优先级 (较大的模型)
"""

    for item in test_candidates[20:40]:
        name = item['name'].split('/')[-1]
        report += f"- [ ] `{name}` ({item['size']}, {item['quant']})\n"

    report += """

### 低优先级 (超大模型，可能需要量化)
"""

    large_models = [categorize_model(m) for m in models if categorize_model(m)['size'] in ['27B-32B', '70B+']]
    large_models.sort(key=lambda x: x['downloads'], reverse=True)

    for item in large_models[:15]:
        name = item['name'].split('/')[-1]
        report += f"- [ ] `{name}` ({item['size']}, {item['quant']}) - 需要测试能否加载\n"

    report += """

---

## 测试状态追踪

| 模型 | 大小 | 量化 | 状态 | 预填充速度 | 生成速度 | 备注 |
|------|------|------|------|-----------|---------|------|
| JoyAI-LLM-Flash-Q4_K_M | 28GB | Q4_K_M | ✅ 已测试 | 471 t/s (16K) | 38 t/s | ctx=16K |
| GLM-4.7-Flash-REAP-23B-A3B | 13GB | IQ4_NL | ✅ 已测试 | 863 t/s (8K) | 32 t/s | ctx=8K |

"""

    return report

def main():
    print("正在获取 HuggingFace Trending GGUF 模型...")
    models = fetch_trending_gguf(limit=100)

    if not models:
        print("获取失败，尝试备用方法...")
        # 备用：使用本地已知模型列表
        return

    print(f"获取到 {len(models)} 个模型")

    report = generate_report(models)

    # 保存报告
    output_file = "/mnt/volume3/llama_cpp/trending_gguf_models.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"报告已保存到: {output_file}")

    # 同时输出摘要
    print("\n=== 模型分布 ===")
    sizes = {}
    for m in models:
        cat = categorize_model(m)
        s = cat['size']
        sizes[s] = sizes.get(s, 0) + 1

    for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"  {size}: {count} 个")

if __name__ == "__main__":
    main()
