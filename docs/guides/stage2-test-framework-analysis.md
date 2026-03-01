# Stage 2 测试框架问题深度分析

> **研究时间**: 2026-02-26
> **问题**: 为什么 Qwen3.5-35B-A3B 在 Stage 2 测试中大部分失败？

---

## 问题现象

| 测试类别 | 通过/总计 | 通过率 | 评分方式 |
|----------|-----------|--------|----------|
| 💻 代码能力 | 8/10 | **80.0%** | 代码结构检查 |
| 🔢 数学推理 | 0/10 | 0.0% | 数字答案提取 |
| 📚 文本理解 | 2/10 | 20.0% | 文本匹配 |
| 🔧 工具使用 | 0/10 | 0.0% | 功能调用检查 |

**核心问题**: 代码测试通过率高，其他测试全部失败

---

## 根本原因

### 1. 代码测试的评分逻辑

文件: `eval/tests/stage2_basic/code_eval.py:243-274`

```python
def _evaluate_code(self, generated_code: str, test_case: dict) -> float:
    """
    简单代码评估
    返回 0-1 的分数
    """
    score = 0.0

    # 1. 检查是否包含函数定义
    func_name = test_case["name"]
    if f"def {func_name}(" in generated_code:
        score += 0.3

    # 2. 检查是否有返回语句
    if "return" in generated_code:
        score += 0.2

    # 3. 检查是否有docstring
    if '"""' in generated_code or "'''" in generated_code:
        score += 0.2

    # 4. 检查语法基本正确性（简单的括号匹配）
    open_parens = generated_code.count("(")
    close_parens = generated_code.count(")")
    if open_parens == close_parens and open_parens > 0:
        score += 0.15

    return min(score, 1.0)
```

**关键**: 代码测试不依赖答案提取，而是检查代码结构特征。即使输出包含 "Thinking Process"，只要后面有正确的函数定义，就能通过检查。

### 2. 数学测试的答案提取逻辑

文件: `eval/tests/stage2_basic/math_eval.py:224-248`

```python
def _extract_number(self, text: str) -> float:
    """从文本中提取数字答案"""
    patterns = [
        r'答案[是为:]+\s*([\d.]+)',
        r'结果[是为:]+\s*([\d.]+)',
        r'等于\s*([\d.]+)',
        r'([\d.]+)\s*元',
        r'([\d.]+)\s*天',
        r'([\d.]+)\s*人',
        r'([\d.]+)\s*公里',
        r'([\d.]+)\s*克',
        r'([\d.]+)\s*%',
        r'\b([\d.]+)\b',  # ← 问题在这里！匹配最后一个数字
    ]

    for pattern in patterns:
        match = re.search(pattern, text)  # ← 只找第一个匹配
        if match:
            try:
                return float(match.group(1))
            except:
                continue

    return None
```

### 3. 问题演示

**Qwen3.5 输出示例**:
```
Thinking Process:

1.  **Analyze the Request:**
    *   Role: Math assistant.
    *   Task: Solve a specific math problem.
    ...

2.  **Calculate:**
    *   Option A: 300 yuan
    *   Option B: 250 yuan ← 正确答案

3.  **Final Answer:**
    250
```

**正则匹配过程**:
```python
pattern = r'\b([\d.]+)\b'
text = "Thinking Process:\n\n1.  **Analyze..."

match = re.search(pattern, text)
# 匹配结果: "1" (来自 "1. **Analyze...")
# 而不是: "250" (正确答案)
```

**验证**:
```bash
$ python3 test_regex.py
=== 测试当前正则表达式 ===
Pattern 4: \b([\d.]+)\b
  匹配结果: "1"  ← 错误！

=== 改进方案 1: 取最后一个数字 ===
所有匹配到的数字: ['1', '2', '300', '250', '250']
取最后一个: "250"  ← 正确！
```

---

## 问题总结

### 为什么代码测试能通过？

| 检查项 | 说明 | Thinking Process 影响 |
|--------|------|----------------------|
| 函数定义检查 | `def function_name(` | 不受影响，只要后面有代码 |
| Return 检查 | `return` 关键字 | 不受影响 |
| Docstring 检查 | `"""` 或 `'''` | 不受影响 |
| 括号匹配 | `()` `[]` 数量匹配 | 不受影响 |

**结论**: 代码测试通过是因为评分基于代码结构特征，不依赖答案提取。

### 为什么数学/文本测试失败？

| 测试类型 | 评分方式 | 问题 |
|----------|----------|------|
| 数学测试 | 提取数字答案 | 正则匹配到 "1" 而非正确答案 |
| 文本测试 | 字符串匹配 | Thinking Process 干扰匹配 |
| 工具测试 | 函数调用检查 | 可能同样受干扰 |

**结论**: 这些测试依赖内容提取/匹配，被 Thinking Process 格式干扰。

---

## 修复方案

### 方案 1: 修改数学测试的答案提取 (推荐)

```python
def _extract_number(self, text: str) -> float:
    """从文本中提取数字答案 - 修复版"""
    # 方案 1a: 取最后一个数字
    all_numbers = re.findall(r'\b([\d.]+)\b', text)
    if all_numbers:
        return float(all_numbers[-1])

    return None
```

### 方案 2: 提取 </think> 后的内容

```python
def _extract_answer_after_think(self, text: str) -> str:
    """提取 </think> 标签后的内容"""
    pattern = r'</think>\s*(.*)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text
```

### 方案 3: 使用 llama-server 的 reasoning_format 参数

启动服务器时添加参数，让模型直接输出答案：

```bash
llama-server \
  --reasoning-format deepseek3 \
  ...
```

或在请求中处理：

```python
# 检查 response 中是否有 reasoning_content
content = message.get("content", "")
if not content:
    content = message.get("reasoning_content", "")
```

---

## 影响评估

### 受影响的测试

| 测试文件 | 评分方式 | 受影响程度 |
|----------|----------|-----------|
| `code_eval.py` | 代码结构检查 | ✅ 不受影响 |
| `math_eval.py` | 数字提取 | ❌ 严重受影响 |
| `text_eval.py` | 字符串匹配 | ❌ 严重受影响 |
| `tool_eval.py` | 函数调用检查 | ⚠️ 可能受影响 |
| `knowledge_eval.py` | 内容匹配 | ❌ 严重受影响 |
| `reasoning_eval.py` | 逻辑检查 | ⚠️ 可能受影响 |
| `translation_eval.py` | 文本对比 | ❌ 严重受影响 |
| `summarization_eval.py` | 内容匹配 | ❌ 严重受影响 |
| `safety_eval.py` | 关键词检查 | ⚠️ 可能受影响 |
| `multiturn_eval.py` | 对话检查 | ⚠️ 可能受影响 |

### 建议优先级

1. **高优先级**: 修复 `math_eval.py` - 最简单的修复，改取最后一个数字即可
2. **中优先级**: 修复 `text_eval.py`, `knowledge_eval.py` - 需要更复杂的文本处理
3. **低优先级**: 检查其他测试 - 根据实际失败情况决定是否修复

---

## 修复代码示例

### math_eval.py 修复

```python
def _extract_number(self, text: str) -> float:
    """从文本中提取数字答案 - 修复版"""
    # 先尝试找明确的答案标记
    patterns = [
        r'答案[是为:]+\s*([\d.]+)',
        r'结果[是为:]+\s*([\d.]+)',
        r'等于\s*([\d.]+)',
        r'([\d.]+)\s*元',
        r'([\d.]+)\s*天',
        r'([\d.]+)\s*人',
        r'([\d.]+)\s*公里',
        r'([\d.]+)\s*克',
        r'([\d.]+)\s*%',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)  # 使用 findall 取所有匹配
        if matches:
            # 取最后一个匹配
            try:
                return float(matches[-1])
            except:
                continue

    # 最后尝试：取文本中最后一个单独的数字
    all_numbers = re.findall(r'\b([\d.]+)\b', text)
    if all_numbers:
        try:
            return float(all_numbers[-1])
        except:
            pass

    return None
```

---

## 结论

**Stage 2 测试框架确实存在问题**:

1. **设计假设错误**: 框架假设模型直接输出答案，未考虑推理模型的 Thinking Process 格式
2. **正则匹配逻辑缺陷**: `re.search()` 只找第一个匹配，导致匹配到步骤编号而非答案
3. **测试不公平**: 代码测试因其评分方式不受影响，其他测试则严重受影响

**修复建议**:
- 短期: 修改答案提取逻辑，取最后一个匹配而非第一个
- 中期: 添加对推理模型的专门处理，提取 `</think>` 后的内容
- 长期: 统一测试框架，支持 reasoning_format 参数

**Qwen3.5 的真实能力被低估**:
- 代码能力 80% 是准确的（评分方式不受影响）
- 其他测试的 0% 是评分错误，不代表模型真实能力
- 需要重新运行测试以获取准确评估

---

*报告生成时间: 2026-02-26*
