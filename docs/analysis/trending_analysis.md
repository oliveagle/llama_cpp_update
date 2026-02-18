# HuggingFace Trending GGUF 模型分析报告 (按类别分类)

> **生成时间**: 2026-02-17 13:09
> **数据来源**: https://hf-mirror.com/models?library=gguf
> **分析模型数**: 93
> **有效模型**: 4
> **大小限制**: <=40GB (V100 32GB)
> **架构分布**: Qwen(3), Yi(1)

---

## 执行摘要

| 指标 | 数值 |
|------|------|
| 有效模型总数 | 4 |
| 显存过大无法测试 (>40GB) | 1 |
| 已测试/已记录 | 4 |

### 类别分布
| 类别 | 数量 | 说明 |
|------|------|------|
| LLM | 4 | - |


---

## LLM 类别

| 优先级 | 模型 | 架构 | 大小 | 下载量 | 说明 |
|--------|------|------|------|--------|------|
| 10/10 | Qwen2.5-32B-Instruct | Qwen | 32B | 4,427,163 | 20-40B  |
| 10/10 | dolphin-2.9.1-yi-1.5-34b | Yi | 34B | 4,203,031 | 20-40B  |
| 6/10 | Qwen3-8B | Qwen | 8B | 4,685,993 | 小模型  |
| 6/10 | Qwen3-1.7B | Qwen | 7B | 4,176,824 | 小模型  |


## 显存过大无法测试

| 模型 | 预估大小 | 原因 |
|------|---------|------|
| gpt-oss-120b | 70GB | 超过V100 32GB限制 |


## 已测试/已记录模型

| 模型 | 状态 |
|------|------|
| Qwen3-0.6B | 📝 已记录 |
| Qwen3-4B | 📝 已记录 |
| Qwen3-4B-Instruct-2507 | 📝 已记录 |
| Qwen3-VL-8B-Instruct | 📝 已记录 |


## 推荐下载命令 (Top 10)

```bash
# 设置镜像
export HF_ENDPOINT=https://hf-mirror.com

# Qwen2.5-32B-Instruct (32B, LLM)
modelscope download --model Qwen/Qwen2.5-32B-Instruct \
  --local_dir /mnt/volume3/modelscope_models/Qwen/

# dolphin-2.9.1-yi-1.5-34b (34B, LLM)
modelscope download --model dphn/dolphin-2.9.1-yi-1.5-34b \
  --local_dir /mnt/volume3/modelscope_models/dphn/

# Qwen3-8B (8B, LLM)
modelscope download --model Qwen/Qwen3-8B \
  --local_dir /mnt/volume3/modelscope_models/Qwen/

# Qwen3-1.7B (7B, LLM)
modelscope download --model Qwen/Qwen3-1.7B \
  --local_dir /mnt/volume3/modelscope_models/Qwen/

```

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
modelscope download --model <作者>/<模型名>   --local_dir /mnt/volume3/modelscope_models/<作者>/

# 然后运行 benchmark
/mnt/volume3/llama_cpp/benchmark_single.sh <模型路径>
```

---

## 原始数据


### 所有候选模型 (JSON)

```json
[
  {
    "id": "Qwen/Qwen2.5-32B-Instruct",
    "size_gb": 20,
    "arch": "Qwen",
    "quant": "Unknown",
    "priority": 10,
    "can_test": true
  },
  {
    "id": "dphn/dolphin-2.9.1-yi-1.5-34b",
    "size_gb": 20,
    "arch": "Yi",
    "quant": "Unknown",
    "priority": 10,
    "can_test": true
  },
  {
    "id": "Qwen/Qwen3-8B",
    "size_gb": 5,
    "arch": "Qwen",
    "quant": "Unknown",
    "priority": 6,
    "can_test": true
  },
  {
    "id": "Qwen/Qwen3-1.7B",
    "size_gb": 4.5,
    "arch": "Qwen",
    "quant": "Unknown",
    "priority": 6,
    "can_test": true
  },
  {
    "id": "sentence-transformers/all-MiniLM-L6-v2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "google-bert/bert-base-uncased",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "google/electra-base-discriminator",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "Falconsai/nsfw_image_detection",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "sentence-transformers/all-mpnet-base-v2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "timm/mobilenetv3_small_100.lamb_in1k",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "FacebookAI/xlm-roberta-base",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "laion/clap-htsat-fused",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "FacebookAI/roberta-large",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "openai/clip-vit-base-patch32",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "pyannote/wespeaker-voxceleb-resnet34-LM",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "BAAI/bge-m3",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "colbert-ir/colbertv2.0",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "pyannote/segmentation-3.0",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "pyannote/speaker-diarization-3.1",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "amazon/chronos-2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "Bingsu/adetailer",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "dima806/fairface_age_image_detection",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "alana89/TabSTAR",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "autogluon/chronos-bolt-small",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "omni-research/Tarsier2-Recap-7b",
    "size_gb": 4.5,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "cross-encoder/ms-marco-MiniLM-L6-v2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "openai-community/gpt2",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "FacebookAI/roberta-base",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  },
  {
    "id": "openai/clip-vit-large-patch14",
    "size_gb": 15,
    "arch": "Other",
    "quant": "Unknown",
    "priority": 0,
    "can_test": true
  }
]
```
