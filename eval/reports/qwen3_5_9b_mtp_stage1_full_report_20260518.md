# Qwen3.5-9B-MTP Stage 1 性能测试报告

> **模型**: Qwen3.5-9B-Q4_K_M (unsloth/Qwen3.5-9B-MTP-GGUF)
> **llama.cpp**: b9196 (7ba22c6a0)
> **测试时间**: 2026-05-18
> **模型文件**: /mnt/eaget-4tb/modelscope_models/Qwen3.5-9B-MTP-GGUF/Qwen3.5-9B-Q4_K_M.gguf (5.6 GB)

---

## NVIDIA V100 (CUDA) 测试结果

| 配置 | MTP | n_max | p_min | Prompt (t/s) | Token Gen (t/s) | 加速比 |
|------|-----|-------|-------|-------------|----------------|--------|
| Baseline | ❌ | - | - | 299.3 | 54.6 | 1.00x |
| MTP n=2 | ✅ | 2 | 0.75 | 255.7 | **72.4** | **1.33x** |
| MTP n=3 | ✅ | 3 | 0.75 | 248.5 | 71.9 | 1.32x |
| MTP n=4 | ✅ | 4 | 0.75 | 247.8 | 71.5 | 1.31x |

### V100 详细数据

**Baseline (无 MTP)**
- Prompt Processing: 87 tokens @ 299.3 t/s (290.7 ms)
- Token Generation (128 tokens):
  - Run 1: 54.6 t/s
  - Run 2: 54.6 t/s
  - Run 3: 54.7 t/s
  - **平均**: 54.6 t/s

**MTP n_max=2, p_min=0.75**
- Prompt Processing: 87 tokens @ 255.7 t/s (340.2 ms)
- Token Generation (128 tokens):
  - Run 1: 74.1 t/s
  - Run 2: 71.4 t/s
  - Run 3: 71.8 t/s
  - **平均**: 72.4 t/s
- **加速比**: 1.33x

**MTP n_max=3, p_min=0.75**
- Prompt Processing: 87 tokens @ 248.5 t/s (350.1 ms)
- Token Generation (128 tokens):
  - Run 1: 68.6 t/s
  - Run 2: 74.3 t/s
  - Run 3: 72.8 t/s
  - **平均**: 71.9 t/s
- **加速比**: 1.32x

**MTP n_max=4, p_min=0.75**
- Prompt Processing: 87 tokens @ 247.8 t/s (351.1 ms)
- Token Generation (128 tokens):
  - Run 1: 72.1 t/s
  - Run 2: 70.4 t/s
  - Run 3: 71.9 t/s
  - **平均**: 71.5 t/s
- **加速比**: 1.31x

---

## AMD Radeon 8060S (Vulkan) 测试结果

| 配置 | MTP | n_max | p_min | Prompt (t/s) | Token Gen (t/s) | 加速比 |
|------|-----|-------|-------|-------------|----------------|--------|
| Baseline | ❌ | - | - | 77.6 | 35.1 | 1.00x |
| MTP n=2 | ✅ | 2 | 0.75 | 232.8 | **48.3** | **1.38x** |
| MTP n=3 | ✅ | 3 | 0.75 | 151.2 | 43.2 | 1.23x |
| MTP n=4 | ✅ | 4 | 0.75 | 229.9 | 42.1 | 1.20x |

### AMD 详细数据

**Baseline (无 MTP)**
- Prompt Processing: 87 tokens @ 77.6 t/s (1121.4 ms)
- Token Generation: 35.1 t/s (3647.8 ms)

**MTP n_max=2, p_min=0.75**
- Prompt Processing: 87 tokens @ 232.8 t/s (373.7 ms)
- Token Generation: **48.3 t/s** (平均)
- **加速比**: 1.38x

---

## 总结

### 性能对比 (Token Generation)

| 后端 | Baseline | MTP n=2 最佳 | 加速比 |
|------|----------|-------------|--------|
| **NVIDIA V100** | 54.6 t/s | 72.4 t/s | **1.33x** |
| **AMD 8060S** | 35.1 t/s | 48.3 t/s | **1.38x** |

### 关键发现

1. **MTP 加速效果稳定**: V100 和 AMD GPU 都获得了约 1.3-1.4x 的加速
2. **最佳参数**: `n_max=2, p_min=0.75` 在两种 GPU 上都是最稳定的配置
3. **V100 更快**: 基线和 MTP 性能都比 AMD 高约 50%
4. **Prompt Processing**: AMD GPU 上 MTP 显著加速 prompt processing (3x)，V100 上变化不大

### 建议

- **NVIDIA V100**: 使用 `--spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-p-min 0.75`
- **AMD 8060S**: 使用 `--spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-p-min 0.75`

---

## 参考资料

- [unsloth/Qwen3.5-9B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-MTP-GGUF)
- [llama.cpp PR #22747 - MTP drafter support](https://github.com/ggml-org/llama.cpp/pull/22747)
- [llama.cpp MTP 实验分支](https://github.com/ggml-org/llama.cpp/tree/gg/spec-mtp-experiments)
