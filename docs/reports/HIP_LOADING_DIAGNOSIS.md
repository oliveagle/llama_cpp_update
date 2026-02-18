# HIP (ROCm) 加载问题深度诊断报告

> **生成时间**: 2026-02-17
> **ROCm 版本**: 7.12-gfx1151
> **GPU**: AMD gfx1151 (Strix Halo, Radeon 8060S)
> **问题**: 模型加载极慢/卡住

---

## 一、问题现象

### 1.1 正常流程 (Vulkan)
```
load_tensors: offloading X layers to GPU
load_tensors: offloaded Y/Y layers to GPU
[完成] -> 服务就绪，可接受请求
```
**耗时**: < 30 秒

### 1.2 异常流程 (HIP)
```
load_tensors: offloading X layers to GPU
load_tensors: offloaded Y/Y layers to GPU  <-- 卡在这里
load_tensors: CPU_Mapped model buffer = XXX MiB
load_tensors: ROCm0 model buffer = XXX MiB  <-- 无限等待
```
**耗时**: > 5 分钟仍无法完成

---

## 二、诊断测试

### 2.1 mmap 测试

| 测试项 | 结果 | 结论 |
|--------|------|------|
| mmap = ON | ❌ 卡住 | 不是 mmap 问题 |
| mmap = OFF | 未测试 | 预计相同 |

**结论**: mmap 不是根本原因

### 2.2 模型大小测试

| 模型 | 大小 | GPU 内存 | 结果 |
|------|------|----------|------|
| Qwen3-4B | 4B | 2.4 GB | ❌ 卡住 |
| Qwen3-0.6B | 0.6B | 358 MB | ❌ 卡住 |

**关键发现**: 即使是 0.6B 小模型 (358MB) 也会卡住！

### 2.3 GPU 状态检查

```
rocm-smi:
  VRAM: 60% 占用 (模型已加载)
  GPU%: 0% (GPU 空闲，无计算)
```

**结论**: 模型数据已在 GPU 内存，但初始化未完成

---

## 三、根本原因分析

### 3.1 可能原因 1: HIP Runtime 初始化问题

**证据**:
- 模型数据已成功 offload 到 GPU
- GPU 内存已占用
- 但后续初始化卡住

**分析**:
HIP runtime 可能在进行某些初始化时卡住：
- kernel 编译/缓存
- memory pool 初始化
- stream/queue 创建

### 3.2 可能原因 2: ROCm 7.12 gfx1151 兼容性

**证据**:
- gfx1151 是较新架构
- ROCm 7.12 早期支持
- 社区反馈类似问题

**参考**:
- https://github.com/ROCm/TheRock/discussions/655
- https://github.com/ROCm/TheRock/issues/3128

### 3.3 可能原因 3: APU 统一内存模式

**证据**:
- Strix Halo 是 APU (共享内存架构)
- 已设置 `HSA_XNACK=1`
- 但仍可能有问题

**分析**:
APU 的内存模型与传统 dGPU 不同，可能需要特殊处理

---

## 四、排除的因素

| 因素 | 状态 | 说明 |
|------|------|------|
| mmap | ❌ 排除 | 小模型测试相同问题 |
| 模型大小 | ❌ 排除 | 0.6B 小模型也卡住 |
| GPU 内存不足 | ❌ 排除 | 358MB << 32GB 可用 |
| 编译问题 | ❌ 排除 | 编译成功，设备识别正常 |
| Flash Attention | ❌ 排除 | 关闭 -fa 仍相同 |
| --fit 参数 | ❌ 排除 | 已使用 --fit off |

---

## 五、解决方案尝试

### 5.1 已尝试 (无效)

| 方案 | 结果 |
|------|------|
| --fit off | ❌ 无改善 |
| HIP Graphs 启用 | ❌ 无改善 |
| HSA_XNACK=1 | ❌ 无改善 |
| 小模型测试 | ❌ 相同问题 |

### 5.2 建议尝试

#### 方案 A: 降级 ROCm 版本
```bash
# 尝试 ROCm 7.2.0 (如果可用)
export ROCM_PATH=/opt/rocm-7.2.0
```

#### 方案 B: 使用 gfx1100 兼容模式
```bash
# 强制使用 gfx1100 (RDNA3) 内核
export HSA_OVERRIDE_GFX_VERSION=11.0.0
```

#### 方案 C: 禁用 Flash Attention
```bash
# 不使用 -fa 参数
./llama-server ... (无 -fa)
```

#### 方案 D: 等待 ROCm 更新
- ROCm 7.3 或更高版本
- llama.cpp HIP 后端改进

---

## 六、当前建议

### 6.1 生产环境

**使用 Vulkan 后端 (8400)**
- 加载快 (< 30s)
- 性能稳定 (66 tps)
- 推荐配置: ctx-size = 8192

### 6.2 开发/测试

**可继续跟踪 HIP 问题**
- 监控 ROCm 更新
- 测试新版本 llama.cpp
- 向 AMD 反馈问题

---

## 七、关键结论

1. **不是 mmap 问题**: 小模型测试相同结果
2. **不是模型大小问题**: 0.6B 模型也卡住
3. **不是内存问题**: GPU 内存充足
4. **可能是 ROCm/gfx1151 兼容性问题**: 需要 AMD 修复
5. **Vulkan 是可靠选择**: 当前生产环境推荐

---

## 八、参考链接

- [ROCm gfx1151 Support Discussion](https://github.com/ROCm/TheRock/discussions/655)
- [ROCm gfx1151 Issue](https://github.com/ROCm/TheRock/issues/3128)
- [AMD Strix Halo ROCm](https://www.phoronix.com/news/AMD-Strix-Halo-ROCm)
- [llama.cpp HIP Backend](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md#hip)

---

*诊断时间: 2026-02-17*
*状态: HIP 加载问题未解决，需要 ROCm/AMD 修复*
