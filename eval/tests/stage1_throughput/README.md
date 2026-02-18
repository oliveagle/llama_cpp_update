# Stage 1 吞吐量测试框架

标准化的 llama.cpp 性能测试框架，支持多后端（Vulkan、CUDA、ROCm），
提供代码复用、配置继承和标准化报告生成。

## 架构概览

```
stage1_throughput/
├── core/                       # 核心模块（代码复用）
│   ├── base_evaluator.py      # 抽象基类，定义通用测试流程
│   ├── metrics.py             # 统计计算（mean, std, p95, p99）
│   ├── data_logger.py         # JSONL 数据记录
│   └── report_generator.py    # Markdown 报告生成
├── runners/                    # 后端特定实现
│   ├── vulkan_runner.py       # Vulkan/gfx1151 运行器
│   ├── cuda_runner.py         # CUDA/V100 运行器
│   └── rocm_runner.py         # ROCm/gfx1151 运行器
├── config/                     # 配置管理
│   ├── backends/              # 后端配置
│   │   ├── vulkan_gfx1151.yaml
│   │   ├── v100_cuda.yaml
│   │   └── rocm_gfx1151.yaml
│   └── models/                # 模型配置
│       ├── generic.yaml       # 通用默认配置
│       ├── minicpm-o-4_5.yaml
│       ├── glm-4-9b.yaml
│       └── ...
├── tests/                      # 分项测试脚本
│   ├── test_prompt_processing.py
│   ├── test_token_generation.py
│   └── test_context_scaling.py
├── scripts/                    # 便捷脚本
│   ├── run_all_tests.py       # 批量运行所有测试
│   └── generate_report.py     # 报告生成
└── results/                    # 结果输出
    ├── raw/                   # JSONL 原始数据
    └── *.md                   # Markdown 报告
```

## 配置系统

### 三级配置继承

1. **通用配置** (`config/models/generic.yaml`)
   - 所有模型的基础默认配置
   - 测试参数默认值

2. **后端配置** (`config/backends/*.yaml`)
   - 服务器二进制路径
   - 环境变量
   - 端口和默认参数

3. **模型配置** (`config/models/*.yaml`)
   - 模型特定的参数覆盖
   - 各后端调优参数

### 配置覆盖示例

```yaml
# models/minicpm-o-4_5.yaml
model:
  id: "MiniCPM-o-4.5"
  backend_overrides:
    vulkan:
      ngl: 80           # Vulkan 使用较少的 GPU 层数
      chat_template: "minicpm-v"
    cuda:
      ngl: 99           # CUDA 使用全部 GPU 层
      chat_template: "minicpm-v"
```

## 使用方式

### 1. 单个测试

```bash
# Prompt 处理速度测试
python tests/test_prompt_processing.py --backend vulkan --model-id minicpm-o-4_5

# Token 生成速度测试
python tests/test_token_generation.py --backend cuda --model-id glm-4-9b --iterations 5

# Context 扩展测试
python tests/test_context_scaling.py --backend cuda --model-id qwen2-5-7b
```

### 2. 批量测试

```bash
# 测试单个模型的所有项目
python scripts/run_all_tests.py --backend vulkan --model-id minicpm-o-4_5

# 测试多个模型
python scripts/run_all_tests.py --backend cuda --models minicpm-o-4_5 glm-4-9b qwen2-5-7b
```

### 3. 生成报告

```bash
# 从最新数据生成报告
python scripts/generate_report.py --backend cuda

# 从指定文件生成报告
python scripts/generate_report.py --data-file results/raw/cuda_V100_20250218_120000.jsonl
```

## 输出格式

### JSONL 原始数据

文件名格式: `{backend}_{device}_{timestamp}.jsonl`

```json
{
  "timestamp": "2025-02-18T12:00:00",
  "backend_type": "cuda",
  "device": "V100",
  "model_id": "MiniCPM-o-4.5",
  "test_type": "prompt_processing",
  "metrics": {
    "prompt_tokens_per_second": 150.5,
    "generation_tokens_per_second": 45.2,
    "total_tokens_per_second": 52.8
  },
  "_meta": {
    "record_id": 0,
    "logged_at": "2025-02-18T12:00:00",
    "backend_type": "cuda",
    "device": "V100"
  }
}
```

### Markdown 报告

文件名格式: `{BACKEND}_{DEVICE}_STAGE1_BENCHMARK_REPORT.md`

包含内容:
- 模型性能排名（按 TPS 排序）
- 详细指标统计（mean ± std）
- 测试元信息

## 扩展指南

### 添加新后端

1. 创建 `config/backends/{backend}_{device}.yaml`
2. 实现 `runners/{backend}_runner.py` 继承 `Stage1Evaluator`
3. 在 `runners/__init__.py` 中导出

### 添加新模型

创建 `config/models/{model_id}.yaml`:

```yaml
model:
  id: "Model-Name"
  gguf_pattern: "*Model*Q4_K_M.gguf"
  backend_overrides:
    vulkan:
      ngl: 99
    cuda:
      ngl: 99
```

### 添加新测试类型

1. 在 `base_evaluator.py` 中实现 `_test_{type}` 方法
2. 创建 `tests/test_{type}.py` 脚本
3. 在 `run_all_tests.py` 中添加

## 设计原则

1. **代码复用**: 通过抽象基类共享测试逻辑
2. **配置驱动**: 行为由 YAML 配置控制，非硬编码
3. **标准格式**: JSONL 数据 + Markdown 报告
4. **文件命名**: 文件名体现后端和设备信息
5. **可扩展**: 易于添加新后端、模型、测试类型
