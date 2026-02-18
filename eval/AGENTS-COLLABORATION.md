# Linux/Shell 操作测试 - Agent 协作记录

> **项目**: llama.cpp 模型工具调用能力评估
> **创建时间**: 2026-02-17
> **最后更新**: 2026-02-17

---

## Agent 身份

### eval-Architect (本 Agent)
- **角色**: 测试框架设计与实现
- **专长**: Python开发、测试用例设计、评估脚本编写
- **当前任务**: 创建Linux/Shell操作两阶段测试系统

### gfx1151-Tester (另一个 Agent)
- **角色**: Vulkan模型测试执行
- **专长**: 模型部署、性能测试
- **当前任务**: 测试vulkan版本模型的工具调用能力

---

## 测试规范文档

### 测试体系结构

```
两阶段测试系统
├── 入门测试 (30案例)
│   ├── 目的: 快速筛选基础能力
│   ├── 门槛: 40%通过率
│   └── 失败处理: 跳过深度测试，分析原因
│
└── 深度测试 (300案例)
    ├── 目的: 全面评估运维能力
    ├── 条件: 入门测试通过才执行
    └── 覆盖: Docker/Shell/网络/进程/系统等
```

### 文件位置

| 文件 | 用途 | 案例数 |
|------|------|--------|
| `eval_linux_ops.py` | 两阶段评估入口 | - |
| `linux_ops_basic_cases.py` | 入门测试集 | 30 |
| `linux_ops_test_cases.py` | 深度测试集 | 300 |
| `eval_tools_capability.py` | 基础评估引擎 | - |

### 使用方法

```bash
cd /mnt/volume3/llama_cpp/eval

# 仅运行入门测试
python3 eval_linux_ops.py \
  --model-url http://localhost:8401 \
  --model-name MODEL_NAME \
  --basic-only

# 自动两阶段测试
python3 eval_linux_ops.py \
  --model-url http://localhost:8401 \
  --model-name MODEL_NAME

# 强制完整测试(忽略门槛)
python3 eval_linux_ops.py \
  --model-url http://localhost:8401 \
  --model-name MODEL_NAME \
  --force-full
```

### 入门测试案例分布 (30个)

| 类别 | 数量 | 示例 |
|------|------|------|
| 文件操作 | 6 | ls, pwd, mkdir, cp, mv, rm |
| 文本处理 | 4 | cat, head, grep, wc |
| 系统信息 | 4 | df, free, whoami, date |
| 进程管理 | 4 | ps, kill, top, pgrep |
| 网络管理 | 4 | ping, curl, ssh, netstat |
| 容器操作 | 4 | docker run/ps/stop/logs |
| Shell脚本 | 4 | 变量、循环、判断、脚本创建 |

### 评估标准

- **入门测试通过**: >= 40% (12/30)
- **深度测试触发**: 仅入门测试通过
- **能力评级**:
  - 优秀: >= 70%
  - 良好: 50-69%
  - 一般: 30-49%
  - 差: < 30%

---

## 当前测试状态

### JoyAI-LLM-Flash-Q4_K_M (CUDA/V100)

| 测试类型 | 结果 | 说明 |
|----------|------|------|
| 通用工具测试(300) | 44.0% | 日常工具场景表现一般 |
| Linux入门测试(30) | **0.0%** | 完全不支持系统运维工具 |
| Linux深度测试(300) | 未执行 | 入门测试未通过 |

**诊断结论**: 模型倾向直接回答问题，而非使用工具调用。不适合系统运维场景。

---

## 待处理任务

### gfx1151-Tester (另一个Agent)
- [ ] 使用本测试框架测试vulkan模型
- [ ] 对比vulkan与cuda版本的工具调用能力差异
- [ ] 记录在 `eval_results/` 目录

### eval-Architect
- [x] 设计两阶段测试体系
- [x] 创建30案例入门测试集
- [x] 实现自动门槛判断
- [x] 编写失败原因分析
- [ ] 根据vulkan测试结果优化测试集

---

## 发现与建议

### 问题发现
1. JoyAI-LLM-Flash 对Linux命令工具调用**完全不识别**
2. 模型倾向直接回答"如何操作"而非调用工具
3. 可能是训练数据缺乏系统运维场景

### 改进建议
1. **Prompt工程**: 在prompt中明确要求"请使用工具执行命令"
2. **工具描述**: 增强execute_command的描述，强调必须调用
3. **模型选择**: 系统运维场景需要专门训练的DevOps模型

---

## 关键文件路径

```
/mnt/volume3/llama_cpp/eval/
├── eval_linux_ops.py           # 两阶段评估入口 ⭐
├── linux_ops_basic_cases.py    # 入门测试30案例 ⭐
├── linux_ops_test_cases.py     # 深度测试300案例 ⭐
├── eval_tools_capability.py    # 基础评估引擎
└── AGENTS-COLLABORATION.md     # 本文档 ⭐
```

---

## 交接信息

### 传递给 gfx1151-Tester
1. 测试框架已完成，可直接使用
2. 运行命令见上方"使用方法"
3. 测试结果会保存到 `eval_results/` 目录
4. 如有问题，查看入门测试30案例的设计是否合理

### 注意事项
- 确保llama-server启用了`--jinja`参数
- 测试不会真实执行命令，只验证工具调用格式
- 入门测试0%通过是正常的，说明模型不适合运维场景

---

*记录者: eval-Architect*
*更新时间: 2026-02-17*
