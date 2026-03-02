# 文档索引

> **项目**: llama.cpp 多后端管理与评估平台
> **最后更新**: 2026-03-02
> **文档版本**: v2.0

---

## 快速入口

| 文档 | 说明 | 位置 |
|------|------|------|
| [项目结构](../PROJECT_STRUCTURE.md) | 完整的目录结构说明 | 根目录 |
| [配置说明](../CLAUDE.md) | 项目配置和使用说明 | 根目录 |
| [协作记录](../AGENTS-COLLABORATION.md) | 多 Agent 协作记录 | 根目录 |
| [使用指南](./guides/) | 各类使用和开发指南 | docs/guides/ |

---

## 文档分类

### 使用指南 (Guides)

| 文档 | 说明 |
|------|------|
| [AMD NPU 实现指南](./guides/amd-npu-implementation-guide.md) | AMD NPU 后端实现完整指南 |
| [RyzenAI 后端指南](./guides/ryzenai-backend-guide.md) | RyzenAI 后端使用指南 |
| [ONNX Runtime 服务器指南](./guides/onnx-runtime-server-guide.md) | ONNX Runtime 服务部署指南 |
| [GGUF to ONNX 转换指南](./guides/gguf-to-onnx.md) | 模型格式转换指南 |
| [Qwen3VL ONNX 转换](./guides/qwen3vl-onnx-conversion.md) | Qwen3VL 模型转换实践 |
| [Embedding 模型指南](./guides/EMBEDDING_MODES.md) | Embedding 模型使用说明 |
| [评测框架说明](./guides/EVALUATION_FRAMEWORK.md) | 评测框架使用指南 |
| [评测工具说明](./guides/EVAL_TOOLS_GUIDE.md) | 评测工具使用说明 |

### 设计文档 (Design)

| 文档 | 说明 |
|------|------|
| [RyzenAI 架构设计](./design/ryzenai-architecture.md) | RyzenAI 架构设计文档 |

### 技术报告 (Reports)

| 文档 | 说明 |
|------|------|
| [HIP 后端报告](./reports/) | HIP 后端性能测试报告 |
| [评测报告](../eval/reports/) | 模型评测报告 |

**技术报告索引**: [reports/INDEX.md](./reports/INDEX.md) - 完整技术报告列表

### 分析报告 (Analysis)

| 文档 | 说明 |
|------|------|
| [NPU Qwen3 基准测试](./guides/npu-qwen3-benchmark.md) | Qwen3 NPU 性能分析 |
| [NPU Qwen3 总结](./guides/npu-qwen3-summary.md) | NPU Qwen3 测试总结 |
| [AMD NPU 实现计划](./guides/amd-npu-implementation-plan.md) | AMD NPU 实现计划 |
| [AMD NPU 总结](./guides/amd-npu-summary.md) | AMD NPU 实现总结 |
| [Stage2 测试框架分析](./guides/stage2-test-framework-analysis.md) | Stage2 测试框架分析 |
| [LLaMA.cpp 缓存行为研究](./guides/llama-cpp-cache-behavior-research.md) | 缓存机制研究 |
| [Nanbeige 代码优化](./guides/nanbeige-coding-optimization.md) | Nanbeige 模型代码优化 |
| [Ruvltra 路由指南](./guides/ruvltra-router-guide.md) | Ruvltra 路由实现指南 |
| [LLaDA2 局限性分析](./analysis/LLaDA2_LIMITATIONS.md) | 扩散模型局限性分析 |
| [20B/40B 模型基准测试](./analysis/benchmark_20b_40b_models.md) | 大模型性能测试 |
| [模型趋势分析](./analysis/trending_gguf_models.md) | GGUF 模型趋势分析 |

**分析报告索引**: [analysis/INDEX.md](./analysis/INDEX.md) - 完整分析报告列表

### 评测结果 (Evaluation Results)

| 文档 | 说明 | 位置 |
|------|------|------|
| [评测结果](../eval/results/) | 各阶段评测结果 | eval/results/ |
| [Web 报告](../eval/web/) | Web 可视化报告 | eval/web/ |
| [Dashboard](~/.agents/dashboard/llama-eval/) | 评测 Dashboard | 外部链接 |

---

## 核心模块文档

### Core - llama.cpp 核心管理

| 文档 | 说明 |
|------|------|
| [服务器管理](../core/scripts/) | 服务器启动/停止脚本 |
| [配置文件](../core/config/) | 模型预设和配置 |
| [systemd 服务](../core/systemd/) | 系统服务配置 |

### Dev - 功能开发

| 文档 | 说明 |
|------|------|
| [NPU 开发](../dev/src/amdxdna_npu/) | AMD XDNA NPU 开发 |
| [ONNX Runtime](../dev/src/onnx-runtime/) | ONNX Runtime 集成 |
| [NanoQuant](../dev/nanoquant/) | 量化工具开发 |
| [RyzenAI](../dev/ryzenai/) | RyzenAI 工具 |

### Eval - 大模型评测

| 文档 | 说明 |
|------|------|
| [评测框架](../eval/framework/) | 评测框架代码 |
| [评测测试](../eval/tests/) | 各阶段评测测试 |
| [评测脚本](../eval/scripts/) | 评测辅助脚本 |
| [评测工具](../eval/tools/) | 评测工具集 |

---

## 外部资源

| 资源 | 说明 | 链接 |
|------|------|------|
| llama.cpp 官方 | 上游项目 | https://github.com/ggerganov/llama.cpp |
| HuggingFace | 模型仓库 | https://huggingface.co/ |
| ModelScope | 模型仓库 (国内) | https://modelscope.cn/ |

---

## 文档维护规范

### 文档分类

- `guides/` - 使用指南、教程、操作说明
- `design/` - 架构设计、技术方案
- `reports/` - 技术报告、测试结果
- `analysis/` - 分析报告、问题诊断

### 文档命名

- 使用小写字母和连字符：`my-guide.md`
- 重要文档可用大写：`EVALUATION_FRAMEWORK.md`
- 中文文档标题使用中文

### 文档结构

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

*文档索引 v2.0 - 2026-03-02*
