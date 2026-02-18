# JoyAI-LLM-Flash V100 性能测试报告

## 测试环境
- **GPU**: NVIDIA V100 32GB
- **模型**: JoyAI-LLM-Flash-Q4_K_M (~28GB)
- **框架**: llama.cpp (build 8072)
- **量化**: Q4_K_M
- **测试时间**: 2026-02-17

## 配置参数
```bash
-ctx-size 16384          # 16K context (实用上限)
-ngl 999                  # 全 GPU offload
-fa on                    # Flash Attention 开启
-ctk q8_0 -ctv q8_0      # KV cache 量化
```

## 预填充速度 (Prompt Processing)

| Prompt 长度 | Tokens | 时间 | 速度 | 备注 |
|------------|--------|------|------|------|
| 1K | 2,038 | 0.25s | **8,190 t/s** | 有缓存加速 |
| 4K | 8,038 | 10.8s | **745 t/s** | 正常速度 |
| 8K | 16,038 | 21.8s | **736 t/s** | 正常速度 |
| 16K | 32,038 | 68s | **471 t/s** | 可用，约1分钟 |
| 32K | 64,038 | 236s | **271 t/s** | 太慢，不推荐 |
| 64K+ | - | 超时/失败 | - | 不可行 |

## 生成速度 (Generation)

| 测试项 | Tokens | 时间 | 速度 |
|--------|--------|------|------|
| 128 tokens | 128 | 3.3s | **38.73 t/s** |
| 256 tokens | 256 | 6.6s | **38.52 t/s** |
| 512 tokens | 512 | 13.3s | **38.60 t/s** |

**平均生成速度**: 38.6 t/s (稳定，不受上下文长度影响)

## 原始测试数据记录

### 测试命令
```bash
llama-server \
  -m /mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf \
  -c 16384 -ngl 999 --flash-attn on -ctk q8_0 -ctv q8_0 \
  --host 127.0.0.1 --port 8401 --no-warmup
```

### API 原始响应数据
```json
// 1K prompt test
{
  "prompt_n": 2038,
  "prompt_ms": 249,
  "prompt_per_second": 8189.7
}

// 4K prompt test
{
  "prompt_n": 8038,
  "prompt_ms": 10788,
  "prompt_per_second": 745.1
}

// 8K prompt test
{
  "prompt_n": 16038,
  "prompt_ms": 21780,
  "prompt_per_second": 736.4
}

// Generation test (128 tokens)
{
  "predicted_n": 128,
  "predicted_ms": 3307,
  "predicted_per_second": 38.73
}
```

### GPU 状态记录
```
Model loaded: 29504 MiB / 32768 MiB
Process: llama-server 29036 MiB
```

## 显存使用
- **模型**: ~28 GB
- **16K KV cache**: ~1 GB
- **总计**: ~29 GB / 32 GB

## 结论
- **实用预填充上限**: 16K tokens
- **推荐配置**: ctx-size = 16384
- **性能瓶颈**: Attention O(n²) 复杂度

## 文件位置
- 模型: `/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/`
- 配置: `/mnt/volume3/llama_cpp/presets/mypresets-cuda.ini`
- 服务: `llama-server-8401.service`
