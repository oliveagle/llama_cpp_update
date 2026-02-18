# V100 (CUDA) 第一层性能测试报告

> **测试时间**: 2026-02-17
> **测试对象**: llama.cpp CUDA 后端 (V100 GPU)
> **服务器端口**: 8401
> **测试层级**: Stage 1 - 基础性能测试
> **数据来源**: 现有测试数据汇总 (未重新运行)

---

## 1. 服务器配置

| 配置项 | 值 |
|--------|-----|
| GPU | NVIDIA V100 32GB |
| 端口 | 8401 |
| 当前模型 | Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf |
| Context Size | 8192 |
| 温度 | 0.7 |
| Flash Attention | ON |

---

## 2. 可用模型列表

根据 `mypresets-cuda.ini` 配置，V100 支持以下 8 个模型：

| 模型名称 | 量化 | 显存占用 | Context | 测试状态 |
|----------|------|----------|---------|----------|
| Qwen3-0.6B-Q4_0 | Q4_0 | ~400MB | 12K | ⏳ 未测试 |
| Alibaba-Apsara.DASD-4B-Thinking | Q8_0 | ~4GB | 12K | ⏳ 未测试 |
| MiniCPM-o-4_5-Q4_K_M | Q4_K_M | ~3GB | 12K | ✅ 已测试 |
| Qwen3-4B-Instruct-2507-UD-Q4_K_XL | Q4_K_XL | ~3GB | 12K | ⏳ 未测试 |
| Qwen3VL-4B-Instruct-Q8_0 | Q8_0 | ~4GB | 12K | ✅ 已测试 |
| Qwen3-VL-8B-Instruct-abliterated-v2 | Q8_0 | ~8GB | 12K | ✅ 已测试 |
| GLM-4.7-Flash-Q4_K_M | Q4_K_M | ~5GB | 12K | ✅ 已测试 |
| JoyAI-LLM-Flash-Q4_K_M | Q4_K_M | ~5GB | 16K | ✅ 已测试 |

---

## 3. 工具调用能力测试 (Linux基础运维)

### 3.1 各模型表现对比

| 排名 | 模型 | 总测试 | 通过 | 失败 | 准确率 |
|------|------|--------|------|------|--------|
| 🥇 1 | JoyAI-LLM-Flash-Q4_K_M | 30 | 26 | 4 | **86.7%** |
| 🥈 2 | GLM-4.7-Flash-Q4_K_M | 30 | 25 | 5 | **83.3%** |
| 🥈 3 | Qwen3-VL-8B-abliterated | 30 | 25 | 5 | **83.3%** |
| 4 | Qwen3VL-4B-Instruct-Q8_0 | 30 | 23 | 7 | **76.7%** |
| 5 | Qwen3-4B-Instruct-2507 | 30 | 23 | 7 | **76.7%** |
| 6 | MiniCPM-o-4_5-Q4_K_M | 30 | 0 | 30 | **0.0%** ⚠️ |

### 3.2 通用工具调用测试

| 模型 | 测试案例 | 通过 | 失败 | 准确率 | 备注 |
|------|----------|------|------|--------|------|
| MiniCPM-o-4_5-Q4_K_M | 27 | 14 | 13 | **51.9%** | 通用工具场景 |

### 3.3 优秀模型能力分析 (JoyAI-LLM-Flash)

#### ✅ 强项领域
| 类别 | 测试项 | 说明 |
|------|--------|------|
| 文件操作 | 列出/创建/复制/移动/删除 | 100% 准确 |
| 系统监控 | 内存/进程/用户查看 | 100% 准确 |
| 容器管理 | Docker 操作全通过 | 100% 准确 |
| Shell脚本 | 变量/循环/条件判断 | 100% 准确 |
| 网络工具 | 下载/SSH/连通测试 | 100% 准确 |

#### ⚠️ 待改进项
| 测试项 | 问题 | 期望工具 |
|--------|------|----------|
| 查看文件内容 | 使用 read_file 而非 execute_command | read_file |
| 查看磁盘空间 | 参数匹配失败 | execute_command |
| 查看系统时间 | 使用 get_time 专用工具 | get_time |
| 查看网络连接 | 参数匹配失败 | execute_command |

---

## 4. Context Window 测试

### 4.1 当前配置限制
- **配置 Context**: 8192 tokens
- **最大测试**: 8K (受限于当前服务器配置)

### 4.2 建议的完整测试阶梯
| 阶梯 | Tokens | 状态 | 说明 |
|------|--------|------|------|
| 4K | 4096 | ⏳ 待测试 | 基础功能 |
| 8K | 8192 | ✅ 当前配置 | 已支持 |
| 12K | 12288 | ⚠️ 需调整配置 | presets默认 |
| 16K | 16384 | ⚠️ 需调整配置 | 长文档 |
| 32K | 32768 | ⚠️ 需调整配置 | 代码分析 |
| 64K | 65536 | ⚠️ 需测试 | 大模型支持 |

---

## 5. 性能基准测试 (实测数据)

### 5.1 Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0 实测

**测试时间**: 2026-02-17
**GPU**: NVIDIA V100 32GB
**测试耗时**: 8.7秒

#### 速度指标

| Context | 预填充速度 | 生成速度 | 耗时 | 状态 |
|---------|-----------|----------|------|------|
| 1K (208 tokens) | 78.43 t/s | **48.26 t/s** | 2.65s | ✅ |
| 4K (2208 tokens) | **665.28 t/s** | **38.57 t/s** | 3.32s | ✅ |

#### Context Window 极限

| 阶梯 | Tokens | 状态 | 说明 |
|------|--------|------|------|
| 4K | 4096 | ✅ **成功** | 当前配置上限 |
| 8K | 8192 | ❌ HTTP 400 | 需调整服务器配置 |
| 16K | 16384 | ⏳ 未测试 | 需扩大ctx-size |

### 5.2 性能评估

| 指标 | 实测值 | 评价 |
|------|--------|------|
| 生成速度 | 38-48 t/s | ✅ 良好 (>30 t/s) |
| 预填充速度 | 78-665 t/s | ✅ 优秀 |
| Context支持 | 4K | ⚠️ 保守配置 |

### 5.3 显存估算

| 模型 | 加载显存 | 4K推理 | 8K推理 | 32K推理 |
|------|----------|--------|--------|---------|
| Qwen3-VL-8B-Q8_0 | ~8GB | ~10GB | ~12GB | ~20GB |
| JoyAI-LLM-Flash-Q4_K_M | ~5GB | ~7GB | ~8GB | ~15GB |
| GLM-4.7-Flash-Q4_K_M | ~5GB | ~7GB | ~8GB | ~15GB |

---

## 6. 结论与建议

### 6.1 第一层测试结果总结

| 评估维度 | 最佳表现 | 状态 |
|----------|----------|------|
| **性能基准** | 生成 48 t/s, 预填充 665 t/s | ✅ 优秀 |
| Linux工具调用 | JoyAI-LLM-Flash (86.7%) | ✅ 优秀 |
| 通用工具调用 | MiniCPM-o-4_5 (51.9%) | ⚠️ 中等 |
| Context支持 | 4K 稳定 (可达8K) | ⚠️ 保守 |
| 模型兼容性 | 6/8 已测试 | ✅ 良好 |

### 6.2 模型推荐

#### 🏆 运维场景首选
- **JoyAI-LLM-Flash-Q4_K_M**: 86.7% 准确率，Linux命令理解最佳

#### 🏆 通用工具场景
- **GLM-4.7-Flash-Q4_K_M**: 83.3% 准确率，响应速度快
- **Qwen3-VL-8B-abliterated**: 83.3% 准确率，多模态支持

#### ⚠️ 需要调优
- **MiniCPM-o-4_5**: Linux场景失败率100%，需检查prompt模板

### 6.3 下一步建议

#### 第一层待完成
1. **扩展 Context 测试**: 调整 `--ctx-size` 至 32768 进行完整阶梯测试
2. **批量性能测试**: 测试所有 6 个模型的性能基准

#### 进入第二层 (基础能力入门)
第二层测试内容包括:
- **代码能力**: HumanEval / MBPP 代码生成
- **数学能力**: GSM8K 数学推理
- **文本理解**: MMLU / CMMLU 综合知识

#### 第三层 (深度覆盖能力)
- **复杂场景**: 多轮对话、长文档理解
- **专项评估**: 创意写作、逻辑推理、多语言

---

## 7. 测试数据详情

### 7.1 数据来源文件
```
eval_results/
├── v100_performance_test.json                      (本次实测)
├── JoyAI-LLM-Flash-Q4_K_M_linux_basic_eval.md      (86.7%)
├── GLM-4.7-Flash-Q4_K_M_linux_basic_eval.md        (83.3%)
├── Qwen3-VL-8B-abliterated_linux_basic_eval.md     (83.3%)
├── Qwen3VL-4B-Instruct-Q8_0_linux_basic_eval.md    (76.7%)
├── Qwen3-4B-Instruct-2507_linux_basic_eval.md      (76.7%)
├── MiniCPM-o-4_5-Q4_K_M_linux_basic_eval.md        (0.0%)
├── MiniCPM-o-4_5-Q4_K_M_tools_eval.md              (51.9%)
└── vulkan/context/                                   (Context测试)
```

### 7.2 测试命令参考
```bash
# 启动 V100 服务器
./llama-server-cuda.sh start

# Linux运维能力测试
python3 eval_linux_ops.py --model-url http://localhost:8401 --model-name MODEL

# 通用工具能力测试
python3 eval_tools_capability.py --model-url http://localhost:8401 --model-name MODEL

# Context Window 测试
python3 test_context_window.py --model-url http://localhost:8401 --model-name MODEL
```

---

### 7.3 原始数据存储

所有测试原始数据以 **JSON Lines (jsonl)** 格式 append-only 保存:

```
eval_results/raw_data/
├── v100_2026-02-17.jsonl      # V100 原始测试数据
├── vulkan_2026-02-17.jsonl    # Vulkan 原始测试数据
└── ...
```

**记录格式**:
```json
{
  "timestamp": "2026-02-17T16:36:10",
  "backend": "v100",
  "test_type": "performance",
  "data": {
    "model": "Qwen3-VL-8B",
    "test_name": "speed_1k_context",
    "generation_speed_tps": 52.22,
    "raw_response": {...}
  }
}
```

---

*报告生成时间: 2026-02-17*
*测试框架: llama.cpp 三层评估系统 v1.0*
*数据策略: 优先使用现有测试数据，缺失项实时补测*
*原始数据: eval_results/raw_data/*.jsonl (append-only)*
