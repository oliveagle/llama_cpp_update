#!/usr/bin/env python3
"""Run lm-eval with proper arguments"""
import subprocess
import sys

cmd = [
    sys.executable, "-m", "lm_eval",
    "--model", "local-completions",
    "--model_args", "model=JoyAI-LLM-Flash-Q4_K_M,base_url=http://localhost:8401/v1/completions,num_concurrent=1,max_retries=3,tokenized_requests=False,tokenizer=Qwen/Qwen2.5-7B-Instruct",
    "--tasks", "gsm8k,mmlu",
    "--batch_size", "1",
    "--output_path", "./eval_results/JoyAI_full",
]

print("Running:", " ".join(cmd))
result = subprocess.run(cmd)
sys.exit(result.returncode)
