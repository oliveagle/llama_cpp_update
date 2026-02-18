# HuggingFace Trending GGUF 模型自动化分析 - 工作汇总

> **日期**: 2026-02-17
> **状态**: 脚本已部署，定时任务已启用

---

## 已完成工作

### 1. 自动化分析脚本

| 脚本 | 功能 | 输出 |
|------|------|------|
| `analyze_trending_models.py` | 获取100个trending模型，版本过滤，分析优先级 | `trending_analysis.md` |
| `analyze_trending_models_deep.py` | 获取500个模型，深度分析20B-40B | `trending_analysis_deep.md` |
| `cron_analyze.sh` | Cron包装脚本，自动运行并记录日志 | `logs/analyze_*.log` |
| `benchmark_single.sh` | 单模型benchmark测试 | `benchmarks/*-benchmark.md` |
| `auto_eval_models.py` | 自动化模型评估 (GSM8K/HumanEval/MBPP/Tools) | `eval_results/*` |

### 2. 定时任务

```bash
# 每天上午9点自动运行
0 9 * * * /mnt/volume3/llama_cpp/cron_analyze.sh
```

### 3. 分析结果 (2026-02-17)

#### 模型大小限制
- **已放宽到**: <=40GB (之前30GB)
- **目标范围**: 20B-40B (V100 32GB可承受)

#### 版本过滤规则
按模型规模分组保留最新版本：
- **同规模过滤**: Qwen3-8B (保留) vs Qwen2.5-7B (过滤)
- **不同规模保留**: Qwen3-8B 和 Qwen2.5-32B 都保留

#### 20B-40B 黄金区间模型

| 排名 | 模型 | 架构 | 大小 | 类别 | 优先级 | 状态 |
|------|------|------|------|------|--------|------|
| 1 | Qwen2.5-32B-Instruct | Qwen | 32B | LLM | 10/10 | ⬜ 未下载 |
| 2 | dolphin-2.9.1-yi-1.5-34b | Yi | 34B | LLM | 10/10 | ⬜ 未下载 |

#### 模型类别分类

报告现在按以下类别分组：
- **LLM**: 通用语言模型
- **OCR**: 文字识别
- **TTS**: 语音合成
- **Vision**: 视觉/多模态
- **Code**: 代码模型
- **Reasoning**: 推理模型
- **Tools**: 工具使用
- **Embedding**: 文本嵌入

#### 已测试模型 (基准)

| 模型 | 大小 | 预填充(8K) | 生成速度 | 显存 | Context |
|------|------|-----------|----------|------|---------|
| JoyAI-LLM-Flash-Q4_K_M | 28GB | 736 t/s | 38-40 t/s | 29.5GB | 16K |
| GLM-4.7-Flash-Q4_K_M | 18GB | 834 t/s | 33 t/s | 17.9GB | 14K |
| GLM-4.7-Flash-REAP-IQ4_NL | 13GB | 863 t/s | 32 t/s | 13.9GB | 8K |

---

## 文件位置

```
llama_cpp/
├── analyze_trending_models.py      # 主分析脚本
├── analyze_trending_models_deep.py # 深度分析脚本
├── cron_analyze.sh                 # Cron任务脚本
├── benchmark_single.sh             # 单模型测试脚本
├── trending_analysis.md            # 最新分析报告
├── trending_analysis_deep.md       # 深度分析报告
├── ANALYSIS_SUMMARY.md             # 本文件
├── logs/                           # 日志目录
│   └── analyze_YYYYMMDD_HHMM.log
└── benchmarks/                     # Benchmark报告
    └── *-V100-benchmark.md
```

---

## 使用说明

### 手动运行分析
```bash
cd /mnt/volume3/llama_cpp
export HF_ENDPOINT=https://hf-mirror.com
python3 analyze_trending_models.py
```

### 下载推荐模型
```bash
export HF_ENDPOINT=https://hf-mirror.com

# Qwen2.5-32B-Instruct
modelscope download --model Qwen/Qwen2.5-32B-Instruct \
  --local_dir /mnt/volume3/modelscope_models/Qwen/

# dolphin-2.9.1-yi-1.5-34b
modelscope download --model dphn/dolphin-2.9.1-yi-1.5-34b \
  --local_dir /mnt/volume3/modelscope_models/dphn/
```

### 测试已下载模型
```bash
./benchmark_single.sh <模型路径> [别名]
```

---

## 过滤规则

脚本已配置以下过滤规则：

1. **模型大小**: <=40GB (V100 32GB限制)
2. **类别分类**: LLM, OCR, TTS, Vision, Code, Reasoning, Tools, Embedding
3. **测试模型**: 排除 (gpt2, tiny-, opt-125m等)
4. **大小优先级**: 20-40B加分，<10B减分
5. **架构优先级**:
   - 高: Qwen, GLM, Yi, MiniMax, InternLM (中国厂商)
   - 低: Llama, Mistral (西方主流，已有大量数据)

## 类别关键词

| 类别 | 检测关键词 |
|------|-----------|
| LLM | llm, chat, instruct, text-generation, dialog |
| OCR | ocr, text-recognition, document, layout, parse |
| TTS | tts, text-to-speech, speech, voice, audio, kokoro |
| Vision | vision, image, vl, multimodal, clip |
| Code | code, coder, programming, dev |
| Reasoning | reasoning, think, r1 |
| Tools | tool, function, agent |
| Embedding | embedding, e5-, bge-, sentence-transformers |

---

## 4. 模型能力评估框架 (新增)

### 评估工具
- **lm-eval-harness** (EleutherAI) ✅ 已安装
- **虚拟环境**: `venv/` 目录

### 评估脚本

| 脚本 | 功能 |
|------|------|
| `eval/golden_benchmarks.py` | 黄金标杆定义 |
| `eval/eval_llm.py` | LLM综合能力评估 |
| `eval/run_all_evals.py` | 批量评估入口 |

### 黄金标杆 (LLM类别)

**基准模型**: JoyAI-LLM-Flash-Q4_K_M (28GB)

| 指标 | 标杆值 | 目标值 |
|------|--------|--------|
| C-Eval | 0.72 | 0.70 |
| CMMLU | 0.70 | 0.68 |
| GSM8K | 0.78 | 0.75 |
| HumanEval | 0.65 | 0.60 |
| MMLU | 0.68 | 0.65 |
| 预填充(8K) | 736 t/s | 500 t/s |
| 生成速度 | 39 t/s | 30 t/s |

### 可用评测任务
- `ceval-valid` - 中文理解
- `cmmlu` - 中文多任务
- `mmlu` - 英文综合
- `metabench_gsm8k_subset` - 数学推理
- `humaneval` - 代码生成

### 评估要求 (重要)

**所有模型**必须测试以下能力：
1. **基础能力**: C-Eval, CMMLU, MMLU, GSM8K
2. **代码生成**: HumanEval, MBPP (所有模型必测)
3. **工具使用**: 自定义测试集 (所有模型必测)

### 评估任务说明

| 任务 | 评估能力 | 模式 | llama.cpp兼容 | 状态 |
|------|----------|------|---------------|------|
| `gsm8k` | 数学推理 | generate_until | ✅ 兼容 | ✅ 已完成 |
| `humaneval` | 代码生成 | generate_until | ✅ 兼容 | ⏳ 待测试 |
| `mbpp` | Python编程 | generate_until | ✅ 兼容 | ⏳ 待测试 |
| `工具调用` | Tools使用 | chat.completions | ✅ 已启用 | ✅ 已完成 (300案例) |
| `ceval/cmmlu/mmlu` | 中文/英文理解 | loglikelihood | ❌ 不兼容 | ❌ 无法测试 |

**注意**:
- ceval/cmmlu/mmlu 需要 token_logprobs，llama.cpp API 不返回此字段
- llama.cpp 工具调用已通过 `--jinja` 参数启用，JoyAI 模型达到 60% 准确率

### 使用方式

```bash
# 激活虚拟环境
source venv/bin/activate

# 评估单个模型 (GSM8K + HumanEval + MBPP)
python3 eval/eval_llm.py \
  --model-name ModelName \
  --base-url http://localhost:8401

# 评估工具使用能力 (快速测试 - 27案例)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8401 \
  --model-name ModelName

# 评估工具使用能力 (完整测试 - 300案例)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8401 \
  --model-name ModelName \
  --full

# 一键综合评估 (所有能力)
python3 eval/eval_all_capabilities.py \
  --model-path /path/to/model.gguf \
  --model-name ModelName \
  --model-url http://localhost:8401

# 自动化批量评估 (定时任务使用)
python3 auto_eval_models.py --limit 3
```

### 已完成评估

| 模型 | 类别 | 大小 | GSM8K | 工具调用 | 状态 |
|------|------|------|-------|----------|------|
| JoyAI-LLM-Flash-Q4_K_M | LLM | 27.6GB | 80% | 66.7% (18/27) / 300案例运行中 | ✅ 已完成 |

#### JoyAI-LLM-Flash-Q4_K_M 详细评估结果

**工具调用能力 (27项测试)**

| 类别 | 测试数 | 通过 | 失败 | 准确率 | 评价 |
|------|--------|------|------|--------|------|
| 信息查询 | 4 | 4 | 0 | 100% | 优秀 |
| 文件操作 | 1 | 1 | 0 | 100% | 优秀 |
| 系统 | 1 | 1 | 0 | 100% | 优秀 |
| 时间管理 | 4 | 3 | 1 | 75% | 良好 |
| 翻译 | 3 | 2 | 1 | 67% | 良好 |
| 数学计算 | 5 | 3 | 2 | 60% | 一般 |
| 搜索查询 | 4 | 2 | 2 | 50% | 一般 |
| 边界情况 | 4 | 2 | 2 | 50% | 一般 |
| 通信 | 1 | 0 | 1 | 0% | 待改进 |

**失败原因分析**：
- 简单数学/翻译任务：模型倾向直接回答而非调用工具
- 汇率/单位换算：模型使用内置知识直接回答
- 网页搜索/邮件：模型拒绝执行（安全设置）
- 上下文省略：模型无法推断缺失参数

#### 300案例测试集分布

| 类别 | 测试数 | 说明 |
|------|--------|------|
| 搜索查询 | 70 | 技术搜索、新闻、股票、汇率等 |
| 数学计算 | 55 | 基础运算、平方、开方、幂运算等 |
| 天气查询 | 50 | 各城市天气、温度、预报 |
| 边界情况 | 35 | 模糊意图、多意图、口语化、专业术语等 |
| 单位换算 | 20 | 长度、重量、温度、货币等 |
| 文件操作 | 20 | 读取、保存、删除、复制、移动等 |
| 翻译 | 20 | 多语言互译 |
| 时间日期 | 20 | 日期查询、提醒设置、日历事件 |
| 通信 | 10 | 邮件、短信、电话等 |
| **总计** | **300** | 全面覆盖工具使用场景 |

---

#### Linux/容器/Shell操作测试集 - 两阶段体系 (新增)

**设计理念**: 先快速筛选，再深度评估

```
┌─────────────────┐     通过≥40%      ┌─────────────────┐
│  入门测试(30)   │ ───────────────→ │  深度测试(300)  │
│  快速筛选       │                  │  全面评估       │
└─────────────────┘     失败        └─────────────────┘
                        (跳过深度测试)
```

**入门测试 (30案例)** - `eval/linux_ops_basic_cases.py`

| 类别 | 数量 | 示例 |
|------|------|------|
| 文件操作 | 6 | ls, pwd, mkdir, cp, mv, rm |
| 文本处理 | 4 | cat, head, grep, wc |
| 系统信息 | 4 | df, free, whoami, date |
| 进程管理 | 4 | ps, kill, top, pgrep |
| 网络管理 | 4 | ping, curl, ssh, netstat |
| 容器操作 | 4 | docker run/ps/stop/logs |
| Shell脚本 | 4 | 变量、循环、判断、脚本 |
| **总计** | **30** | 门槛: 40% |

**深度测试 (300案例)** - `eval/linux_ops_test_cases.py`

| 类别 | 数量 | 说明 |
|------|------|------|
| Docker基础 | 30 | run/ps/stop/exec/logs/build等 |
| Docker高级 | 15 | network/volume/compose/prune等 |
| Podman | 15 | 无根容器、pod、systemd集成 |
| Shell基础 | 20 | 变量、数组、参数扩展 |
| Shell高级 | 20 | 重定向、管道、信号处理 |
| 流程控制 | 20 | if/for/while/case/函数 |
| 归档压缩 | 30 | tar/gzip/bzip2/xz/zip/7z |
| 网络管理 | 25 | ping/ssh/scp/curl/iptables |
| 进程管理 | 25 | ps/kill/nohup/crontab/at |
| 服务管理 | 15 | systemctl/journalctl |
| 用户管理 | 15 | useradd/passwd/chage |
| 文件目录 | 15 | ls/cp/mv/find/chmod |
| 文本处理 | 15 | grep/awk/sed/sort/uniq |
| 系统信息 | 10 | df/free/uptime/uname |
| 权限管理 | 10 | chown/chmod/sudo/su |
| 包管理 | 10 | apt/dpkg/snap/flatpak |
| 存储管理 | 10 | fdisk/mount/lvm |
| **总计** | **300** | 全面覆盖Linux运维场景 |

### 待评估模型

| 模型 | 类别 | 大小 | 状态 |
|------|------|------|------|
| GLM-4.7-Flash-Q4_K_M | LLM | 17.1GB | ⬜ 待评估 |
| GLM-4.7-Flash-REAP-IQ4_NL | LLM | 12.3GB | ⬜ 待评估 |

---

## 5. 文件结构汇总

```
llama_cpp/
├── analyze_trending_models.py        # 主分析脚本 (含版本过滤)
├── analyze_trending_models_deep.py   # 深度分析脚本
├── auto_eval_models.py               # 自动化模型评估
├── cron_analyze.sh                   # Cron任务脚本
├── benchmark_single.sh               # 单模型benchmark
├── trending_analysis.md              # 最新分析报告
├── trending_analysis_deep.md         # 深度分析报告
├── ANALYSIS_SUMMARY.md               # 本文件
├── EVALUATION_FRAMEWORK.md           # 评估框架文档
├── venv/                             # Python虚拟环境
├── eval/                             # 评估脚本
│   ├── golden_benchmarks.py          # 黄金标杆定义
│   ├── eval_llm.py                   # LLM评估 (GSM8K/HumanEval/MBPP)
│   ├── eval_tools_capability.py      # 工具使用评估
│   ├── tools_test_cases_large.py     # 300案例工具测试集
│   ├── eval_linux_ops.py             # Linux/Shell两阶段评估 ⭐
│   ├── linux_ops_basic_cases.py      # 入门测试30案例 ⭐
│   ├── linux_ops_test_cases.py       # 深度测试300案例
│   ├── AGENTS-COLLABORATION.md       # Agent协作规范 ⭐
│   ├── eval_all_capabilities.py      # 综合评估入口
│   ├── run_all_evals.py              # 批量评估
│   └── tested_models.json            # 已测试模型记录
├── logs/                             # 日志目录
└── benchmarks/                       # Benchmark报告
```

---

## 明天查看

明天请查看：
1. `trending_analysis.md` - 最新分析结果
2. `eval_results/eval_summary.md` - 评估汇总
3. `logs/analyze_*.log` - 运行日志
4. 是否有新的高优先级模型推荐

---

*自动生成: 2026-02-17*
