# V100 CUDA 性能测试标准

> **文档版本**: 1.0
> **创建时间**: 2026-02-17
> **适用对象**: llama.cpp CUDA 后端 (V100 GPU)

---

## 1. 测试目标

建立标准化的性能基准测试流程，用于：
- 评估不同模型在 V100 上的性能表现
- 对比模型间的预填充速度和生成速度
- 确定每个模型的最大支持 Context 大小
- 为模型选型提供数据支持

---

## 2. 测试环境

| 配置项 | 规格 |
|--------|------|
| GPU | NVIDIA Tesla V100 32GB |
| 显存带宽 | 900 GB/s |
| CUDA 版本 | 12.5 |
| llama.cpp 端口 | 8401 |
| 服务器地址 | http://localhost:8401 |

---

## 3. 测试梯度

### Context 大小梯度

| 级别 | Tokens | 用途 |
|------|--------|------|
| 4K | 4,096 | 基础对话 |
| 8K | 8,192 | 标准对话 |
| 12K | 12,288 | 长文档摘要 |
| 16K | 16,384 | 代码分析 |
| 24K | 24,576 | 中等长度文档 |
| 32K | 32,768 | RAG 应用 |
| 48K | 49,152 | 长代码文件 |
| 64K | 65,536 | 论文分析 |
| 96K | 98,304 | 书籍章节 |
| 128K | 131,072 | 超长文档 |

---

## 4. 测试指标

### 4.1 预填充速度 (Prompt Processing Speed)

**定义**: 模型处理输入 prompt 的 token 处理速度

**计算方式**:
```
预填充速度 (t/s) = prompt_tokens / elapsed_time
```

**评分标准**:
| 等级 | 速度范围 | 评价 |
|------|----------|------|
| 🌟 优秀 | > 500 t/s | 长文本处理能力强 |
| ✅ 良好 | 200-500 t/s | 正常水平 |
| ⚠️ 一般 | 100-200 t/s | 可接受 |
| ❌ 较差 | < 100 t/s | 需要优化 |

### 4.2 生成速度 (Generation Speed)

**定义**: 模型生成输出 token 的速度

**计算方式**:
```
生成速度 (t/s) = completion_tokens / elapsed_time
```

**评分标准**:
| 等级 | 速度范围 | 评价 |
|------|----------|------|
| 🌟 优秀 | > 50 t/s | 实时交互无感知延迟 |
| ✅ 良好 | 30-50 t/s | 流畅体验 |
| ⚠️ 一般 | 15-30 t/s | 可接受但有延迟感 |
| ❌ 较差 | < 15 t/s | 体验较差 |

### 4.3 首 Token 延迟 (TTFT - Time To First Token)

**定义**: 从发送请求到收到第一个生成 token 的时间

**评分标准**:
| 等级 | 延迟范围 | 评价 |
|------|----------|------|
| 🌟 优秀 | < 0.5s | 瞬时响应 |
| ✅ 良好 | 0.5-2s | 快速响应 |
| ⚠️ 一般 | 2-5s | 可接受 |
| ❌ 较差 | > 5s | 响应慢 |

### 4.4 最大支持 Context

**定义**: 模型能够成功处理的最大上下文长度

**测试方法**: 从 4K 开始逐级测试，直到请求失败

---

## 5. 测试模型列表

| 模型 | 量化 | 预估显存 | 默认 Context |
|------|------|----------|--------------|
| Qwen3-0.6B-Q4_0 | Q4_0 | ~400MB | 12K |
| Alibaba-Apsara.DASD-4B-Thinking.Q8_0 | Q8_0 | ~4GB | 12K |
| MiniCPM-o-4_5-Q4_K_M | Q4_K_M | ~3GB | 12K |
| Qwen3-4B-Instruct-2507-UD-Q4_K_XL | Q4_K_XL | ~3GB | 12K |
| Qwen3VL-4B-Instruct-Q8_0 | Q8_0 | ~4GB | 12K |
| Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0 | Q8_0 | ~8GB | 12K |
| GLM-4.7-Flash-Q4_K_M | Q4_K_M | ~5GB | 12K |
| JoyAI-LLM-Flash-Q4_K_M | Q4_K_M | ~5GB | 16K |

---

## 6. 测试流程

### 6.1 准备阶段

1. 确保 V100 服务器已启动 (端口 8401)
2. 验证所有模型文件存在且可访问
3. 清理 GPU 缓存，确保测试环境干净

### 6.2 执行阶段

对于每个模型:
1. **探测最大 Context**: 从 4K 开始逐级测试，找到最大支持值
2. **详细性能测试**: 在所有支持的 Context 大小上测试:
   - 预填充速度
   - 生成速度
   - 首 Token 延迟
3. **记录原始数据**: 保存每次测试的详细数据

### 6.3 输出规范

**JSON 数据文件**:
```json
{
  "model": "model_name",
  "display_name": "Model Display Name",
  "timestamp": "2026-02-17T10:00:00",
  "max_context_supported": 12288,
  "context_tests": [
    {
      "context_size": 4096,
      "prompt_tokens": 4096,
      "completion_tokens": 128,
      "prompt_speed_tps": 665.28,
      "gen_speed_tps": 38.57,
      "ttft_ms": 3320,
      "elapsed_sec": 3.32,
      "status": "success"
    }
  ]
}
```

**Markdown 报告**:
- 性能概览表
- 每个模型的详细数据表
- 速度排名
- Context 支持排名
- 关键发现和建议

---

## 7. 数据存储

```
eval_results/
├── V100_PERFORMANCE_TESTING_STANDARD.md      # 本文件
├── V100_ALL_MODELS_PERFORMANCE_REPORT.md     # 完整报告
├── v100_all_models_performance.json          # 完整JSON数据
└── performance/
    ├── {model_name}_perf.json                # 单个模型数据
    └── ...
```

---

## 8. 测试脚本

**主脚本**: `benchmark_all_models.py`

**使用方法**:
```bash
# 激活环境
source ~/venvs/model_tools/bin/activate

# 运行测试
python3 benchmark_all_models.py

# 后台运行
python3 benchmark_all_models.py > logs/benchmark_$(date +%Y%m%d).log 2>&1 &
```

---

## 9. 预期结果

### 9.1 速度预期 (基于 V100 性能)

| 模型大小 | 预期预填充 | 预期生成 |
|----------|-----------|----------|
| < 1B | 800-1500 t/s | 60-100 t/s |
| 4B | 600-1000 t/s | 40-70 t/s |
| 8B | 400-800 t/s | 30-50 t/s |

### 9.2 Context 支持预期

| 显存占用 | 最大 Context |
|----------|-------------|
| < 5GB | 32K-64K |
| 5-10GB | 16K-32K |
| > 10GB | 8K-16K |

---

## 10. 注意事项

1. **显存限制**: V100 32GB，测试大 Context 时注意 OOM
2. **超时设置**: 128K context 测试可能需要 >300s 超时
3. **模型切换**: 每次测试前确保模型已正确加载
4. **温度设置**: 使用 temperature=0.1 保证输出一致性
5. **测试顺序**: 建议从大到小测试，避免重复加载

---

*文档版本: 1.0*
*最后更新: 2026-02-17*
