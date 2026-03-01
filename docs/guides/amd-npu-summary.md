# AMD NPU Linux 支持研究总结

> **研究完成时间**: 2026-02-20
> **机器**: AMD Ryzen AI MAX+ 395 (Strix Halo)
> **内核**: 6.14.0-1020-oem
> **驱动**: amdxdna (已加载)

---

## 关键发现

### 1. 硬件状态 ✅

您的机器配备 **AMD Ryzen AI MAX+ 395** NPU:
- **设备 ID**: [1022:17F0] XDNA2 架构
- **驱动**: `amdxdna.ko` 已加载
- **固件**: `/lib/firmware/amdnpu/17f0_11/npu.sbin`
- **DRM 接口**: 完整的内核头文件可用

### 2. Lemonade SDK 分析 ✅

Lemonade 通过两种方式支持 AMD NPU:

| 后端 | 模型格式 | Linux 支持 | 来源 |
|------|----------|------------|------|
| **FastFlowLM** | .q4nx (专有) | ✅ 是 (内核≥7.0) | GitHub |
| **RyzenAI-Server** | .onnx (开放) | ✅ 是 | Lemonade 下载 |

**关键代码位置**:
- `/tmp/lemonade/src/cpp/server/backends/fastflowlm_server.cpp`
- `/tmp/lemonade/src/cpp/server/backends/ryzenaiserver.cpp`
- `/tmp/lemonade/src/cpp/server/system_info.cpp`

### 3. FastFlowLM Linux 实现细节

**驱动检测**:
```cpp
// 通过 /sys/class/accel 检测 amdxdna 驱动
fs::path driver_link = entry.path() / "device" / "driver";
std::string driver_name = fs::read_symlink(driver_link).filename();
// driver_name == "amdxdna" → NPU 可用
```

**内核版本检查**:
```cpp
// 最低要求：内核 7.0
// 当前机器：6.14.0 → 需要升级内核或使用 XDNA 方案
struct utsname uts;
uname(&uts);  // 返回 "6.14.0-1020-oem"
```

**启动命令**:
```bash
flm serve <model> --ctx-len 8192 --port 8001 --host 127.0.0.1
```

### 4. 您的机器状态

**当前内核**: `6.14.0-1020-oem`

**FastFlowLM 要求**: 内核 ≥ 7.0 ❌ **不满足**

**RyzenAI-Server 要求**: 内核 ≥ 6.8 ✅ **满足**

---

## 推荐方案

### 方案 A: 集成 RyzenAI-Server (推荐)

**优势**:
- ✅ 内核要求低 (≥6.8)
- ✅ 您的机器满足要求
- ✅ ONNX 模型格式开放
- ✅ Lemonade 已验证

**实施步骤**:
1. 从 Lemonade 提取 ryzenai-server 二进制
2. 在 llama.cpp 中添加 `--ryzenai` 选项
3. 通过独立进程启动 ryzenai-server
4. HTTP 转发推理请求

**估算时间**: 1-2 周

### 方案 B: 等待/升级内核使用 FastFlowLM

**要求**: 升级到 Linux 内核 7.0+

**选项**:
1. 升级内核 (可能影响系统稳定性)
2. 等待上游内核合并到 Ubuntu 24.04

**估算时间**: 不确定 (取决于内核发布周期)

### 方案 C: 原生 ggml-npu 开发

**优势**:
- 完全控制
- GGUF 格式支持
- 最佳性能

**挑战**:
- 需要 AMD XRT 运行时
- 开发周期长 (2-3 个月)
- 需要专业知识

---

## 立即可执行的测试

### 1. 检查 NPU 状态

```bash
# 检查驱动加载
lsmod | grep amdxdna

# 检查 NPU 设备
ls -la /sys/class/accel/

# 查看 NPU 信息
cat /sys/class/accel/*/device/vbnv 2>/dev/null
```

### 2. 测试 RyzenAI-Server

```bash
# 从 Lemonade 复制 ryzenai-server
cp /tmp/lemonade/src/cpp/build/Release/ryzenai-server /usr/local/bin/

# 下载 ONNX 模型
# (从 HuggingFace: amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu)

# 启动服务
ryzenai-server --model model.onnx --port 8001

# 测试推理
curl http://localhost:8001/v1/chat/completions \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

### 3. 检查 FLM 兼容性

```bash
# 检查是否安装 FLM
which flm

# 如果已安装，检查版本
flm version

# 检查内核版本
uname -r  # 当前：6.14.0-1020-oem
# 需要：≥7.0
```

---

## 文档输出

已创建以下技术文档:

1. **实现计划** (`docs/guides/amd-npu-implementation-plan.md`)
   - 完整的架构设计
   - 三阶段实施计划
   - DRM API 封装细节

2. **集成指南** (`docs/guides/amd-npu-integration-guide.md`)
   - FastFlowLM 集成代码
   - RyzenAI-Server 集成代码
   - 构建和测试说明

---

## 下一步行动

### 推荐 (本周)

1. **测试 RyzenAI-Server**
   ```bash
   # 从 Lemonade 提取二进制
   /tmp/lemonade/src/cpp/build/Release/ryzenai-server --help

   # 下载测试模型
   # https://huggingface.co/amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu
   ```

2. **评估集成工作量**
   - 审查 Lemonade 的 ryzenaiserver.cpp
   - 确定需要的修改
   - 创建 GitHub issue 追踪进度

### 备选 (如有 FLM 安装)

1. **升级内核到 7.0+**
   - 评估风险
   - 测试 FLM 功能

2. **集成 FLM 到 llama.cpp**
   - 按照集成指南实施

---

## 联系 AMD

如需进一步技术支持，建议联系:

1. **AMD Ryzen AI 软件团队**
   - https://github.com/amd/ryzenai-sw
   - 询问 XRT 运行时获取方式

2. **FastFlowLM 团队**
   - https://github.com/FastFlowLM/FastFlowLM
   - 询问 Linux SDK 和内核要求

3. **Lemonade SDK 团队**
   - https://github.com/lemonade-sdk/lemonade
   - 学习他们的集成经验

---

*研究报告完成时间：2026-02-20*
*研究者：Claude Code Agent*
