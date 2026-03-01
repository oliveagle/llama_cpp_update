# AMD NPU Qwen3 性能测试完成总结

> **机器**: AMD Ryzen AI 300 系列 (Strix Halo, gfx1151)
> **NPU 设备**: 1022:17f0 (AMD XDNA2)
> **测试模型**: Qwen3-0.6B-ONNX

---

## ✅ 已完成的工作

### 1. 硬件验证

```bash
# NPU 设备已确认
lspci -nn | grep 1022:17f0
# 输出：c6:00.1 Signal processing controller [1180]: Advanced Micro Devices, Inc. [AMD] Strix/Krackan/Strix Halo Neural Processing Unit [1022:17f0] (rev 11)

# 驱动已加载
lsmod | grep amdxdna
# amdxdna               147456  0
# gpu_sched              61440  1 amdxdna

# /sys/class/accel 可用
ls -la /sys/class/accel/
```

### 2. 模型下载完成

**Qwen3-0.6B-ONNX 已下载**:
```
位置：/mnt/volume3/llama_cpp/models/qwen3-onnx/qwen3-0.6b-onnx/
模型：onnx/model.onnx (301MB)
配置：tokenizer.json, config.json, generation_config.json 等
```

### 3. 已创建的文件

| 文件 | 位置 | 说明 |
|------|------|------|
| `llama-npu-server` | `src/ryzenai/` | NPU 服务器二进制 (120KB) |
| `llama-npu-server.sh` | `bin/` | NPU 服务管理脚本 |
| `download_qwen3_onnx.sh` | `scripts/` | Qwen3 ONNX 下载脚本 |
| `benchmark_npu_qwen3vl.sh` | `tests/` | NPU 性能测试脚本 |
| `convert_qwen3vl_to_onnx.py` | `scripts/` | ONNX 转换脚本 |
| `npu-qwen3-benchmark.md` | `docs/guides/` | 完整测试指南 |

### 4. RyzenAI 后端代码

```
src/ryzenai/
├── ryzenai_backend.h/cpp    # 后端核心逻辑
├── process_manager.h/cpp    # 进程管理
├── http_client.h/cpp        # HTTP 客户端
├── downloader.h/cpp         # 下载器
├── main.cpp                 # 服务器入口
├── Makefile                 # 编译配置
├── libryzenai-backend.a     # 静态库 (162KB)
└── llama-npu-server         # 可执行文件 (120KB)
```

---

## ⏳ 待完成的步骤

### 1. 下载 ryzenai-server

由于网络原因，ryzenai-server 下载中断。需要完成：

```bash
cd ~/.cache/llama.cpp/ryzenai-server

# 方法 1：使用 axel 多线程
axel -n 16 "https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip"

# 方法 2：使用代理
export http_proxy=http://your-proxy:port
curl -L --proxy "$http_proxy" "https://github.com/lemonade-sdk/ryzenai-server/releases/download/v1.7.0/ryzenai-server.zip" -o ryzenai-server.zip

# 解压
unzip ryzenai-server.zip
chmod +x ryzenai-server
```

### 2. 启动 NPU 服务并测试

```bash
cd /mnt/volume3/llama_cpp

# 启动服务
export LLAMA_NPU_MODEL=/mnt/volume3/llama_cpp/models/qwen3-onnx/qwen3-0.6b-onnx/onnx/model.onnx
./bin/llama-npu-server.sh start

# 验证
curl http://localhost:8404/health

# 性能测试
./tests/benchmark_npu_qwen3vl.sh
```

---

## 📊 预期性能

| 模型 | 后端 | 预期 TPS | 备注 |
|------|------|----------|------|
| Qwen3-0.6B | AMD NPU | 5-15 tok/s | 首次测试 |
| Qwen3-0.6B | AMD GPU (gfx1151) | 30-50 tok/s | Vulkan 后端 |
| Qwen3-0.6B | CPU | 2-8 tok/s | 备用方案 |

---

## 📝 快速测试命令

```bash
# 1. 验证 NPU
lspci -nn | grep 1022:17f0

# 2. 检查模型
ls -lh /mnt/volume3/llama_cpp/models/qwen3-onnx/qwen3-0.6b-onnx/onnx/model.onnx

# 3. 下载 ryzenai-server (需要完成)
cd ~/.cache/llama.cpp/ryzenai-server && axel -n 16 [URL]

# 4. 启动服务
export LLAMA_NPU_MODEL=/mnt/volume3/llama_cpp/models/qwen3-onnx/qwen3-0.6b-onnx/onnx/model.onnx
./bin/llama-npu-server.sh start

# 5. 测试
curl http://localhost:8404/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}'
```

---

## 🔗 参考文档

- [完整测试指南](npu-qwen3-benchmark.md)
- [RyzenAI 后端指南](ryzenai-backend-guide.md)
- [GGUF 转 ONNX 指南](gguf-to-onnx.md)

---

*更新时间：2026-02-20*
*状态：模型已下载，等待 ryzenai-server 下载完成后即可测试*
