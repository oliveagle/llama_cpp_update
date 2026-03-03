# llama.cpp 项目目录结构

> **最后更新**: 2026-03-04
> **整理说明**: 按功能模块重组为三大核心模块
> **最新变更**: 能力评测输出目录统一到 eval/results/capabilities/

---

## 项目目标

本项目有三大核心目标：

1. **llama.cpp 核心管理** - 支持 CUDA 和 Vulkan 两种后端的服务器管理和更新
2. **llama.cpp 功能开发** - 新功能实验和开发（NPU、ONNX、其他实验性工作）
3. **大模型本地化评估** - 各种大模型的评测框架和评估结果

---

## 目录概览

```
llama_cpp/
├── CLAUDE.md / AGENTS.md           # 项目配置
├── PROJECT_STRUCTURE.md            # 本文件 (目录结构说明)
├── README.md / LICENSE             # 说明和许可证
├── AGENTS-COLLABORATION.md         # 多 Agent 协作记录
│
├── core/                           # [模块 1] llama.cpp 核心管理
│   ├── bin/                        # 可执行脚本
│   ├── config/                     # 配置文件 (presets, nginx, versions.json)
│   ├── systemd/                    # systemd 服务
│   ├── scripts/                    # 服务器启动脚本
│   ├── downloads/                  # 下载的 llama.cpp 版本
│   └── logs/                       # 服务日志
│
├── dev/                            # [模块 2] llama.cpp 功能开发
│   ├── src/                        # 源代码 (NPU, ONNX Runtime, RyzenAI)
│   ├── nanoquant/                  # NanoQuant 量化工具
│   ├── ryzenai/                    # RyzenAI NPU 工具
│   ├── build/                      # 构建输出
│   └── experimental/               # 实验性功能
│
├── eval/                           # [模块 3] 大模型本地化评估
│   ├── frameworks/                 # 评测框架 (LiveCodeBench, 等)
│   ├── lib/                        # 评测库
│   ├── framework/                  # 评测框架 (原 eval/framework)
│   ├── tests/                      # 评测测试 (stage1/stage2/stage3/stage4)
│   ├── scripts/                    # 评测脚本
│   ├── tools/                      # 评测工具 (benchmark, test, utils)
│   ├── web/                        # Web 报告
│   ├── results/                    # 评测结果
│   │   ├── capabilities/          # 能力评测输出
│   │   │   ├── knowledge/         # 知识库能力
│   │   │   ├── multiturn/         # 多轮对话能力
│   │   │   ├── reasoning/         # 推理能力
│   │   │   └── safety/            # 安全能力
│   │   ├── stage1/                # Stage 1 测试输出
│   │   ├── stage2/                # Stage 2 测试输出
│   │   ├── stage3/                # Stage 3 测试输出
│   │   ├── stage4/                # Stage 4 测试输出
│   │   └── frameworks/            # 评测框架输出
│   ├── reports/                    # 评测报告
│   ├── config/                     # 评测配置
│   ├── model_configs/              # 模型配置
│   ├── eval_results/               # 评测结果 (软链接)
│   └── [顶层评测脚本]
│
├── docs/                           # 文档目录
│   ├── guides/                     # 使用指南
│   ├── design/                     # 设计文档
│   └── inbox/                      # 待整理文档
│
├── models/                         # 模型相关
│   ├── configs/                    # 模型配置
│   ├── tokenizer_configs/          # Tokenizer 配置
│   ├── cache/                      # 模型缓存
│   ├── Nanbeige4.1-3B/             # Nanbeige 模型
│   ├── lfm2.5-audio/               # 音频模型
│   ├── qwen3-onnx/                 # Qwen3 ONNX 模型
│   └── ruvltra/                    # Ruvltra 模型
│
├── tmp/                            # 临时文件
├── current -> core/downloads/llama-b8183  # 当前版本链接
├── current-rocm -> core/downloads/current-rocm
└── eval_results -> /home/oliveagle/.agents/dashboard/llama-eval/eval_results
```

---

## 核心模块详解

### 模块 1: `core/` - llama.cpp 核心管理

负责 llama.cpp 的日常运维，包括：
- 服务器启动/停止
- 版本更新
- CUDA 和 Vulkan 双后端支持

#### `core/bin/` - 可执行脚本

| 脚本 | 功能 | 端口 |
|------|------|------|
| `llama-server-vulkan.sh` | Vulkan 服务器主控 (AMD gfx1151) | 8400 |
| `llama-server-cuda.sh` | CUDA 服务器主控 (V100) | 8401 |
| `llama-server-embedding.sh` | Embedding 服务器 (Qwen3) | 13232 |
| `llama-server-llada2-mini.sh` | LLaDA2-mini 专用 | 8400 |
| `llama-server-nanbeige-3b.sh` | Nanbeige 3B 专用 | 8400 |
| `llama-server-step3-vl-10b.sh` | Step3-VL 10B 专用 | 8400 |
| `llama-server-youtu-vl-4b.sh` | Youtu-VL 4B 专用 | 8400 |
| `llama-npu-server.sh` | NPU 服务器 | - |
| `llama-onnx-server.sh` | ONNX Runtime 服务器 | - |
| `llama-onnx-cuda.sh` | ONNX CUDA 脚本 | - |
| `llama-xdna-*.sh` | XDNA NPU 相关脚本 | - |
| `llama-server-ruvltra.sh` | Ruvltra 专用脚本 | - |
| `llama-version-manager.sh` | 版本管理脚本 | - |
| `manage-llama-binaries.sh` | 二进制管理脚本 | - |
| `update-llama-cpp.sh` | 统一更新脚本 | - |
| `update_report.sh` | 报告更新脚本 | - |
| `download-lfm-audio.sh` | 下载音频模型脚本 | - |
| `nanbeige-code-server.sh` | Nanbeige 代码服务器 | - |

#### `core/config/` - 配置文件

| 文件/目录 | 说明 |
|-----------|------|
| `presets/mypresets.ini` | Vulkan 模型预设 (端口 8400) |
| `presets/mypresets-cuda.ini` | CUDA 模型预设 (端口 8401) |
| `presets/mypresets-hip.ini` | HIP 后端预设 |
| `nginx.conf` | nginx 配置文件 |
| `versions.json` | llama.cpp 版本信息 |

#### `core/scripts/` - 服务器脚本 (旧版)

| 脚本 | 用途 |
|------|------|
| `llama-server-vulkan.sh` | Vulkan 服务器启动 |
| `llama-server-cuda.sh` | CUDA 服务器启动 |
| `llama-server-embedding.sh` | Embedding 服务器启动 |
| `llama-server-*.sh` | 其他各种服务器启动脚本 |

#### `core/downloads/` - 下载的 llama.cpp 版本

存放下载的预编译 llama.cpp 二进制包。

#### `core/logs/` - 服务日志

存放 llama.cpp 服务运行日志。

#### `core/systemd/` - systemd 服务

存放 systemd 服务配置文件。

---

### 模块 2: `dev/` - llama.cpp 功能开发

用于 llama.cpp 新功能的实验和开发。

#### `dev/src/` - 源代码

| 目录 | 说明 |
|------|------|
| `amdxdna_npu/` | AMD XDNA NPU 相关代码 |
| `onnx-runtime/` | ONNX Runtime 相关代码 |
| `ryzenai/` | RyzenAI 相关代码 |

#### `dev/nanoquant/` - NanoQuant 量化工具

自主开发的量化工具，包含：
- `src/` - 源代码
- `tests/` - 测试
- `docs/` - 文档
- `models/` - 模型相关

#### `dev/ryzenai/` - RyzenAI NPU 工具

RyzenAI 相关的工具和脚本。

#### `dev/build/` - 构建输出

各种构建产物。

#### `dev/experimental/` - 实验性功能

实验性代码和功能。

---

### 模块 3: `eval/` - 大模型本地化评估

用于各种大模型的评测和评估。

#### `eval/frameworks/` - 评测框架

| 框架 | 说明 |
|------|------|
| `LiveCodeBench/` | LiveCodeBench 评测框架 |

#### `eval/tests/` - 评测测试

按阶段组织的评测：

| 目录 | 说明 |
|------|------|
| `tests/stage1_throughput/` | Stage 1 吞吐量测试 |
| `tests/stage1_performance/` | Stage 1 性能测试 |
| `tests/stage2_basic/` | Stage 2 基础能力测试 |
| `tests/stage3_deep/` | Stage 3 深度能力测试 |
| `tests/stage4_specialized/` | Stage 4 专项测试 |

#### `eval/scripts/` - 评测脚本

各种评测辅助脚本。

#### `eval/tools/` - 评测工具

| 目录 | 说明 |
|------|------|
| `tools/benchmark/` - 基准测试脚本 |
| `tools/test/` - 测试脚本 |
| `tools/utils/` - 实用工具 |

#### `eval/web/` - Web 报告

Web 版评测报告。

#### `eval/results/` - 评测结果

评测结果输出。

#### `eval/reports/` - 评测报告

评测报告文档。

#### `eval/lib/` - 评测库

评测核心库代码。

#### `eval/framework/` - 评测框架 (原 eval/framework)

原有的评测框架代码。

#### `eval/config/` - 评测配置

评测配置文件。

#### `eval/model_configs/` - 模型配置

评测用的模型配置。

#### 顶层评测脚本

| 脚本 | 用途 |
|------|------|
| `eval_llm.py` | LLM 评测 |
| `eval_all_capabilities.py` | 全能力评测 |
| `eval_tools_capability.py` | 工具能力评测 |
| `eval_linux_ops.py` | Linux 操作评测 |
| `eval_joyai_flash.py` | JoyAI Flash 评测 |
| `eval_joyai_stage3.py` | JoyAI Stage 3 评测 |
| `capability_test.py` / `_v2.py` | 能力测试 |
| `run_all_evals.py` | 运行所有评测 |
| `golden_benchmarks.py` | 基准测试 |
| `linux_ops_test_cases.py` | Linux 操作测试用例 |
| `tools_test_cases_large.py` | 工具测试用例 |

---

### `models/` - 模型相关

模型配置、缓存等。

---

### `docs/` - 文档

| 目录 | 说明 |
|------|------|
| `docs/guides/` - 使用指南 |
| `docs/design/` - 设计文档 |
| `docs/inbox/` - 待整理文档 |

---

### `tmp/` - 临时文件

临时文件存放目录。

---

## 服务端口分配

| 服务 | 端口 | GPU | 说明 |
|------|------|-----|------|
| llama.cpp Vulkan | 8400 | AMD gfx1151 | Strix Halo |
| llama.cpp CUDA | 8401 | NVIDIA V100 | Tesla V100 |
| llama.cpp Embedding | 13232 | AMD gfx1151 | Qwen3 Embedding |
| vLLM V100 | 8403 | NVIDIA V100 | 预留 |
| vLLM ROCm | 8405 | AMD gfx1151 | 预留 |

---

## 快速命令参考

### 启动服务 (core/)

```bash
# Vulkan (AMD)
./core/bin/llama-server-vulkan.sh start

# CUDA (V100)
./core/bin/llama-server-cuda.sh start

# Embedding
./core/bin/llama-server-embedding.sh start
```

### 运行评测 (eval/)

```bash
# Stage 2 测试
python3 eval/eval_llm.py --model MODEL_NAME

# 全能力评测
python3 eval/eval_all_capabilities.py

# 运行所有评测
python3 eval/run_all_evals.py
```

### 功能开发 (dev/)

```bash
# NanoQuant
cd dev/nanoquant
python3 main.py

# ONNX Runtime
cd dev/src/onnx-runtime
```

---

## 重组历史

---

## 重组历史

### 2026-03-04 - 能力评测输出目录调整

**目标**: 将评测输出目录统一到 eval/results/ 下

**变更**:
- knowledge/ → eval/results/capabilities/knowledge/
- multiturn/ → eval/results/capabilities/multiturn/
- reasoning/ → eval/results/capabilities/reasoning/
- safety/ → eval/results/capabilities/safety/ (含 stage3_2026-03-03.jsonl)

**新增目录结构**:
```
eval/results/
├── capabilities/          # 能力评测输出
│   ├── knowledge/         # 知识库能力
│   ├── multiturn/         # 多轮对话能力
│   ├── reasoning/         # 推理能力
│   └── safety/            # 安全能力
├── frameworks/            # 评测框架输出
├── stage1/                # Stage 1 测试输出
├── stage2/                # Stage 2 测试输出
└── stage3/                # Stage 3 测试输出
```

### 2026-03-03 - 根目录清理

**目标**: 清理根目录杂散文件，统一文件结构

**变更**:
- 移动所有 `test_*.py` 文件 → `eval/tests/`
- 移动所有 `check_*.py` 文件 → `eval/tests/`
- 合并 `downloads/` → `core/downloads/`
- 移动 `*.log` 文件 → `eval/logs/`
- 更新 `current` 符号链接 → `core/downloads/llama-b8183`
- 创建 `current-rocm` 符号链接 → `core/downloads/current-rocm`

**整理后根目录**:
```
llama_cpp/
├── CLAUDE.md / AGENTS.md / PROJECT_STRUCTURE.md
├── README.md / LICENSE / AGENTS-COLLABORATION.md
├── core/         # llama.cpp 核心管理
├── dev/          # 功能开发
├── eval/         # 大模型评测
├── docs/         # 文档
├── models/       # 模型
├── tmp/          # 临时文件
├── logs/         # 日志
├── current -> core/downloads/llama-b8183
├── current-rocm -> core/downloads/current-rocm
└── update-llama-cpp-v2.sh  # 统一更新脚本
```

### 2026-02-25 - 按功能模块重组

**目标**: 将项目按三大核心模块重组

**变更**:
- 新建 `core/` - llama.cpp 核心管理 (服务器、更新、配置)
- 新建 `dev/` - 功能开发 (src, nanoquant, ryzenai, build)
- 扩展 `eval/` - 大模型评测 (LiveCodeBench, tests, scripts, web)
- 移动 `LiveCodeBench/` → `eval/frameworks/`
- 移动 `bin/` → `core/bin/`
- 移动 `config/` → `core/config/`
- 移动 `systemd/` → `core/systemd/`
- 移动 `downloads/` → `core/downloads/`
- 移动 `logs/` → `core/logs/`
- 移动 `scripts/server/` → `core/scripts/`
- 移动 `src/` → `dev/src/`
- 移动 `nanoquant/` → `dev/nanoquant/`
- 移动 `ryzenai/` → `dev/ryzenai/`
- 移动 `build/` → `dev/build/`
- 移动 `tests/` → `eval/tests/`
- 移动 `scripts/` → `eval/scripts/`
- 移动 `reports/` → `eval/results/`
- 移动 `web/` → `eval/web/`
- 清理空目录

**新的目录结构**:
```
llama_cpp/
├── core/    # llama.cpp 核心管理
├── dev/     # 功能开发
├── eval/    # 大模型评测
├── docs/    # 文档
├── models/  # 模型
└── tmp/     # 临时文件
```

### 2026-02-18 - 首次全面重组

**变更**:
- 新建 `bin/` 目录存放可执行脚本
- 新建 `config/` 目录存放配置文件
- 新建 `tests/` 目录存放测试脚本
- 新建 `web/` 目录存放 Web 报告
- 重组 `eval_results/` 按阶段和后端分类

---

*目录结构整理完成 - 2026-03-04*
