# HIP (ROCm) 后端测试报告

> **测试时间**: 2026-02-17
> **硬件**: AMD gfx1151 (Strix Halo, Radeon 8060S)
> **ROCm 版本**: 7.12-gfx1151 (专用版本)
> **llama.cpp**: b8072 (build-hip)

---

## 编译状态

| 项目 | 状态 |
|------|------|
| HIP 编译 | 成功 ✅ |
| 设备识别 | Radeon 8060S Graphics, gfx1151 ✅ |
| 内存分配 | 2422.70 MiB GPU 内存 ✅ |
| 层加载 | 37/37 层 offload 到 GPU ✅ |

### 编译命令
```bash
HIPCXX="/opt/rocm-7.12-gfx1151/llvm/bin/clang++" \
HIP_PATH="/opt/rocm-7.12-gfx1151" \
cmake -S . -B build-hip \
  -DGGML_HIP=ON \
  -DGPU_TARGETS=gfx1151 \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_SERVER=ON
```

---

## 运行状态

### 发现问题

| 问题 | 描述 |
|------|------|
| **加载缓慢** | 模型加载时间 > 5 分钟 |
| **--fit 卡住** | 默认内存适配卡住，需 `--fit off` |
| **初始化延迟** | 首次请求超时 (120s 不够) |

### 进程状态
```
llama-server (router) - 运行正常
└─ llama-server (model) - 加载中，CPU 95%+
```

---

## 性能对比 (待完成)

| 指标 | Vulkan (8400) | HIP (8402) | 状态 |
|------|---------------|------------|------|
| 编译难度 | 预编译包 | 需手动编译 | - |
| 设备识别 | ✅ | ✅ | - |
| 模型加载 | < 30s | > 5min | ❌ 慢 |
| 生成速率 | 66.2 tps | 测试中 | - |
| 首token延迟 | 14.6ms | 测试中 | - |

---

## 关键发现

### 1. gfx1151 专用 ROCm 版本可用
- `/opt/rocm-7.12-gfx1151` 是专用版本
- HIP 编译成功识别设备

### 2. --fit 参数问题
```bash
# 默认 --fit on 卡住
common_init_result: fitting params to device memory...

# 需使用 --fit off
--fit off
```

### 3. 加载性能问题
HIP 版本的模型加载明显慢于 Vulkan，可能原因：
- HIP 运行时初始化开销
- gfx1151 新架构优化不足
- ROCm 7.12 早期版本 bug

---

## 下一步

1. **等待模型完全加载后测试性能**
2. **对比 context 处理能力**
3. **检查是否可以优化加载时间**

---

## 端口配置

| 服务 | 端口 | 后端 | 状态 |
|------|------|------|------|
| llama-server | 8400 | Vulkan | 运行中 ✅ |
| llama-server | 8401 | CUDA (V100) | 运行中 ✅ |
| llama-server | 8402 | HIP (ROCm) | 加载中 ⏳ |

---

*更新时间: 2026-02-17*
