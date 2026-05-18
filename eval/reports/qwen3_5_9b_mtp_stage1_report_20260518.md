# Qwen3.5-9B-MTP Stage 1 性能测试报告

> **模型**: Qwen3.5-9B-Q4_K_M (unsloth/Qwen3.5-9B-MTP-GGUF)
> **后端**: Vulkan (AMD Radeon 8060S, 128GB)
> **测试时间**: 2026-05-18
> **llama.cpp**: b9196
> **模型文件**: /mnt/eaget-4tb/modelscope_models/Qwen3.5-9B-MTP-GGUF/Qwen3.5-9B-Q4_K_M.gguf (5.6 GB)

## 测试结果

| 配置 | MTP | n_max | p_min | Prompt (t/s) | Token Gen (t/s) | 加速比 |
|------|-----|-------|-------|-------------|----------------|--------|
| Baseline | ❌ | - | - | 77.6 | 35.1 | 1.00x |
| MTP n=2 | ✅ | 2 | 0.75 | 232.8 | **48.3** | **1.38x** |
| MTP n=3 | ✅ | 3 | 0.75 | 151.2 | 43.2 | 1.23x |
| MTP n=4 | ✅ | 4 | 0.75 | 229.9 | 42.1 | 1.20x |

## 详细数据

### Baseline (无 MTP)
- Prompt Processing: 87 tokens @ 77.6 t/s (1121.4 ms)
- Token Generation (128 tokens): 35.1 t/s (3647.8 ms)

### MTP n_max=2, p_min=0.75
- Prompt Processing: 87 tokens @ 232.8 t/s (373.7 ms)
- Token Generation (128 tokens):
  - Run 1: 51.0 t/s (2510.6 ms)
  - Run 2: 47.1 t/s (2715.6 ms)
  - Run 3: 46.9 t/s (2730.0 ms)
  - **平均**: 48.3 t/s
- **加速比**: 1.38x

### MTP n_max=3, p_min=0.75
- Prompt Processing: 87 tokens @ 151.2 t/s (575.5 ms)
- Token Generation (128 tokens):
  - Run 1: 42.9 t/s (2980.8 ms)
  - Run 2: 33.3 t/s (3842.2 ms)
  - Run 3: 53.4 t/s (2398.1 ms)
  - **平均**: 43.2 t/s
- **加速比**: 1.23x

### MTP n_max=4, p_min=0.75
- Prompt Processing: 87 tokens @ 229.9 t/s (378.4 ms)
- Token Generation (128 tokens):
  - Run 1: 34.9 t/s (3668.2 ms)
  - Run 2: 48.2 t/s (2657.9 ms)
  - Run 3: 43.2 t/s (2965.0 ms)
  - **平均**: 42.1 t/s
- **加速比**: 1.20x

## 总结

- **最佳配置**: MTP n_max=2, p_min=0.75
- **最佳速度**: 48.3 tokens/s
- **加速比**: 1.38x vs 基线 35.1 tokens/s
- **Prompt 加速**: MTP 开启后 prompt processing 也显著加速 (77.6 → 232.8 t/s)

### 观察

1. **n_max=2 最稳定**: 三次运行的方差最小，加速效果最稳定
2. **n_max=3 波动大**: 33.3-53.4 t/s，波动较大，可能是某些文本的 MTP 接受率不稳定
3. **n_max=4 不理想**: 更大的 draft 数量反而降低了性能，推测是接受率下降导致更多的 reject
4. **Prompt Processing 加速**: MTP 开启后 prompt processing 也有 2-3x 加速，这是一个意外的好处

### 建议

- 生产环境推荐: `--spec-type draft-mtp --spec-draft-n-max 2 --spec-draft-p-min 0.75`
- 如果追求更高的速度，可以尝试 `p_min=0.90` 以提高接受率
