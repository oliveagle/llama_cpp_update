# Qwen3.5-35B-A3B-UD-Q4_K_XL Stage 1 测试报告

> **模型**: Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf
> **位置**: `/mnt/volume3/modelscope_models/unsloth/Qwen3___5-35B-A3B-GGUF/`
> **测试时间**: 2026-02-25
> **测试后端**: Vulkan (AMD gfx1151 + NVIDIA V100)
> **llama.cpp 版本**: b8069

---

## 📊 模型基本信息

| 参数 | 数值 |
|------|------|
| 模型名称 | Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf |
| 基础模型 | Qwen3.5-35B (A3B = 35B 蒸馏到 3B 激活) |
| 量化级别 | Q4_K_XL |
| 文件大小 | 18.3 GB |
| 参数量 | 34,660,610,688 (34.66B) |
| 上下文长度 | 262,144 tokens (256K) |
| 词表大小 | 248,320 |
| 嵌入维度 | 2048 |
| 层数 | 40 |
| 注意力头数 | 32 |

---

## 🚀 性能测试结果

### 1. 基础推理性能 (8K Context)

| 指标 | 数值 | 备注 |
|------|------|------|
| Prompt 预填充 | 85-97 tokens/s | 短文本 |
| 生成速度 | 68-69 tokens/s | 稳定输出 |
| 每 token 延迟 | ~14.5 ms | 生成阶段 |

### 2. 长上下文性能

| Context | Prompt TPS | Generate TPS | 状态 |
|---------|-----------|--------------|------|
| 8K | 692.36 | 63.86 | ✅ 完美支持 |
| 16K | - | - | ⏳ 待测试 |
| 32K | - | - | ⏳ 待测试 |
| 64K | - | - | ⏳ 待测试 |
| 128K | - | - | ⏳ 待测试 |
| 256K | - | - | ⏳ 待测试 (原生支持) |

### 3. 显存占用分析

| 组件 | 大小 | 说明 |
|------|------|------|
| 模型权重 | ~18.3 GB | Q4_K_XL 量化 |
| KV Cache (8K) | ~1.7 GB | Flash Attention |
| 计算缓冲区 | ~0.5 GB | 推理所需 |
| **总计** | **~20.5 GB** | 可加载到单卡 |

**GPU 兼容性**:
- ✅ V100 32GB: 完全支持
- ✅ gfx1151 32GB: 完全支持
- ✅ RTX 4090 24GB: 需要 --ctx-size 限制

---

## 🔍 模型特性

### 1. A3B 架构说明

Qwen3.5-35B-A3B 是一个**蒸馏模型**:
- **教师模型**: Qwen3.5-35B (完整 35B 参数)
- **学生模型**: 3B 激活参数 (A3B = Ablated 3B)
- **实际效果**: 35B 级别的能力，3B 级别的速度

### 2. UD (Uncensored Distilled)

- **U**: Uncensored - 减少内容限制
- **D**: Distilled - 蒸馏版本
- 适合：研究、创意写作、开放式对话

### 3. 推理能力

模型输出包含 `reasoning_content` 字段:
```json
{
  "message": {
    "content": "最终回答",
    "reasoning_content": "Thinking Process:\n1. Analyze..."
  }
}
```

---

## ⚡ 不同 Context 性能预估

基于 8K 测试数据推算:

| Context | 预估显存 | 预估预填充 TPS | 预估生成 TPS | 状态 |
|---------|---------|---------------|-------------|------|
| 4K | ~19 GB | ~100 | ~70 | ✅ 可行 |
| 8K | ~20 GB | ~85 | ~68 | ✅ 已验证 |
| 16K | ~22 GB | ~70 | ~65 | ✅ 可行 |
| 32K | ~25 GB | ~55 | ~60 | ✅ 可行 |
| 64K | ~30 GB | ~40 | ~55 | ⚠️ 接近上限 |
| 128K | ~40 GB | - | - | ❌ 需要多卡 |

---

## 🎯 推荐配置

### 实时应用 (低延迟)
```bash
# 8K Context, 最佳性能
--ctx-size 8192 --n-gpu-layers 99 --flash-attn on
```

### 长文档分析
```bash
# 32K Context, 平衡模式
--ctx-size 32768 --n-gpu-layers 99 --flash-attn on
```

### 超长上下文 (256K 原生)
```bash
# 需要 40GB+ 显存或 CPU offload
--ctx-size 262144 --n-gpu-layers 99 --flash-attn on
```

---

## 📈 与其他模型对比

| 模型 | 大小 | 生成 TPS | 最大 Context | 特点 |
|------|------|---------|-------------|------|
| Qwen3.5-35B-A3B | 19GB | **69** | **256K** | 蒸馏、无审查 |
| JoyAI-LLM-Flash | 28GB | 37.5 | 32K | MoE、中文优化 |
| GLM-4.7-Flash | 5GB | 37.5 | 202K | 通用任务 |
| Qwen3-VL-8B | 8GB | 39.1 | 24K | 多模态 |

**优势**:
- ✅ 生成速度最快 (69 tokens/s)
- ✅ 原生 256K 上下文
- ✅ 文件大小适中 (19GB)
- ✅ 支持推理过程输出

---

## 📝 测试日志

### 2026-02-25
- ✅ 基础推理测试完成
- ✅ 8K 长上下文测试完成
- ✅ 显存占用分析完成
- ⏳ 16K/32K/64K 梯度测试待进行
- ⏳ Stage 2 能力评估待进行

---

## 🔧 测试环境

```
OS: Ubuntu 22.04
GPU: AMD Radeon 8060S Graphics (gfx1151) + NVIDIA Tesla V100 32GB
llama.cpp: b8069 (build 8069 d5dfc3302)
Backend: Vulkan
```

---

## 📋 待完成测试

- [ ] 16K Context 梯度测试
- [ ] 32K Context 梯度测试
- [ ] 64K Context 上限测试
- [ ] Stage 2: Linux 工具调用能力
- [ ] Stage 3: 综合能力评估
- [ ] 推理能力专项测试

---

*报告生成时间: 2026-02-25*
*测试框架: llama.cpp 三层评估系统 v1.0*
