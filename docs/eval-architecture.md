# llama.cpp eval 目录架构文档

## 目录概览

```
llama_cpp/eval/
├── 核心评估框架
│   ├── eval_all_capabilities.py        # 全能力评估入口
│   ├── eval_llm.py                     # LLM 基础评估
│   ├── eval_tools_capability.py        # Linux 工具调用评估
│   ├── eval_linux_ops.py              # Linux 操作评估
│   ├── eval_joyai_flash.py            # JoyAI Flash 评估
│   ├── eval_joyai_stage3.py           # JoyAI Stage 3 评估
│   ├── golden_benchmarks.py           # 金标准基准测试
│   ├── linux_ops_test_cases.py        # Linux 操作测试用例
│   ├── tools_test_cases_large.py      # 工具调用测试用例
│   ├── capability_test.py / _v2.py    # 能力测试
│   ├── batch_context_test.py          # 上下文测试
│   └── batch_test_models.sh           # 批处理测试脚本
│
├── 项目内部框架
│   ├── framework/                     # 内部评估框架
│   │   ├── base.py                    # 基础类
│   │   ├── runner.py                  # 运行器
│   │   ├── report.py                  # 报告生成
│   │   ├── __init__.py               # 框架入口
│   │   └── __pycache__               # 编译缓存
│   ├── lib/                          # 评估库
│   ├── config/                       # 配置文件
│   ├── model_configs/                # 模型配置
│   └── tests/                        # 单元测试
│
├── 外部标准测试框架
│   ├── frameworks/
│   │   ├── LiveCodeBench/             # LiveCodeBench 评测框架 (子模块)
│   │   │   ├── lcb_runner/            # LCB 运行器
│   │   │   │   ├── benchmarks/        # 基准测试
│   │   │   │   ├── evaluation/       # 评估逻辑
│   │   │   │   ├── prompts/          # 提示词
│   │   │   │   ├── runner/           # 运行器
│   │   │   │   └── utils/            # 工具
│   │   │   ├── assets/               # 资源文件
│   │   │   ├── poetry.lock           # Python 依赖
│   │   │   ├── pyproject.toml       # 项目配置
│   │   │   └── uv.lock              # UV 包管理器依赖
│   │   └── {LiveCodeBench}/          # 空占位目录
│
├── 评估结果与报告
│   ├── eval_results/                 # 评估结果输出
│   │   ├── capabilities/            # 能力评估输出
│   │   │   ├── knowledge/           # 知识库能力 (2026-03-03)
│   │   │   ├── multiturn/           # 多轮对话能力 (2026-03-03)
│   │   │   ├── reasoning/           # 推理能力 (2026-03-03)
│   │   │   └── safety/              # 安全能力 (2026-03-03)
│   │   ├── stage1/                 # Stage 1 测试结果
│   │   ├── stage2/                 # Stage 2 测试结果
│   │   ├── stage3/                 # Stage 3 测试结果
│   │   ├── stage4/                 # Stage 4 测试结果
│   │   ├── raw_data/               # 原始测试数据
│   │   └── joyai_flash/            # JoyAI Flash 专门结果
│   │
│   ├── logs/                       # 评估日志
│   ├── reports/                    # 最终报告
│   └── web/                        # Web 报告界面
│
├── 临时目录
├── knowledge/                      # 知识库能力 (2026-02-28) - 待整理
├── multiturn/                      # 多轮对话能力 (2026-02-28) - 待整理
└── reasoning/                      # 推理能力 (2026-02-28) - 待整理
```

## 核心评估框架说明

### 1. 主要评估脚本

| 文件 | 功能 |
|------|------|
| `eval_all_capabilities.py` | 全能力评估入口，整合所有能力维度 |
| `eval_llm.py` | LLM 基础能力评估，包括文本生成、理解等 |
| `eval_tools_capability.py` | 工具调用能力评估，重点测试 Linux 命令调用 |
| `eval_linux_ops.py` | Linux 操作能力测试，覆盖系统管理、文件操作等 |
| `eval_joyai_flash.py` | JoyAI Flash 模型专门优化测试 |
| `eval_joyai_stage3.py` | JoyAI Stage 3 专门测试 |

### 2. 测试用例库

| 文件 | 功能 |
|------|------|
| `linux_ops_test_cases.py` | 包含 300+ Linux 操作测试用例 |
| `tools_test_cases_large.py` | 包含大量工具调用测试用例 |
| `golden_benchmarks.py` | 金标准基准测试 |

### 3. 内部框架 (`framework/`)

```
eval/framework/
├── base.py           # 基础评估类和接口定义
├── runner.py         # 评估运行器，负责执行测试流程
└── report.py         # 报告生成器，负责格式化输出结果
```

## 外部标准测试框架

### LiveCodeBench (lcb_runner)

**位置**: `/mnt/volume3/llama_cpp/eval/frameworks/LiveCodeBench/`

LiveCodeBench 是一个专业的代码生成和代码执行评估框架，包含：

1. **评估维度**:
   - 代码生成 (Code Generation)
   - 代码执行 (Code Execution)
   - 测试输出预测 (Test Output Prediction)
   - 自我修复 (Self Repair)

2. **架构特点**:
   - 模块化架构，支持多种模型调用方式
   - 集成多种 LM 风格（Claude, Cohere, DeepSeek, Fireworks, Gemini, Grok, Mistral, OAI, Together, vLLM 等）
   - 支持少样本示例学习
   - 全面的评估指标和报告生成

3. **测试场景**:
   - 代码理解与生成
   - 测试驱动开发
   - 调试与优化
   - 系统设计

## 评估结果组织

### 能力评估输出 (`capabilities/`)

```
eval/eval_results/capabilities/
├── knowledge/         # 知识库能力 (2026-03-03)
│   └── stage3_2026-03-03.jsonl
├── multiturn/         # 多轮对话能力 (2026-03-03)
│   └── stage3_2026-03-03.jsonl
├── reasoning/         # 推理能力 (2026-03-03)
│   └── stage3_2026-03-03.jsonl
└── safety/            # 安全能力 (2026-03-03)
    └── stage3_2026-03-03.jsonl
```

### 按阶段组织的测试

| 阶段 | 内容 |
|------|------|
| **Stage 1** | 基础吞吐量、上下文大小测试，初步性能评估 |
| **Stage 2** | 基础能力测试，包括文本生成、理解等 |
| **Stage 3** | 深度能力测试，包括推理、多轮对话、知识库等 |
| **Stage 4** | 专项测试，如代码、安全、工具调用等 |

## 架构改进建议

### 1. 当前架构问题

1. **目录重复**: `/eval/` 根目录下的 `knowledge/`、`multiturn/`、`reasoning/` 与 `/eval/eval_results/capabilities/` 内容重复，但日期不同
2. **架构不一致**: 内部框架与外部框架（LiveCodeBench）并存，但集成度不够
3. **测试覆盖**: 缺少统一的测试规划和标准测试集使用策略

### 2. 优化建议

```
eval/
├── core/              # 核心评估框架
├── external/          # 外部标准测试框架
│   └── LiveCodeBench/
├── tests/             # 测试用例库
├── data/              # 原始测试数据
├── results/           # 评估结果
│   ├── capabilities/
│   ├── stages/
│   └── external/
├── reports/           # 最终报告
└── utils/             # 工具函数
```

## 使用外部测试框架的策略

### LiveCodeBench 集成方案

1. **保留作为外部框架**: 将 LiveCodeBench 作为专业的代码评估框架
2. **集成到内部框架**: 创建适配器，将 LCB 测试结果格式化为内部格式
3. **数据同步**: 定期同步 LCB 的评估结果到内部结果目录
4. **报告整合**: 在最终报告中整合 LCB 的评估数据

### 测试运行策略

1. **常规评估** - 使用内部框架进行快速评估
2. **专业代码评估** - 使用 LiveCodeBench 进行深度测试
3. **基准对比** - 同时使用两种框架，进行结果验证

## 下一步工作

1. 整理重复的评估结果目录
2. 增强外部框架的集成
3. 制定详细的测试计划，包括标准测试集使用
4. 优化结果存储和报告生成