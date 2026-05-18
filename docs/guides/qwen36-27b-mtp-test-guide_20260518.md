# Qwen3.6-27B MTP 测试指南

> **更新时间**: 2026-05-18
> **状态**: 测试失败 - AMD GPU 显存不足（详见评估报告）

## 概述

MTP (Multi-Token Prediction) 是 Qwen3.6 模型内置的推测解码功能，无需额外的 draft 模型，可实现 1.5-2x 的推理加速。

## 模型信息

- **模型**: unsloth/Qwen3.6-27B-MTP-GGUF
- **文件**: Qwen3.6-27B-Q4_K_M.gguf
- **大小**: ~15.3 GB
- **位置**: `/mnt/eaget-4tb/modelscope_models/Qwen3.6-27B-MTP-GGUF/`

## llama.cpp 支持

- **最低版本**: b8645+ (2026-05-16 之后)
- **参数**: `--spec-type draft-mtp`
- **可调参数**:
  - `--spec-draft-n-max`: 最大 draft token 数 (2-4)
  - `--spec-draft-p-min`: 最小接受概率 (0.75-0.90)

## 测试脚本

### 文件位置
`/mnt/eaget-4tb/llama_cpp/eval/tests/stage1/test_qwen36_27b_mtp_stage1.py`

### 运行方法

```bash
cd /mnt/eaget-4tb/llama_cpp
python3 eval/tests/stage1/test_qwen36_27b_mtp_stage1.py
```

### 测试内容

1. **基线测试** - 无 MTP 的基准性能
2. **MTP n_max=2** - 每次 draft 2 个 token
3. **MTP n_max=3** - 每次 draft 3 个 token
4. **MTP n_max=4** - 每次 draft 4 个 token
5. **MTP n_max=3, p_min=0.90** - 更严格的接受阈值

### 测试指标

- **Prompt Processing**: 长 prompt 吞入速度
- **Token Generation**: 短 prompt，多 token 生成速度
- **加速比**: MTP vs 基线的速度提升

## 手动测试命令

### CUDA (V100)
```bash
/mnt/eaget-4tb/llama_cpp/current/llama-server \
  -m /mnt/eaget-4tb/modelscope_models/Qwen3.6-27B-MTP-GGUF/Qwen3.6-27B-Q4_K_M.gguf \
  --ctx-size 8192 \
  --n-gpu-layers 99 \
  --port 8480 \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  --spec-draft-p-min 0.75
```

### Vulkan (AMD gfx1151)
```bash
AMD_VULKAN_ICD=/usr/share/vulkan/icd.d/amdvlk64.json \
/mnt/eaget-4tb/llama_cpp/current/llama-server \
  -m /mnt/eaget-4tb/modelscope_models/Qwen3.6-27B-MTP-GGUF/Qwen3.6-27B-Q4_K_M.gguf \
  --ctx-size 8192 \
  --n-gpu-layers 99 \
  --port 8480 \
  --spec-type draft-mtp \
  --spec-draft-n-max 3 \
  --spec-draft-p-min 0.75
```

## 预期性能

根据社区报告：
- **基线**: ~30 tokens/s (27B Q4_K_M on V100)
- **MTP n=3**: ~45-50 tokens/s (1.5-1.7x 加速)
- **MTP n=4**: ~50-60 tokens/s (1.7-2.0x 加速)
- **接受率**: ~70-90%

## 参考资料

- [Unsloth Qwen3.6-27B-MTP-GGUF](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF)
- [llama.cpp MTP PR #22747](https://github.com/ggml-org/llama.cpp/pull/22747)
- r/LocalLLaMA MTP 讨论帖

## 下一步

1. 等待模型下载完成 (~20 分钟)
2. 运行测试脚本
3. 分析结果，确定最佳 MTP 参数
4. 更新 systemd 服务配置
