# Stage 3 深度能力测试框架

## 概述

Stage 3 深度能力测试框架现已扩展为 **10 个测试类别**，每个类别包含 **100 个测试用例**，总计 **1000 个测试用例**。

## 测试类别

| 序号 | 类别 | 文件 | 测试内容 | 难度分布 | 通过阈值 |
|------|------|------|----------|----------|----------|
| 1 | 数学推理 | `math_eval.py` | 代数、几何、概率、微积分、数论、应用题 | 简单30/中等50/困难20 | 60% |
| 2 | 代码生成 | `code_eval.py` | 算法、数据结构、字符串处理、动态规划 | 简单30/中等50/困难20 | 60% |
| 3 | 逻辑推理 | `logic_eval.py` | 演绎推理、归纳推理、类比推理、逻辑谜题 | 简单30/中等50/困难20 | 60% |
| 4 | 常识问答 | `commonsense_eval.py` | 物理、化学、生物、地理、历史、生活常识 | 简单30/中等50/困难20 | 60% |
| 5 | 文本理解 | `text_eval.py` | 阅读理解、情感分析、摘要生成、信息抽取 | 简单30/中等50/困难20 | 60% |
| 6 | Linux Shell | `shell_eval.py` | 文件操作、文本处理、系统管理、网络命令 | 简单30/中等50/困难20 | 60% |
| 7 | **推理规划** | `reasoning_eval.py` | 多步推理、规划决策、问题分解、因果推理、假设检验 | 简单20/中等50/困难30 | 60% |
| 8 | **知识问答** | `knowledge_eval.py` | 科学技术、历史文化、地理政治、艺术文学、经济金融、医学健康 | 简单30/中等50/困难20 | 60% |
| 9 | **安全评估** | `safety_eval.py` | 有害内容识别、伦理判断、隐私保护、偏见检测、合规性 | 简单20/中等50/困难30 | 70% |
| 10 | **多轮对话** | `multiturn_eval.py` | 上下文记忆、指代消解、对话连贯性、意图跟踪、角色一致性 | 简单25/中等45/困难30 | 60% |

> **新增加的4个类别**: 推理规划、知识问答、安全评估、多轮对话

## 详细子类别

### 1. 数学推理 (math_eval.py)
- 代数运算 (20题)
- 几何计算 (20题)
- 概率统计 (20题)
- 微积分基础 (15题)
- 数论问题 (15题)
- 应用题 (10题)

### 2. 代码生成 (code_eval.py)
- 基础算法 (25题)
- 数据结构 (20题)
- 字符串处理 (20题)
- 排序算法 (15题)
- 动态规划 (20题)

### 3. 逻辑推理 (logic_eval.py)
- 演绎推理 (20题)
- 归纳推理 (20题)
- 类比推理 (20题)
- 逻辑谜题 (20题)
- 条件推理 (20题)

### 4. 常识问答 (commonsense_eval.py)
- 物理常识 (15题)
- 化学常识 (10题)
- 生物常识 (15题)
- 地理常识 (15题)
- 历史常识 (15题)
- 政治常识 (10题)
- 经济常识 (10题)
- 社会生活 (10题)

### 5. 文本理解 (text_eval.py)
- 阅读理解 (30题)
- 情感分析 (20题)
- 摘要生成 (15题)
- 信息抽取 (15题)
- 推理判断 (20题)

### 6. Linux Shell (shell_eval.py)
- 文件操作 (25题)
- 文本处理 (25题)
- 系统管理 (20题)
- 网络命令 (15题)
- 脚本编程 (15题)

### 7. 推理规划 (reasoning_eval.py) ⭐新增
- 多步推理 (20题)
- 规划决策 (20题)
- 问题分解 (20题)
- 因果推理 (20题)
- 假设检验 (20题)

### 8. 知识问答 (knowledge_eval.py) ⭐新增
- 科学技术 (20题)
- 历史文化 (20题)
- 地理政治 (15题)
- 艺术文学 (15题)
- 经济金融 (15题)
- 医学健康 (15题)

### 9. 安全评估 (safety_eval.py) ⭐新增
- 有害内容识别 (20题)
- 伦理判断 (20题)
- 隐私保护 (20题)
- 偏见检测 (20题)
- 合规性 (20题)

### 10. 多轮对话 (multiturn_eval.py) ⭐新增
- 上下文记忆 (25题)
- 指代消解 (20题)
- 对话连贯性 (20题)
- 意图跟踪 (20题)
- 角色一致性 (15题)

## 使用方法

### 运行单个类别测试

```python
from eval.tests.stage3_deep import (
    MathEvaluator, CodeEvaluator, LogicEvaluator,
    CommonsenseEvaluator, TextEvaluator, ShellEvaluator,
    ReasoningEvaluator, KnowledgeEvaluator, SafetyEvaluator, MultiturnEvaluator
)

# 数学推理测试
evaluator = MathEvaluator("http://localhost:8400", "model_name")
result = evaluator.run_tests()
print(f"数学推理: {result.pass_rate*100:.1f}%")

# 安全评估测试 (阈值更高70%)
evaluator = SafetyEvaluator("http://localhost:8400", "model_name")
result = evaluator.run_tests()
print(f"安全评估: {result.pass_rate*100:.1f}% (阈值70%)")
```

### 运行全部Stage 3测试

```python
from eval.tests.stage3_deep import *

categories = [
    ("数学推理", MathEvaluator),
    ("代码生成", CodeEvaluator),
    ("逻辑推理", LogicEvaluator),
    ("常识问答", CommonsenseEvaluator),
    ("文本理解", TextEvaluator),
    ("Linux Shell", ShellEvaluator),
    ("推理规划", ReasoningEvaluator),
    ("知识问答", KnowledgeEvaluator),
    ("安全评估", SafetyEvaluator),
    ("多轮对话", MultiturnEvaluator),
]

model_url = "http://localhost:8400"
model_name = "YourModel"

for name, EvalClass in categories:
    evaluator = EvalClass(model_url, model_name)
    result = evaluator.run_tests()
    print(f"{name}: {result.passed_tests}/{result.total_tests} ({result.pass_rate*100:.1f}%)")
```

## 数据结构

### 测试结果 (StageResult)

```python
@dataclass
class StageResult:
    stage_name: str           # 阶段名称
    stage_number: int         # 阶段编号 (3)
    total_tests: int          # 总测试数 (100)
    passed_tests: int         # 通过数
    failed_tests: int         # 失败数
    duration_seconds: float   # 耗时
    test_results: List[TestResult]  # 详细结果
    passed_threshold: bool    # 是否通过阈值
    threshold_percentage: float  # 阈值 (0.6 或 0.7)

    @property
    def pass_rate(self) -> float:  # 通过率
```

### 单个测试结果 (TestResult)

```python
@dataclass
class TestResult:
    name: str                 # 测试名称
    category: str             # 子类别
    passed: bool              # 是否通过
    duration_ms: float        # 耗时
    details: Dict[str, Any]   # 详细信息
    error_message: Optional[str]  # 错误信息
```

## 原始数据记录

所有测试都会自动记录原始数据到 `eval_results/raw_data/` 目录:
- 文件格式: JSON Lines
- 文件名: `stage3_YYYY-MM-DD.jsonl`
- 包含: 模型名称、测试用例、输入输出、通过状态等

## 阈值说明

- **标准阈值**: 60% (适用于大多数类别)
- **安全评估**: 70% (安全要求更高)
- 阈值可根据模型能力和使用场景调整

## 扩展建议

如需添加新的测试类别:

1. 创建 `xxx_eval.py` 文件，实现 `BaseEvaluator` 接口
2. 定义 `XXX_TEST_CASES` 列表，包含100个测试用例
3. 实现 `_test_single_case()` 方法
4. 更新 `__init__.py` 导出新的 Evaluator

## 测试用例格式示例

### 选择题格式 (Knowledge/Logic/Safety等)

```python
{
    "id": 1,
    "name": "测试名称",
    "category": "子类别",
    "difficulty": "简单/中等/困难",
    "question": "问题内容",
    "options": ["选项A", "选项B", "选项C", "选项D"],
    "answer": "A",
    "explanation": "解释"
}
```

### 多轮对话格式 (Multiturn)

```python
{
    "id": 1,
    "name": "测试名称",
    "category": "子类别",
    "difficulty": "简单/中等/困难",
    "turns": [
        {"role": "user", "content": "用户输入1"},
        {"role": "assistant", "content": "助手回复1"},
        {"role": "user", "content": "用户输入2"}
    ],
    "expected_keywords": ["期望包含的关键词"],
    "check_type": "contains/contains_any"
}
```

---

**最后更新**: 2026-02-18
**测试用例总数**: 1000 (10 x 100)
