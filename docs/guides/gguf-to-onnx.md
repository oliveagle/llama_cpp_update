# GGUF 转 ONNX 模型指南

> **重要**: GGUF 格式不能直接转换为 ONNX。需要从原始 PyTorch 模型重新导出。

---

## 1. 格式说明

| 格式 | 说明 | 用途 |
|------|------|------|
| **GGUF** | llama.cpp 专用量化格式 | CPU/GPU 推理 (llama.cpp) |
| **ONNX** | 开放神经网络交换格式 | 通用 ML 推理 (AMD NPU 等) |
| **Safetensors** | PyTorch 权重格式 | 模型训练/存储 |

**转换流程**:
```
Safetensors/PY 模型
       ↓
   ONNX 导出 (使用 transformers 或 optimum)
       ↓
ONNX Runtime GenAI 优化 (AMD NPU 需要)
       ↓
   Ryzen AI 部署
```

---

## 2. AMD Ryzen AI 支持的模型

### 2.1 官方支持的模型

AMD 官方提供了以下模型的 ONNX 版本：

| 模型 | 大小 | 链接 |
|------|------|------|
| Llama-3.2-1B-Instruct | 1B | [HF](https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu) |
| Llama-3.2-3B-Instruct | 3B | [HF](https://huggingface.co/amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu) |
| Qwen2.5-0.5B | 0.5B | [AMD Collection](https://huggingface.co/collections/amd/ryzenai-15-llm-npu-models-6859846d7c13f81298990db0) |

### 2.2 Qwen3-VL-4B 状态

**截至 2026-02-20**，AMD 官方**尚未**提供 Qwen3-VL-4B 的 ONNX 模型。

**替代方案**:
1. 使用 GGUF 格式在 Vulkan/CUDA 后端运行（推荐）
2. 自行转换模型到 ONNX（复杂，需要 ONNX 导出经验）

---

## 3. 通用 ONNX 转换方法

### 3.1 环境准备

```bash
# 创建虚拟环境
python -m venv ~/venvs/onnx-export
source ~/venvs/onnx-export/bin/activate

# 安装依赖
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers optimum onnx onnxruntime-genai
```

### 3.2 使用 Optimum 导出

```python
from optimum.exporters.onnx import export_from_model, main_export
from transformers import AutoModelForCausalLM, AutoTokenizer

# 模型路径
model_id = "Qwen/Qwen3-VL-4B-Instruct"

# 导出
main_export(
    model_name_or_path=model_id,
    output="./qwen3-vl-4b-onnx",
    task="text-generation",
    opset=17,
)
```

### 3.3 使用 Transformers 直接导出

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "Qwen/Qwen3-VL-4B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    trust_remote_code=True
)

# 准备示例输入
dummy_input = tokenizer("Hello, world!", return_tensors="pt")

# 导出
torch.onnx.export(
    model,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "qwen3-vl-4b.onnx",
    opset_version=17,
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "logits": {0: "batch_size", 1: "sequence_length"}
    }
)
```

---

## 4. AMD Ryzen AI 优化

### 4.1 使用 ONNX Runtime GenAI

AMD RyzenAI-Server 基于 ONNX Runtime GenAI，需要特定的模型优化：

```bash
# 安装 ONNX Runtime GenAI (AMD NPU 版本)
pip install onnxruntime-genai-directml
```

### 4.2 模型优化脚本

```python
import onnx
from onnxruntime.quantization import quantize_dynamic, QuantType

# 加载模型
model_path = "qwen3-vl-4b.onnx"

# 量化（可选，减小体积）
quantize_dynamic(
    model_path,
    "qwen3-vl-4b-quant.onnx",
    weight_type=QuantType.QUInt8
)
```

---

## 5. 使用现有 GGUF 模型（推荐方案）

由于 ONNX 转换复杂，**推荐使用 GGUF 格式在 Vulkan/CUDA 后端运行**：

### 5.1 Vulkan 后端 (AMD GPU)

```bash
# 下载 Qwen3-VL-4B GGUF
git lfs install
git clone https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF

# 启动 Vulkan 服务器
./bin/llama-server-vulkan.sh start

# 测试
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen3-VL-4B",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 5.2 CUDA 后端 (NVIDIA GPU)

```bash
# 启动 CUDA 服务器
./bin/llama-server-cuda.sh start
```

---

## 6. 性能比较

| 后端 | 硬件 | 预期性能 | 备注 |
|------|------|----------|------|
| Vulkan | AMD GPU | 20-50 tok/s | 推荐 |
| CUDA | NVIDIA GPU | 30-80 tok/s | 推荐 |
| RyzenAI NPU | AMD NPU | TBD | 需 ONNX 模型 |
| CPU | 通用 CPU | 5-15 tok/s | 兼容性好 |

---

## 7. 模型下载

### 7.1 GGUF 模型（推荐）

```bash
# ModelScope（国内镜像）
export HF_ENDPOINT=https://hf-mirror.com
git clone $HF_ENDPOINT/Qwen/Qwen3-VL-4B-Instruct-GGUF

# HuggingFace
git clone https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF
```

### 7.2 ONNX 模型（AMD 官方）

```bash
# Llama-3.2-1B ONNX
git clone https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu

# Llama-3.2-3B ONNX
git clone https://huggingface.co/amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu
```

---

## 8. 测试 NPU 性能

一旦有了 ONNX 模型，可以使用以下脚本测试：

```bash
# 设置模型路径
export LLAMA_NPU_MODEL=/path/to/model.onnx

# 运行基准测试
./tests/benchmark_npu_qwen3vl.sh
```

---

## 9. 参考资料

- [AMD Ryzen AI 文档](https://ryzenai.docs.amd.com/)
- [ONNX Runtime GenAI](https://github.com/microsoft/onnxruntime-genai)
- [Optimum ONNX Export](https://huggingface.co/docs/optimum/onnx/export_models)
- [Qwen3-VL GGUF](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF)

---

*文档创建时间：2026-02-20*
