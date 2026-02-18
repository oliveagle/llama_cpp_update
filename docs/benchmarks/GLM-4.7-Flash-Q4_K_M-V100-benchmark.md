# GLM-4.7-Flash-Q4_K_M V100 性能测试报告

## 测试环境
- **GPU**: NVIDIA V100 32GB
- **模型**: GLM-4.7-Flash-Q4_K_M
- **框架**: llama.cpp (build 8072)
- **量化**: Q4_K_M
- **测试时间**: 2026-02-17

## 模型信息
- **架构**: DeepSeek2 (MoE)
- **参数量**: 30B (激活 3B)
- **专家数**: 64 (激活 4)
- **层数**: 47
- **文件大小**: 17.05 GiB
- **上下文训练长度**: 202752

## 配置参数
```bash
-ctx-size 16384
-ngl 999
-fa on
-ctk q8_0 -ctv q8_0
```

## 预填充速度 (Prompt Processing)

| Prompt 长度 | Tokens | 时间 | 速度 | 状态 |
|------------|--------|------|------|------|
| 1K | 2,006 | 2.9s | **693 t/s** | ✅ |
| 4K | 8,006 | 10.1s | **797 t/s** | ✅ |
| 8K | 16,006 | 19.2s | **834 t/s** | ✅ |
| 16K | - | - | - | ❌ 失败 |

## 生成速度 (Generation)

| 测试项 | Tokens | 时间 | 速度 |
|--------|--------|------|------|
| 128 tokens | 128 | 3.8s | **33.38 t/s** |

**平均生成速度**: 33.4 t/s

## 原始测试数据记录

### 测试命令
```bash
llama-server \
  -m /mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf \
  -c 16384 -ngl 999 --flash-attn on -ctk q8_0 -ctv q8_0 \
  --host 127.0.0.1 --port 8402 --no-warmup
```

### API 原始响应数据
```json
// 1K prompt test
{
  "prompt_n": 2006,
  "prompt_ms": 2895,
  "prompt_per_second": 693.0
}

// 4K prompt test
{
  "prompt_n": 8006,
  "prompt_ms": 10052,
  "prompt_per_second": 796.5
}

// 8K prompt test
{
  "prompt_n": 16006,
  "prompt_ms": 19182,
  "prompt_per_second": 834.4
}

// Generation test (128 tokens)
{
  "predicted_n": 128,
  "predicted_ms": 3834,
  "predicted_per_second": 33.38
}
```

### Context 上限测试记录
```
ctx=4096:  ✅ OK, VRAM=17902MiB
ctx=8192:  ✅ OK, VRAM=17902MiB
ctx=12288: ✅ OK, VRAM=17902MiB
ctx=14336: ✅ OK, VRAM=17902MiB
ctx=16384: ❌ Fail (启动失败)
```

### GPU 状态记录
```
Model loaded: 17902 MiB / 32768 MiB
Process: llama-server 17566 MiB
```

## 显存使用
- **模型**: ~17 GB
- **8K KV cache**: ~0.5 GB
- **总计**: ~17.9 GB / 32 GB

## 与 JoyAI 对比

| 指标 | GLM-4.7-Flash (18GB) | JoyAI (28GB) |  winner |
|------|---------------------|--------------|---------|
| 显存占用 | **17.9 GB** | 29.5 GB | GLM ✅ |
| 预填充 8K | **834 t/s** | 736 t/s | GLM ✅ |
| 生成速度 | 33.4 t/s | **38-40 t/s** | JoyAI ✅ |
| 16K 支持 | ❌ | ✅ | JoyAI ✅ |
| 性价比 | ⭐⭐⭐⭐ | ⭐⭐⭐ | GLM ✅ |

## GLM 系列内部对比

| 模型 | 大小 | 预填充 8K | 生成 | 显存 |
|------|------|----------|------|------|
| GLM-4.7-Flash (47B) | 18GB | 834 t/s | 33.4 t/s | 17.9GB |
| GLM-4.7-Flash-REAP (23B) | 13GB | 863 t/s | 32.6 t/s | 13.9GB |

**结论**: REAP 版本性价比更高

## 结论
- **优势**: 显存占用低 (17.9GB)，预填充速度快
- **劣势**: 生成速度一般，16K 不支持
- **适用场景**: 显存受限，需要快速预填充的场景

## 文件位置
- 模型: `/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/`

## Context 上限测试 (梯度测试)

| Context | 状态 | VRAM | 备注 |
|---------|------|------|------|
| 4K (4096) | ✅ OK | 17.9GB | 稳定运行 |
| 8K (8192) | ✅ OK | 17.9GB | 稳定运行 |
| 12K (12288) | ✅ OK | 17.9GB | 稳定运行 |
| 14K (14336) | ✅ OK | 17.9GB | 临界值 |
| 16K (16384) | ❌ Fail | - | 启动失败 |

**结论**: GLM-4.7-Flash 在 V100 32GB 上的**实用上限约 14K**，远低于其训练长度 200K。

**对比**:
| 模型 | 实用 Context | 训练 Context | 显存占用 |
|------|-------------|-------------|---------|
| GLM-4.7-Flash | **~14K** | 200K | 17.9GB |
| JoyAI-LLM-Flash | **16K** | 128K | 29.5GB |
| GLM-4.7-Flash-REAP | **~8K** | - | 13.9GB |

