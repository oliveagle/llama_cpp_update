# GGUF 模型能力评估框架

> **目标**: 建立标准化模型评估体系，设置各类别黄金标杆

---

## 0. 评估要求 (重要!)

### 所有模型必须评估的能力

无论模型属于哪个类别，**所有模型**都必须测试以下能力：

| 必测能力 | 评估工具 | 关键指标 |
|---------|---------|---------|
| 基础能力 | lm-eval | C-Eval, CMMLU, MMLU, GSM8K |
| **代码生成** | HumanEval, MBPP | **pass@1 - 所有模型必测** |
| **工具使用** | eval_tools_capability.py | **准确率 - 所有模型必测** |

### 一键评估命令

```bash
# 激活虚拟环境
source venv/bin/activate

# 综合能力评估 (基础 + 代码 + 工具)
python3 eval/eval_all_capabilities.py \
  --model-path /path/to/model.gguf \
  --model-name ModelName \
  --model-url http://localhost:8401
```

---

## 1. 评估框架选型

### 推荐方案: llm-eval-harness (EleutherAI)

**已安装** ✅

```bash
# 安装 (已使用venv)
python3 -m venv venv
source venv/bin/activate
pip install lm-eval

# 验证
lm-eval --help
```

**可用评测任务**:
- `ceval-valid` - 中文理解
- `cmmlu` - 中文多任务
- `mmlu` - 英文综合
- `metabench_gsm8k_subset` - 数学推理
- `humaneval` - 代码生成
- `mbpp` - 多语言代码

**优势**:
- 支持llama.cpp后端 (通过gguf参数)
- 200+标准化评测数据集
- 社区认可度高

### 备选方案: OpenCompass

```bash
# 适合中文模型评估
pip install opencompass
```

---

## 2. 各类别评估指标与黄金标杆

### LLM (通用语言模型)

| 评测任务 | 数据集 | 黄金标杆 | 说明 |
|----------|--------|----------|------|
| 中文理解 | C-Eval | Qwen2.5-72B | 高中/大学/专业科目 |
| 英文理解 | MMLU | Llama-3.1-70B | 57个学科 |
| 推理能力 | GSM8K | Qwen2.5-72B | 数学应用题 |
| 代码能力 | HumanEval | DeepSeek-Coder-33B | 函数生成 |
| 长文本 | LongBench | GLM-4-9B | 128K上下文 |
| 对齐评测 | MT-Bench | GPT-4 | 多轮对话质量 |

**本地黄金标杆 (V100可承受)**:
- **基准**: JoyAI-LLM-Flash-Q4_K_M (28GB)
- **性能目标**: C-Eval >= 70%, GSM8K >= 75%

### OCR (文字识别)

| 评测任务 | 数据集 | 黄金标杆 | 说明 |
|----------|--------|----------|------|
| 印刷体识别 | ICDAR-2019 | PaddleOCR-CRNN | 中英文 |
| 手写识别 | IAM | TrOCR | 英文手写 |
| 文档理解 | DocVQA | LayoutLMv3 | 版面分析 |
| 表格识别 | TableBank | Table-Transformer | 结构化输出 |

**本地黄金标杆**:
- **待确定**: 需要寻找<=40GB的OCR模型

### TTS (语音合成)

| 评测任务 | 指标 | 黄金标杆 | 说明 |
|----------|------|----------|------|
| 音质 | MOS | XTTS-v2 | 主观评分 |
| 相似度 | SIM | CosyVoice | 与参考音频相似度 |
| 鲁棒性 | WER | 标准ASR反测 | 语音识别错误率 |

**本地黄金标杆**:
- **待确定**: Kokoro-82M较小，需要中等规模模型

### Vision (视觉/多模态)

| 评测任务 | 数据集 | 黄金标杆 | 说明 |
|----------|--------|----------|------|
| 视觉问答 | VQAv2 | Qwen3-VL-8B | 理解准确率 |
| 文本VQA | TextVQA | Qwen3-VL-8B | 图中文字理解 |

**本地黄金标杆 (V100可承受)**:
- **基准**: Qwen3-VL-8B-Instruct (8GB) ✅ 已下载
- **备选**: Qwen3-VL-4B-Instruct (4GB) ✅ 已下载

### Code (代码模型)

| 评测任务 | 数据集 | 黄金标杆 | 说明 |
|----------|--------|----------|------|
| 代码生成 | HumanEval | DeepSeek-Coder-33B | pass@1 |
| 多语言 | MBPP | CodeLlama-34B | Python/C++/Java |
| 代码补全 | RepoBench | StarCoder2-15B | 长上下文 |

**本地黄金标杆 (V100可承受)**:
- **候选**: Qwen3-Coder-Next (已下载，需测试)

### Reasoning (推理模型)

| 评测任务 | 数据集 | 黄金标杆 | 说明 |
|----------|--------|----------|------|
| 数学推理 | GSM8K | DeepSeek-R1-32B | 思维链 |
| 逻辑推理 | LogiQA | QwQ-32B | 逻辑推断 |
| 科学推理 | ScienceQA | O1-mini | 多模态推理 |

**本地黄金标杆**:
- **待确定**: 需要寻找推理专用模型

---

## 3. 评估脚本设计

### 脚本结构

```
eval/
├── eval_llm.py           # LLM综合评估
├── eval_ocr.py           # OCR评估
├── eval_tts.py           # TTS评估
├── eval_vision.py        # 视觉评估
├── eval_code.py          # 代码评估
├── eval_embedding.py     # Embedding评估
├── golden_benchmarks.py  # 黄金标杆定义
└── run_all_evals.py      # 批量评估入口
```

### 黄金标杆定义格式

```python
GOLDEN_BENCHMARKS = {
    "LLM": {
        "model": "JoyAI-LLM-Flash-Q4_K_M",
        "size_gb": 28,
        "metrics": {
            "C-Eval": 0.72,
            "GSM8K": 0.78,
            "HumanEval": 0.65,
        }
    },
    "OCR": {
        "model": "TBD",
        "metrics": {"Accuracy": 0.95}
    },
    # ...
}
```

---

## 4. 评估流程

### 步骤1: 安装依赖
```bash
pip install lm-eval openai  # 用于API调用
```

### 步骤2: 启动模型服务
```bash
# 使用现有的llama-server启动待测模型
./llama-server-cuda.sh start
```

### 步骤3: 运行评估
```bash
# 评估单个模型
python eval/eval_llm.py --model-url http://localhost:8401 --model-name <name>

# 对比黄金标杆
python eval/compare_with_golden.py --category LLM --model <model_id>
```

### 步骤4: 生成报告
```bash
python eval/generate_report.py --output report.md
```

---

## 5. 当前状态

### 已确定本地黄金标杆

| 类别 | 模型 | 大小 | 状态 |
|------|------|------|------|
| LLM | JoyAI-LLM-Flash-Q4_K_M | 28GB | ✅ 已测试 |
| LLM | GLM-4.7-Flash-Q4_K_M | 18GB | ✅ 已测试 |
| LLM | GLM-4.7-Flash-REAP-IQ4_NL | 13GB | ✅ 已测试 |

### 待确定黄金标杆

- OCR: 需要寻找<=40GB模型
- TTS: 需要寻找<=40GB模型
- Vision: Qwen2-VL-7B需要测试
- Code: Qwen3-Coder-Next需要测试
- Reasoning: 需要寻找推理专用模型
- Embedding: bge-m3需要测试

---

## 6. 下一步行动

1. **安装lm-eval-harness**
2. **确定各类别黄金标杆模型**
3. **创建评估脚本**
4. **运行基线评估** (对已有模型)
5. **建立自动化流程**
