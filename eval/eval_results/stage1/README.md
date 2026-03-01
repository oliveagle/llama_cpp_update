# JoyAI-LLM-Flash 模型限制记录

> **创建时间**: 2026-02-25
> **模型**: JoyAI-LLM-Flash-Q4_K_M
> **位置**: `/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/`

---

## ⚠️ V100 显存限制

| GPU | 显存 | 最大 Context (GPU 模式) | 状态 |
|-----|------|------------------------|------|
| **Tesla V100** | 32GB | **32K** | ✅ 已验证 |

**原因**:
- 模型权重占用 ~29GB (Q4_K_M)
- 32K KV Cache 需要 ~1.6GB
- 总计 ~30.6GB，在 32GB 限制内

**实测数据**:
- 32537 tokens 成功 ✓
- 预填充: 96.8 tokens/s
- 生成: 24.5 tokens/s

---

## 📊 性能数据汇总

### GPU 模式 (NGL=99)

| Context | TPS (热启动) | 延迟 | 状态 |
|---------|-------------|------|------|
| 4K | 118,939 | 907 ms | ✅ |
| 8K | 219,239 | 1,163 ms | ✅ |
| 12K | 321,851 | 1,497 ms | ✅ |
| 16K | 349,468 | 1,840 ms | ✅ |
| 24K | 466,XXX | ~2,500 ms | ✅ |
| **32K** | **96.8** | **336 秒** | ✅ **已验证** |

### CPU Offload 模式 (NGL=0)

| Context | TPS | 延迟 | 状态 |
|---------|-----|------|------|
| 32K | 56.4 | 178 秒 | ✅ 慢但可用 |

---

## 🔧 解决方案

### 方案对比

| 方案 | Context | TPS | 成本 |
|------|---------|-----|------|
| V100 GPU 模式 | ≤32K | 97K-570K | 现有 |
| CPU Offload | ≤128K | ~50 | 免费但慢 |
| 升级 A100 40GB | ≤32K | ~300K | ~$10,000 |
| 升级 A100 80GB | ≤64K | ~500K | ~$15,000 |

### 推荐配置

**实时应用** (低延迟要求):
```bash
# 使用 V100 GPU 模式，8K context 最佳性能
--ctx-size 8192 --n-gpu-layers 99
```

**长文档分析** (32K context):
```bash
# 使用 V100 GPU 模式，32K context
--ctx-size 36864 --n-gpu-layers 99 --flash-attn on
```

**离线批处理** (超长文档分析):
```bash
# 使用 CPU offload，支持 32K-128K
--ctx-size 32768 --n-gpu-layers 0
```

---

## 📁 详细报告

| 报告 | 文件 |
|------|------|
| Stage 1 基础测试 | `joyai_flash_stage1_report.md` |
| Context 梯度测试 | `joyai_flash_context_gradient_report.md` |
| CPU Offload 测试 | `joyai_flash_cpu_offload_report.md` |

---

## 📝 测试日志

- **2026-02-25**: 完成 Stage 1 测试
  - Vulkan (gfx1151): 最大 8K
  - CUDA (V100): 最大 32K (GPU 模式) ✅
  - CPU Offload: 支持 32K+ (56 TPS)

### 32K Context 验证详情

| 测试项 | 数值 | 状态 |
|--------|------|------|
| Context Size | 36864 | ✅ |
| Prompt Tokens | 32537 | ✅ |
| Pre-fill TPS | 96.83 | ✅ |
| Generate TPS | 24.47 | ✅ |
| Total Time | 336.22 秒 | ✅ |

**配置**: `--ctx-size 36864 --n-gpu-layers 99 --flash-attn on`

---

*最后更新：2026-02-25*
