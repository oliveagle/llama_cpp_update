# RyzenAI Backend 使用指南

> **功能**: AMD NPU 推理支持 via RyzenAI-Server
> **模型格式**: ONNX
> **平台**: Linux (内核 ≥ 6.8)

---

## 1. 系统要求

### 硬件要求
- **AMD Ryzen AI 300 系列** 或更新处理器
- **NPU**: XDNA 或 XDNA2 架构

### 软件要求
- **Linux 内核**: ≥ 6.8
- **驱动**: amdxdna (已加载)
- **依赖**: libcurl, libzip

### 检查要求

```bash
# 检查内核版本
uname -r  # 需要 ≥ 6.8

# 检查驱动
lsmod | grep amdxdna

# 检查 NPU
lspci | grep "1022:17f0\|1022:1502"
```

---

## 2. 安装

### 2.1 安装依赖

```bash
sudo apt update
sudo apt install libcurl4-openssl-dev libzip-dev
```

### 2.2 编译 RyzenAI 后端

```bash
cd /mnt/volume3/llama_cpp/src/ryzenai
make
```

### 2.3 下载 ryzenai-server

```bash
# 使用 llama-server 下载
./llama-server --ryzenai-download
```

或者手动下载:
```bash
# 从 GitHub 下载
wget https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip

# 解压到缓存目录
mkdir -p ~/.cache/llama.cpp/ryzenai-server
unzip ryzenai-server.zip -d ~/.cache/llama.cpp/ryzenai-server/
chmod +x ~/.cache/llama.cpp/ryzenai-server/ryzenai-server
```

---

## 3. 使用

### 3.1 准备 ONNX 模型

从 HuggingFace 下载 AMD 优化的 ONNX 模型:

- [Ryzen AI NPU 模型集合](https://huggingface.co/collections/amd/ryzenai-15-llm-npu-models-6859846d7c13f81298990db0)
- [Ryzen AI Hybrid 模型集合](https://huggingface.co/collections/amd/ryzenai-15-llm-hybrid-models-6859a64b421b5c27e1e53899)

示例下载:
```bash
# 下载 Llama-3.2-1B-Instruct ONNX 模型
git lfs install
git clone https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu
```

### 3.2 启动服务

```bash
# 基本用法
./llama-server --ryzenai \
    --ryzenai-model /path/to/model.onnx \
    --port 8400

# 指定上下文长度
./llama-server --ryzenai \
    --ryzenai-model /path/to/model.onnx \
    --ryzenai-ctx-size 4096 \
    --port 8400

# 调试模式
./llama-server --ryzenai \
    --ryzenai-model /path/to/model.onnx \
    --debug
```

### 3.3 测试推理

```bash
# 聊天完成
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    "max_tokens": 256
  }'

# 文本完成
curl http://localhost:8400/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Once upon a time",
    "max_tokens": 128
  }'
```

---

## 4. 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--ryzenai` | 启用 RyzenAI 后端 | - |
| `--ryzenai-model <path>` | ONNX 模型路径 | - |
| `--ryzenai-ctx-size <n>` | 上下文长度 | 8192 |
| `--ryzenai-port <n>` | ryzenai-server 端口 | 自动选择 |
| `--ryzenai-download` | 下载 ryzenai-server 并退出 | - |

### 环境变量

| 变量 | 说明 |
|------|------|
| `LLAMA_RYZENAI_SERVER_BIN` | 自定义 ryzenai-server 路径 |
| `LLAMA_RYZENAI_SERVER_VERSION` | ryzenai-server 版本 |

---

## 5. 性能优化

### 5.1 NPU 功耗模式

```bash
# 设置 NPU 为高性能模式
sudo amd-smi power --set-mode high
```

### 5.2 内存分配

确保系统有足够内存:
- 1B 模型：约 2GB
- 3B 模型：约 4GB
- 7B 模型：约 8GB

### 5.3 上下文长度

根据模型大小和内存调整:
```bash
# 小模型可使用更长上下文
--ryzenai-ctx-size 16384

# 大模型使用较短上下文
--ryzenai-ctx-size 2048
```

---

## 6. 故障排除

### 6.1 ryzenai-server 未找到

**错误**: `ryzenai-server not found`

**解决**:
```bash
# 下载 ryzenai-server
./llama-server --ryzenai-download

# 或手动安装
wget https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip
unzip ryzenai-server.zip -d ~/.cache/llama.cpp/ryzenai-server/
```

### 6.2 模型加载失败

**错误**: `Model not found`

**解决**:
- 检查模型路径是否正确
- 确认模型是 ONNX 格式 (.onnx)
- 检查文件权限

### 6.3 端口冲突

**错误**: `Port already in use`

**解决**:
```bash
# 指定其他端口
--ryzenai-port 8003
```

### 6.4 NPU 不可用

**错误**: 服务启动后无法响应

**检查**:
```bash
# 检查驱动
lsmod | grep amdxdna

# 检查内核版本
uname -r  # 需要 ≥ 6.8

# 查看 NPU 状态
dmesg | grep -i npu
```

---

## 7. 支持的模型

### 官方支持模型

| 模型 | 大小 | 格式 | 链接 |
|------|------|------|------|
| Llama-3.2-1B-Instruct | 1B | ONNX | [HF](https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu) |
| Llama-3.2-3B-Instruct | 3B | ONNX | [HF](https://huggingface.co/amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu) |
| Qwen2.5-0.5B | 0.5B | ONNX | [HF](https://huggingface.co/collections/amd/ryzenai-15-llm-npu-models-6859846d7c13f81298990db0) |

### 模型转换

如需转换其他模型，参考 AMD 官方指南:
- [Ryzen AI 模型准备指南](https://ryzenai.docs.amd.com/en/latest/oga_model_prepare.html)

---

## 8. 参考资料

- [RyzenAI-Server GitHub](https://github.com/lemonade-sdk/ryzenai-server)
- [Lemonade SDK](https://github.com/lemonade-sdk/lemonade)
- [ONNX Runtime GenAI](https://github.com/microsoft/onnxruntime-genai)
- [AMD Ryzen AI 文档](https://ryzenai.docs.amd.com/)

---

*文档创建时间：2026-02-20*
