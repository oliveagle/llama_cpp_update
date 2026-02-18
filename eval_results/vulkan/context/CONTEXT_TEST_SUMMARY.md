# Context Window 阶梯测试报告

> **测试时间**: 2026-02-17
> **测试端点**: http://localhost:8400
> **测试 Agent**: gfx1151-Tester
> **硬件**: AMD gfx1151 (Strix Halo, 32GB VRAM)
> **配置**: ctx-size=131072, flash-attn=on

---

## 测试梯度

| 梯度 | Token 数量 | 说明 |
|------|-----------|------|
| 4K | 4,096 | 基础测试 |
| 8K | 8,192 | 标准长文本 |
| 16K | 16,384 | 长文档处理 |
| 32K | 32,768 | 论文/报告 |
| 64K | 65,536 | 长书籍 |
| 128K | 131,072 | 极限测试 |

---

## Qwen3-4B-Instruct-2507-UD-Q4_K_XL 测试结果

| 梯度 | Target | Actual Tokens | 响应时间 | 答案正确 | 状态 |
|------|--------|---------------|----------|----------|------|
| **4K** | 4K | 9,772 | 0.1s | ✅ | ✅ 成功 |
| **8K** | 8K | 19,515 | 46.4s | ✅ | ✅ 成功 |
| **16K** | 16K | - | - | - | ❌ HTTP 500 |
| 32K | 32K | - | - | - | ⏹️ 停止测试 |
| 64K | 64K | - | - | - | ⏹️ 未测试 |
| 128K | 128K | - | - | - | ⏹️ 未测试 |

### 结果分析

**最大可用 Context**: **8K** (实际 19,515 tokens)

**16K 失败原因**: HTTP 500 错误，可能是显存分配失败

**性能表现**:
- 4K: 响应极快 (0.1s)，成功召回 needle
- 8K: 响应较慢 (46.4s)，成功召回 needle
- 16K+: 服务器错误

---

## 其他模型测试状态

| 模型 | 4K | 8K | 16K | 32K | 最大可用 |
|------|----|----|-----|-----|----------|
| GLM-4.7-Flash-Q4_K_M | ✅ | ⏳ | ⏳ | ⏳ | 待测 |
| Qwen3-4B-Instruct | ✅ | ✅ | ❌ | - | **8K** |
| MiniCPM-o-4_5-Q4_K_M | ⏳ | ⏳ | ⏳ | ⏳ | 待测 |
| Qwen3VL-4B-Instruct-Q8_0 | ⏳ | ⏳ | ⏳ | ⏳ | 待测 |
| Qwen3-Coder-Next-Q4_K_M | ⏳ | ⏳ | ⏳ | ⏳ | 待测 |
| Qwen3-VL-8B-Instruct-Q8_0 | ⏳ | ⏳ | ⏳ | ⏳ | 待测 |
| MiroThinker-30B.Q8_0 | ⏳ | ⏳ | ⏳ | ⏳ | 待测 |

---

## 技术限制说明

### 当前限制
1. **配置限制**: 虽然设置了 ctx-size=131072，但实际可用受限于显存
2. **AMD Vulkan**: gfx1151 在 Vulkan 后端下显存管理可能有限制
3. **KV Cache**: 长 context 需要大量显存存储 KV cache

### 优化建议
如需测试更大 context:
1. 使用更小的量化格式 (Q4_K_M 替代 Q8_0)
2. 使用 CUDA 后端 (V100 32GB 显存更充足)
3. 减少 batch size 和并发数
4. 尝试使用 `--cache-type-k q4_0` 压缩 KV cache

---

## 原始数据

### Qwen3-4B 4K 测试详情
```json
{
  "target_tokens": 4096,
  "actual_tokens": 9772,
  "response_time": 0.1,
  "correct": true,
  "answer": "小狗"
}
```

### Qwen3-4B 8K 测试详情
```json
{
  "target_tokens": 8192,
  "actual_tokens": 19515,
  "response_time": 46.4,
  "correct": true,
  "answer": "小狗"
}
```

### Qwen3-4B 16K 错误详情
```
HTTP 500: Internal Server Error
可能原因: 显存分配失败
```

---

## 结论

**Qwen3-4B-Instruct** 在 Vulkan 后端下:
- **推荐最大 Context**: 8K (实际约 19K tokens)
- **极限 Context**: 8K
- **性能**: 4K 极速 (0.1s)，8K 可用 (46s)

**待完成工作**:
- [ ] 测试其他 6 个模型的 context 能力
- [ ] 在 CUDA 后端 (V100) 上对比测试

---

*报告生成时间: 2026-02-17*
*Agent: gfx1151-Tester*
