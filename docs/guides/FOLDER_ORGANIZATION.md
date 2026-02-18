# 目录整理总结

> **整理时间**: 2026-02-18
> **整理范围**: `/mnt/volume3/llama_cpp`

---

## 整理背景

项目根目录积累了大量脚本文件（超过 60 个），包括：
- 服务器管理脚本
- 性能测试脚本
- 模型测试脚本
- 工具脚本
- 文档文件

这些文件混杂在一起，难以快速定位所需脚本。

---

## 整理方案

### 新目录结构

```
scripts/
├── server/      # 服务器管理脚本
├── benchmark/   # 性能测试脚本
├── test/        # 测试脚本
├── tools/       # 工具脚本
└── utils/       # 实用工具

docs/
├── guides/      # 使用指南
├── reports/     # 技术报告
└── analysis/    # 分析报告
```

---

## 整理统计

### 脚本分类 (63 个)

| 类别 | 数量 | 说明 |
|------|------|------|
| `scripts/server/` | 15 | llama-server 各后端/模型专用启动脚本 |
| `scripts/benchmark/` | 14 | 性能测试和基准测试脚本 |
| `scripts/test/` | 18 | Stage2/Stage3 评测及功能测试脚本 |
| `scripts/tools/` | 4 | 模型分析、趋势获取等工具 |
| `scripts/utils/` | 12 | 更新脚本、配置查找等实用工具 |

### 文档分类 (13 个)

| 类别 | 数量 | 说明 |
|------|------|------|
| `docs/guides/` | 3 | Embedding 指南、评测框架说明 |
| `docs/reports/` | 5 | HIP 后端报告、诊断报告 |
| `docs/analysis/` | 5 | 模型分析、趋势分析 |

### 新增文件

| 文件 | 用途 |
|------|------|
| `PROJECT_STRUCTURE.md` | 完整的目录结构说明文档 |
| `docs/guides/FOLDER_ORGANIZATION.md` | 本整理总结文档 |

---

## 路径变更

### 服务器脚本

| 原路径 | 新路径 |
|--------|--------|
| `./llama-server-vulkan.sh` | `./scripts/server/llama-server-vulkan.sh` |
| `./llama-server-cuda.sh` | `./scripts/server/llama-server-cuda.sh` |
| `./llama-server-embedding.sh` | `./scripts/server/llama-server-embedding.sh` |
| `./llama-server-*.sh` | `./scripts/server/llama-server-*.sh` |

### 更新脚本

| 原路径 | 新路径 |
|--------|--------|
| `./update-llama-cpp.sh` | `./scripts/utils/update-llama-cpp.sh` |

### 测试脚本

| 原路径 | 新路径 |
|--------|--------|
| `./test_*.py` | `./scripts/test/test_*.py` |
| `./stage2_*.py` | `./scripts/test/stage2_*.py` |
| `./stage3_*.py` | `./scripts/test/stage3_*.py` |
| `./diagnose_*.py` | `./scripts/test/diagnose_*.py` |
| `./check_*.py` | `./scripts/test/check_*.py` |

### 基准脚本

| 原路径 | 新路径 |
|--------|--------|
| `./bench_*.sh` | `./scripts/benchmark/bench_*.sh` |
| `./bench_*.py` | `./scripts/benchmark/bench_*.py` |
| `./benchmark_all_models.py` | `./scripts/benchmark/benchmark_all_models.py` |

### 文档

| 原路径 | 新路径 |
|--------|--------|
| `./EMBEDDING_MODELS.md` | `./docs/guides/EMBEDDING_MODELS.md` |
| `./EVALUATION_FRAMEWORK.md` | `./docs/guides/EVALUATION_FRAMEWORK.md` |
| `./EVAL_TOOLS_GUIDE.md` | `./docs/guides/EVAL_TOOLS_GUIDE.md` |
| `./HIP_*.md` | `./docs/reports/HIP_*.md` |
| `./ANALYSIS_SUMMARY.md` | `./docs/analysis/ANALYSIS_SUMMARY.md` |
| `./trending_*.md` | `./docs/analysis/trending_*.md` |
| `./benchmark_20b_40b_models.md` | `./docs/analysis/benchmark_20b_40b_models.md` |

---

## 更新后的使用方式

### 启动服务

```bash
# Vulkan 服务器
./scripts/server/llama-server-vulkan.sh start

# CUDA 服务器
./scripts/server/llama-server-cuda.sh start

# Embedding 服务器
./scripts/server/llama-server-embedding.sh start
```

### 运行测试

```bash
# Stage 2 测试
python3 scripts/test/stage2_single_model_test.py --model MODEL_NAME

# Stage 3 测试
python3 scripts/test/stage3_comprehensive_test.py --model MODEL_NAME

# 全模型测试
python3 scripts/test/test_all_gguf_models.py
```

### 性能测试

```bash
# 全模型基准
./scripts/benchmark/bench_all_models.sh

# Python 版
python3 scripts/benchmark/benchmark_all_models.py

# GLM-4.7 专项
python3 scripts/benchmark/bench_glm47.py
```

### 更新 llama.cpp

```bash
./scripts/utils/update-llama-cpp.sh vulkan
./scripts/utils/update-llama-cpp.sh cuda
```

---

## 保留在根目录的文件

以下文件保留在项目根目录：

| 文件 | 原因 |
|------|------|
| `CLAUDE.md` | 项目主配置文档 |
| `AGENTS.md` | 指向 CLAUDE.md 的软链接 |
| `AGENTS-COLLABORATION.md` | Agent 协作记录 |
| `PROJECT_STRUCTURE.md` | 目录结构说明 |
| `README.md` | 项目说明 |
| `LICENSE` | 许可证 |

---

## 维护建议

1. **新增脚本**: 根据功能放入对应子目录
2. **命名规范**: 保持 `类别_功能.扩展名` 格式
3. **权限设置**: `.sh` 脚本保持可执行权限
4. **文档更新**: 修改 `PROJECT_STRUCTURE.md` 同步变更

---

*整理完成 - 2026-02-18*
