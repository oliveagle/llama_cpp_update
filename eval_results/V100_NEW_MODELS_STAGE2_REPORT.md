# V100 CUDA 新模型第二层测试报告

> **测试时间**: 2026-02-18
> **测试平台**: V100-CUDA (llama.cpp b8073)
> **测试标准**: Stage 2 (代码+数学+文本 = 30项)

---

## 📊 新模型测试结果

| 模型 | 代码 | 数学 | 文本 | 总分 | 状态 | 问题 |
|------|------|------|------|------|------|------|
| **Step3-VL-10B-Q4_K_M** | 66.7% | 72.7% | 100% | **79.8%** | ✅ | 表现良好 (chat template 已修复) |
| **LLaDA2.0-mini-preview** | N/A | N/A | N/A | **N/A** | ❌ | 架构不支持 |
| **Youtu-VL-4B-Q8_0** | 100% | 63.6% | 100% | **86.7%** | ✅ | 优秀 (chat template 已修复) |
| **Nanbeige-4.1-3B-Q8_0** | 44.4% | 54.5% | 30.0% | **43.3%** | ⚠️ | 推理模型 (reasoning_content) |

---

## 🔍 问题分析

### 1. Step3-VL-10B-Q4_K_M ✅ (已修复)
- **架构**: Qwen3
- **问题**: ~~最初配置了错误的 chat template~~
- **修复**: 移除 `--chat-template qwen2` 参数
- **最终成绩**: 代码 66.7% | 数学 72.7% | 文本 100% | **总分 79.8%**
- **状态**: 表现良好，可用

### 2. LLaDA2.0-mini-preview-Q4_0 ❌
- **架构**: llada2 (未知架构)
- **问题**: llama.cpp 无法加载
- **错误**: `unknown model architecture: 'llada2'`
- **结论**: 当前 llama.cpp 版本不支持此架构

### 3. Youtu-VL-4B-Instruct-Q8_0 ✅ (已修复)
- **架构**: DeepSeek2
- **问题**: ~~最初配置错误，使用了 qwen2 chat template~~
- **修复**: 移除 chat template 参数后测试正常
- **最终成绩**: 代码 100% | 数学 63.6% | 文本 100% | **总分 86.7%**
- **状态**: 与 Vulkan 表现一致，推荐用于生产环境

### 4. Nanbeige-4.1-3B-Q8_0 ⚠️ (推理模型 - 已修复)
- **架构**: Llama
- **问题**: ~~输出在 `reasoning_content` 字段，普通测试无法获取~~
- **修复**: 测试脚本已更新，支持 `reasoning_content` 字段提取
- **最终成绩**: 代码 44.4% | 数学 54.5% | 文本 30.0% | **总分 43.3%**
- **状态**: 及格，但文本理解较弱
- **特点**: 这是推理模型，输出包含思考过程

---

## 📈 与现有模型对比

| 模型 | 总分 | 对比 |
|------|------|------|
| **Qwen3-4B** (现有) | 90.1% | ⭐⭐⭐⭐⭐ 优秀 |
| **JoyAI-LLM-Flash** (现有) | 88.1% | ⭐⭐⭐⭐⭐ 优秀 |
| **Youtu-VL-4B** (新) | 86.7% | ⭐⭐⭐⭐⭐ 优秀 (已验证) |
| **Step3-VL-10B** (新) | 79.8% | ⭐⭐⭐⭐ 良好 (已修复) |
| **Nanbeige-4.1-3B** (新) | 43.3% | ⭐⭐⭐ 及格 (推理模型) |
| **LLaDA2.0-mini** (新) | N/A | ❌ 架构不支持 |

---

## 💡 结论

**4个新模型最终验证结果：**

| 模型 | 状态 | 总分 | 说明 |
|------|------|------|------|
| **Youtu-VL-4B-Q8_0** | ✅ 优秀 | 86.7% | 可加入生产环境 |
| **Step3-VL-10B** | ✅ 良好 | 79.8% | chat template 修复后可用 |
| **Nanbeige-4.1-3B** | ⭐⭐⭐ 及格 | 43.3% | 推理模型，文本理解较弱 |
| **LLaDA2.0-mini** | ❌ 不支持 | N/A | 架构 llada2 不被 llama.cpp 支持 |

### 问题根因汇总

#### 1. Chat Template 配置错误 (Youtu-VL-4B, Step3-VL-10B)
**症状**: 输出混乱、成绩异常低
**原因**: 手动指定了错误的 `--chat-template`，与模型实际架构不匹配
**修复**: 移除 `--chat-template` 参数，让 llama.cpp 自动检测

#### 2. 推理模型输出格式 (Nanbeige-4.1-3B)
**症状**: 测试显示 0%，但日志显示模型在工作
**原因**: 这是推理模型，输出在 `reasoning_content` 字段，`content` 为空
**修复**: 测试脚本已更新，当 `content` 为空时自动尝试 `reasoning_content`
**最终成绩**: 43.3%（及格，但文本理解较弱 30%）

#### 3. 架构不支持 (LLaDA2.0-mini)
**症状**: 模型无法加载
**原因**: llama.cpp b8073 不支持 `llada2` 架构
**解决**: 等待 llama.cpp 更新

### 已修复的测试脚本
- `eval/tests/stage2_basic/code_eval.py` - 支持 `reasoning_content`
- `eval/tests/stage2_basic/math_eval.py` - 支持 `reasoning_content`
- `eval/tests/stage2_basic/text_eval.py` - 支持 `reasoning_content`

### 建议
- **✅ Youtu-VL-4B (86.7%) 和 Step3-VL-10B (79.8%) 可加入生产环境**
- **⚠️ Nanbeige-4.1-3B (43.3%) 及格但文本理解较弱，谨慎使用**
- **❌ LLaDA2.0-mini 暂时不可用**
- 新模型部署前务必先验证基础对话能力，再运行完整测试

---

*报告生成时间: 2026-02-18*
