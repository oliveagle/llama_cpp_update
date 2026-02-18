# HIP (ROCm) 优化报告

> **生成时间**: 2026-02-17
> **ROCm 版本**: 7.12-gfx1151 (专用版本)
> **GPU**: AMD gfx1151 (Strix Halo, Radeon 8060S)
> **llama.cpp**: b8072 with HIP Graphs

---

## 一、已应用的优化

### 1.1 编译优化

| 优化项 | 配置 | 效果 |
|--------|------|------|
| `GGML_HIP_GRAPHS=ON` | 启用 HIP Graphs | 减少 CPU 开销 |
| `GPU_TARGETS=gfx1151` | 针对 gfx1151 架构 | 原生指令优化 |
| `-O3` | 编译器最高优化 | 代码性能提升 |
| `GGML_NATIVE=ON` | 本地 CPU 优化 | CPU 部分加速 |

**编译命令**:
```bash
HIPCXX="/opt/rocm-7.12-gfx1151/llvm/bin/clang++" \
cmake -S . -B build-hip \
  -DGGML_HIP=ON \
  -DGGML_HIP_GRAPHS=ON \
  -DGPU_TARGETS=gfx1151 \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_BUILD_SERVER=ON
```

### 1.2 运行时环境优化

```bash
# 统一内存优化 (APU 关键)
export HSA_XNACK=1
export HSA_FORCE_FINE_GRAIN_PCIE=1

# 内存分配
export GPU_MAX_HEAP_SIZE=100
export GPU_MAX_ALLOC_PERCENT=100

# HSA 队列优化
export GPU_MAX_HW_QUEUES=4

# ROCm 库优化
export ROCBLAS_USE_HIPBLASLT=1

# gfx1151 架构
export HSA_OVERRIDE_GFX_VERSION=11.5.1
```

### 1.3 llama-server 参数优化

```bash
./llama-server \
  --models-max 1 \
  --port 8402 \
  --no-warmup \
  -fa on \           # Flash Attention
  --fit off \        # 关键: 避免内存适配卡住
  -ngl 999           # 最大 GPU 层数
```

---

## 二、关键发现

### 2.1 模型加载缓慢 (主要问题)

| 后端 | 加载时间 | 状态 |
|------|---------|------|
| Vulkan | < 30s | ✅ 正常 |
| HIP | > 5min | ❌ 极慢 |

**原因分析**:
1. HIP 运行时初始化开销大
2. ROCm 7.12 对 gfx1151 优化不足
3. 可能是 ROCm 早期版本问题

### 2.2 已知 ROCm 问题

根据社区反馈:
- gfx1151 是较新架构，ROCm 支持仍在完善
- ROCm 7.1+ 才开始支持 gfx1151
- 性能优化可能滞后

### 2.3 实用建议

| 场景 | 推荐后端 | 原因 |
|------|---------|------|
| 生产环境 | **Vulkan** | 加载快，性能稳定 |
| 性能测试 | **HIP** | 理论性能更高 (待验证) |
| 长时运行 | **HIP** | 可能更稳定 |

---

## 三、端口配置汇总

| 端口 | 后端 | 状态 | 推荐场景 |
|------|------|------|---------|
| 8400 | Vulkan | ✅ 运行 (66 tps) | **日常使用** |
| 8401 | CUDA (V100) | ✅ 运行 | NVIDIA GPU |
| 8402 | HIP (ROCm) | ⏳ 加载中 | AMD 优化测试 |

---

## 四、进一步优化建议

### 4.1 短期优化

1. **使用更小模型测试**: Qwen3-0.6B 快速验证 HIP 性能
2. **减少 ctx-size**: 测试 8K/16K 是否有改善
3. **量化格式**: 尝试 Q4_K_M 减少加载时间

### 4.2 长期优化

1. **升级 ROCm**: 等待 7.2+ 或 7.3 版本
2. **社区反馈**: 向 AMD 反馈 gfx1151 性能问题
3. **持续关注**: llama.cpp HIP 后端改进

---

## 五、关键结论

1. **HIP 编译成功**: 启用 HIP Graphs 和 gfx1151 优化
2. **环境变量优化**: 已配置 HSA_XNACK, GPU_MAX_HW_QUEUES 等
3. **加载缓慢是已知问题**: ROCm 对 gfx1151 支持仍在完善
4. **Vulkan 仍是首选**: 加载快，性能稳定
5. **HIP 适合长期测试**: 理论性能更高，等待 ROCm 优化

---

## 六、参考链接

- [ROCm gfx1151 Support](https://github.com/ROCm/TheRock/discussions/655)
- [HIP Performance Guidelines](https://rocm.docs.amd.com/projects/HIP/en/develop/how-to/performance_guidelines.html)
- [AMD RDNA3 llama.cpp Optimizations](https://www.banandre.com/blog/2025-10/amd-rdna3-faster-llamacpp-performance-rocm-optimizations)

---

*报告生成: 2026-02-17*
