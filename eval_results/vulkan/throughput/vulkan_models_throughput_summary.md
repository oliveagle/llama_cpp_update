# Vulkan 版本模型吞吐量测试报告

> **测试时间**: 2026-02-17
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester
> **硬件**: AMD gfx1151 (Strix Halo, 32GB VRAM)
> **配置**: ctx-size=8192, flash-attn=on

---

## 第一梯队入门测试 - 基础吞吐量

| 模型 | 参数量 | 首token延迟 | 生成速率 | 总时间 | 状态 |
|------|--------|------------|----------|--------|------|
| GLM-4.7-Flash-Q4_K_M | 4.7B | 671ms | 40.7 tps | 48.0s | ✅ |
| Qwen3-4B-Instruct-2507-UD-Q4_K_XL | 4B | 124ms | 54.0 tps | 7.0s | ✅ |
| MiniCPM-o-4_5-Q4_K_M | 4.5B | 66ms | 41.9 tps | 7.1s | ✅ |
| Qwen3VL-4B-Instruct-Q8_0 | 4B | 38ms | 50.2 tps | 5.6s | ✅ |
| Qwen3-Coder-Next-Q4_K_M | - | 185ms | 32.1 tps | 184.7s | ✅ (首次加载慢) |
| Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0 | 8B | 65ms | 26.6 tps | 12.5s | ✅ |

---

## 性能分析

### 生成速率排名
1. **Qwen3-4B-Instruct**: 54.0 tps (最快)
2. **Qwen3VL-4B-Instruct**: 50.2 tps
3. **MiniCPM-o-4_5**: 41.9 tps
4. **GLM-4.7-Flash**: 40.7 tps
5. **Qwen3-Coder-Next**: 32.1 tps (首次加载)
6. **Qwen3-VL-8B**: 26.6 tps

### 观察
- 4B 级别模型在 Vulkan 上能达到 50+ tps
- 8B 模型约为 26 tps
- 首次模型加载需要编译 Vulkan shader，时间较长
- 量化格式影响速度 (Q4_K_M vs Q8_0)

---

## 原始数据

```json
{
  "timestamp": "2026-02-17T15:10:00",
  "backend": "vulkan",
  "models": [
    {
      "name": "GLM-4.7-Flash-Q4_K_M",
      "prompt_ms": 671.33,
      "prompt_tps": 16.38,
      "predicted_tps": 40.69,
      "total_time_s": 48.0
    },
    {
      "name": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL",
      "prompt_ms": 124.20,
      "prompt_tps": 112.72,
      "predicted_tps": 54.00,
      "total_time_s": 6.96
    },
    {
      "name": "MiniCPM-o-4_5-Q4_K_M",
      "prompt_ms": 65.69,
      "prompt_tps": 137.01,
      "predicted_tps": 41.92,
      "total_time_s": 7.08
    },
    {
      "name": "Qwen3VL-4B-Instruct-Q8_0",
      "prompt_ms": 37.73,
      "prompt_tps": 238.57,
      "predicted_tps": 50.24,
      "total_time_s": 5.65
    },
    {
      "name": "Qwen3-Coder-Next-Q4_K_M",
      "prompt_ms": 185.25,
      "prompt_tps": 48.58,
      "predicted_tps": 32.11,
      "total_time_s": 184.68
    },
    {
      "name": "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0",
      "prompt_ms": 64.58,
      "prompt_tps": 139.37,
      "predicted_tps": 26.56,
      "total_time_s": 12.52
    }
  ]
}
```

---

## 待测试模型

- [ ] MiroThinker-v1.5-30B.Q8_0 (30B 大模型)
- [ ] MiniCPM-o-4_5-vision-F16 (视觉编码器)
- [ ] mmproj 视觉投影层

---

*报告生成时间: 2026-02-17*
