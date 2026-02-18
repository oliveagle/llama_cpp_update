# llama.cpp 模型评估框架

> **项目**: llama.cpp 双实例模型能力验证
> **评估维度**: 吞吐量/Context、综合能力、Linux Shell

---

## 目录结构

```
eval_results/
├── vulkan/                          # Vulkan 版本测试结果
│   ├── throughput/                  # 吞吐量测试
│   ├── context/                     # Context 大小测试
│   ├── comprehensive/               # 综合能力测试
│   ├── linux_shell/                 # Linux Shell 测试
│   └── raw_data/                    # 原始测试数据
├── cuda/                            # CUDA 版本测试结果
└── reports/                         # 汇总报告
```

---

## 1. 吞吐量测试 (Throughput)

### 测试目的
测量模型的响应速度和 token 生成速率。

### 测试指标
| 指标 | 说明 | 单位 |
|------|------|------|
| 首 token 延迟 | 从请求到首个 token 返回的时间 | ms |
| 生成速率 | tokens per second | tps |
| 总响应时间 | 完整响应时间 | s |

### 报告模板

```markdown
# 吞吐量测试报告 - {模型名称}

> **测试时间**: {timestamp}
> **测试端点**: {base_url}
> **测试 Agent**: {agent_name}
> **硬件**: {gpu_info}

---

## 测试配置

| 参数 | 值 |
|------|-----|
| 模型 | {model_name} |
| 量化格式 | {quantization} |
| 上下文大小 | {ctx_size} |
| 温度 | {temperature} |
| 测试次数 | {test_count} |

---

## 测试结果

### 短文本生成 (100 tokens)

| 测试项 | 首 token 延迟 | 生成速率 | 总时间 |
|--------|--------------|----------|--------|
| 简单对话 | {ttft} ms | {tps} tps | {total}s |
| 代码生成 | {ttft} ms | {tps} tps | {total}s |
| 推理任务 | {ttft} ms | {tps} tps | {total}s |

### 中等文本生成 (500 tokens)

| 测试项 | 首 token 延迟 | 生成速率 | 总时间 |
|--------|--------------|----------|--------|
| 故事生成 | {ttft} ms | {tps} tps | {total}s |

### 长文本生成 (2000 tokens)

| 测试项 | 首 token 延迟 | 生成速率 | 总时间 |
|--------|--------------|----------|--------|
| 长文生成 | {ttft} ms | {tps} tps | {total}s |

---

## 原始数据存档

**JSON 文件**: `{model_name}_throughput_raw.json`

```json
{
  "model": "模型名称",
  "timestamp": "2026-02-17T10:00:00",
  "config": {...},
  "results": [
    {
      "test_name": "简单对话",
      "prompt_tokens": 10,
      "completion_tokens": 100,
      "ttft_ms": 150,
      "tps": 45.2,
      "total_time_s": 2.35
    }
  ]
}
```

---

## 结论与建议

{conclusion}
```

---

## 2. Context 大小测试

### 测试目的
验证模型能够处理的最大上下文长度。

### 测试层级
| 层级 | Token 数量 | 预期结果 |
|------|-----------|---------|
| 4K | 4096 | 必须通过 |
| 8K | 8192 | 必须通过 |
| 16K | 16384 | 推荐通过 |
| 32K | 32768 | 可选测试 |
| 64K | 65536 | 可选测试 |
| 100K | 102400 | 可选测试 |

### 报告模板

```markdown
# Context 大小测试报告 - {模型名称}

> **测试时间**: {timestamp}
> **测试端点**: {base_url}
> **测试 Agent**: {agent_name}

---

## 测试方法

使用"大海捞针"(Needle in a Haystack)测试:
- 在长上下文的特定位置插入关键信息
- 要求模型回忆该信息
- 验证信息保留率

---

## 测试结果

| Context 大小 | 状态 | 响应时间 | 准确率 | 备注 |
|-------------|------|---------|--------|------|
| 4K | ✅/❌ | {time}s | {accuracy}% | {notes} |
| 8K | ✅/❌ | {time}s | {accuracy}% | {notes} |
| 16K | ✅/❌ | {time}s | {accuracy}% | {notes} |
| 32K | ✅/❌ | {time}s | {accuracy}% | {notes} |
| 64K | ✅/❌ | {time}s | {accuracy}% | {notes} |
| 100K | ✅/❌ | {time}s | {accuracy}% | {notes} |

### 详细结果

#### 4K Context
- **测试内容**: {description}
- **关键信息位置**: 开头/中间/结尾
- **模型回答**: {response}
- **正确性**: ✅/❌

---

## 原始数据存档

**JSON 文件**: `{model_name}_context_raw.json`

```json
{
  "model": "模型名称",
  "timestamp": "2026-02-17T10:00:00",
  "results": [
    {
      "context_size": 4096,
      "needle_position": "middle",
      "correct": true,
      "response_time": 3.5
    }
  ]
}
```

---

## 最大可用 Context

**推荐最大上下文**: {max_context} tokens

**原因**: {reasoning}
```

---

## 3. 综合能力测试

### 测试目的
评估模型在多个维度上的能力表现。

### 测试维度
| 维度 | 测试内容 | 评估方式 |
|------|---------|---------|
| 数学推理 | GSM8K、基础数学 | 准确率 |
| 代码能力 | HumanEval、MBPP | pass@1 |
| 逻辑推理 | 逻辑题、推理链 | 人工评估 |
| 常识问答 | 常识性问题 | 准确率 |
| 文本理解 | 阅读理解、摘要 | ROUGE/人工 |

### 报告模板

```markdown
# 综合能力测试报告 - {模型名称}

> **测试时间**: {timestamp}
> **测试工具**: lm-eval-harness / 自定义测试集
> **测试 Agent**: {agent_name}

---

## 测试概览

| 能力维度 | 测试集 | 得分 | 状态 |
|---------|--------|------|------|
| 数学推理 | GSM8K | {score}% | ✅/❌ |
| 代码生成 | HumanEval | {score}% | ✅/❌ |
| 代码生成 | MBPP | {score}% | ✅/❌ |
| 逻辑推理 | 自定义 | {score}% | ✅/❌ |
| 常识问答 | 自定义 | {score}% | ✅/❌ |
| 文本理解 | 自定义 | {score}% | ✅/❌ |

---

## 详细结果

### 数学推理 (GSM8K)

**得分**: {score}%

**示例测试**:
| 题目 | 正确答案 | 模型回答 | 正确性 |
|------|---------|---------|--------|
| {question} | {answer} | {response} | ✅/❌ |

---

### 代码生成 (HumanEval)

**Pass@1**: {score}%

**示例测试**:
| 题目 | 状态 | 代码 |
|------|------|------|
| {task_id} | ✅/❌ | ```python\n{code}\n``` |

---

### 逻辑推理

**准确率**: {accuracy}%

**测试案例**:
| 问题 | 期望答案 | 模型回答 | 结果 |
|------|---------|---------|------|
| {question} | {expected} | {actual} | ✅/❌ |

---

## 原始数据存档

**JSON 文件**: `{model_name}_comprehensive_raw.json`

**lm-eval 结果**: `{model_name}_results.json`

---

## 能力雷达图

```
数学推理:    ████████░░ {score}%
代码生成:    ██████░░░░ {score}%
逻辑推理:    ███████░░░ {score}%
常识问答:    ████████░░ {score}%
文本理解:    ███████░░░ {score}%
```

---

## 结论

{conclusion}
```

---

## 4. Linux Shell 操作能力测试

### 测试目的
评估模型识别和调用 Linux Shell 工具的能力。

### 测试内容
| 类别 | 测试项 | 期望工具 |
|------|--------|---------|
| 文件操作 | 创建/读取/删除文件 | write_file, read_file |
| 目录操作 | 列出/切换目录 | execute_command(ls, cd) |
| 系统信息 | 查看系统状态 | execute_command(df, top) |
| 进程管理 | 查看/终止进程 | execute_command(ps, kill) |
| Docker 操作 | 容器管理 | execute_command(docker) |
| 网络操作 | 网络诊断 | execute_command(ping, curl) |

### 报告模板

```markdown
# Linux Shell 能力测试报告 - {模型名称}

> **测试时间**: {timestamp}
> **测试端点**: {base_url}
> **测试 Agent**: {agent_name}
> **测试集**: tools_test_cases (27/300 cases)

---

## 测试概览

| 类别 | 测试数 | 通过数 | 工具调用率 | 准确率 |
|------|--------|--------|-----------|--------|
| 文件操作 | {count} | {passed} | {rate}% | {accuracy}% |
| 目录操作 | {count} | {passed} | {rate}% | {accuracy}% |
| 系统信息 | {count} | {passed} | {rate}% | {accuracy}% |
| 进程管理 | {count} | {passed} | {rate}% | {accuracy}% |
| Docker 操作 | {count} | {passed} | {rate}% | {accuracy}% |
| **总计** | {total} | {passed} | **{rate}%** | **{accuracy}%** |

---

## 详细结果

### 文件操作测试

| 测试项 | 提示词 | 期望工具 | 实际工具 | 参数正确 | 结果 |
|--------|--------|---------|---------|---------|------|
| 创建文件 | {prompt} | write_file | {actual} | ✅/❌ | ✅/❌ |
| 读取文件 | {prompt} | read_file | {actual} | ✅/❌ | ✅/❌ |

### 系统信息测试

| 测试项 | 提示词 | 期望命令 | 实际命令 | 结果 |
|--------|--------|---------|---------|------|
| 磁盘使用 | {prompt} | df -h | {actual} | ✅/❌ |
| 内存使用 | {prompt} | free -h | {actual} | ✅/❌ |

---

## 原始数据存档

**JSON 文件**: `{model_name}_linux_shell_raw.json`

```json
{
  "model": "模型名称",
  "timestamp": "2026-02-17T10:00:00",
  "total_cases": 27,
  "tool_call_rate": 75.5,
  "accuracy": 68.2,
  "results": [
    {
      "test_name": "创建文件",
      "prompt": "...",
      "expected_tool": "write_file",
      "actual_tool": "write_file",
      "arguments_correct": true,
      "passed": true
    }
  ]
}
```

**详细日志**: `{model_name}_linux_eval.log`

---

## 工具调用示例

### 成功案例

**输入**: {prompt}

**输出**:
```json
{
  "tool_calls": [{
    "function": {
      "name": "execute_command",
      "arguments": {"command": "ls -la"}
    }
  }]
}
```

### 失败案例

**输入**: {prompt}

**输出**: {response}

**问题**: {failure_reason}

---

## 结论

{conclusion}

**建议**:
- {recommendation1}
- {recommendation2}
```

---

## 执行命令参考

### Vulkan 版本 (端口 8400)

```bash
# 1. 基础吞吐量 + Context 测试
python3 eval/eval_throughput.py \
  --model-url http://localhost:8400 \
  --model-name MODEL_NAME \
  --output-dir eval_results/vulkan/throughput

# 2. 综合能力测试
python3 eval/eval_all_capabilities.py \
  --model-path /path/to/model.gguf \
  --model-name MODEL_NAME \
  --model-url http://localhost:8400 \
  --output-dir eval_results/vulkan/comprehensive

# 3. Linux Shell 测试
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8400 \
  --model-name MODEL_NAME \
  --output-dir eval_results/vulkan/linux_shell \
  --linux
```

### CUDA 版本 (端口 8401)

```bash
# 同上，将 8400 替换为 8401
# 输出目录改为 eval_results/cuda/
```

---

## 数据存档规范

每个测试必须保存以下文件:

```
eval_results/{backend}/{test_type}/
├── {model_name}_{test_type}_report.md    # 人类可读报告
├── {model_name}_{test_type}_raw.json     # 原始数据
└── {model_name}_{test_type}.log          # 测试日志 (可选)
```

---

*框架版本: 1.0*
*最后更新: 2026-02-17*
