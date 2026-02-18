# llama.cpp 项目目录结构

> **最后更新**: 2026-02-18
> **整理说明**: 本目录经过全面重组，建立清晰的模块化结构

---

## 目录概览

```
llama_cpp/
├── CLAUDE.md                   # 项目主配置文档 (技术规范)
├── AGENTS.md -> CLAUDE.md      # Agent 协作入口
├── AGENTS-COLLABORATION.md     # 多 Agent 协作记录
├── PROJECT_STRUCTURE.md        # 本文件 (目录结构说明)
├── README.md                   # 项目说明
├── LICENSE                     # 许可证
│
├── bin/                        # 可执行脚本
│   ├── llama-server-*.sh       # 服务器管理脚本
│   └── update*.sh              # 更新脚本
│
├── config/                     # 配置文件
│   ├── presets/                # llama.cpp 预设配置
│   │   ├── mypresets.ini       # Vulkan 预设 (端口 8400)
│   │   └── mypresets-cuda.ini  # CUDA 预设 (端口 8401)
│   └── nginx.conf              # nginx 配置
│
├── docs/                       # 文档目录
│   ├── guides/                 # 使用指南
│   ├── reports/                # 技术报告
│   ├── analysis/               # 分析报告
│   └── benchmarks/             # 性能测试报告
│
├── eval/                       # 评测框架
│   ├── lib/                    # 评测库
│   ├── run_stage2_single_model_v2.py
│   ├── generate_report.py
│   └── ...
│
├── eval_results/               # 评测结果
│   ├── stage1/                 # Stage 1 测试结果
│   │   ├── performance/        # 吞吐量测试
│   │   │   ├── vulkan/         # Vulkan 性能
│   │   │   └── cuda/           # CUDA 性能
│   │   └── context/            # 上下文测试
│   │       ├── vulkan/         # Vulkan 上下文
│   │       └── cuda/           # CUDA 上下文
│   ├── stage2/                 # Stage 2 测试结果
│   │   ├── vulkan/             # Vulkan Stage 2
│   │   ├── cuda/               # CUDA Stage 2
│   │   └── events/             # 事件流数据
│   ├── stage3/                 # Stage 3 测试结果
│   │   ├── vulkan/             # Vulkan Stage 3
│   │   ├── cuda/               # CUDA Stage 3
│   │   └── tools/              # 工具使用测试
│   └── raw_data/               # 原始数据
│       ├── vulkan/             # Vulkan 原始日志
│       └── cuda/               # CUDA 原始日志
│
├── models/                     # 模型配置
│   └── embedding/              # Embedding 模型配置
│
├── scripts/                    # 工具脚本
│   ├── benchmark/              # 性能测试脚本
│   ├── test/                   # 测试脚本
│   ├── tools/                  # 工具脚本
│   └── utils/                  # 实用工具脚本
│
├── tests/                      # 项目测试脚本
│   └── test_*.py               # 各种测试脚本
│
├── web/                        # Web 报告
│   ├── index.html              # 报告首页
│   ├── stage1.html             # Stage 1 报告
│   ├── stage2.html             # Stage 2 报告
│   ├── stage3.html             # Stage 3 报告
│   └── methodology.html        # 测试规范
│
├── downloads/                  # 下载的 llama.cpp 版本
│   ├── llama-b8069/            # 当前 Vulkan 版本
│   └── ...
│
├── current -> downloads/...    # 当前使用的版本链接
├── logs/                       # 服务日志
└── venv/                       # Python 虚拟环境
```

---

## 核心目录详解

### `bin/` - 可执行脚本

| 脚本 | 功能 | 端口 |
|------|------|------|
| `llama-server-vulkan.sh` | Vulkan 服务器主控 (AMD gfx1151) | 8400 |
| `llama-server-cuda.sh` | CUDA 服务器主控 (V100) | 8401 |
| `llama-server-embedding.sh` | Embedding 服务器 (Qwen3) | 13232 |
| `llama-server-llada2-mini.sh` | LLaDA2-mini 专用 | 8400 |
| `llama-server-nanbeige-3b.sh` | Nanbeige 3B 专用 | 8400 |
| `llama-server-step3-vl-10b.sh` | Step3-VL 10B 专用 | 8400 |
| `llama-server-youtu-vl-4b.sh` | Youtu-VL 4B 专用 | 8400 |
| `update-llama-cpp.sh` | 统一更新脚本 (Vulkan/CUDA) | - |
| `update_report.sh` | 报告更新脚本 | - |

**使用方式**:
```bash
./bin/llama-server-vulkan.sh start    # 启动
./bin/llama-server-vulkan.sh stop     # 停止
./bin/llama-server-vulkan.sh status   # 状态
```

### `config/` - 配置文件

| 文件/目录 | 说明 |
|-----------|------|
| `presets/mypresets.ini` | Vulkan 模型预设 (端口 8400) |
| `presets/mypresets-cuda.ini` | CUDA 模型预设 (端口 8401) |
| `presets/mypresets-hip.ini` | HIP 后端预设 |
| `nginx.conf` | nginx 配置文件 |

### `scripts/` - 工具脚本

#### `scripts/benchmark/` - 性能测试脚本

| 脚本 | 用途 |
|------|------|
| `bench_all_models.sh` | 全模型批量测试 |
| `bench_all_models.py` | Python 版全模型测试 |
| `bench_glm47.py` | GLM-4.7 专项测试 |
| `bench_qwen3_comprehensive.sh` | Qwen3 综合测试 |
| `bench_vulkan_multi_gpu.sh` | 多 GPU Vulkan 测试 |

#### `scripts/test/` - 测试脚本

| 脚本 | 用途 |
|------|------|
| `test_all_gguf_models.py` | 全 GGUF 模型测试 |
| `test_rope_128k.py` | 128K RoPE 测试 |
| `explore_128k_context.py` | 128K 上下文探索 |
| `stage2_test_32k_all_models.py` | Stage2 32K 测试 |
| `stage3_comprehensive_test.py` | Stage3 综合测试 |

#### `scripts/tools/` - 工具脚本

| 脚本 | 用途 |
|------|------|
| `analyze_trending_models.py` | 热门模型分析 |
| `fetch_trending_gguf.py` | 获取热门 GGUF |
| `auto_eval_models.py` | 自动模型评测 |

#### `scripts/utils/` - 实用工具

| 脚本 | 用途 |
|------|------|
| `find-optimal-config.sh` | 查找最优配置 |
| `benchmark_single.sh` | 单模型基准 |
| `quick_context_test.py` | 快速上下文测试 |
| `check_invalid_models.sh` | 检查无效模型 |

### `tests/` - 项目测试脚本

| 脚本 | 用途 |
|------|------|
| `test_3_missing_models.py` | 缺失模型检测 |
| `test_new_models_stage2.py` | 新模型 Stage 2 测试 |
| `test_remaining_5_models_tool.py` | 剩余模型工具测试 |

### `docs/` - 文档目录

#### `docs/guides/` - 使用指南

| 文档 | 内容 |
|------|------|
| `EMBEDDING_MODELS.md` | Embedding 模型使用指南 |
| `EVALUATION_FRAMEWORK.md` | 评测框架说明 |

#### `docs/reports/` - 技术报告

| 文档 | 内容 |
|------|------|
| `HIP_BACKEND_REPORT.md` | HIP 后端报告 |
| `CONFIG_ALIGNMENT_REPORT.md` | 配置对齐报告 |

#### `docs/analysis/` - 分析报告

| 文档 | 内容 |
|------|------|
| `ANALYSIS_SUMMARY.md` | 分析总结 |
| `trending_analysis.md` | 热门模型分析 |

#### `docs/benchmarks/` - 性能测试报告

| 文档 | 内容 |
|------|------|
| `*-V100-benchmark.md` | V100 各模型基准报告 |

### `web/` - Web 报告

| 文件 | 说明 |
|------|------|
| `index.html` | 报告导航首页 |
| `stage1.html` | Stage 1 性能测试报告 |
| `stage2.html` | Stage 2 基础能力报告 |
| `stage3.html` | Stage 3 综合能力报告 |
| `methodology.html` | 测试方法规范 |
| `app.py` | 报告服务器 (可选) |

### `eval_results/` - 评测结果

按阶段和后端组织的测试结果：

```
eval_results/
├── stage1/
│   ├── performance/
│   │   ├── vulkan/         # Vulkan 吞吐量测试
│   │   └── cuda/           # CUDA 吞吐量测试
│   └── context/
│       ├── vulkan/         # Vulkan 上下文测试
│       └── cuda/           # CUDA 上下文测试
├── stage2/
│   ├── vulkan/             # Vulkan Stage 2 结果
│   ├── cuda/               # CUDA Stage 2 结果
│   └── events/vulkan/      # 事件流数据
├── stage3/
│   ├── vulkan/             # Vulkan Stage 3 结果
│   ├── cuda/               # CUDA Stage 3 结果
│   └── tools/              # 工具使用测试
└── raw_data/
    ├── vulkan/             # Vulkan 原始日志
    └── cuda/               # CUDA 原始日志
```

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

### 启动服务
```bash
# Vulkan (AMD)
./bin/llama-server-vulkan.sh start

# CUDA (V100)
./bin/llama-server-cuda.sh start

# Embedding
./bin/llama-server-embedding.sh start
```

### 运行测试
```bash
# Stage 2 测试
python3 eval/run_stage2_single_model_v2.py --model MODEL_NAME

# 全模型测试
python3 scripts/test/test_all_gguf_models.py
```

### 性能测试
```bash
# 运行所有基准
./scripts/benchmark/bench_all_models.sh

# GLM-4.7 专项
python3 scripts/benchmark/bench_glm47.py
```

### 更新 llama.cpp
```bash
# 更新 Vulkan 版本
./bin/update-llama-cpp.sh vulkan

# 更新 CUDA 版本
./bin/update-llama-cpp.sh cuda
```

### 查看报告
```bash
# 通过 nginx 容器
./bin/update_report.sh
# 访问 http://localhost:8080
```

---

## 注意事项

1. **脚本权限**: 所有 `.sh` 脚本已设置为可执行 (`chmod +x`)
2. **路径引用**: 脚本中使用相对路径，需在项目根目录执行
3. **虚拟环境**: Python 脚本使用 `/mnt/volume3/llama_cpp/venv` 环境
4. **日志位置**: 服务日志保存在 `logs/` 目录
5. **模型位置**: GGUF 模型存储在 `/mnt/volume3/gguf/` (按模型分子目录)

---

## 文件命名规范

- **服务器脚本**: `llama-server-{后端}-{模型}[-rope].sh`
- **测试脚本**: `{test|stageN}_{功能}.py`
- **基准脚本**: `bench_{模型|功能}.[sh|py]`
- **工具脚本**: `{动词}_{功能}.py`

---

## 重组历史

### 2026-02-18 - 全面重组

**变更**:
- 新建 `bin/` 目录存放可执行脚本
- 新建 `config/` 目录存放配置文件
- 新建 `tests/` 目录存放测试脚本
- 新建 `web/` 目录存放 Web 报告 (原 `report_web/`)
- 移动 `benchmarks/` → `docs/benchmarks/`
- 重组 `eval_results/` 按阶段和后端分类

**移动的文件**:
- 5 个服务器管理脚本 → `bin/`
- 3 个测试脚本 → `tests/`
- 整个 `presets/` → `config/presets/`
- 整个 `report_web/` → `web/`
- 整个 `benchmarks/` → `docs/benchmarks/`
- 112 个测试结果文件 → `eval_results/` 子目录

---

*目录结构整理完成 - 2026-02-18*
