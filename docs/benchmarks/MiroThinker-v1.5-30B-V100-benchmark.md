# MiroThinker-v1.5-30B V100 性能测试报告

## 测试环境
- **GPU**: NVIDIA V100 32GB
- **模型**: MiroThinker-v1.5-30B
- **框架**: llama.cpp
- **测试时间**: 2026-02-17/02:41

## 原始测试数据

```json
{}
```

## GPU 状态
```
显存使用: 616MiB
```

## 测试命令
```bash
llama-server \
  -m /mnt/volume3/hf_models/mradermacher/MiroThinker-v1.5-30B-GGUF/MiroThinker-v1.5-30B.Q8_0.gguf \
  -c 16384 -ngl 999 \
  --flash-attn on -ctk q8_0 -ctv q8_0 \
  --host 127.0.0.1 --port 8403 --no-warmup
```
