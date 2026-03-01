# ONNX Runtime Server 使用指南

## 概述

ONNX Runtime Server 是一个基于 ONNX Runtime 的高性能推理服务，支持多种 Execution Provider：

- **CPU**: 默认，适用于所有系统
- **CUDA**: NVIDIA GPU 加速
- **ROCm**: AMD GPU 加速
- **XDNA**: AMD XDNA2 NPU (需要特殊编译)
- **OpenVINO**: Intel OpenVINO 加速
- **TensorRT**: NVIDIA TensorRT 加速

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
source ~/venvs/py312/bin/activate

# 安装依赖
pip install onnxruntime flask numpy
```

### 2. 启动服务

```bash
# 使用默认配置启动
./bin/llama-onnx-server.sh start

# 使用指定模型启动
LLAMA_ONNX_MODEL=/path/to/model.onnx ./bin/llama-onnx-server.sh start

# 使用特定 EP 启动
LLAMA_ONNX_EP=cpu ./bin/llama-onnx-server.sh start
```

### 3. 测试服务

```bash
# 健康检查
curl http://localhost:8406/health

# 列出会话
curl http://localhost:8406/sessions

# 查看日志
./bin/llama-onnx-server.sh logs
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLAMA_ONNX_HOST` | 服务器地址 | `0.0.0.0` |
| `LLAMA_ONNX_PORT` | 服务器端口 | `8406` |
| `LLAMA_ONNX_MODEL` | ONNX 模型路径 | Qwen3-0.6B INT8 |
| `LLAMA_ONNX_EP` | Execution Provider | `cpu` |
| `LLAMA_ONNX_THREADS` | CPU 线程数 | `1` |
| `LLAMA_ONNX_VENV` | Python 虚拟环境 | `py312` |

## API 文档

### 健康检查

```bash
GET /health
```

响应：
```json
{
  "status": "ok",
  "sessions": 1
}
```

### 列出会话

```bash
GET /sessions
```

响应：
```json
{
  "sessions": ["default"],
  "stats": {
    "default": {
      "inference_count": 0,
      "total_time_ms": 0.0,
      "average_time_ms": 0,
      "ep": "CPUExecutionProvider",
      "model_path": "/path/to/model.onnx"
    }
  }
}
```

### 创建会话

```bash
POST /sessions
Content-Type: application/json

{
  "session_id": "my_model",
  "model_path": "/path/to/model.onnx",
  "ep": "cpu",
  "num_threads": 4
}
```

响应：
```json
{
  "session_id": "my_model",
  "model_path": "/path/to/model.onnx",
  "ep": "CPUExecutionProvider",
  "inputs": [...],
  "outputs": [...]
}
```

### 运行推理

```bash
POST /sessions/<session_id>/run
Content-Type: application/json

{
  "inputs": {
    "input_ids": [[1, 2, 3]],
    "attention_mask": [[1, 1, 1]],
    "position_ids": [[0, 1, 2]]
  }
}
```

响应：
```json
{
  "outputs": {
    "logits": [[...]],
    "present.0.key": [...]
  },
  "stats": {
    "inference_count": 1
  }
}
```

## 管理命令

```bash
# 启动服务
./bin/llama-onnx-server.sh start

# 停止服务
./bin/llama-onnx-server.sh stop

# 重启服务
./bin/llama-onnx-server.sh restart

# 查看状态
./bin/llama-onnx-server.sh status

# 查看日志
./bin/llama-onnx-server.sh logs

# 测试模型
./bin/llama-onnx-server.sh test

# 列出可用模型
./bin/llama-onnx-server.sh list
```

## 可用模型

当前已下载的 Qwen3-0.6B ONNX 模型：

| 模型 | 大小 | 量化 | 说明 |
|------|------|------|------|
| `model.onnx` | 301 MB | 无 | 标准 ONNX |
| `model_fp16.onnx` | 1.2 GB | FP16 | 半精度 |
| `model_int8.onnx` | 590 MB | INT8 | 推荐 |
| `model_q4.onnx` | 877 MB | Q4 | 4-bit |
| `model_q4f16.onnx` | 544 MB | Q4F16 | 混合量化 |

## 使用指定模型

```bash
# 使用 INT8 模型
LLAMA_ONNX_MODEL=/mnt/volume3/llama_cpp/models/qwen3-onnx/Qwen3-0.6B-ONNX/onnx/model_int8.onnx \
  ./bin/llama-onnx-server.sh start

# 使用 FP16 模型
LLAMA_ONNX_MODEL=/mnt/volume3/llama_cpp/models/qwen3-onnx/Qwen3-0.6B-ONNX/onnx/model_fp16.onnx \
  ./bin/llama-onnx-server.sh start

# 使用 Q4 模型
LLAMA_ONNX_MODEL=/mnt/volume3/llama_cpp/models/qwen3-onnx/Qwen3-0.6B-ONNX/onnx/model_q4.onnx \
  ./bin/llama-onnx-server.sh start
```

## Systemd 服务

### 安装服务

```bash
# 复制 systemd 服务文件
sudo cp systemd/llama-onnx-server.service /etc/systemd/system/

# 重新加载 systemd
sudo systemctl daemon-reload

# 启用服务
sudo systemctl enable llama-onnx-server

# 启动服务
sudo systemctl start llama-onnx-server
```

### 管理服务

```bash
# 查看状态
sudo systemctl status llama-onnx-server

# 启动/停止/重启
sudo systemctl start llama-onnx-server
sudo systemctl stop llama-onnx-server
sudo systemctl restart llama-onnx-server

# 查看日志
sudo journalctl -u llama-onnx-server -f
```

## 性能优化

### CPU 优化

```bash
# 增加线程数
LLAMA_ONNX_THREADS=4 ./bin/llama-onnx-server.sh start

# 或设置环境变量
export OMP_NUM_THREADS=4
export OPENBLAS_NUM_THREADS=4
```

### 使用特定 EP

```bash
# CUDA (需要编译带 CUDA EP 的 ORT)
LLAMA_ONNX_EP=cuda ./bin/llama-onnx-server.sh start

# ROCm (需要编译带 ROCm EP 的 ORT)
LLAMA_ONNX_EP=rocm ./bin/llama-onnx-server.sh start

# OpenVINO
LLAMA_ONNX_EP=openvino ./bin/llama-onnx-server.sh start
```

## 故障排查

### 模型加载失败

```bash
# 检查模型文件
ls -lh $LLAMA_ONNX_MODEL

# 测试模型
./bin/llama-onnx-server.sh test
```

### 端口冲突

```bash
# 检查端口占用
netstat -tlnp | grep 8406

# 使用其他端口
LLAMA_ONNX_PORT=8407 ./bin/llama-onnx-server.sh start
```

### 查看日志

```bash
# 查看实时日志
./bin/llama-onnx-server.sh logs

# 或直接查看
tail -f /mnt/volume3/llama_cpp/logs/onnx-server.log
```

## 下一步

- **XDNA NPU 支持**: 需要编译带 XDNA EP 的 ONNX Runtime
- **性能测试**: 运行基准测试脚本
- **多模型支持**: 加载多个模型进行对比测试

## 相关链接

- [ONNX Runtime 官方文档](https://onnxruntime.ai/)
- [ONNX Runtime GitHub](https://github.com/onnxruntime/onnxruntime)
- [XDNA Execution Provider](https://github.com/onnxruntime/onnxruntime/tree/main/onnxruntime/core/providers/xdna)
