# llama-npu-server 独立服务指南

> **AMD NPU 推理服务** - 基于 RyzenAI-Server (ONNX Runtime GenAI)
> **端口**: 8404 (默认)
> **平台**: Linux (内核 ≥ 6.8)

> **⚠️ 状态: 搁置 (2026-02-20)**
>
> 官方 `ryzenai-server` **仅支持 Windows 11**，无 Linux 版本。
>
> 本指南和代码已保留，等待以下替代方案：
> - [DragonNPU Framework](https://github.com/In2infinity/dragon-npu) - 通用 NPU 框架
> - ONNX Runtime + Vitis AI Execution Provider - 直接集成
> - AMD ROCm 7.2 Linux 支持
>
> 如需在 Linux 上使用 AMD NPU，请参考上述替代方案。

---

## 1. 快速开始

### 1.1 编译

```bash
cd /mnt/volume3/llama_cpp/src/ryzenai
make server
```

编译完成后生成 `llama-npu-server` 可执行文件（约 120KB）。

### 1.2 下载 ryzenai-server

```bash
# 方法 1: 使用管理脚本
./bin/llama-npu-server.sh download

# 方法 2: 直接运行
./src/ryzenai/llama-npu-server --download

# 方法 3: 指定版本
export LLAMA_RYZENAI_SERVER_VERSION=v1.7.0
./src/ryzenai/llama-npu-server --download
```

### 1.3 启动服务

```bash
# 设置环境变量
export LLAMA_NPU_MODEL=/path/to/model.onnx
export LLAMA_NPU_PORT=8404
export LLAMA_NPU_HOST=127.0.0.1

# 启动
./bin/llama-npu-server.sh start
```

### 1.4 测试 API

```bash
# 聊天完成
curl http://localhost:8404/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "max_tokens": 256
  }'

# 文本完成
curl http://localhost:8404/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Once upon a time",
    "max_tokens": 128
  }'

# 健康检查
curl http://localhost:8404/health
```

---

## 2. 命令行参数

### 2.1 直接运行

```bash
./src/ryzenai/llama-npu-server [选项]

选项:
  -m, --model <path>      ONNX 模型路径 (必需)
  --port <n>              服务器端口 (默认：0=自动选择)
  --host <addr>           绑定地址 (默认：127.0.0.1)
  --ctx-size <n>          上下文长度 (默认：8192)
  --debug                 启用调试模式
  --download              下载 ryzenai-server 并退出
  --version               显示版本
  -h, --help              显示帮助
```

### 2.2 管理脚本

```bash
./bin/llama-npu-server.sh {start|stop|restart|status|logs|download}
```

| 命令 | 说明 |
|------|------|
| `start` | 启动服务 |
| `stop` | 停止服务 |
| `restart` | 重启服务 |
| `status` | 查看状态 |
| `logs` | 查看实时日志 |
| `download [version]` | 下载 ryzenai-server |

### 2.3 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLAMA_NPU_MODEL` | ONNX 模型路径 | - |
| `LLAMA_NPU_PORT` | 服务端口 | 0 (自动) |
| `LLAMA_NPU_HOST` | 绑定地址 | 127.0.0.1 |
| `LLAMA_NPU_CTX_SIZE` | 上下文长度 | 8192 |
| `LLAMA_RYZENAI_SERVER_VERSION` | ryzenai-server 版本 | v1.7.0 |
| `LLAMA_RYZENAI_SERVER_BIN` | 自定义 ryzenai-server 路径 | - |

---

## 3. Systemd 服务

### 3.1 安装服务

```bash
# 编辑服务文件（修改模型路径等）
vim /mnt/volume3/llama_cpp/systemd/llama-npu-server.service

# 安装
sudo /mnt/volume3/llama_cpp/systemd/install-npu-service.sh
```

### 3.2 服务管理

```bash
# 启动
sudo systemctl start llama-npu-server.service

# 停止
sudo systemctl stop llama-npu-server.service

# 重启
sudo systemctl restart llama-npu-server.service

# 查看状态
sudo systemctl status llama-npu-server.service

# 开机自启
sudo systemctl enable llama-npu-server.service

# 查看日志
journalctl -u llama-npu-server -f
```

### 3.3 服务文件配置

编辑 `/etc/systemd/system/llama-npu-server.service`:

```ini
[Service]
# 修改这些配置
Environment="LLAMA_NPU_MODEL=/path/to/your/model.onnx"
Environment="LLAMA_NPU_PORT=8404"
Environment="LLAMA_NPU_HOST=127.0.0.1"
```

---

## 4. 获取 ONNX 模型

### 4.1 从 HuggingFace 下载

```bash
# 安装 git-lfs
sudo apt install git-lfs
git lfs install

# 下载 AMD RyzenAI 模型
git clone https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu
git clone https://huggingface.co/amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu

# 或使用 HF 镜像
export HF_ENDPOINT=https://hf-mirror.com
git clone $HF_ENDPOINT/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu
```

### 4.2 支持的模型

| 模型 | 大小 | 链接 |
|------|------|------|
| Llama-3.2-1B-Instruct | 1B | [HF](https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu) |
| Llama-3.2-3B-Instruct | 3B | [HF](https://huggingface.co/amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu) |
| Qwen2.5-0.5B | 0.5B | [AMD Collection](https://huggingface.co/collections/amd/ryzenai-15-llm-npu-models-6859846d7c13f81298990db0) |

---

## 5. 故障排除

### 5.1 ryzenai-server 未找到

```bash
# 下载
./bin/llama-npu-server.sh download

# 或手动下载
wget https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip
mkdir -p ~/.cache/llama.cpp/ryzenai-server
unzip ryzenai-server.zip -d ~/.cache/llama.cpp/ryzenai-server/
chmod +x ~/.cache/llama.cpp/ryzenai-server/ryzenai-server
```

### 5.2 模型加载失败

```bash
# 检查模型文件
ls -lh /path/to/model.onnx

# 确认是 ONNX 格式
file /path/to/model.onnx

# 检查权限
chmod 644 /path/to/model.onnx
```

### 5.3 端口冲突

```bash
# 查看端口占用
lsof -i :8404

# 使用其他端口
export LLAMA_NPU_PORT=8405
./bin/llama-npu-server.sh start
```

### 5.4 NPU 不可用

```bash
# 检查内核版本
uname -r  # 需要 ≥ 6.8

# 检查驱动
lsmod | grep amdxdna

# 检查 NPU 设备
lspci | grep "1022:17f0\|1022:1502"

# 查看内核日志
dmesg | grep -i npu
```

### 5.5 查看日志

```bash
# 实时日志
./bin/llama-npu-server.sh logs

# 日志文件
tail -f /mnt/volume3/llama_cpp/logs/llama-npu-server.log

# Systemd 日志
journalctl -u llama-npu-server -n 100
```

---

## 6. 性能优化

### 6.1 NPU 功耗模式

```bash
# 设置高性能模式（需要 root）
sudo amd-smi power --set-mode high
```

### 6.2 上下文长度

根据模型大小调整：

```bash
# 小模型 (0.5B-1B)
export LLAMA_NPU_CTX_SIZE=16384

# 中等模型 (3B)
export LLAMA_NPU_CTX_SIZE=8192

# 大模型 (7B+)
export LLAMA_NPU_CTX_SIZE=4096
```

### 6.3 内存分配

确保系统有足够内存：

| 模型大小 | 所需内存 |
|----------|----------|
| 0.5B | ~1GB |
| 1B | ~2GB |
| 3B | ~4GB |
| 7B | ~8GB |

---

## 7. API 参考

### 7.1 聊天完成

```bash
POST /v1/chat/completions

Request:
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "你好"}
  ],
  "max_tokens": 256,
  "temperature": 0.7
}

Response:
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "你好！有什么我可以帮助你的吗？"
    },
    "finish_reason": "stop"
  }]
}
```

### 7.2 文本完成

```bash
POST /v1/completions

Request:
{
  "prompt": "Once upon a time",
  "max_tokens": 128,
  "temperature": 0.7
}
```

### 7.3 健康检查

```bash
GET /health

Response:
{"status": "ok"}
```

---

## 8. 文件结构

```
llama_cpp/
├── bin/
│   └── llama-npu-server.sh      # 管理脚本
├── src/ryzenai/
│   ├── llama-npu-server         # 可执行文件
│   ├── main.cpp                 # 主程序
│   ├── ryzenai_backend.h/cpp    # 后端逻辑
│   ├── process_manager.h/cpp    # 进程管理
│   ├── http_client.h/cpp        # HTTP 客户端
│   └── downloader.h/cpp         # 下载器
├── logs/
│   └── llama-npu-server.log     # 日志文件
├── systemd/
│   ├── llama-npu-server.service # Systemd 服务
│   └── install-npu-service.sh   # 安装脚本
└── models/
    └── onnx/                    # ONNX 模型目录
        └── model.onnx
```

---

## 9. 参考资料

- [RyzenAI-Server GitHub](https://github.com/lemonade-sdk/ryzenai-server)
- [ONNX Runtime GenAI](https://github.com/microsoft/onnxruntime-genai)
- [AMD Ryzen AI 文档](https://ryzenai.docs.amd.com/)
- [RyzenAI 后端指南](../docs/guides/ryzenai-backend-guide.md)

---

*文档创建时间：2026-02-20*
