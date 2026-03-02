# llama.cpp 多后端管理与评估平台

> **项目描述**: 支持多后端 (CUDA/Vulkan/ROCm/NPU) 的 llama.cpp 管理平台，集成模型评测、性能基准测试和功能开发
>
> **最后更新**: 2026-03-02

---

## 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| **Core** | llama.cpp 核心管理（服务器、更新、配置） | ✅ 稳定运行 |
| **Dev** | 功能开发（NPU、ONNX、实验性功能） | 🔄 持续开发 |
| **Eval** | 大模型评测（多阶段测试、基准测试） | ✅ 完整框架 |

---

## 快速开始

### 启动服务器

```bash
# Vulkan 服务器 (AMD gfx1151) - 端口 8400
./core/bin/llama-server-vulkan.sh start

# CUDA 服务器 (NVIDIA V100) - 端口 8401
./core/bin/llama-server-cuda.sh start

# Embedding 服务器 - 端口 13232
./core/bin/llama-server-embedding.sh start

# 使用 systemd 服务（开机自启）
sudo systemctl start llama-server-8400.service
sudo systemctl start llama-server-8401.service
```

### 运行评测

```bash
# Stage 2 基础能力测试
python3 eval/eval_llm.py --model MODEL_NAME

# 全能力评测
python3 eval/eval_all_capabilities.py

# 运行所有评测
python3 eval/run_all_evals.py
```

### 更新 llama.cpp

```bash
# Vulkan 更新（自动下载预编译包）
./core/bin/update-llama-cpp-v2.sh vulkan

# CUDA 更新（自动源码编译）
./core/bin/update-llama-cpp-v2.sh cuda

# ROCm 更新（自动下载预编译包）
./core/bin/update-llama-cpp-v2.sh rocm
```

---

## 目录结构

```
llama_cpp/
├── CLAUDE.md / AGENTS.md           # 项目配置
├── PROJECT_STRUCTURE.md            # 目录结构说明
├── README.md                       # 本文件
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
│   ├── tests/                      # 评测测试 (stage1/2/3/4)
│   ├── scripts/                    # 评测脚本
│   ├── tools/                      # 评测工具
│   ├── web/                        # Web 报告
│   ├── results/                    # 评测结果
│   └── reports/                    # 评测报告
│
├── docs/                           # 文档目录
│   ├── INDEX.md                    # 文档索引
│   ├── guides/                     # 使用指南
│   ├── design/                     # 设计文档
│   └── inbox/                      # 待整理文档
│
├── models/                         # 模型相关
└── tmp/                            # 临时文件
```

详细说明见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 服务端口分配

| 服务 | 端口 | GPU | 说明 |
|------|------|-----|------|
| llama.cpp Vulkan | 8400 | AMD gfx1151 | Strix Halo NPU |
| llama.cpp CUDA | 8401 | NVIDIA V100 | Tesla V100 |
| llama.cpp Embedding | 13232 | AMD gfx1151 | Qwen3 Embedding |
| vLLM V100 | 8403 | NVIDIA V100 | 预留 |
| vLLM ROCm | 8405 | AMD gfx1151 | 预留 |

---

## 评测框架

### 四阶段评测体系

| 阶段 | 测试内容 | 说明 |
|------|----------|------|
| **Stage 1** | 吞吐量/Context | 基础性能测试 |
| **Stage 2** | 基础能力 | 工具调用、基础推理 |
| **Stage 3** | 深度能力 | Linux Shell、综合工具 |
| **Stage 4** | 专项测试 | 特定领域能力 |

### 评测报告

- **Web 报告**: `eval/web/`
- **详细结果**: `eval/results/`
- **Dashboard**: `~/.agents/dashboard/llama-eval/`

---

## 开发功能

### NPU 支持

- **AMD XDNA NPU**: RyzenAI NPU 后端开发
- **ONNX Runtime**: ONNX 后端支持
- **NanoQuant**: 自定义量化工具

### 实验性功能

- 新模型适配
- 性能优化实验
- 新后端探索

---

## 文档导航

| 类别 | 位置 |
|------|------|
| 📚 **文档索引** | [docs/INDEX.md](docs/INDEX.md) |
| 📖 **使用指南** | [docs/guides/](docs/guides/) |
| 🏗️ **设计文档** | [docs/design/](docs/design/) |
| 📊 **评测报告** | [eval/reports/](eval/reports/) |
| 🔧 **项目结构** | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| ⚙️ **项目配置** | [CLAUDE.md](CLAUDE.md) |

---

## 相关项目

- [llama.cpp 官方仓库](https://github.com/ggerganov/llama.cpp)
- [HuggingFace](https://huggingface.co/)
- [ModelScope](https://modelscope.cn/)

---

## 许可证

详见 [LICENSE](LICENSE) 文件。

---

*最后更新：2026-03-02*
