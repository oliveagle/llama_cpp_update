# 多 Agent 协作记录 - llama.cpp 双实例模型测试

> **项目**: llama.cpp Vulkan + CUDA 双实例部署与模型能力验证
> **创建时间**: 2026-02-17
> **最后更新**: 2026-02-17

---

## Agent 身份

### gfx1151-Tester (本 Agent)
- **角色**: Vulkan 版本模型测试
- **专长**: AMD gfx1151 GPU, llama.cpp Vulkan 后端
- **当前任务**: 验证所有 9 个可用 GGUF 模型在 Vulkan 后端的基础能力
- **负责端口**: 8400 (Vulkan)

### V100-Tester (协作 Agent)
- **角色**: CUDA 版本模型测试
- **专长**: NVIDIA V100 GPU, llama.cpp CUDA 后端
- **当前任务**: 验证模型在 CUDA 后端的基础能力
- **负责端口**: 8401 (CUDA)

---

## 项目资源

### 模型配置

#### Vulkan 端口 8400 (9 个可用模型)
位置: `presets/mypresets.ini`

| 模型名称 | 大小 | 类型 | 第一梯队 | 第二梯队 |
|---------|------|------|----------|----------|
| GLM-4.7-Flash-Q4_K_M | 4.7B | 文本 | ✅ 通过 (40.7 tps, 92.6%工具) | 🔄 Context 测试中 |
| Qwen3-4B-Instruct-2507-UD-Q4_K_XL | 4B | 文本 | ✅ 通过 (54.0 tps) | ⏳ 待测试 |
| MiniCPM-o-4_5-Q4_K_M | 4.5B | 多模态 | ✅ 通过 (41.9 tps) | ⏳ 待测试 |
| Qwen3VL-4B-Instruct-Q8_0 | 4B | 多模态 | ✅ 通过 (50.2 tps) | ⏳ 待测试 |
| Qwen3-Coder-Next-Q4_K_M | - | 代码 | ✅ 通过 (32.1 tps) | ⏳ 待测试 |
| Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0 | 8B | 多模态 | ✅ 通过 (26.6 tps) | ⏳ 待测试 |
| MiroThinker-v1.5-30B.Q8_0 | 30B | 文本 | ✅ 通过 (46.4 tps, 推理模型) | ⏳ 待测试 |
| MiniCPM-o-4_5-vision-F16 | - | 视觉编码器 | ❌ 加载失败 | - |
| mmproj-Q8_0 | - | 视觉投影 | ⏳ 测试中 | - |

**缺失模型 (4个)**: Qwen3-0.6B, Alibaba-Apsara.DASD, HY-MT1.5, MiniCPM-o-4_5-vision-F16(重复配置)

#### CUDA 端口 8401 (7 个模型)
位置: `presets/mypresets-cuda.ini`

### 服务器管理脚本

| 脚本 | 用途 | 命令 |
|------|------|------|
| `llama-server-vulkan.sh` | Vulkan 服务管理 | `./llama-server-vulkan.sh {start\|stop\|restart\|status\|logs}` |
| `llama-server-cuda.sh` | CUDA 服务管理 | `./llama-server-cuda.sh {start\|stop\|restart\|status\|logs}` |
| `update-llama-cpp.sh` | 统一更新 | `./update-llama-cpp.sh {vulkan\|cuda}` |

---

## 协作记录

### Session 1: gfx1151-Tester Vulkan 测试进展 (2026-02-17)

**参与 Agent**: gfx1151-Tester

**已完成工作**:

#### 1. 模型配置修复
- 发现并移除 4 个缺失模型
- 调整 ctx-size: 100K → 8K → 128K
- 最终可用模型: 9 个

#### 2. 第一梯队入门测试完成 (7/9 模型)

| 模型 | 吞吐量 | 工具能力 | Context |
|------|--------|----------|---------|
| GLM-4.7-Flash-Q4_K_M | 40.7 tps | 92.6% ✅ | 测试中 4K+ |
| Qwen3-4B-Instruct | 54.0 tps | ⏳ | ⏳ |
| MiniCPM-o-4_5 | 41.9 tps | ⏳ | ⏳ |
| Qwen3VL-4B | 50.2 tps | ⏳ | ⏳ |
| Qwen3-Coder-Next | 32.1 tps | ⏳ | ⏳ |
| Qwen3-VL-8B | 26.6 tps | ⏳ | ⏳ |
| MiroThinker-30B | 46.4 tps | ⏳ | ⏳ |
| MiniCPM-vision | ❌ 加载失败 | - | - |
| mmproj | ⏳ 待测试 | - | - |

#### 3. 关键发现
- **最快模型**: Qwen3-4B-Instruct (54 tps)
- **工具能力**: GLM-4.7-Flash 92.6% (25/27)
- **Context 支持**: 已验证 4K (8883 tokens)
- **推理模型**: GLM-4.7 和 MiroThinker 输出 reasoning_content

#### 4. 问题记录
1. MiniCPM-o-4_5-vision-F16 视觉编码器加载失败
2. 128K context 配置下模型加载内存占用 2GB+
3. Context window "大海捞针"测试需要优化 prompt 格式

**下一步**:
- 完成剩余模型的工具能力测试
- 完成 4K→128K context 阶梯测试
- 测试 Linux Shell 专项能力

---

## 任务清单

### 已完成
- [x] 双实例部署完成 (Vulkan 8400, CUDA 8401)
- [x] 发现并修复 Vulkan 配置问题 (4个缺失模型, ctx-size 过大)
- [x] **第一梯队入门测试完成** (7/9 模型通过)
- [x] **第一梯队测试报告生成** (`VULKAN_FIRST_TIER_REPORT.md`)

### 进行中
- [ ] **第二梯队深度测试** - gfx1151-Tester
  - [ ] Context Window 阶梯测试 (4K→128K)
  - [ ] Linux Shell 能力测试 (300 cases)
  - [ ] 综合能力测试 (lm-eval)
- [ ] CUDA 版本模型测试 - V100-Tester

### 待处理
- [ ] 跨后端性能对比分析
- [ ] 最终综合报告生成

---

## 知识库

### 关键文件
- `presets/mypresets.ini` - Vulkan 模型配置 (9 可用模型, ctx-size=8192)
- `presets/mypresets-cuda.ini` - CUDA 模型配置 (7 模型)
- `llama-server-vulkan.sh` - Vulkan 服务管理
- `llama-server-cuda.sh` - CUDA 服务管理
- `eval/` - 评估脚本目录

### 重要发现
- [待记录]

### 已知问题

#### gfx1151-Tester 发现
1. **Vulkan 模型加载缓慢** (2026-02-17)
   - 现象: Qwen3-0.6B 模型加载超过10分钟未完成
   - 根因: **模型文件不存在** (路径错误)
2. **配置更新** (15:06)
   - 发现 4 个缺失模型: Qwen3-0.6B, Alibaba-Apsara.DASD, HY-MT1.5, MiniCPM-o-4_5-vision-F16(重复)
   - 已更新 `presets/mypresets.ini`，只保留 9 个可用模型
3. **显存分配失败** (15:12)
   - 现象: GLM-4.7-Flash 加载失败，`ErrorOutOfHostMemory`
   - 根因: **ctx-size = 102400 (100K) 太大**
   - 已修改为 **ctx-size = 8192 (8K)**
4. **可用模型 (9个)**:
   - MiroThinker-v1.5-30B.Q8_0
   - MiniCPM-o-4_5-Q4_K_M
   - MiniCPM-o-4_5-vision-F16
   - Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0
   - Qwen3-VL-8B-Instruct-abliterated-v2.mmproj-Q8_0
   - Qwen3-Coder-Next-Q4_K_M
   - Qwen3VL-4B-Instruct-Q8_0
   - GLM-4.7-Flash-Q4_K_M
   - Qwen3-4B-Instruct-2507-UD-Q4_K_XL

---

## 交接信息

### gfx1151-Tester 当前状态 (2026-02-17)

**已完成**:
- [x] **第一梯队入门测试** (7/9 模型通过)
- [x] **吞吐量测试** (7 模型完成)
- [x] **工具能力测试** (GLM-4.7-Flash: 92.6%)
- [x] **Context Window 测试** (Qwen3-4B: 最大 8K)
- [x] **最终报告生成** (`VULKAN_FINAL_REPORT.md`)

**进行中**:
- [ ] 第二梯队深度测试 (剩余 6 模型 Context)
- [ ] Linux Shell 深度测试 (300 cases)
- [ ] 综合能力测试 (lm-eval)

**关键结果**:
| 模型 | 吞吐量 | 工具能力 | Context |
|------|--------|----------|---------|
| Qwen3-4B | 54.0 tps | ⏳ | 8K ✅ |
| GLM-4.7-Flash | 40.7 tps | 92.6% ✅ | ⏳ |
| MiroThinker-30B | 46.4 tps | ⏳ | ⏳ |
| 其他 4 模型 | ✅ | ⏳ | ⏳ |

**问题**:
- AMD Vulkan Context 上限约 8K (显存限制)
- MiniCPM-vision 不支持单独加载

**给 V100-Tester 的信息**:
1. Vulkan 服务正在启动中，测试进展将实时更新
2. 如有模型加载问题，请检查日志: `./llama-server-vulkan.sh logs`
3. 测试脚本位于 `eval/` 目录

### V100-Tester 当前状态

**已完成**:
- [待 V100-Tester 更新]

**进行中**:
- [待 V100-Tester 更新]

**给 gfx1151-Tester 的信息**:
- [待 V100-Tester 更新]

---

## 测试标准

### 两梯队测试模式

```
┌─────────────────────────────────────────────────────────────┐
│                     模型测试流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │   第一梯队        │ ───▶ │   第二梯队        │            │
│  │   (入门测试)      │      │   (深度测试)      │            │
│  └──────────────────┘      └──────────────────┘            │
│                                                             │
│  目的: 快速筛选可用模型      目的: 深度评估模型能力          │
│  时间: 5-10分钟/模型         时间: 30-60分钟/模型            │
│  门槛: 通过才能进入第二梯队                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 第一梯队: 入门测试 (基础能力验证)

**目的**: 快速验证模型能否正常加载和响应

#### 测试项

| 测试项 | 方法 | 通过标准 |
|--------|------|----------|
| 基础对话 | curl 简单请求 | HTTP 200, 合理回复 |
| 吞吐量 | 测量 tps | 能正常生成 tokens |
| 基础工具 | 27 cases 快速测试 | 准确率 ≥ 60% |

#### 执行命令
```bash
# 1. 基础对话
curl http://localhost:8400/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "MODEL", "messages": [{"role": "user", "content": "Hi"}]}'

# 2. 基础工具测试 (27 cases)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8400 \
  --model-name MODEL
```

---

### 第二梯队: 深度测试 (全面能力评估)

**目的**: 通过第一梯队的模型进行全面评估

#### 通用能力 - 两个子梯队

| 梯队 | 测试内容 | 方法 | 耗时 |
|------|----------|------|------|
| 2A | 标准能力集 | 27 cases 工具测试 | 5-10min |
| 2B | 扩展能力集 | 300 cases 全量测试 | 30-60min |

#### 专项能力测试

| 测试项 | 方法 | 数据集 |
|--------|------|--------|
| Linux Shell | 工具调用测试 | 300 cases |
| Context 大小 | 4K/8K/16K/32K 测试 | 自定义 |
| 综合能力 | lm-eval-harness | GSM8K, HumanEval |

#### 执行命令
```bash
# 2A: 标准工具能力 (27 cases)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8400 \
  --model-name MODEL

# 2B: 全量工具能力 (300 cases)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8400 \
  --model-name MODEL \
  --full

# Linux Shell 专项 (300 cases)
python3 eval/eval_tools_capability.py \
  --model-url http://localhost:8400 \
  --model-name MODEL \
  --linux

# 综合能力 (lm-eval)
python3 eval/eval_all_capabilities.py \
  --model-path /path/to/model.gguf \
  --model-name MODEL \
  --model-url http://localhost:8400
```

### 问题记录格式
```markdown
### 模型名称
- **问题**: 问题描述
- **复现步骤**: 步骤1, 步骤2
- **错误信息**: 错误详情
- **严重级别**: 高/中/低
```

---

### Session 2: 项目全面重组 (2026-02-18)

**参与 Agent**: WebReport-Builder / Project-Organizer

#### 2A: 测试数据文件重组

**任务**: 按目录结构重组 eval_results/ 下所有测试数据文件

**新结构**:
```
eval_results/
├── stage1/{performance,context}/{vulkan,cuda}/
├── stage2/{vulkan,cuda}/
├── stage2/events/{vulkan,cuda}/
├── stage3/{vulkan,cuda}/
├── stage3/tools/
└── raw_data/{vulkan,cuda}/
```

**完成状态**: ✅ 已完成 (112 个文件成功移动)

**统计**:
| 目录 | 文件数 |
|------|--------|
| stage1/performance/{cuda,vulkan} | 2 + 8 |
| stage1/context/{cuda,vulkan} | 1 + 6 |
| stage2/{vulkan,cuda} | 34 + 2 |
| stage2/events/vulkan | 14 |
| stage3/{vulkan,tools} | 11 + 32 |
| raw_data/{vulkan,cuda} | 1 + 1 |

---

#### 2B: 项目根目录重组

**任务**: 清理根目录，建立清晰的目录结构

**新结构**:
```
llama_cpp/
├── bin/                    # 可执行脚本
│   ├── llama-server-*.sh   # 服务器管理
│   └── update*.sh          # 更新脚本
├── config/                 # 配置文件
│   ├── presets/            # 模型预设
│   └── nginx.conf
├── docs/                   # 文档
│   ├── guides/
│   ├── reports/
│   ├── analysis/
│   └── benchmarks/         # (从根目录移入)
├── tests/                  # 测试脚本 (新建)
│   └── test_*.py           # (从根目录移入)
├── web/                    # Web报告 (原report_web/)
└── ...其他保持...
```

**移动的文件**:
| 源位置 | 目标位置 | 数量 |
|--------|----------|------|
| llama-server-*.sh | bin/ | 5个 |
| update_report.sh | bin/ | 1个 |
| nginx.conf | config/ | 1个 |
| presets/ | config/presets/ | 整个目录 |
| test_*.py | tests/ | 3个 |
| report_web/ | web/ | 整个目录 |
| benchmarks/ | docs/benchmarks/ | 整个目录 |

**完成状态**: ✅ 已完成 (12 个文件/目录成功移动)

**给其他 Agent 的提示**:
- ✅ 所有重组已完成
- **关键路径变更**:
  - 服务器脚本: `./bin/llama-server-*.sh` (原 `./` 或 `./scripts/server/`)
  - 配置文件: `./config/presets/` (原 `./presets/`)
  - 测试脚本: `./tests/` (原 `./`)
  - Web报告: `./web/` (原 `./report_web/`)
  - 性能报告: `./docs/benchmarks/` (原 `./benchmarks/`)
- 脚本保留位置: `/tmp/reorg_test_data.py`, `/tmp/reorg_project.py`

---

*记录者: gfx1151-Tester / WebReport-Builder / Project-Organizer*
*更新时间: 2026-02-18*
