# AMD XDNA NPU 实现指南

> **目标**: 在 Linux 上使用 AMD XDNA NPU (Strix Halo) 进行模型推理
> **状态**: 演示实现已完成
> **更新时间**: 2026-02-21

---

## 概述

本项目实现了 AMD XDNA NPU (Strix Halo gfx1151) 的推理支持，通过直接与 `amdxdna` 内核模块通信来检测和使用 NPU 硬件。

### 硬件要求

- **CPU**: AMD Ryzen 系列（支持 XDNA2）
- **NPU**: AMD XDNA2 (Strix Halo, gfx1151)
- **内核**: Linux 5.15+ (支持 amdxdna 驱动)
- **内存**: 建议 16GB+

### 软件依赖

```bash
# Python 虚拟环境
source ~/venvs/py312/bin/activate

# Python 包
pip install flask numpy
```

---

## XDNA NPU 检测

### 1. 检查内核模块

```bash
# 检查 amdxdna 模块是否加载
lsmod | grep amdxdna

# 输出示例:
# amdxdna               147456  0
```

### 2. 检查模块状态

```bash
# 检查 amdxdna 模块状态
cat /sys/module/amdxdna/initstate

# 预期输出: live
```

### 3. 查看 NPU 信息

```bash
# 通过 API 查询
curl http://localhost:8408/xdna/info

# 响应示例:
# {
#   "coresize": 147456,
#   "initstate": "live",
#   "module_loaded": true,
#   "sysfs_path": "/sys/module/amdxdna/drivers/pci:amdxdna"
# }
```

---

## 服务器架构

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│              XDNA NPU 推理服务器架构                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │ Flask API       │ ───▶ │ XDNA 检测        │            │
│  │ (端口 8408)      │      │ amdxdna 模块    │            │
│  └──────────────────┘      └──────────────────┘            │
│           │                                              │
│           ▼                                              │
│  ┌──────────────────┐                                    │
│  │ 模拟推理引擎    │   (等待 AMD 官方 SDK)             │
│  └──────────────────┘                                    │
│                                                             │
│  通信协议: HTTP (OpenAI 兼容)                           │
│  硬件访问: sysfs (amdxdna)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 文件结构

```
src/amdxdna_npu/
└── xdna_npu_infer.py    # XDNA NPU 推理服务器

bin/
└── llama-xdna-npu.sh      # 服务器管理脚本

logs/
└── xdna-npu-server.log   # 运行日志

docs/guides/
└── xdna-npu-implementation.md  # 本文档
```

---

## 使用方法

### 启动服务器

```bash
# 基本启动
./bin/llama-xdna-npu.sh start

# 指定模型
MODEL_PATH=/path/to/model.onnx ./bin/llama-xdna-npu.sh start

# 指定端口
PORT=8080 ./bin/llama-xdna-npu.sh start
```

### 停止服务器

```bash
./bin/llama-xdna-npu.sh stop
```

### 查看状态

```bash
./bin/llama-xdna-npu.sh status
```

### 查看日志

```bash
./bin/llama-xdna-npu.sh logs
```

---

## API 文档

### 1. 健康检查

```bash
GET /health
```

**响应**:
```json
{
  "status": "ok" | "error",
  "npu_available": true,
  "model_loaded": true,
  "xdna_state": "live" | "not loaded"
}
```

### 2. XDNA NPU 信息

```bash
GET /xdna/info
```

**响应**:
```json
{
  "coresize": 147456,
  "initsize": 0,
  "initstate": "live",
  "module_loaded": true,
  "sysfs_path": "/sys/module/amdxdna/drivers/pci:amdxdna"
}
```

### 3. 创建推理会话

```bash
POST /sessions
Content-Type: application/json

{
  "model_path": "/path/to/model.onnx"
}
```

**响应**:
```json
{
  "id": "default",
  "status": "created",
  "model_path": "/path/to/model.onnx",
  "npu_available": true,
  "note": "This is a demo implementation. Actual XDNA NPU inference requires AMD official Linux support."
}
```

### 4. 运行推理

```bash
POST /sessions/<session_id>/run
Content-Type: application/json

{
  "inputs": [
    {
      "name": "input_1",
      "value": [1.0, 2.0, 3.0]
    }
  ]
}
```

**响应**:
```json
{
  "session_id": "default",
  "outputs": [
    {
      "name": "output_1",
      "value": [2.0, 3.0, 4.0],
      "shape": [1, 3]
    }
  ],
  "inference_time_ms": 1.23,
  "device": "AMD XDNA NPU (simulated)"
}
```

### 5. OpenAI 兼容聊天 API

```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "xdna-npu",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ]
}
```

**响应**:
```json
{
  "id": "chatcmpl-123456",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "xdna-npu",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'm doing well!"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  },
  "system_info": {
    "device": "AMD XDNA NPU (Strix Halo)",
    "note": "This is a simulated implementation. Actual NPU inference requires AMD RyzenAI SDK for Linux.",
    "npu_state": "live"
  }
}
```

---

## 当前限制

### 1. 演示实现

当前实现是一个演示，用于展示：
- ✅ XDNA NPU 硬件检测
- ✅ 基本的 API 框架
- ✅ HTTP 接口设计

**非演示功能**:
- ❌ 实际 NPU 硬件推理
- ❌ 通过 ioctl 与 amdxdna 驱动通信
- ❌ 使用 XDNA 固件进行 AI 加速计算
- ❌ 完整的 tokenizer 和模型加载

### 2. AMD 官方 SDK 状态

| SDK | Windows | Linux | 状态 |
|-----|---------|-------|------|
| RyzenAI SDK | ✅ 完整支持 | ⚠️ 有限支持 | 主要用于 Windows |
| amdxdna 驱动 | ✅ 可用 | ✅ 可用 | Linux 内核支持 |
| XDNA 固件 | ✅ 可用 | ✅ 可用 | 需要专用工具 |

### 3. 为什么需要 AMD 官方 SDK

实际使用 XDNA NPU 进行推理需要:

1. **固件接口**: 访问 XDNA 固件的 AI 引擎
2. **内存管理**: 管理 NPU 的专用内存
3. **模型编译**: 将 ONNX 模型编译为 XDNA 可执行格式
4. **推理调度**: 高效地在 NPU 上调度计算任务

这些功能需要 AMD 提供的专用库和工具，目前 Windows 版本完整，Linux 版本有限。

---

## 未来改进方向

### 短期 (1-3 个月)

1. **等待 AMD 官方支持**
   - 关注 AMD RyzenAI SDK Linux 版本发布
   - 测试新的 SDK 功能

2. **完善演示实现**
   - 改进 tokenizer 集成
   - 添加更多模型支持
   - 优化 API 接口

### 中期 (3-6 个月)

1. **ioctl 接口研究**
   - 研究 amdxdna 驱动的 ioctl 接口
   - 实现基本的命令发送

2. **XDNA 固件交互**
   - 研究 XDNA 固件加载
   - 实现基本的计算任务

### 长期 (6-12 个月)

1. **完整的 NPU 推理实现**
   - 实现完整的 NPU 推理管道
   - 支持常用模型格式
   - 优化性能

2. **ONNX Runtime EP 集成**
   - 创建 ONNX Runtime XDNA EP
   - 与标准 ONNX 模型兼容

---

## 故障排除

### 问题: amdxdna 模块未加载

**症状**:
```bash
lsmod | grep amdxdna
# 无输出
```

**解决方案**:
```bash
# 检查内核版本
uname -r

# 检查模块是否存在
modinfo amdxdna

# 尝试加载模块
sudo modprobe amdxdna
```

### 问题: 服务器启动失败

**症状**:
```
服务器启动失败
查看日志: tail -f logs/xdna-npu-server.log
```

**解决方案**:
```bash
# 查看日志
tail -f logs/xdna-npu-server.log

# 检查端口占用
lsof -i :8408

# 检查虚拟环境
source ~/venvs/py312/bin/activate
python3 --version
```

---

## 相关资源

### AMD 官方资源

- [AMD RyzenAI](https://www.amd.com/en/technologies/ryzen-ai)
- [AMD GPUOpen](https://github.com/GPUOpen-Tools/rocAL)
- [amdxdna 驱动源码](https://github.com/amd/xdna-driver)

### 开源项目

- [ONNX Runtime](https://github.com/microsoft/onnxruntime)
- [llama.cpp](https://github.com/ggerganov/llama.cpp)

### 本项目文件

- 协作文档: `AGENTS-COLLABORATION.md`
- 推理服务器: `src/amdxdna_npu/xdna_npu_infer.py`
- 管理脚本: `bin/llama-xdna-npu.sh`
- 运行日志: `logs/xdna-npu-server.log`

---

## 总结

本项目成功实现了 AMD XDNA NPU 的检测和基本推理框架。虽然当前实现使用模拟推理，但提供了完整的 API 设计和硬件检测机制。

### 关键成果

- ✅ XDNA NPU 硬件检测 (amdxdna 模块)
- ✅ Flask HTTP API 服务器
- ✅ OpenAI 兼容的聊天 API
- ✅ 管理脚本和日志系统
- ✅ 完整的文档和示例

### 下一步行动

1. 等待 AMD 发布 RyzenAI SDK Linux 完整版
2. 研究 amdxdna ioctl 接口
3. 实现实际的 NPU 推理
4. 集成到 ONNX Runtime 作为自定义 EP

---

**文档版本**: 1.0
**最后更新**: 2026-02-21
**状态**: 演示实现可用，等待 AMD 官方 Linux SDK
