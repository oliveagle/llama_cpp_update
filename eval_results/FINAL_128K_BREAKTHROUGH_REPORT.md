# V100 CUDA 128K Context 突破 - 最终报告

> **测试时间**: 2026-02-17
> **GPU**: NVIDIA V100 32GB
> **RoPE 缩放**: YaRN
> **Agent**: V100-CUDA

---

## 🎯 突破成果总览

成功将 **4 个模型** 从原生 32K 扩展到 **128K context**！

### 成功突破模型

| 排名 | 模型 | 参数量 | 原生 Context | RoPE Scale | 128K 耗时 | 显存 |
|------|------|--------|-------------|-----------|----------|------|
| 🥇 1 | **Qwen3-VL-8B** | 8B | 32K | 4.0x | 86.4s | ~28GB |
| 🥈 2 | **Qwen3-4B** | 4B | 32K | 4.0x | 83.3s | ~20GB |
| 🥉 3 | **Qwen3VL-4B** | 4B | 32K | 4.0x | 83.6s | ~22GB |
| 4 | **Qwen3-0.6B** | 0.6B | 32K | 3.2x | 43.0s | ~15GB |

---

## 📊 详细性能数据

### Qwen3-VL-8B (8B 参数)

| Context | Tokens | 耗时 | 速度 |
|---------|--------|------|------|
| 16K | 16,384 | 7.5s | ~2,200 t/s |
| 32K | 32,767 | 12.1s | ~2,700 t/s |
| 64K | 65,536 | 22.5s | ~2,900 t/s |
| 96K | 98,305 | 62.4s | ~1,600 t/s |
| **128K** | **131,071** | **86.4s** | **~1,500 t/s** |

### Qwen3-4B (4B 参数)

| Context | Tokens | 耗时 | 速度 |
|---------|--------|------|------|
| 32K | 32,767 | 17.6s | ~1,900 t/s |
| 64K | 65,536 | 38.1s | ~1,700 t/s |
| 96K | 98,305 | 60.1s | ~1,600 t/s |
| **128K** | **131,071** | **83.3s** | **~1,600 t/s** |

### Qwen3VL-4B (4B 参数)

| Context | Tokens | 耗时 |
|---------|--------|------|
| 32K | 32,767 | 16.4s |
| 64K | 65,536 | 36.7s |
| 96K | 98,305 | 58.9s |
| **128K** | **131,071** | **83.6s** |

### Qwen3-0.6B (0.6B 参数)

| Context | Tokens | 耗时 |
|---------|--------|------|
| 32K | 32,767 | ~8s |
| 64K | 65,536 | ~15s |
| 96K | 98,305 | ~25s |
| **128K** | **131,071** | **~43s** |

---

## 🔧 RoPE YaRN 缩放配置

### 通用启动参数

```bash
llama-server \
    -m MODEL.gguf \
    --host 0.0.0.0 \
    --port 8401 \
    -c 131072 \
    -n 4096 \
    -ngl 99 \
    --chat-template qwen2 \
    --rope-scaling yarn \
    --rope-scale 4.0 \
    --yarn-orig-ctx 32768 \
    -np 1
```

### 参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `--rope-scaling` | yarn | YaRN 缩放方法 |
| `--rope-scale` | 3.2~4.0 | 扩展倍数 |
| `--yarn-orig-ctx` | 32768 | 原始 context |
| `-c` | 131072 | 目标 128K |

---

## 🚀 启动脚本列表

已创建专用启动脚本：

```bash
# Qwen3-0.6B (最轻量，128K 最快)
./llama-server-cuda-rope-direct.sh start

# Qwen3-4B
./llama-server-qwen3-4b-rope.sh start

# Qwen3VL-4B
./llama-server-qwen3vl-4b-rope.sh start

# Qwen3-VL-8B (最大，8B 参数)
./llama-server-qwen3-vl-8b-rope.sh start
```

---

## 💡 关键发现

### 1. 性能趋势
- **小模型更快**: Qwen3-0.6B 128K 仅需 43s，而 8B 需要 86s
- **速度稳定**: 所有模型在 128K 时保持 1,500+ t/s 的预填充速度

### 2. 显存占用
- **Qwen3-0.6B**: 15GB (46%)
- **Qwen3-4B**: 20GB (61%)
- **Qwen3VL-4B**: 22GB (67%)
- **Qwen3-VL-8B**: 28GB (87%) - 接近极限

### 3. 限制因素
- **GLM-4.7-Flash**: 架构兼容性问题，未能突破
- **V100 32GB**: 8B 模型接近显存上限，256K 可能 OOM

---

## 📁 生成的文件

```
eval_results/
├── FINAL_128K_BREAKTHROUGH_REPORT.md      # 本报告
├── MULTI_MODEL_128K_ROPE_SUCCESS.md       # 多模型报告
├── QWEN3_0.6B_128K_ROPE_SUCCESS.md        # 单模型报告
└── CONTEXT_CLIFF_DIAGNOSIS_REPORT.md      # 诊断报告

llama-server-*.sh                          # 启动脚本
├── llama-server-cuda-rope-direct.sh       # Qwen3-0.6B
├── llama-server-qwen3-4b-rope.sh          # Qwen3-4B
├── llama-server-qwen3vl-4b-rope.sh        # Qwen3VL-4B
└── llama-server-qwen3-vl-8b-rope.sh       # Qwen3-VL-8B

*.py                                       # 测试脚本
├── explore_128k_context.py
├── test_rope_128k.py
├── test_rope_128k_completion.py
├── quick_context_test.py
└── test_models_individual.py
```

---

## 🎯 下一步建议

### 1. 质量评估 (推荐)
使用 "大海捞针" 测试验证 128K 时的信息召回能力
```bash
python3 eval/test_context_256k.py --model-url http://localhost:8401 --model-name MODEL
```

### 2. 256K 尝试
- **候选**: Qwen3-0.6B (显存占用最低)
- **配置**: `--rope-scale 6.4 -c 262144`
- **风险**: 可能超时或 OOM

### 3. 其他架构
- 测试 Llama、Mistral 等非 Qwen 架构
- 验证 RoPE 缩放的通用性

---

## 🏆 总结

通过 **YaRN RoPE 缩放技术**，在 V100 32GB 上成功突破了 **4 个 Qwen3 系列模型** 到 **128K context**：

- ✅ **Qwen3-0.6B**: 43s (最快)
- ✅ **Qwen3-4B**: 83s
- ✅ **Qwen3VL-4B**: 84s
- ✅ **Qwen3-VL-8B**: 86s (最大)

这是 V100 CUDA + llama.cpp 在长上下文处理上的重大突破！

---

*报告生成时间: 2026-02-17*
*测试 Agent: V100-CUDA*
*协作 Agent: gfx1151-Tester*
