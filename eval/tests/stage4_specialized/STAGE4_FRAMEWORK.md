# Stage 4 专项能力测试框架

## 概述

Stage 4 专项能力测试是针对特定领域的深度评估，包含两个专项：

| 专项 | 题目数 | 测试时长 | 通过阈值 |
|------|--------|----------|----------|
| **编程能力** | 1000 题 | ~2 小时 | 60% |
| **运维能力 (DevOps/SRE)** | 1000 题 | ~2 小时 | 60% |

## 测试类别

### 编程能力测试 (Programming Ability Test)

| 子类别 | 题目数 | 难度分布 (E/M/H) | 题型 |
|--------|--------|-----------------|------|
| 基础语法 | 150 | 50/70/30 | 选择 + 代码生成 |
| 算法与数据结构 | 250 | 80/120/50 | 代码生成 |
| 系统设计 | 150 | 40/70/40 | 选择 + 简答 |
| 代码调试 | 150 | 60/60/30 | 选择 + 改错 |
| 工程实践 | 150 | 50/70/30 | 选择 + 代码生成 |
| 数据库与 SQL | 150 | 60/60/30 | 选择 + SQL 编写 |

### 运维能力测试 (DevOps/SRE Ability Test)

| 子类别 | 题目数 | 难度分布 (E/M/H) | 题型 |
|--------|--------|-----------------|------|
| Linux 系统管理 | 200 | 70/90/40 | 选择 + 命令编写 |
| 容器与编排 | 200 | 60/100/40 | 选择 + YAML 编写 |
| 网络与安全 | 150 | 50/70/30 | 选择 + 配置编写 |
| 监控与日志 | 150 | 50/70/30 | 选择 + 查询编写 |
| CI/CD 与自动化 | 150 | 50/70/30 | 选择 + Pipeline 编写 |
| 云服务与 IaC | 150 | 50/70/30 | 选择 + Terraform |

## 使用方法

### 运行编程能力测试

```python
from eval.tests.stage4_specialized.programming import ProgrammingEvaluator

evaluator = ProgrammingEvaluator(
    model_url="http://localhost:8400",
    model_name="JoyAI-LLM-Flash-Q4_K_M"
)
result = evaluator.run_tests()
print(f"编程能力：{result.pass_rate*100:.1f}%")
```

### 运行运维能力测试

```python
from eval.tests.stage4_specialized.devops import DevOpsEvaluator

evaluator = DevOpsEvaluator(
    model_url="http://localhost:8400",
    model_name="JoyAI-LLM-Flash-Q4_K_M"
)
result = evaluator.run_tests()
print(f"运维能力：{result.pass_rate*100:.1f}%")
```

### 运行单个子类别测试

```python
# 只测试算法部分
from eval.tests.stage4_specialized.programming.algorithm_eval import run_algorithm_test

result = run_algorithm_test(
    model_url="http://localhost:8400",
    model_name="JoyAI-LLM-Flash-Q4_K_M"
)
```

## 数据结构

### 测试用例格式

**选择题格式**:
```python
{
    "id": 1,
    "name": "测试名称",
    "category": "子类别",
    "difficulty": "简单/中等/困难",
    "question": "问题内容",
    "options": ["选项 A", "选项 B", "选项 C", "选项 D"],
    "answer": "A",
    "explanation": "解释说明"
}
```

**代码生成格式**:
```python
{
    "id": 1,
    "name": "两数之和",
    "category": "基础算法",
    "difficulty": "简单",
    "prompt": "def two_sum(nums: list[int], target: int) -> list[int]:\n    '''...'''",
    "test_cases": [
        {"input": [[2,7,11,15], 9], "expected": [0,1]}
    ],
    "keywords": ["def", "return"]
}
```

## 评分标准

- **选择题**: 答案完全匹配
- **代码题**: 通过所有测试用例
- **关键词匹配**: 包含预期关键词

## 输出文件

测试结果保存在 `eval_results/stage4/`:
- `raw_data/` - 原始 JSONL 数据
- `programming/` - 编程测试结果
- `devops/` - 运维测试结果

---

*最后更新*: 2026-02-24
*题目总数*: 2000 (编程 1000 + 运维 1000)
