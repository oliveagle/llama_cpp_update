# AMD NPU Qwen3 性能测试完整指南

> **机器**: AMD Ryzen AI 300 系列 (Strix Halo, gfx1151)
> **NPU 设备**: 1022:17f0 (AMD XDNA2)
> **模型**: Qwen3-0.6B-ONNX
> **目标**: 测试 NPU 推理吞吐性能 (tokens/s)

---

## 1. 硬件验证

### 1.1 检查 NPU 设备

```bash
# 查看 NPU PCI 设备
lspci -nn | grep "1022:17f0"
# 输出：c6:00.1 Signal processing controller [1180]: Advanced Micro Devices, Inc. [AMD] Strix/Krackan/Strix Halo Neural Processing Unit [1022:17f0] (rev 11)

# 检查 amdxdna 驱动
lsmod | grep amdxdna
# amdxdna               147456  0
# gpu_sched              61440  1 amdxdna

# 检查加速设备
ls -la /sys/class/accel/
```

### 1.2 系统要求

| 要求 | 检查命令 | 期望值 |
|------|----------|--------|
| 内核版本 | `uname -r` | ≥ 6.8 |
| amdxdna 驱动 | `lsmod | grep amdxdna` | 已加载 |
| NPU 设备 | `lspci -nn \| grep 1022:17f0` | 已检测到 |

---

## 2. 模型准备

### 2.1 下载 Qwen3-0.6B ONNX 模型

**模型信息**:
- 来源：[onnx-community/Qwen3-0.6B-ONNX](https://huggingface.co/onnx-community/Qwen3-0.6B-ONNX)
- 大小：~315 MB
- 格式：ONNX (Float32)

**下载方法 A：使用脚本**

```bash
cd /mnt/volume3/llama_cpp

# 使用下载脚本
export HF_ENDPOINT=https://hf-mirror.com
./scripts/download_qwen3_onnx.sh ~/models/qwen3-onnx 0.6B
```

**下载方法 B：手动下载**

```bash
# 创建目录
mkdir -p ~/models/qwen3-onnx
cd ~/models/qwen3-onnx

# 克隆仓库
export HF_ENDPOINT=https://hf-mirror.com
git lfs install
git clone $HF_ENDPOINT/onnx-community/Qwen3-0.6B-ONNX qwen3-0.6b-onnx

# 如果 LFS 下载失败，用 wget 下载大文件
cd qwen3-0.6b-onnx
wget -c "https://hf-mirror.com/onnx-community/Qwen3-0.6B-ONNX/resolve/main/onnx/model.onnx" \
  -O onnx/model.onnx
```

**验证下载**:

```bash
ls -lh ~/models/qwen3-onnx/qwen3-0.6b-onnx/onnx/model.onnx
# 应该显示约 301MB
```

---

## 3. ryzenai-server 安装

### 3.1 下载 ryzenai-server

```bash
# 创建目录
mkdir -p ~/.cache/llama.cpp/ryzenai-server
cd ~/.cache/llama.cpp/ryzenai-server

# 下载 ryzenai-server v1.7.0
wget https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip

# 解压
unzip ryzenai-server.zip

# 验证
ls -la ryzenai-server
chmod +x ryzenai-server
./ryzenai-server --help
```

### 3.2 使用 llama-npu-server 下载

```bash
cd /mnt/volume3/llama_cpp

# 下载 ryzenai-server
./bin/llama-npu-server.sh download
```

---

## 4. 启动 NPU 服务

### 4.1 启动命令

```bash
cd /mnt/volume3/llama_cpp

# 设置模型路径
export LLAMA_NPU_MODEL=$HOME/models/qwen3-onnx/qwen3-0.6b-onnx/model.onnx

# 启动服务
./bin/llama-npu-server.sh start
```

### 4.2 手动启动

```bash
./src/ryzenai/llama-npu-server \
  --model $HOME/models/qwen3-onnx/qwen3-0.6b-onnx/model.onnx \
  --port 8404 \
  --host 127.0.0.1 \
  --ctx-size 4096
```

### 4.3 验证服务

```bash
# 检查健康状态
curl http://localhost:8404/health

# 应该返回：{"status":"ok"}
```

---

## 5. 性能测试

### 5.1 快速测试

```bash
# 单次推理测试
curl -X POST http://localhost:8404/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 100
  }' | jq '.usage'
```

### 5.2 吞吐量基准测试

```bash
cd /mnt/volume3/llama_cpp

# 运行测试脚本
./tests/benchmark_npu_qwen3vl.sh
```

### 5.3 手动测试（5 次平均）

```bash
#!/bin/bash
URL="http://localhost:8404"
PROMPT="Please explain what is machine learning in simple terms."

echo "Running 5 iterations..."
for i in {1..5}; do
  START=$(date +%s.%N)
  RESP=$(curl -s -X POST "$URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{\"messages\": [{\"role\": \"user\", \"content\": \"$PROMPT\"}], \"max_tokens\": 200}")

  END=$(date +%s.%N)
  TOKENS=$(echo "$RESP" | jq -r '.usage.completion_tokens // 0')
  DUR=$(echo "$END - $START" | bc)

  if [ "$TOKENS" != "0" ] && [ -n "$TOKENS" ]; then
    TPS=$(echo "scale=2; $TOKENS / $DUR" | bc)
    echo "Run $i: ${DUR}s | $TOKENS tok | ${TPS} tok/s"
  else
    echo "Run $i: FAILED"
  fi
done
```

---

## 6. 预期性能

| 模型 | 后端 | 预期 TPS |
|------|------|----------|
| Qwen3-0.6B | AMD NPU | 5-15 tok/s |
| Qwen3-0.6B | AMD GPU (gfx1151) | 30-50 tok/s |
| Qwen3-0.6B | NVIDIA V100 | 40-80 tok/s |

**注意**: NPU 性能取决于：
- NPU 功耗模式（高性能模式更好）
- 模型量化精度（Int8 vs Float32）
- 上下文长度

---

## 7. 故障排除

### 7.1 ryzenai-server 启动失败

```bash
# 检查 NPU 是否可用
lspci -nn | grep 1022:17f0

# 检查驱动
dmesg | grep -i amdxdna 2>/dev/null || journalctl -k | grep amdxdna

# 检查日志
tail -f /mnt/volume3/llama_cpp/logs/llama-npu-server.log
```

### 7.2 模型加载失败

```bash
# 验证 ONNX 文件
ls -lh ~/models/qwen3-onnx/qwen3-0.6b-onnx/model.onnx

# 检查路径
echo $LLAMA_NPU_MODEL
```

### 7.3 内存不足

```bash
# 检查内存
free -h

# 减小上下文长度
export LLAMA_NPU_CTX_SIZE=2048
```

---

## 8. 文件清单

| 文件 | 位置 | 用途 |
|------|------|------|
| `llama-npu-server` | `src/ryzenai/` | NPU 服务器二进制 |
| `llama-npu-server.sh` | `bin/` | 管理脚本 |
| `download_qwen3_onnx.sh` | `scripts/` | 模型下载脚本 |
| `benchmark_npu_qwen3vl.sh` | `tests/` | 性能测试脚本 |
| `model.onnx` | `~/models/qwen3-onnx/...` | ONNX 模型 |

---

## 9. 参考链接

- [RyzenAI-Server GitHub](https://github.com/lemonade-sdk/ryzenai-server)
- [Qwen3-0.6B-ONNX](https://huggingface.co/onnx-community/Qwen3-0.6B-ONNX)
- [AMD Ryzen AI 文档](https://ryzenai.docs.amd.com/)

---

*文档更新时间：2026-02-20*
*机器：AMD Ryzen AI 300 (Strix Halo, gfx1151)*
