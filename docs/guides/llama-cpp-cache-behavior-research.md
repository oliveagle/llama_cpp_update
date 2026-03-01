# llama.cpp 缓存行为差异研究报告

> **研究时间**: 2026-02-26
> **研究主题**: 为什么 Qwen3.5-35B-A3B 的 prompt 缓存效果明显差于 JoyAI-LLM-Flash

---

## 问题描述

在 Stage 1 Context 梯度测试中，发现两个模型的缓存行为存在显著差异：

| 模型 | 架构 | Cold | Cache | 缓存效果 |
|------|------|------|-------|----------|
| JoyAI-LLM-Flash | DeepSeek2 | 254ms | 34ms | **86% 提升** |
| Qwen3.5-35B-A3B | Qwen35MoE | 115ms | 98ms | **15% 提升** |

Qwen3.5 的缓存几乎不起作用，这是为什么？

---

## 调查过程

### 1. 排除版本差异

- JoyAI 测试使用: b8069 (Vulkan)
- Qwen3.5 测试使用: b8134 (CUDA)
- **验证**: 用 b8134 CUDA 测试 JoyAI，缓存效果依然存在 (254ms → 34ms)
- **结论**: 不是版本问题

### 2. 排除后端差异

- 用相同 CUDA 后端测试两个模型
- JoyAI 缓存有效，Qwen3.5 缓存失效
- **结论**: 不是后端问题

### 3. 分析日志差异

**JoyAI (缓存有效)**:
```
selected slot by LCP similarity, sim_best = 1.000
prompt processing progress, n_tokens = 43, batch.n_tokens = 1
```
→ 只计算 1 个 token，42 个从缓存读取

**Qwen3.5 (缓存失效)**:
```
selected slot by LCP similarity, sim_best = 1.000
failed to truncate tokens with position >= 14 - clearing the memory
slot prompt_clear: clearing prompt with 14 tokens
prompt processing progress, n_tokens = 15, batch.n_tokens = 15
```
→ 缓存被清除，重新计算全部 15 个 token

### 4. 源码分析

#### 发现 1: Qwen35MoE 是 Hybrid 架构

文件: `src/llama-arch.cpp:2833`

```cpp
bool llm_arch_is_hybrid(const llm_arch & arch) {
    switch (arch) {
        case LLM_ARCH_JAMBA:
        case LLM_ARCH_FALCON_H1:
        case LLM_ARCH_QWEN35:       // ← Qwen3.5
        case LLM_ARCH_QWEN35MOE:    // ← Qwen3.5 MoE
            return true;
        ...
    }
}
```

#### 发现 2: Hybrid 架构使用 Checkpoint 机制

文件: `tools/server/server-context.cpp:2473-2510`

```cpp
// make checkpoints only for completion tasks
do_checkpoint = do_checkpoint && slot.task->type == SERVER_TASK_TYPE_COMPLETION;

// make a checkpoint of the parts of the memory that cannot be rolled back.
// checkpoints are created only if:
// - the model uses SWA and we are not using `swa_full`
// - the model architecture is marked as recurrent or hybrid
do_checkpoint = do_checkpoint && (
        llama_model_is_recurrent(model) ||
        llama_model_is_hybrid(model) ||
        (llama_model_n_swa(model) > 0 && !params_base.swa_full)
        );
```

#### 发现 3: Hybrid 架构缓存失效时强制完整重处理

文件: `tools/server/server-context.cpp:2377`

```cpp
SLT_WRN(slot, "forcing full prompt re-processing due to lack of cache data "
        "(likely due to SWA or hybrid/recurrent memory, see %s)\n",
        "https://github.com/ggml-org/llama.cpp/pull/13194#issuecomment-2868343055");
n_past = 0;  // ← 强制从头计算
```

#### 发现 4: Truncate 失败导致缓存清除

文件: `tools/server/server-context.cpp:2430`

```cpp
if (!llama_memory_seq_rm(llama_get_memory(ctx), slot.id, p0, -1)) {
    SLT_WRN(slot, "failed to truncate tokens with position >= %d - clearing the memory\n", p0);
    slot.prompt_clear(true);  // ← 清除缓存
    slot.n_prompt_tokens_cache = 0;
}
```

---

## 根本原因

### 架构差异

| 特性 | 标准 Transformer (JoyAI) | Hybrid (Qwen3.5) |
|------|-------------------------|------------------|
| 架构类型 | DeepSeek2 | Qwen35MoE |
| 是否 Hybrid | ❌ 否 | ✅ 是 |
| 缓存机制 | 标准 KV 缓存 | Context Checkpoint |
| 缓存粒度 | Token 级别 | Checkpoint 级别 (~512 tokens) |
| `llama_memory_seq_rm` | ✅ 支持 | ❌ 可能失败 |
| 缓存失效行为 | 清除并重新计算部分 | 强制完整重新处理 |

### 为什么 Qwen3.5 是 Hybrid?

Qwen3.5 系列模型使用了**混合架构**，结合了：
- Transformer attention 层
- Mamba/SSM (State Space Model) 层
- 特殊的 recurrent 内存机制

这导致传统的 KV 缓存机制无法直接使用，需要 checkpoint 机制来管理状态。

---

## 结论

### 不是 Bug，是设计特性

缓存行为差异是 **by design**，不是 llama.cpp 的版本问题或 bug。

- **JoyAI** (DeepSeek2): 标准 transformer，完整 KV 缓存复用，缓存效果极好
- **Qwen3.5** (Qwen35MoE): Hybrid 架构，使用 checkpoint 机制，缓存效果受限

### 影响

对于 Stage 1 吞吐量测试：
- JoyAI 的 TPS 数据包含冷启动和热启动的巨大差异
- Qwen3.5 的热启动提升不明显
- **公平对比应该使用冷启动数据**（迭代 1）

### 相关代码

- `src/llama-arch.cpp:2833` - Hybrid 架构定义
- `tools/server/server-context.cpp:2377` - Hybrid 缓存处理
- `tools/server/server-context.cpp:2430` - Truncate 失败处理

### 参考

- GitHub PR: https://github.com/ggml-org/llama.cpp/pull/13194#issuecomment-2868343055
- 相关 commit: `da348c9df` - models : fix qwen3.5 beta/gate shapes
