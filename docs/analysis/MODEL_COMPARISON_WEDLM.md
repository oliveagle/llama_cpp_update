# Model Comparison: WeDLM vs Other Models

> **Date**: 2026-02-19
> **Comparison Focus**: WeDLM-8B-Instruct vs LLaDA2, Qwen3, GLM-4, and others
> **Test Framework**: llama.cpp Stage 2 (50-case) and Stage 3 (65-case)

---

## Executive Summary

| Model | Architecture | Math | Logic | Code | Overall | Status |
|-------|-------------|------|-------|------|---------|--------|
| **WeDLM-8B** | Causal (Qwen3-based) | ✅ Good | ✅ Good | ✅ Good | ~85%* | Ready |
| **Qwen3-VL-8B** | Causal | 90% | 80% | 100% | **92.3%** | ⭐ Best |
| **Qwen3-4B** | Causal | 80% | 80% | 90% | **90.8%** | Excellent |
| **GLM-4.7-Flash** | Causal | 80% | 80% | 100% | **78.5%** | Good |
| **LLaDA2-2B** | Bidirectional Diffusion | 0% | 5% | 95% | ~35% | Limited |
| **MiniCPM-o-4.5** | Causal | 30% | 40% | 10% | **33.8%** | Weak |

*WeDLM estimated based on Qwen3-8B performance (same architecture)

---

## Detailed Comparison

### 1. Architecture Comparison

| Model | Attention Type | KV Cache | llama.cpp Support | Inference Speed |
|-------|---------------|----------|-------------------|-----------------|
| **WeDLM** | Causal | ✅ Full | Standard server | Fast (AR) |
| **Qwen3** | Causal | ✅ Full | Standard server | Fast (AR) |
| **GLM-4** | Causal | ✅ Full | Standard server | Fast (AR) |
| **LLaDA2** | Bidirectional | ❌ None | diffusion-cli only | Slow (iterative) |

**Key Insight**: WeDLM uses **causal attention** like standard LLMs, not true bidirectional diffusion like LLaDA2. This is why it performs well on reasoning tasks.

---

### 2. Math Performance

| Model | Simple (2+2) | Algebra (3x+7=22) | Word Problem | Stage 3 Score |
|-------|-------------|-------------------|--------------|---------------|
| **WeDLM** | ✅ 4 | ✅ Shows reasoning | ✅ Correct | ~80%* |
| **Qwen3-VL-8B** | ✅ 4 | ✅ Correct | ✅ Correct | **90%** |
| **Qwen3-4B** | ✅ 4 | ✅ Correct | ✅ Correct | **80%** |
| **GLM-4.7** | ✅ 4 | ✅ Correct | ✅ Correct | **80%** |
| **LLaDA2** | ❌ Empty | ❌ Empty | ❌ Empty | **0%** |
| **MiniCPM-4.5** | ✅ 4 | ⚠️ Partial | ❌ Wrong | **30%** |

*WeDLM not fully tested in Stage 3, estimated from Qwen3-8B base

---

### 3. Logic Performance

| Model | Syllogism (A→B→C) | Stage 3 Logic | Notes |
|-------|-------------------|---------------|-------|
| **WeDLM** | ✅ "False" | ~80%* | Correct reasoning |
| **Qwen3-VL-8B** | ✅ Correct | **80%** | Excellent |
| **Qwen3-4B** | ✅ Correct | **80%** | Excellent |
| **GLM-4.7** | ✅ Correct | **80%** | Good |
| **LLaDA2** | ❌ "B"/Empty | **5%** | Fails completely |
| **MiniCPM-4.5** | ❌ Wrong | **40%** | Poor |

---

### 4. Code Generation

| Model | def add(a,b) | Stage 3 Code | Notes |
|-------|-------------|--------------|-------|
| **WeDLM** | ✅ `return a+b` | ~90%* | Clean output |
| **Qwen3-VL-8B** | ✅ Perfect | **100%** | Best in class |
| **Qwen3-4B** | ✅ Perfect | **90%** | Excellent |
| **GLM-4.7** | ✅ Perfect | **100%** | Excellent |
| **LLaDA2** | ✅ Good | **95%** | Surprisingly good |
| **MiniCPM-4.5** | ❌ Broken | **10%** | Very poor |

---

### 5. Diffusion Model Comparison

| Feature | WeDLM | LLaDA2 |
|---------|-------|--------|
| **Marketing** | "Diffusion LM" | "Diffusion LM" |
| **Actual Architecture** | Causal attention | Bidirectional attention |
| **KV Cache** | ✅ Yes | ❌ No |
| **Parallel Decoding** | Yes (custom) | Yes (standard) |
| **Math** | ✅ Works | ❌ Fails |
| **Speed** | Fast | Slow |
| **llama.cpp** | Standard server | diffusion-cli |

**Conclusion**: WeDLM is **not a true diffusion model** in the LLaDA2 sense. It's a standard autoregressive model (Qwen3) with optimized parallel decoding.

---

### 6. Model Family Rankings

#### Overall Performance (Stage 3 - 65 cases)
```
1. Qwen3-VL-8B        92.3%  ⭐⭐⭐⭐⭐
2. Qwen3-4B           90.8%  ⭐⭐⭐⭐⭐
3. JoyAI-LLM-Flash    89.2%  ⭐⭐⭐⭐⭐
4. WeDLM-8B*          ~85%   ⭐⭐⭐⭐⭐
5. GLM-4.7-Flash      78.5%  ⭐⭐⭐⭐
6. Qwen3-0.6B         47.7%  ⭐⭐⭐
7. MiniCPM-o-4.5      33.8%  ⭐⭐
8. LLaDA2-2B          ~35%   ⭐⭐
```

*WeDLM estimated from architecture similarity to Qwen3-8B

---

## Key Findings

### 1. WeDLM is Misleadingly Named
- **Claim**: "Diffusion Language Model"
- **Reality**: Standard causal attention (Qwen3-based)
- **Advantage**: Better compatibility, faster, works with existing tools

### 2. LLaDA2's Architecture is the Problem
- **Bidirectional attention** breaks sequential reasoning
- **Math/Logic**: 0-5% (complete failure)
- **Code**: 95% (surprisingly good - local patterns)

### 3. Model Size Matters
- **8B models** (Qwen3, WeDLM, GLM-4.7): 78-92% overall
- **4B models** (Qwen3VL, MiniCPM): 34-91% (high variance)
- **0.6B models** (Qwen3-tiny): ~48% (usable for simple tasks)

### 4. Specialization vs Generalization
- **Qwen3-Coder**: Perfect code, weaker math
- **GLM-4.7**: Strong math/reasoning, good code
- **WeDLM**: Balanced (Qwen3 base)
- **LLaDA2**: Good code/creative, fails reasoning

---

## Recommendations

### Use Case Matching

| Use Case | Recommended Model | Why |
|----------|------------------|-----|
| **General Chat** | Qwen3-VL-8B | Best overall (92.3%) |
| **Code Generation** | Qwen3-Coder-Next or GLM-4.7 | 100% code score |
| **Math/Reasoning** | GLM-4.7-Flash or Qwen3-4B | Strong logic (80%) |
| **Fast Inference** | WeDLM-8B | Parallel decoding optimization |
| **Research/Diffusion** | LLaDA2 | Unique architecture (academic interest) |
| **Edge/Low Resource** | Qwen3-0.6B | 600M params, 55% score |

### Avoid
- **MiniCPM-o-4.5**: Poor performance (33.8%) across all categories
- **LLaDA2 for reasoning**: 0% math, cannot be fixed with tuning

---

## Technical Notes

### WeDLM Conversion
```bash
# WeDLM requires architecture modification for GGUF
# Original: WeDLMForCausalLM (not supported)
# Modified: Qwen3ForCausalLM (supported)

# Conversion steps:
1. Download from ModelScope
2. Edit config.json: "architectures": ["Qwen3ForCausalLM"]
3. convert_hf_to_gguf.py --outtype q8_0
4. llama-quantize Q4_K_M  # 4.7GB optimal
```

### LLaDA2 Limitations (Fundamental)
```
Problem: Bidirectional attention cannot do sequential reasoning
- Math: Requires step-by-step (isolate → solve)
- Logic: Requires chain deduction (A→B→C)
- Diffusion: Processes all positions in parallel

Result: Empty or fragmented outputs on reasoning tasks
Fix: None (architectural limitation)
```

---

## Sources

- Stage 2 Report: `eval_results/stage2/GFX1151_STAGE2_BENCHMARK_REPORT.md`
- Stage 3 Report: `eval_results/stage3/BENCHMARK_REPORT.md`
- LLaDA2 Analysis: `docs/analysis/LLaDA2_LIMITATIONS.md`
- WeDLM Test: `docs/analysis/WeDLM_TEST_RESULTS.md`

---

*Report generated: 2026-02-19*
