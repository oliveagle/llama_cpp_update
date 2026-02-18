# V100 CUDA 64K Context 配置指南

> **目标**: 64K context 作为实际上限（替代之前的128K）
> **原因**: 128K 处理速度较慢，64K 是性能与容量的最佳平衡点
> **更新时间**: 2026-02-17

---

## 🎯 配置变更说明

### 从 128K 调整到 64K 的原因

1. **处理速度**: 64K 处理时间约 35-50秒，128K 需要 85-130秒
2. **显存占用**: 64K KV cache 约 3-4GB，128K 需要 6-7GB
3. **实用性**: 大多数长文档场景 64K 已足够（约 4-5万字）
4. **稳定性**: 64K 下所有模型运行更稳定

---

## 📊 各模型 64K 配置

### 1. Qwen3-0.6B-Q4_0 (原生 32K)

```bash
./llama-server-cuda-rope-direct.sh start
```

**RoPE 参数**:
- `--rope-scaling yarn`
- `--rope-scale 2.0` (32K → 64K)
- `--yarn-orig-ctx 32768`
- `-c 65536`

**性能预估**:
- 64K 处理时间: ~35秒
- 显存占用: ~18GB

---

### 2. MiniCPM-o-4.5-Q4_K_M (原生 40K)

```bash
./llama-server-minicpm-o-rope.sh start
```

**RoPE 参数**:
- `--rope-scaling yarn`
- `--rope-scale 1.6` (40K → 64K)
- `--yarn-orig-ctx 40960`
- `-c 65536`

**性能预估**:
- 64K 处理时间: ~40秒
- 显存占用: ~12GB

---

### 3. Qwen3-4B / Qwen3VL-4B (原生 32K)

**RoPE 参数**:
- `--rope-scaling yarn`
- `--rope-scale 2.0`
- `--yarn-orig-ctx 32768`
- `-c 65536`

**性能预估**:
- 64K 处理时间: ~45秒
- 显存占用: ~18GB

---

### 4. Qwen3-VL-8B (原生 32K)

**RoPE 参数**:
- `--rope-scaling yarn`
- `--rope-scale 2.0`
- `--yarn-orig-ctx 32768`
- `-c 65536`

**性能预估**:
- 64K 处理时间: ~50秒
- 显存占用: ~22GB

---

### 5. JoyAI-LLM-Flash (原生 128K)

```bash
./llama-server-joyai-32k.sh start  # 已限制 32K
```

**说明**: 28GB 模型，64K KV cache 需要 ~3GB，总计 ~31GB（接近上限）
**建议**: 限制在 32K 运行

---

### 6. GLM-4.7-Flash-REAP (原生 202K)

```bash
./llama-server-glm47-reap-rope.sh start
```

**说明**: 原生 202K，但 64K 处理较慢（约 5.5ms/token）
**建议**: 适合 32K，64K 可用但需耐心等待

---

## 🏆 推荐配置矩阵

| 模型 | 推荐 Context | RoPE Scale | 显存占用 | 处理时间 |
|------|-------------|------------|----------|----------|
| Qwen3-0.6B | **64K** | 2.0x | ~18GB | ~35s |
| MiniCPM-o-4.5 | **64K** | 1.6x | ~12GB | ~40s |
| Qwen3-4B | **64K** | 2.0x | ~18GB | ~45s |
| Qwen3VL-4B | **64K** | 2.0x | ~18GB | ~45s |
| Qwen3-VL-8B | **64K** | 2.0x | ~22GB | ~50s |
| JoyAI-LLM-Flash | **32K** | N/A | ~30GB | ~60s |
| GLM-4.7-REAP | **32K** | N/A | ~18GB | ~45s |

---

## 🚀 快速启动命令

```bash
# 最快 64K (Qwen3-0.6B)
./llama-server-cuda-rope-direct.sh start

# 多模态 64K (MiniCPM-o-4.5)
./llama-server-minicpm-o-rope.sh start

# 大模型 64K (Qwen3-VL-8B)
./llama-server-qwen3-vl-8b-rope.sh start
```

---

## 📁 相关文件

| 文件 | 说明 |
|------|------|
| `llama-server-cuda-rope-direct.sh` | Qwen3-0.6B 64K |
| `llama-server-minicpm-o-rope.sh` | MiniCPM-o-4.5 64K |
| `llama-server-qwen3-4b-rope.sh` | Qwen3-4B 64K |
| `llama-server-qwen3vl-4b-rope.sh` | Qwen3VL-4B 64K |
| `llama-server-qwen3-vl-8b-rope.sh` | Qwen3-VL-8B 64K |
| `llama-server-joyai-32k.sh` | JoyAI 32K (上限) |
| `llama-server-glm47-reap-rope.sh` | GLM-4.7-REAP 64K |

---

## ⚠️ 注意事项

1. **32K 仍是黄金标准**: 所有模型都能稳定运行 32K
2. **64K 需要 RoPE**: 原生 context < 64K 的模型需要 RoPE 缩放
3. **大模型限制**: 超过 20GB 的模型建议限制在 32K
4. **速度权衡**: 64K 比 32K 慢 2-3 倍，根据场景选择

---

*配置更新: 2026-02-17*
*目标调整: 128K → 64K*
