# GGUF 模型评测工具指南

> 按类别推荐最适合的评测工具

---

## 1. LLM (通用语言模型)

### 首选: lm-eval-harness ✅ 已安装
```bash
source venv/bin/activate
lm-eval run --model gguf --model_args base_url=<模型路径> --tasks cevalid,cmmlu,mmlu,gsm8k
```

**支持任务**: C-Eval, CMMLU, MMLU, GSM8K, HumanEval, MBPP 等 200+

### 备选: OpenCompass (中文更强)
```bash
pip install opencompass
# 支持 C-Eval, CMMLU, Gaokao 等中文评测
```

---

## 2. Vision (视觉/多模态)

### 首选: VLMEvalKit
```bash
git clone https://github.com/open-compass/VLMEvalKit.git
cd VLMEvalKit
pip install -e .

# 运行评测
python run.py --data VQAv2 TextVQA --model Qwen3-VL-8B --mode infer
```

**支持数据集**: VQAv2, TextVQA, MMBench, SEED-Bench, MM-Vet

### 备选: lmms-eval
```bash
pip install lmms-eval
# 专门针对多模态模型的评测框架
```

---

## 3. Code (代码模型)

### 首选: CodeXGLUE + HumanEval
```bash
# HumanEval (已包含在 lm-eval 中)
lm-eval run --tasks humaneval --model gguf --model_args base_url=<模型路径>

# 或使用原始 HumanEval
pip install human-eval
```

### 完整方案: BigCode Evaluation Harness
```bash
git clone https://github.com/bigcode-project/bigcode-evaluation-harness.git
cd bigcode-evaluation-harness
pip install -e .

# 评测
accelerate launch main.py \
  --model <模型路径> \
  --tasks humaneval,mbpp \
  --temperature 0.2 \
  --n_samples 1
```

**支持任务**: HumanEval, MBPP, DS-1000, Multiple-E 等

---

## 4. OCR (文字识别)

### 首选: PaddleOCR 评测工具
```bash
pip install paddleocr paddlepaddle

# 使用 ICDAR 数据集评测
python -m paddleocr.eval \
  --model_dir <模型路径> \
  --use_gpu true \
  --dataset icdar2019
```

### 备选: MMOCR
```bash
git clone https://github.com/open-mmlab/mmocr.git
cd mmocr
pip install -v -e .

# 评测
python tools/test.py \
  configs/textrecog/satrn/satrn_icdar2015.py \
  <模型权重>
```

### 文档理解: DocVQA 评测
```bash
pip install datasets
python -c "
from datasets import load_dataset
dataset = load_dataset('docvqa')
# 自定义评测脚本
"
```

---

## 5. TTS (语音合成)

### 首选: SpeechBrain
```bash
pip install speechbrain

# 使用 MOS 评测
python -m speechbrain.utils.tts_eval \
  --model_path <模型路径> \
  --test_data <测试音频>
```

### 自然度评测: MOS/CMOS
```bash
# 需要人工评分，或使用 ASR 反测
pip install transformers
python eval_tts_mos.py --model <模型> --references <参考音频>
```

### 客观指标: Mel Cepstral Distortion
```bash
pip install pypesq pystoi
python eval_tts_objective.py --generated <生成音频> --reference <参考音频>
```

---

## 6. Reasoning (推理模型)

### 首选: lm-eval (数学推理)
```bash
lm-eval run --tasks gsm8k,mathqa,logiqa --model gguf --model_args base_url=<模型路径>
```

### 高级推理: MATH Dataset
```bash
git clone https://github.com/hendrycks/math.git
cd math
python eval_math.py --model <模型路径>
```

### 综合推理: AGIEval
```bash
# 包含高考、公务员考试等
pip install agieval
python -m agieval.run --model <模型路径> --tasks gaokao-math,lsat
```

---

## 7. Embedding (文本嵌入) - 暂不测试

### 首选: MTEB
```bash
pip install mteb

# 运行评测
python -m mteb.run \
  --model <模型路径> \
  --tasks STS17,STS22,BIOSSES
```

---

## 8. Tools/Agent (工具使用)

### 首选: ToolBench
```bash
git clone https://github.com/OpenBMB/ToolBench.git
cd ToolBench
pip install -r requirements.txt

# 评测
python toolbench_eval.py --model <模型路径>
```

### 备选: APIBench
```bash
pip install apibench
python -m apibench.run --model <模型路径> --dataset toolformer
```

---

## 快速安装脚本

```bash
#!/bin/bash
# 安装所有评测工具

source venv/bin/activate

# LLM (已有)
# lm-eval 已安装

# Vision
pip install VLMEvalKit

# Code
pip install human-eval

# OCR
pip install paddleocr paddlepaddle

# TTS
pip install speechbrain pypesq pystoi

# Reasoning (使用 lm-eval)
# 已有 gsm8k

# Agent
pip install toolbench
```

---

## 评测矩阵汇总

| 类别 | 首选工具 | 关键数据集 | 安装难度 |
|------|----------|-----------|---------|
| LLM | lm-eval ✅ | C-Eval, MMLU, GSM8K | 低 |
| Vision | VLMEvalKit | VQAv2, TextVQA | 中 |
| Code | lm-eval / BigCode | HumanEval, MBPP | 低/中 |
| OCR | PaddleOCR | ICDAR2019, DocVQA | 中 |
| TTS | SpeechBrain | MOS, WER | 中 |
| Reasoning | lm-eval | GSM8K, MATH | 低 |
| Tools | ToolBench | ToolBench | 中 |
| Embedding | MTEB | STS, BIOSSES | 低 |

---

## 明日行动建议

1. **安装 Vision 评测**: VLMEvalKit
2. **测试 Qwen3-VL-8B** 作为 Vision 黄金标杆
3. **安装 Code 评测**: BigCode Harness
4. **测试 Qwen3-Coder-Next** 作为 Code 黄金标杆
5. **llama.cpp 支持检查**: 确认 lm-eval 的 gguf backend 是否正常工作
