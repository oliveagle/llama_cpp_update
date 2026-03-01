# Qwen3.5-35B-A3B-UD Stage 2 测试报告

> **测试时间**: 2026-02-26
> **模型**: Qwen3.5-35B-A3B-UD-Q4_K_XL
> **后端**: CUDA (V100 32GB)
> **llama.cpp**: b8134

---

## 测试摘要

| 测试类别 | 通过/总计 | 通过率 | 耗时(秒) | 状态 |
|----------|-----------|--------|----------|------|
| 💻 代码能力 | 8/10 | **80.0%** | 164.5 | ✅ 优秀 |
| 🔢 数学推理 | 0/10 | 0.0% | 82.5 | ⚠️ 需改进 |
| 📚 文本理解 | 2/10 | 20.0% | 12.0 | ⚠️ 需改进 |
| 🔧 工具使用 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 🧠 逻辑推理 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 🌍 知识问答 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 🌐 翻译能力 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 📝 摘要总结 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 🛡️ 安全合规 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |
| 💬 多轮对话 | 0/10 | 0.0% | 0.0 | ❌ 未完成 |

**总计**: 10/100 (10.0%)
**评级**: ⭐⭐ 需改进

---

## 详细分析

### ✅ 代码能力 (8/10)

通过测试:
- `has_close_elements` - 检查列表元素距离
- `truncate_number` - 截断小数
- `below_zero` - 检查余额是否低于零
- `intersperse` - 列表元素间插入分隔符
- `count_vowels` - 统计元音字母
- `remove_duplicates` - 移除重复元素
- `is_palindrome` - 检查回文
- `fibonacci` - 斐波那契数列

失败测试:
- `separate_paren_groups` - 括号分组分离
- `mean_absolute_derivative` - 平均绝对导数

**分析**: 代码能力表现优秀，模型能够理解编程任务并生成正确的 Python 代码。

---

### ⚠️ 数学推理 (0/10)

**问题**: 所有数学测试均失败

**示例问题**:
```
一个商店正在促销。买3件衬衫每件25元，或者买5件衬衫每件20元。
如果小明想买12件衬衫，最少需要多少钱？
预期答案: 245
```

**模型输出**:
```
Thinking Process:

1.  **Analyze the Request:**
    *   Role: Math assistant.
    *   Task: Solve a specific math problem.
    *   Constraint: Output *only* the final answer number.
    ...
```

**根本原因**:
1. Qwen3.5 是**推理模型**，会在回复中包含思考过程
2. 测试框架期望直接数字答案，无法正确解析 "Thinking Process" 格式
3. 答案提取逻辑失败，返回了错误的数值

---

### ⚠️ 服务器连接问题

**现象**: 工具使用及后续测试全部失败，错误信息:
```
HTTPConnectionPool(host='localhost', port=8402):
Max retries exceeded with url: /v1/chat/completions
Connection refused
```

**原因**: 测试过程中 llama-server 进程可能因超时或资源问题停止。

---

## 关键发现

### 1. 模型特性: 推理模型 (Thinking Model)

Qwen3.5-35B-A3B 在回复中包含思考过程:

```
<think>
1. Analyze the request...
2. Determine the logic...
3. Implement the solution...
</think>

最终答案
```

这与非推理模型（如 JoyAI-LLM-Flash）的直接回答方式不同。

### 2. 测试框架兼容性

当前 Stage 2 测试框架**未针对推理模型优化**:
- 答案提取正则表达式不匹配 thinking 格式
- 需要添加 `--reasoning-format` 支持或后处理逻辑

### 3. 代码能力验证

尽管存在格式问题，代码能力测试仍通过 8/10，证明:
- 模型编程能力较强
- 代码生成任务不受 thinking 格式影响（评分基于代码执行结果）

---

## 改进建议

### 1. 针对推理模型的测试改进

```python
# 在测试框架中添加 reasoning 格式解析
import re

def extract_answer(response):
    # 尝试提取 </think> 后的内容
    think_pattern = r'</think>\s*(.*)'
    match = re.search(think_pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response
```

### 2. llama-server 启动参数

使用 `--reasoning-format` 参数控制思考过程输出:

```bash
llama-server \
  --reasoning-format deepseek3 \
  # 或其他支持的格式
```

### 3. 重新测试

建议修复测试框架后重新运行完整测试，以获取准确的能力评估。

---

## 对比参考

| 模型 | 架构 | 代码能力 | 备注 |
|------|------|----------|------|
| Qwen3.5-35B-A3B | Qwen35MoE (Hybrid) | 80% | 推理模型，thinking 格式 |
| JoyAI-LLM-Flash | DeepSeek2 | ?% | 非推理模型，直接回答 |

*注: 由于测试框架兼容性问题，直接对比可能不公平*

---

## 原始数据

- JSON 结果: `Qwen3.5-35B-A3B-UD-Q4_K_XL_stage2.json`
- 测试脚本: `eval/scripts/stage2/run_stage2_qwen35.py`
- 服务器日志: `/tmp/qwen35_stage2_server.log`

---

*报告生成时间: 2026-02-26*
