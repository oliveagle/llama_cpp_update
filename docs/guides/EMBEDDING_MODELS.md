# Embedding 模型 Context 大小记录

## 当前支持的模型

| 模型 | 架构 | Context | 维度 | 说明 |
|------|------|---------|------|------|
| Qwen3-Embedding-8B | qwen3 | **32K** (32768) | 4096 | 纯文本专用，效果最佳 |
| Qwen3-VL-Embedding-2B | qwen3vl | **32K** (32768) | 64-2048 (可调) | 多模态，30+语言，1.7GB |
| Qwen3-VL-Embedding-8B | qwen3vl | **32K** (32768) | 64-4096 (可调) | 多模态，30+语言，7.5GB，需 8GB+ 显存 |
| Granite-Embedding-107M | bert | 8K | 384 | 轻量级，多语言 |

## V-L 模型特性

**Qwen3-VL-Embedding** 系列支持：
- **输入模态**: 文本、图像、截图、视频，以及任意多模态组合
- **语言**: 30+ 种语言
- **自定义维度**: 64 到 4096 (8B) / 64 到 2048 (2B) 可调

## Context 配置建议

```bash
# Qwen3 Embedding 模型 - 32K 可用
./llama-server --embedding --pooling mean -c 32768 ...

# V-L Embedding 模型 - 32K 上下文
./llama-server --embedding --pooling mean -c 32768 ...
```

## 已知限制

1. **V-L 模型纯文本效果**: 即使是 8B 参数量，纯文本 embedding 效果仍不如专用文本模型
   - 原因: M-RoPE 位置编码设计用于图文混合输入
   - 训练数据: 主要用图文对训练，纯文本 embedding 训练不足

2. **需要使用 `--no-warmup`**: V-L 模型在 warmup 阶段可能崩溃

## API 端点

```bash
# 纯文本输入
curl http://localhost:13232/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "text to embed"}'

# 图文混合输入 (V-L 模型)
curl http://localhost:13232/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"input": "<image>describe this image"}'
```
