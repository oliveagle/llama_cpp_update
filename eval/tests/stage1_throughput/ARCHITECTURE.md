# Stage 1 吞吐量/性能测试框架架构

## 设计目标

- **多后端支持**: Vulkan(gfx1151), CUDA(V100), ROCm等
- **模型调优**: 通用配置 + 按模型调优配置
- **代码复用**: 基础类共享，后端特定逻辑分离
- **标准化输出**: JSONL格式原始数据 + Markdown报告

## 目录结构

```
stage1_throughput/
├── ARCHITECTURE.md          # 本文档
├── config/                  # 配置目录
│   ├── backends/           # 后端配置
│   │   ├── vulkan_gfx1151.yaml
│   │   ├── v100_cuda.yaml
│   │   └── rocm_gfx1030.yaml
│   └── models/             # 模型调优配置
│       ├── _default.yaml   # 默认配置
│       ├── qwen3-4b.yaml
│       ├── glm-4.7-flash.yaml
│       └── ...
├── core/                   # 核心代码（复用层）
│   ├── __init__.py
│   ├── base_evaluator.py   # 基础评估器
│   ├── metrics.py          # 指标计算
│   ├── data_logger.py      # JSONL数据记录
│   └── report_generator.py # 报告生成
├── tests/                  # 具体测试项
│   ├── __init__.py
│   ├── test_prompt_processing.py  # 提示处理速度
│   ├── test_token_generation.py   # Token生成速度
│   ├── test_context_scaling.py    # Context扩展
│   └── test_batch_inference.py    # 批量推理
├── runners/                # 后端特定运行器
│   ├── __init__.py
│   ├── vulkan_runner.py
│   ├── cuda_runner.py
│   └── base_runner.py
├── results/                # 测试结果目录
│   ├── raw/               # JSONL原始数据
│   │   ├── vulkan_gfx1151_20250218_120000.jsonl
│   │   └── v100_cuda_20250218_130000.jsonl
│   └── reports/           # Markdown报告
│       ├── V100_STAGE1_BENCHMARK_REPORT.md
│       └── GFX1151_STAGE1_BENCHMARK_REPORT.md
├── scripts/                # 便捷脚本
│   ├── run_vulkan_all.sh
│   ├── run_v100_all.sh
│   └── run_single_model.sh
└── requirements.txt

## 文件命名规范

### 1. 配置文件
- 后端配置: `{backend}_{device}.yaml` → `vulkan_gfx1151.yaml`, `v100_cuda.yaml`
- 模型配置: `{model_family}_{size}.yaml` → `qwen3_4b.yaml`, `glm4_9b.yaml`

### 2. 测试数据 (JSONL)
- 原始数据: `{backend}_{device}_{timestamp}.jsonl`
- 示例: `v100_cuda_20250218_143022.jsonl`

### 3. 汇总数据
- 按模型: `{model_id}_{backend}_{timestamp}_summary.json`
- 示例: `qwen3-4b_v100_20250218_143022_summary.json`

### 4. 报告文件
- 后端报告: `{BACKEND}_STAGE1_BENCHMARK_REPORT.md`
- 跨后端对比: `CROSS_BACKEND_STAGE1_COMPARISON.md`
- 模型专项: `{MODEL}_STAGE1_ANALYSIS.md`

## JSONL数据格式标准

```json
{
  "timestamp": "2026-02-18T14:30:22.123456",
  "backend": {
    "type": "cuda",
    "device": "V100",
    "compute_capability": "7.0"
  },
  "model": {
    "id": "Qwen3-4B-Instruct",
    "gguf_file": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf",
    "quantization": "Q4_K_XL",
    "parameters": "4B"
  },
  "test_config": {
    "prompt_length": 4096,
    "max_tokens": 512,
    "temperature": 0.7,
    "ngl": 99,
    "n_ctx": 32768
  },
  "test_type": "token_generation",
  "metrics": {
    "prompt_tokens": 4096,
    "completion_tokens": 512,
    "total_tokens": 4608,
    "prompt_processing_time_ms": 245.6,
    "generation_time_ms": 8234.2,
    "total_time_ms": 8479.8,
    "prompt_tokens_per_second": 16675.1,
    "generation_tokens_per_second": 62.2,
    "total_tokens_per_second": 543.0
  },
  "raw_response": {
    "timings": {
      "prompt_n": 4096,
      "prompt_ms": 245.6,
      "predicted_n": 512,
      "predicted_ms": 8234.2
    }
  }
}
```

## 配置继承体系

```yaml
# backends/v100_cuda.yaml
backend:
  type: cuda
  device: V100
  compute_capability: "7.0"
  memory_gb: 32

defaults:
  n_ctx: 32768
  ngl: 99
  n_batch: 512

test_suites:
  prompt_processing:
    prompt_lengths: [512, 1024, 2048, 4096, 8192, 16384, 32768]
    max_tokens: 1

  token_generation:
    prompt_length: 1024
    max_tokens_list: [256, 512, 1024, 2048]

  context_scaling:
    base_context: 4096
    max_context: 131072
    step_multiplier: 2
```

```yaml
# models/qwen3_4b.yaml
extends: backends/v100_cuda.yaml

model:
  family: qwen3
  name: Qwen3-4B-Instruct
  context_training: 32768

# 模型特定调优
optimized_params:
  temperature: 0.6
  top_p: 0.9
  repeat_penalty: 1.05

# 该模型在V100上的特殊配置
v100_specific:
  ngl: 99  # 可以全部 offload
  n_ctx: 32768  # 最大支持 context
```

## 测试项定义

| 测试项 | 文件 | 指标 |
|--------|------|------|
| 提示处理速度 | test_prompt_processing.py | tokens/second (prefill) |
| Token生成速度 | test_token_generation.py | tokens/second (generation) |
| Context扩展 | test_context_scaling.py | 最大有效context |
| 批量推理 | test_batch_inference.py | throughput (requests/sec) |
| 内存使用 | test_memory_usage.py | VRAM usage pattern |

## 代码复用架构

```python
# core/base_evaluator.py
class Stage1Evaluator(ABC):
    """Stage 1 基础评估器"""

    def __init__(self, backend_config, model_config):
        self.backend = backend_config
        self.model = model_config
        self.logger = DataLogger()

    @abstractmethod
    def setup_server(self):
        """后端特定的服务器启动"""
        pass

    def run_test(self, test_type: str, params: dict):
        """通用测试执行流程"""
        # 1. 准备测试
        self._prepare(test_type, params)

        # 2. 执行测试（后端特定）
        result = self._execute(params)

        # 3. 记录数据（通用）
        self.logger.log(result)

        # 4. 计算指标（通用）
        metrics = self._calculate_metrics(result)

        return metrics

# runners/vulkan_runner.py
class VulkanRunner(Stage1Evaluator):
    def setup_server(self):
        # Vulkan 特定的服务器启动逻辑
        pass

# runners/cuda_runner.py
class CudaRunner(Stage1Evaluator):
    def setup_server(self):
        # CUDA 特定的服务器启动逻辑
        pass
```

## 报告生成流程

1. **原始数据收集** → JSONL文件
2. **数据聚合** → 按模型/后端统计
3. **指标计算** → 平均/最大/最小/std
4. **可视化数据** → 图表数据准备
5. **报告渲染** → Markdown生成
