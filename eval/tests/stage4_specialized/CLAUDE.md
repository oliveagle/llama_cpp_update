# Stage 4 专项能力测试

## 目录结构

```
stage4_specialized/
├── STAGE4_FRAMEWORK.md          # 框架文档
├── CLAUDE.md                    # 配置文档
├── __init__.py                  # 模块导出
├── base.py                      # 基础评估器
├── utils.py                     # 通用工具 (shuffle_options 等) ⭐ 新增
├── run_stage4.py                # 主运行脚本
├── programming/                 # 编程能力测试 (1050+ 题)
│   ├── __init__.py
│   ├── base_syntax_eval.py      # 150 题 - Python 基础语法 (✅ 已优化)
│   ├── algorithm_eval.py        # 250 题 - 算法与数据结构 (✅ 已优化)
│   ├── system_design_eval.py    # 150 题 - 系统设计 (✅ 已优化)
│   ├── debugging_eval.py        # 150 题 - 代码调试 (✅ 已优化)
│   ├── engineering_eval.py      # 150 题 - 工程实践 (✅ 已优化)
│   ├── database_eval.py         # 150 题 - 数据库与 SQL (✅ 已优化)
│   ├── leetcode_eval.py         # LeetCode 编程题 (实际代码验证)
│   ├── multiturn_eval.py        # 多轮对话测试 (基础版)
│   └── multiturn_reasoning_eval.py  # 50 题 - 多轮对话推理 (增强版)
└── devops/                      # 运维能力测试 (1000 题，✅ 已全部优化)
    ├── __init__.py
    ├── linux_eval.py            # 200 题 - Linux 系统管理 (✅ 已优化)
    ├── container_eval.py        # 200 题 - 容器与编排 (✅ 已优化)
    ├── network_security_eval.py # 150 题 - 网络与安全 (✅ 已优化)
    ├── monitoring_eval.py       # 150 题 - 监控与日志 (✅ 已优化)
    ├── cicd_eval.py             # 150 题 - CI/CD 与自动化 (✅ 已优化)
    └── cloud_iac_eval.py        # 150 题 - 云服务与 IaC (✅ 已优化)
```

## 快速开始

### 生成所有题目

```bash
cd /mnt/volume3/llama_cpp/eval/tests/stage4_specialized

# 生成编程能力 1000 题
python3 run_stage4.py --type programming --generate-only

# 生成运维能力 1000 题
python3 run_stage4.py --type devops --generate-only

# 生成所有题目
python3 run_stage4.py --type all --generate-only
```

### 运行完整测试

```bash
# 运行编程能力测试 (1000 题)
python3 run_stage4.py --type programming

# 运行运维能力测试 (1000 题)
python3 run_stage4.py --type devops

# 运行所有测试 (2000 题)
python3 run_stage4.py --type all
```

### 运行单个子类别

```bash
cd /mnt/volume3/llama_cpp/eval/tests/stage4_specialized

# 编程子类别
python3 programming/base_syntax_eval.py
python3 programming/algorithm_eval.py
python3 programming/system_design_eval.py
python3 programming/debugging_eval.py
python3 programming/engineering_eval.py
python3 programming/database_eval.py
python3 programming/leetcode_eval.py           # LeetCode 编程题
python3 programming/multiturn_reasoning_eval.py --generate-only  # 多轮对话推理 (生成题目)
python3 programming/multiturn_reasoning_eval.py  # 多轮对话推理 (运行测试)

# 运维子类别
python3 devops/linux_eval.py
python3 devops/container_eval.py
python3 devops/network_security_eval.py
python3 devops/monitoring_eval.py
python3 devops/cicd_eval.py
python3 devops/cloud_iac_eval.py
```

## 选择题优化 (已完成 ✅)

**所有 16 个评估模块已全部添加选项打乱功能：**

### 编程能力 (6 个模块 ✅)
| 模块 | 题目数 | 答案分布验证 |
|------|--------|--------------|
| `base_syntax_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `algorithm_eval.py` | 250 | ✅ A:11, B:6, C:8, D:5 (已验证) |
| `system_design_eval.py` | 150 | ✅ A:6, B:9, C:5, D:10 (已验证) |
| `debugging_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `engineering_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `database_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |

### 运维能力 (6 个模块 ✅)
| 模块 | 题目数 | 答案分布验证 |
|------|--------|--------------|
| `linux_eval.py` | 200 | ✅ A:9, B:13, C:13, D:15 (已验证) |
| `container_eval.py` | 200 | ✅ A/B/C/D 均匀分布 |
| `network_security_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `monitoring_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `cicd_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |
| `cloud_iac_eval.py` | 150 | ✅ A/B/C/D 均匀分布 |

### 实现方式
每个模块通过 `utils.py` 中的 `shuffle_options()` 函数实现：
```python
from utils import shuffle_options

# 生成题目时
shuffled_opts, new_answer = shuffle_options(template)
# 选项被打乱，答案字母自动映射到新位置
```

### 新增多轮对话测试 (2 个模块)
| 模块 | 题目数 | 说明 |
|------|--------|------|
| `multiturn_eval.py` | 50+ | 基础版多轮对话测试 |
| `multiturn_reasoning_eval.py` | 50 | 增强版多轮对话推理 (13 个类别) |

## 题目分布

### 编程能力 (1050+ 题)

| 子类别 | 题目数 | 难度分布 | 题型 | 预计用时 |
|--------|--------|----------|------|----------|
| 基础语法 | 150 | 简单40%/中等45%/困难15% | 选择+代码 | 15 分钟 |
| 算法与数据结构 | 250 | 简单30%/中等50%/困难20% | 选择+代码 | 30 分钟 |
| 系统设计 | 150 | 简单30%/中等50%/困难20% | 选择+简答 | 15 分钟 |
| 代码调试 | 150 | 简单40%/中等40%/困难20% | 选择+改错 | 15 分钟 |
| 工程实践 | 150 | 简单35%/中等45%/困难20% | 选择+代码 | 15 分钟 |
| 数据库与 SQL | 150 | 简单35%/中等45%/困难20% | 选择+SQL | 15 分钟 |
| LeetCode 编程题 | 10+ | 简单30%/中等50%/困难20% | 实际代码验证 | 10 分钟 |
| 多轮对话推理 | 50 | 简单30%/中等50%/困难20% | 多轮对话 | 15 分钟 |
| **总计** | **1050+** | - | - | **~2.5 小时** |

### 选择题优化 (已验证)

✅ **选项打乱功能**: `algorithm_eval.py` 中的 `shuffle_options()` 函数确保每次生成题目时选项顺序随机打乱，答案均匀分布在 A/B/C/D

✅ **答案分布验证**: 实际测试显示答案分布均匀 (示例: A:11, B:6, C:8, D:5)

### 运维能力 (1000 题)

| 子类别 | 题目数 | 难度分布 | 预计用时 |
|--------|--------|----------|----------|
| Linux 系统管理 | 200 | 简单35%/中等45%/困难20% | 20 分钟 |
| 容器与编排 | 200 | 简单35%/中等45%/困难20% | 20 分钟 |
| 网络与安全 | 150 | 简单35%/中等45%/困难20% | 15 分钟 |
| 监控与日志 | 150 | 简单35%/中等45%/困难20% | 15 分钟 |
| CI/CD 与自动化 | 150 | 简单35%/中等45%/困难20% | 15 分钟 |
| 云服务与 IaC | 150 | 简单35%/中等45%/困难20% | 15 分钟 |
| **总计** | **1000** | - | **~2 小时** |

## 评估结果

评估结果保存在 `eval_results/stage4/` 目录:
- `raw_data/` - 原始测试数据 (JSONL)
- `*_questions.json` - 生成的题目
- `*_report.md` - Markdown 测试报告

## 通过率阈值

- **优秀**: >= 80%
- **良好**: >= 60%
- **需改进**: < 60%

## 命令行参数

```bash
python3 run_stage4.py [选项]

选项:
  --type {programming,devops,algorithm,all}  测试类型 (默认: all)
  --model-url URL                           模型 API 地址 (默认: http://localhost:8400)
  --model-name NAME                         模型名称 (默认: JoyAI-LLM-Flash-Q4_K_M)
  --output-dir DIR                          输出目录 (默认: eval_results/stage4)
  --generate-only                           只生成题目，不运行测试
```
