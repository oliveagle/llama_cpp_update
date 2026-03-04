# Eval 评估架构文档

> **创建时间**: 2026-03-04
> **最后更新**: 2026-03-04
> **版本**: v2.0

---

## 一、架构概览

```
eval/
├── run.py                      # 统一命令行入口 ⭐
│   ├── run.py stage1 --model xxx
│   ├── run.py stage2 --model xxx
│   ├── run.py stage3 --model xxx
│   ├── run.py all --model xxx
│   └── run.py benchmark
│
├── framework/                  # 核心框架
│   ├── base.py                # 基础类 (BaseEvaluator, StageResult, TestResult)
│   ├── runner.py              # 测试执行器 (EvaluationRunner)
│   └── report.py              # 报告生成器 (ReportGenerator)
│
├── tests/                      # 测试脚本
│   ├── stage1/                # Stage 1 - 性能基准测试
│   │   ├── test_qwen35_4b_stage1.py
│   │   ├── test_qwen35_9b_stage1.py
│   │   └── test_qwen35_27b.py
│   ├── stage2/                # Stage 2 - 基础能力测试
│   │   ├── capability_test.py
│   │   └── capability_test_v2.py
│   └── stage3/                # Stage 3 - 深度能力测试
│       ├── eval_tools_capability.py
│       └── test_qwen35_*_stage3.py
│
├── results/                    # 评估结果输出 ⭐ 标准化
│   ├── stage1/                # 性能测试结果
│   ├── stage2/                # 基础能力结果
│   ├── stage3/                # 深度能力结果
│   └── capabilities/          # 综合能力评测
│
├── eval_results/               # 评估报告输出
│   └── MODEL_LEADERBOARD.md   # 模型排行榜
│
├── frameworks/                 # 第三方框架集成
│   └── LiveCodeBench/         # 代码能力评估
│
├── model_configs/              # 模型调优配置
│   ├── base.py
│   ├── qwen3.py
│   ├── joyai_llm_flash.py
│   └── glm4.py
│
├── tools/                      # 性能测试工具
│   └── benchmark_all_models.py
│
├── golden_benchmarks.py        # 黄金标杆定义
└── config.py                   # 系统配置 ⭐ 新增
```

---

## 二、三层评估体系

### Stage 1 - 性能基准测试

| 测试项 | 说明 | 指标 |
|--------|------|------|
| Prompt Processing | 预填充速度 | tokens/s |
| Token Generation | 生成速度 | tokens/s |
| Context Scaling | 不同 Context 大小性能 | 4K/8K/16K/32K/128K |
| VRAM Usage | 显存占用 | GB |

**测试脚本**: `tests/stage1/test_*.py`

### Stage 2 - 基础能力测试 (10 大类 30 cases)

| 类别 | Cases | 说明 |
|------|-------|------|
| 基础对话 | 4 | 多语言问候、能力边界 |
| 代码能力 | 6 | Python/JS/SQL/正则 |
| 逻辑推理 | 5 | 数学题/概率/悖论 |
| 角色扮演 | 3 | 翻译/老师/客服 |
| 知识问答 | 4 | 历史/科学/地理/计算机 |
| 创意写作 | 2 | 短故事/诗歌 |
| 多轮对话 | 2 | 记忆测试/上下文 |
| 格式化输出 | 2 | JSON/Markdown |
| 安全测试 | 1 | 无害拒绝 |
| 长文本理解 | 1 | 摘要 |

**测试脚本**: `tests/stage2/capability_test_v2.py`

### Stage 3 - 深度能力测试

| 测试项 | 说明 |
|--------|------|
| 工具调用 | Linux 命令执行 |
| 复杂任务 | 多步骤规划 |
| 代码解释 | 调试/优化 |

**测试脚本**: `tests/stage3/eval_tools_capability.py`

---

## 三、使用指南

### 快速开始

```bash
cd /mnt/volume3/llama_cpp/eval

# 1. Stage 1 - 性能测试
python run.py stage1 --model Qwen3-0.6B --ctx-size 8192

# 2. Stage 2 - 基础能力
python run.py stage2 --model JoyAI-LLM-Flash

# 3. Stage 3 - 深度能力
python run.py stage3 --model GLM-4.7-Flash

# 4. 完整评估
python run.py all --model Qwen3-4B

# 5. 查看排行榜
python run.py leaderboard
```

### 直接运行脚本

```bash
# Stage 1
python tests/stage1/test_qwen35_4b_stage1.py

# Stage 2
python tests/stage2/capability_test_v2.py

# Stage 3
python tests/stage3/eval_tools_capability.py
```

### API 配置

```bash
# 默认使用 localhost:8400
python run.py stage1 --model xxx --url http://localhost:8400

# 使用 CUDA 实例 (端口 8401)
python run.py stage1 --model xxx --url http://localhost:8401
```

---

## 四、数据流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  模型配置   │ ──→ │  测试执行   │ ──→ │  结果收集   │
│ model_configs│     │  runner.py  │     │ StageResult │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  排行榜更新  │ ←── │  报告生成   │ ←── │  JSON 输出  │
│LEADERBOARD.md│     │ report.py   │     │ results/    │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 五、配置管理

### config.py 配置项

```python
# 默认 API 地址
DEFAULT_API_URL = "http://localhost:8400"

# Stage 通过门槛
STAGE2_THRESHOLD = 0.6  # 60%
STAGE3_THRESHOLD = 0.5  # 50%

# Context 大小选项
CTX_SIZES = [4096, 8192, 16384, 32768, 65536]
```

### 模型配置

```python
# model_configs/ 目录下每个模型独立配置
- qwen3.py           # Qwen3 系列
- joyai_llm_flash.py # JoyAI 配置
- glm4.py            # GLM-4 配置
```

---

## 六、输出格式

### JSON 结果格式

```json
{
  "model": "Qwen3-4B",
  "timestamp": "2026-03-04T14:00:00",
  "stage": 1,
  "results": {
    "prefill_speed": 3500,
    "generation_speed": 38,
    "vram_usage_gb": 3.2
  }
}
```

### Markdown 报告格式

```markdown
# Qwen3-4B 性能评估报告

## 总体概况
| 指标 | 值 |
|------|-----|
| 生成速度 | 38 tokens/s |
| 预填充速度 | 3500 tokens/s |
| 显存占用 | 3.2 GB |
```

---

## 七、相关文件

- [MODEL_LEADERBOARD.md](./eval_results/MODEL_LEADERBOARD.md) - 模型排行榜
- [golden_benchmarks.py](./golden_benchmarks.py) - 黄金标杆定义
- [framework/CLAUDE.md](./framework/CLAUDE.md) - 框架配置

---

## 八、变更历史

### v2.0 (2026-03-04)
- ✅ 创建统一入口 `run.py`
- ✅ 标准化输出目录 `results/stage{1,2,3}/`
- ✅ 整合测试脚本到 `tests/` 目录
- ✅ 创建配置模块 `config.py`
- ✅ 完善架构文档

### v1.0 (2026-02-18)
- 初始三层评估体系建立
- 基础框架类实现

---

*最后更新：2026-03-04*
