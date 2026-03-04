# llama.cpp 评估系统 v2.1

> **创建时间**: 2026-03-04
> **架构版本**: v2.1
> **状态**: ✅ 已完成 (已整理)

---

## 快速开始

### 统一入口

```bash
cd /mnt/volume3/llama_cpp/eval

# 查看所有命令
python3 run.py --help

# Stage 1 - 性能测试
python3 run.py stage1 --model Qwen3-0.6B

# Stage 2 - 基础能力
python3 run.py stage2 --model JoyAI-LLM-Flash

# Stage 3 - 深度能力
python3 run.py stage3 --model GLM-4.7-Flash

# 完整评估
python3 run.py all --model Qwen3-4B

# 查看排行榜
python3 run.py leaderboard
```

---

## 架构概览

```
三层评估体系:

Stage 1 (性能基准)
├─ 预填充速度 (tokens/s)
├─ 生成速度 (tokens/s)
└─ Context 缩放测试

Stage 2 (基础能力 - 30 cases)
├─ 基础对话 (4)
├─ 代码能力 (6)
├─ 逻辑推理 (5)
├─ 角色扮演 (3)
├─ 知识问答 (4)
├─ 创意写作 (2)
├─ 多轮对话 (2)
├─ 格式化输出 (2)
├─ 安全测试 (1)
└─ 长文本理解 (1)

Stage 3 (深度能力)
├─ 工具调用
├─ 复杂任务规划
└─ 代码解释
```

---

## 目录结构

```
eval/
├── run.py                      # ⭐ 统一入口
├── config.py                   # ⭐ 系统配置
├── verify_architecture.py      # 架构验证脚本
│
├── framework/                  # 核心框架
│   ├── base.py                # 基础类
│   ├── runner.py              # 执行器
│   ├── report.py              # 报告生成
│   └── __init__.py
│
├── tests/                      # 测试脚本
│   ├── stage1/                # 性能测试
│   │   ├── performance_test.py
│   │   ├── test_context_*.py
│   │   └── test_*_stage1.py
│   ├── stage2/                # 基础能力
│   │   ├── capability_test.py
│   │   └── capability_test_v2.py
│   └── stage3/                # 深度能力
│       ├── eval_tools_capability.py
│       ├── eval_linux_ops*.py
│       ├── linux_ops_*.py
│       ├── test_*_stage3.py
│       └── run_v100_tool_test_all_models.py
│
├── results/                    # ⭐ 结果输出
│   ├── stage1/
│   ├── stage2/
│   ├── stage3/
│   └── capabilities/          # 能力评测结果
│       ├── knowledge/         # 知识问答结果
│       ├── multiturn/         # 多轮对话结果
│       ├── reasoning/         # 推理能力结果
│       └── safety/            # 安全测试结果
│
├── tools/                      # 评估工具 ⭐ 新增
│   ├── eval_llm.py
│   ├── eval_model.py
│   ├── eval_all_capabilities.py
│   ├── eval_joyai_*.py
│   ├── run_all_evals.py
│   ├── run_context_test.py
│   ├── benchmark_all_models.py
│   └── bench_*.py
│
├── eval_results/               # 评估报告
│   └── MODEL_LEADERBOARD.md
│
├── docs/                       # 文档
│   └── eval-architecture.md
│
├── frameworks/                 # 第三方框架
│   └── LiveCodeBench/
│
├── model_configs/              # 模型配置
│   ├── qwen3.py
│   ├── joyai_llm_flash.py
│   └── glm4.py
│
└── utils/                      # 工具函数
    └── context_predictor.py
```

---

## 配置说明

### API 地址

| 实例 | 端口 | 命令 |
|------|------|------|
| Vulkan (AMD) | 8400 | `--url http://localhost:8400` |
| CUDA (V100) | 8401 | `--url http://localhost:8401` |
| Embedding | 13232 | `--url http://localhost:13232` |

### 通过门槛

| Stage | 门槛 | 说明 |
|-------|------|------|
| Stage 1 | N/A | 性能测试无门槛 |
| Stage 2 | 60% | 基础能力 60% 通过率 |
| Stage 3 | 50% | 深度能力 50% 通过率 |

---

## 输出格式

### JSON 结果

保存在 `results/stage{1,2,3}/`:

```json
{
  "model": "Qwen3-0.6B",
  "timestamp": "2026-03-04T15:00:00",
  "stage": 1,
  "results": {
    "prefill_speed": 3500,
    "generation_speed": 38
  }
}
```

### Markdown 报告

保存在 `eval_results/`:

- `MODEL_LEADERBOARD.md` - 模型排行榜
- `{model}_evaluation_{timestamp}.md` - 单个模型报告

---

## 验证架构

```bash
cd /mnt/volume3/llama_cpp/eval
python3 verify_architecture.py
```

预期输出：
```
✅ 所有检查通过!
✅ 架构验证完成 - 一切正常!
```

---

## 相关文件

- [架构文档](./docs/eval-architecture.md) - 详细架构说明
- [模型排行榜](./eval_results/MODEL_LEADERBOARD.md) - 性能排名
- [黄金标杆](./golden_benchmarks.py) - 基准定义

---

## 变更历史

### v2.1 (2026-03-04 整理)

**目录整理**:
- ✅ 移动 `knowledge/` → `results/capabilities/knowledge/`
- ✅ 移动 `multiturn/` → `results/capabilities/multiturn/`
- ✅ 移动 `reasoning/` → `results/capabilities/reasoning/`
- ✅ 移动 `safety/` → `results/capabilities/safety/`
- ✅ 移动 Context 测试 → `tests/stage1/`
- ✅ 移动 Linux ops 脚本 → `tests/stage3/`
- ✅ 移动 eval 脚本 → `tools/`
- ✅ 移动 run 脚本 → `tools/`

**根目录精简**:
- 从 21 个 .py 文件 → 6 个核心文件
- 保留：`run.py`, `config.py`, `golden_benchmarks.py`, `verify_architecture.py`

### v2.0 (2026-03-04)

**新增**:
- ✅ 统一入口 `run.py`
- ✅ 配置模块 `config.py`
- ✅ 标准化输出目录 `results/stage{1,2,3}/`
- ✅ 架构验证脚本
- ✅ 完整文档

**改进**:
- ✅ 测试脚本整合到 `tests/` 目录
- ✅ 框架类导出优化
- ✅ Stage 1 性能测试模块化

### v1.0 (2026-02-18)

- 初始三层评估体系
- 基础框架实现

---

*最后更新：2026-03-04*
