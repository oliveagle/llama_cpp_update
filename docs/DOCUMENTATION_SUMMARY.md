# 项目文档整理报告

> **整理时间**: 2026-03-02
> **整理范围**: `/mnt/volume3/llama_cpp`
> **整理人**: Claude Code Agent

---

## 整理背景

项目原有文档分散在各处，缺乏统一的索引和组织结构。本次整理旨在建立清晰的文档体系，便于后续维护和查阅。

---

## 完成的工作

### 1. 创建文档索引体系

| 文件 | 位置 | 说明 |
|------|------|------|
| [文档索引](./docs/INDEX.md) | `docs/INDEX.md` | 项目文档总入口 |
| [分析报告索引](./docs/analysis/INDEX.md) | `docs/analysis/INDEX.md` | 分析报告目录 |
| [技术报告索引](./docs/reports/INDEX.md) | `docs/reports/INDEX.md` | 技术报告目录 |
| [待整理文档](./docs/inbox/README.md) | `docs/inbox/README.md` | 待整理文档临时目录 |

### 2. 更新项目 README

- **文件**: `README.md`
- **变更**: 完全重写，反映最新的项目结构和功能
- **新增内容**:
  - 三大核心模块说明 (Core/Dev/Eval)
  - 快速开始命令
  - 目录结构图
  - 服务端口分配表
  - 评测框架说明
  - 文档导航链接

### 3. 文档分类统计

#### 现有文档分布

| 分类 | 文件数 | 说明 |
|------|--------|------|
| `docs/guides/` | 16 | 使用指南、教程 |
| `docs/design/` | 1 | 架构设计文档 |
| `docs/analysis/` | 13 | 分析报告 |
| `docs/reports/` | 5+ | 技术报告 |
| `docs/inbox/` | 1 | 待整理目录说明 |

#### 核心文档列表

**使用指南 (16 篇)**:
- AMD NPU 实现指南
- RyzenAI 后端指南
- ONNX Runtime 服务器指南
- GGUF to ONNX 转换指南
- Qwen3VL ONNX 转换
- Embedding 模型指南
- 评测框架说明
- 评测工具说明
- NPU Qwen3 基准测试
- NPU Qwen3 总结
- AMD NPU 实现计划
- AMD NPU 总结
- Stage2 测试框架分析
- LLaMA.cpp 缓存行为研究
- Nanbeige 代码优化
- Ruvltra 路由指南

**设计文档 (1 篇)**:
- RyzenAI 架构设计

**分析报告 (13 篇)**:
- LLaDA2 局限性分析
- MiniCPM-SALA-GGUF 分析
- 20B/40B 模型基准测试
- 模型对比分析
- Rust Coder 对比
- WeDLM 测试结果
- RyzenAI 服务器分析
- GGUF 模型趋势分析
- 深度趋势分析
- 趋势分析
- 全模型对比
- 分析总结

---

## 新的文档结构

```
docs/
├── INDEX.md                        # 文档总索引 (新增)
├ ├── guides/                       # 使用指南
│   ├── amd-npu-implementation-guide.md
│   ├── ryzenai-backend-guide.md
│   ├── onnx-runtime-server-guide.md
│   ├── gguf-to-onnx.md
│   ├── qwen3vl-onnx-conversion.md
│   ├── EMBEDDING_MODELS.md
│   ├── EVALUATION_FRAMEWORK.md
│   ├── EVAL_TOOLS_GUIDE.md
│   ├── npu-qwen3-benchmark.md
│   ├── npu-qwen3-summary.md
│   ├── amd-npu-implementation-plan.md
│   ├── amd-npu-summary.md
│   ├── stage2-test-framework-analysis.md
│   ├── llama-cpp-cache-behavior-research.md
│   ├── nanbeige-coding-optimization.md
│   └── ruvltra-router-guide.md
│
├ ├── design/                       # 设计文档
│   └── ryzenai-architecture.md
│
├ ├── analysis/                     # 分析报告
│   ├── INDEX.md                    # 分析报告索引 (新增)
│   ├── LLaDA2_LIMITATIONS.md
│   ├── benchmark_20b_40b_models.md
│   ├── trending_gguf_models.md
│   └── ... (共 13 篇)
│
├ ├── reports/                      # 技术报告
│   ├── INDEX.md                    # 技术报告索引 (新增)
│   └── HIP_*.md                    # HIP 后端报告
│
└── inbox/                          # 待整理文档
    └── README.md                   # 目录说明 (新增)
```

---

## 文档导航

### 快速入口

| 需求 | 推荐文档 |
|------|----------|
| 启动服务器 | [README.md](../README.md#快速开始) |
| 项目结构 | [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) |
| 配置说明 | [CLAUDE.md](../CLAUDE.md) |
| 使用指南 | [docs/guides/](./guides/) |
| 评测框架 | [EVALUATION_FRAMEWORK.md](./guides/EVALUATION_FRAMEWORK.md) |
| 分析报告 | [docs/analysis/](./analysis/) |

### 按主题查找

| 主题 | 相关文档 |
|------|----------|
| AMD NPU | amd-npu-implementation-guide.md, amd-npu-summary.md |
| 模型评测 | EVALUATION_FRAMEWORK.md, EVAL_TOOLS_GUIDE.md |
| ONNX | onnx-runtime-server-guide.md, gguf-to-onnx.md, qwen3vl-onnx-conversion.md |
| 性能分析 | npu-qwen3-benchmark.md, benchmark_20b_40b_models.md |

---

## 文档维护规范

### 新增文档流程

1. **创建** - 新文档先放入 `docs/inbox/`
2. **分类** - 确定文档类型 (指南/设计/报告/分析)
3. **移动** - 移动到对应分类目录
4. **索引** - 更新相应 INDEX.md 文件

### 文档命名规范

- 使用小写字母和连字符：`my-guide.md`
- 重要文档可用大写：`EVALUATION_FRAMEWORK.md`
- 中文文档标题使用中文

### 文档结构模板

```markdown
# 文档标题

> **说明**: 简要说明
> **最后更新**: YYYY-MM-DD

## 概述

文档内容概述

## 详细内容

...

## 相关文件

- [相关文档](./related-doc.md)
```

---

## 待改进事项

### 短期改进

1. **补充缺失文档**
   - [ ] Core 模块使用说明
   - [ ] Dev 模块开发指南
   - [ ] Eval 模块评测指南

2. **优化现有文档**
   - [ ] 更新过时的命令和路径
   - [ ] 添加更多示例代码
   - [ ] 补充图表和流程图

3. **索引完善**
   - [ ] 添加关键词索引
   - [ ] 添加文档间交叉引用
   - [ ] 创建常见问题 FAQ

### 长期改进

1. **文档自动化**
   - [ ] 自动生成 API 文档
   - [ ] 自动更新评测报告
   - [ ] 文档版本管理

2. **多语言支持**
   - [ ] 中文文档为主
   - [ ] 关键文档提供英文版本

---

## 总结

本次整理建立了清晰的文档索引体系，包含：

- **1 个总索引**: `docs/INDEX.md`
- **3 个分类索引**: guides/, analysis/, reports/
- **30+ 篇文档**: 涵盖使用指南、设计文档、技术报告、分析报告

文档体系已初具规模，能够满足日常开发和运维需求。后续将按照维护规范持续更新和完善。

---

*整理报告完成 - 2026-03-02*
