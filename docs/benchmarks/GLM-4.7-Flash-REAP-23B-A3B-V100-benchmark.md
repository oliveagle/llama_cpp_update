# GLM-4.7-Flash-REAP-23B-A3B V100 性能测试报告

## 测试环境
- **GPU**: NVIDIA V100 32GB
- **模型**: GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL (~13GB)
- **框架**: llama.cpp (build 8072)
- **量化**: IQ4_NL (4.5 bpw)
- **测试时间**: 2026-02-17

## 模型信息
- **架构**: DeepSeek2 (MoE)
- **参数**: 23B (激活 3B)
- **专家数**: 48 (激活 4)
- **层数**: 47
- **上下文训练长度**: 202752 (约 200K)

## 配置参数
```bash
-ctx-size 16384          # 16K context
-ngl 999                  # 全 GPU offload
-fa on                    # Flash Attention 开启
-ctk q8_0 -ctv q8_0      # KV cache 量化
```

## 预填充速度 (Prompt Processing)

| Prompt 长度 | Tokens | 时间 | 速度 | 状态 |
|------------|--------|------|------|------|
| 1K | 2,006 | 2.6s | **764 t/s** | ✅ |
| 4K | 8,006 | 9.5s | **844 t/s** | ✅ |
| 8K | 16,006 | 18.6s | **863 t/s** | ✅ |
| 16K | - | - | - | ❌ 失败 |

## 生成速度 (Generation)
- **速度**: ~32.6 t/s

## 显存使用
- **模型**: ~12.5 GB
- **16K KV cache**: ~0.5 GB
- **总计**: ~13.9 GB / 32 GB

## 与 JoyAI 对比

| 指标 | GLM-REAP (13GB) | JoyAI (28GB) |
|------|-----------------|--------------|
| 预填充 8K | 863 t/s | 736 t/s |
| 生成速度 | 32.6 t/s | 38-40 t/s |
| 显存占用 | 13.9 GB | 29.5 GB |
| 16K 支持 | ❌ | ✅ |

## 结论
- **实用预填充上限**: 8K tokens
- **性能特点**: 比 JoyAI 更省显存，但生成速度稍慢
- **适用场景**: 显存受限但需要 MoE 模型的场景

## 文件位置
- 模型: `/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-REAP-23B-A3B-GGUF/`
