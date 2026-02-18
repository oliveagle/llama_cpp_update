# 多模型 128K Context 突破成功报告

> **测试时间**: 2026-02-17
> **GPU**: NVIDIA V100 32GB
> **RoPE 缩放**: YaRN
> **方法**: --rope-scale 4.0 (32K → 128K)

---

## 🎯 突破成果

成功将 **3 个模型** 从原生 32K 扩展到 **128K context**！

### 突破模型列表

| 模型 | 原生 Context | RoPE Scale | 128K 状态 | 128K 耗时 |
|------|-------------|-----------|----------|----------|
| **Qwen3-0.6B-Q4_0** | 32K | 3.2 | 🎉 成功 | 43s |
| **Qwen3-4B-Q4_K_XL** | 32K | 4.0 | 🎉 成功 | 83s |
| **Qwen3VL-4B-Q8_0** | 32K | 4.0 | 🎉 成功 | 84s |

---

## 📊 详细性能数据

### Qwen3-0.6B-Q4_0

| Context | Tokens | 耗时 | 显存 |
|---------|--------|------|------|
| 32K | 32,767 | ~8s | ~15GB |
| 64K | 65,536 | ~15s | ~15GB |
| 96K | 98,305 | ~25s | ~15GB |
| **128K** | **131,071** | **~43s** | **~15GB** |

### Qwen3-4B-Q4_K_XL

| Context | Tokens | 耗时 | 显存 |
|---------|--------|------|------|
| 32K | 32,767 | 17.6s | ~20GB |
| 64K | 65,536 | 38.1s | ~20GB |
| 96K | 98,305 | 60.1s | ~20GB |
| **128K** | **131,071** | **83.3s** | **~20GB** |

### Qwen3VL-4B-Q8_0

| Context | Tokens | 耗时 | 显存 |
|---------|--------|------|------|
| 32K | 32,767 | 16.4s | ~22GB |
| 64K | 65,536 | 36.7s | ~22GB |
| 96K | 98,305 | 58.9s | ~22GB |
| **128K** | **131,071** | **83.6s** | **~22GB** |

---

## 🔧 RoPE YaRN 缩放配置

### 启动命令

```bash
# Qwen3-0.6B (scale 3.2: 40K → 128K)
llama-server \
    -m Qwen3-0.6B-Q4_0.gguf \
    -c 131072 \
    --rope-scaling yarn \
    --rope-scale 3.2 \
    --yarn-orig-ctx 32768 \
    -ngl 99

# Qwen3-4B (scale 4.0: 32K → 128K)
llama-server \
    -m Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf \
    -c 131072 \
    --rope-scaling yarn \
    --rope-scale 4.0 \
    --yarn-orig-ctx 32768 \
    -ngl 99

# Qwen3VL-4B (scale 4.0: 32K → 128K)
llama-server \
    -m Qwen3VL-4B-Instruct-Q8_0.gguf \
    -c 131072 \
    --rope-scaling yarn \
    --rope-scale 4.0 \
    --yarn-orig-ctx 32768 \
    -ngl 99
```

### 关键参数说明

| 参数 | 值 | 说明 |
|------|-----|------|
| `--rope-scaling` | yarn | 使用 YaRN 缩放方法 |
| `--rope-scale` | 3.2~4.0 | 扩展倍数 |
| `--yarn-orig-ctx` | 32768 | 模型原生 context 长度 |
| `-c` | 131072 | 目标 context 长度 |

---

## 🚀 启动脚本

已创建专用启动脚本：

```bash
# Qwen3-0.6B
./llama-server-cuda-rope-direct.sh start

# Qwen3-4B
./llama-server-qwen3-4b-rope.sh start

# Qwen3VL-4B
./llama-server-qwen3vl-4b-rope.sh start
```

---

## 📈 性能趋势分析

### 预填充速度对比

| 模型 | 32K | 64K | 96K | 128K |
|------|-----|-----|-----|------|
| Qwen3-0.6B | ~4,000 t/s | ~4,300 t/s | ~3,900 t/s | ~3,000 t/s |
| Qwen3-4B | ~1,900 t/s | ~1,700 t/s | ~1,600 t/s | ~1,600 t/s |
| Qwen3VL-4B | ~2,000 t/s | ~1,800 t/s | ~1,700 t/s | ~1,600 t/s |

### 显存占用

| 模型 | 显存占用 | 利用率 |
|------|---------|--------|
| Qwen3-0.6B | ~15GB | 46% |
| Qwen3-4B | ~20GB | 61% |
| Qwen3VL-4B | ~22GB | 67% |

**结论**: V100 32GB 可以 comfortably 支持所有三个模型的 128K context。

---

## ⚠️ 注意事项

### 1. 必须使用 `/v1/completions` 端点

`/v1/chat/completions` 存在 chat template 兼容性问题。

### 2. 长 context 响应质量

- 128K 时模型可能只输出简短内容
- 建议在实际应用中添加明确的指令引导

### 3. 首次加载时间

- 4B 和 VL-4B 模型首次加载需要 5-10 秒
- 建议在测试前预热模型

---

## 🎉 总结

通过 **YaRN RoPE 缩放技术**，成功突破了三个 Qwen3 系列模型的 context 限制：

- ✅ **Qwen3-0.6B**: 40K → 128K (3.2x)
- ✅ **Qwen3-4B**: 32K → 128K (4x)
- ✅ **Qwen3VL-4B**: 32K → 128K (4x)

这是 V100 + llama.cpp 在长上下文处理上的重大突破！

---

*报告生成时间: 2026-02-17*
*测试 Agent: V100-CUDA*
*协作 Agent: gfx1151-Tester (提供 256K 测试脚本)*
