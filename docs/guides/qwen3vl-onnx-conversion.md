# Qwen3-VL-4B ONNX 转换指南

> **重要提示**: GGUF 格式**无法**转换为 ONNX。必须从原始 PyTorch 模型转换。

---

## 1. 问题说明

### 为什么 GGUF 不能转 ONNX？

| 格式 | 内容 | 可否转换 |
|------|------|----------|
| **Safetensors/PY** | 完整权重 + 结构 | ✅ 可转 ONNX |
| **GGUF** | 仅量化权重 | ❌ 无法恢复结构 |

**GGUF 是量化后的"编译产物"，就像无法从可执行文件反编译回源代码一样。**

---

## 2. 可行方案

### 方案 A：使用 AMD 官方 ONNX 模型（推荐）

AMD 官方已提供部分模型的 ONNX 版本：

```bash
# 下载 AMD 官方 ONNX 模型
./scripts/download_amd_onnx_models.sh ~/models/ryzenai-onnx llama-3.2-1b

# 或使用 HuggingFace
export HF_ENDPOINT=https://hf-mirror.com
git clone $HF_ENDPOINT/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu \
  ~/models/ryzenai-onnx/llama-3.2-1b
```

**支持的模型**:
- Llama-3.2-1B-Instruct
- Llama-3.2-3B-Instruct
- Qwen2.5-0.5B-Instruct

### 方案 B：从 PyTorch 转换 Qwen3-VL-4B

需要下载原始模型并转换：

```bash
# 1. 创建虚拟环境
uv venv ~/venvs/onnx-export --seed --python python3.12
source ~/venvs/onnx-export/bin/activate

# 2. 安装依赖
pip install torch torchvision
pip install transformers optimum[exporters] onnx onnxruntime-genai

# 3. 下载原始 Qwen3-VL-4B 模型
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download Qwen/Qwen3-VL-4B-Instruct \
  --local-dir ~/models/Qwen3-VL-4B-Instruct-Original

# 4. 运行转换脚本
cd /mnt/volume3/llama_cpp
python scripts/convert_qwen3vl_to_onnx.py \
  ~/models/Qwen3-VL-4B-Instruct-Original \
  ~/models/Qwen3-VL-4B-ONNX
```

---

## 3. 转换脚本说明

### 脚本位置
`/mnt/volume3/llama_cpp/scripts/convert_qwen3vl_to_onnx.py`

### 用法

```bash
# 基本用法
python convert_qwen3vl_to_onnx.py <模型路径> <输出目录>

# 示例 - 从本地模型
python convert_qwen3vl_to_onnx.py \
  /mnt/volume3/modelscope_models/Qwen/Qwen3-VL-4B-Instruct-Original \
  ./qwen3vl-onnx

# 示例 - 从 HuggingFace 直接下载
python convert_qwen3vl_to_onnx.py \
  Qwen/Qwen3-VL-4B-Instruct \
  ./qwen3vl-onnx
```

### 依赖安装

```bash
# 使用现有虚拟环境
source ~/venvs/model_tools/bin/activate

# 安装必要依赖
pip install torch transformers optimum[exporters] onnx

# 或使用脚本自动安装
./scripts/setup_onnx_export_env.sh
```

---

## 4. 实际测试（使用现有模型）

由于 Qwen3-VL-4B 转换复杂，**建议先用现有模型测试 NPU 性能**：

### 4.1 下载 Llama-3.2-1B ONNX

```bash
mkdir -p ~/models/ryzenai-onnx
cd ~/models/ryzenai-onnx

export HF_ENDPOINT=https://hf-mirror.com
git clone $HF_ENDPOINT/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu
```

### 4.2 启动 NPU 服务

```bash
cd /mnt/volume3/llama_cpp

# 下载 ryzenai-server
./bin/llama-npu-server.sh download

# 启动服务
export LLAMA_NPU_MODEL=~/models/ryzenai-onnx/Llama-3.2-1B-Instruct-onnx-ryzenai-npu/model.onnx
./bin/llama-npu-server.sh start
```

### 4.3 运行性能测试

```bash
# 使用测试脚本
./tests/benchmark_npu_qwen3vl.sh

# 或手动测试
curl http://localhost:8404/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 100
  }'
```

---

## 5. Qwen3-VL-4B 转换注意事项

### 技术挑战

1. **视觉语言模型**: Qwen3-VL 包含视觉编码器和语言模型
2. **多模态输入**: 需要同时处理图像和文本
3. **复杂架构**: 包含 RoPE、SwiGLU 等特殊组件

### 可能的解决方案

1. **仅导出文本部分**: 先测试文本生成性能
2. **使用官方工具**: 等待 AMD 官方支持
3. **使用 GGUF 替代**: 在 Vulkan/CUDA 后端运行 GGUF 版本

---

## 6. 推荐方案

**对于 Qwen3-VL-4B，推荐使用 Vulkan 后端**：

```bash
# 1. 下载 GGUF 模型
export HF_ENDPOINT=https://hf-mirror.com
git clone $HF_ENDPOINT/Qwen/Qwen3-VL-4B-Instruct-GGUF \
  /mnt/volume3/modelscope_models/Qwen/Qwen3-VL-4B-Instruct-GGUF

# 2. 启动 Vulkan 服务器
export LLAMA_VULKAN_MODEL="/mnt/volume3/modelscope_models/Qwen/Qwen3-VL-4B-Instruct-GGUF/Qwen3VL-4B-Instruct-Q8_0.gguf"
./bin/llama-server-vulkan.sh start

# 3. 性能测试
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好"}], "max_tokens": 256}'
```

---

## 7. 文件清单

| 文件 | 用途 |
|------|------|
| `scripts/convert_qwen3vl_to_onnx.py` | ONNX 转换脚本 |
| `scripts/download_amd_onnx_models.sh` | AMD 官方模型下载 |
| `tests/benchmark_npu_qwen3vl.sh` | NPU 性能测试 |
| `docs/guides/gguf-to-onnx.md` | GGUF/ONNX 格式说明 |

---

## 8. 总结

| 需求 | 推荐方案 |
|------|----------|
| **测试 NPU 性能** | 使用 Llama-3.2-1B ONNX |
| **使用 Qwen3-VL-4B** | Vulkan 后端 (GGUF) |
| **转换 Qwen3-VL** | 等待官方支持或自行研究 |

---

*文档创建时间：2026-02-20*
