# JoyAI-LLM-Flash-Q4_K_M 综合能力评估报告

> **评估时间**: 2026-02-17 12:51
> **模型路径**: /mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf

---

## 评估项目

| 能力维度 | 评估工具 | 状态 |
|---------|---------|------|
| 基础能力 | lm-eval-harness | ❌ |
| 代码生成 | HumanEval, MBPP | ❌ |
| 工具使用 | 自定义测试集 | ✅ |

---

## 详细报告

### 1. 基础能力评估

**错误**: 

### 2. 工具使用能力评估

报告文件: `./eval_results/JoyAI-LLM-Flash-Q4_K_M/JoyAI-LLM-Flash-Q4_K_M_tools_eval.md`

---

## 与黄金标杆对比

基础能力评测完成后，请运行对比脚本:

```bash
python3 -c "
from golden_benchmarks import compare_with_golden, print_comparison
results = {'C-Eval': 0.75, 'GSM8K': 0.80}  # 填入实际结果
comparison = compare_with_golden('LLM', results)
print_comparison(comparison)
"
```

---

## 结论

待填写...

