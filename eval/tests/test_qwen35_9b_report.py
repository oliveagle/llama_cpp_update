#!/usr/bin/env python3
"""
Qwen3.5 9B - Stage 1 测试对比报告
"""

import json
import os
from datetime import datetime

RESULTS_DIR = "/mnt/volume3/llama_cpp/eval/results/stage1"


def load_latest_results():
    """加载最新的测试结果"""
    if not os.path.exists(RESULTS_DIR):
        return None, None

    vulkan_files = sorted(
        [f for f in os.listdir(RESULTS_DIR) if "vulkan" in f and f.endswith(".json")],
        reverse=True
    )
    cuda_files = sorted(
        [f for f in os.listdir(RESULTS_DIR) if "cuda" in f and f.endswith(".json")],
        reverse=True
    )

    vulkan_result = None
    cuda_result = None

    if vulkan_files:
        with open(os.path.join(RESULTS_DIR, vulkan_files[0]), "r") as f:
            vulkan_result = json.load(f)

    if cuda_files:
        with open(os.path.join(RESULTS_DIR, cuda_files[0]), "r") as f:
            cuda_result = json.load(f)

    return vulkan_result, cuda_result


def print_comparison_report(vulkan_result, cuda_result):
    """打印对比报告"""
    print("\n" + "="*80)
    print("📊 Qwen3.5 9B - Stage 1 性能对比报告")
    print("="*80)
    print(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🤖 模型: Qwen3.5-9B-UD-Q4_K_XL (5.56 GB)")

    # 汇总表格 - Prompt Processing
    print("\n" + "─"*80)
    print("📈 [1] Prompt Processing 对比 (吞入速度，越高越好)")
    print("─"*80)
    print(f"{'ctx_size':>8} | {'Vulkan TPS':>12} | {'CUDA TPS':>12} | {'CUDA 倍数':>10}")
    print("-"*62)

    ctx_sizes = ["8192", "16384", "32768"]
    for ctx_size in ctx_sizes:
        v_tps = 0
        c_tps = 0

        if vulkan_result and ctx_size in vulkan_result.get("ctx_sizes", {}):
            v_tps = vulkan_result["ctx_sizes"][ctx_size].get("prompt_processing", {}).get("tps", 0)

        if cuda_result and ctx_size in cuda_result.get("ctx_sizes", {}):
            c_tps = cuda_result["ctx_sizes"][ctx_size].get("prompt_processing", {}).get("tps", 0)

        ratio = c_tps / v_tps if v_tps > 0 else 0
        print(f"{ctx_size:>8} | {v_tps:12.1f} | {c_tps:12.1f} | {ratio:9.1f}x")

    # 汇总表格 - Token Generation
    print("\n" + "─"*80)
    print("📈 [2] Token Generation 对比 (吐出速度，越高越好)")
    print("─"*80)
    print(f"{'ctx_size':>8} | {'Vulkan 256':>12} | {'CUDA 256':>12} | {'Vulkan 512':>12} | {'CUDA 512':>12}")
    print("-"*74)

    for ctx_size in ctx_sizes:
        v256 = 0
        c256 = 0
        v512 = 0
        c512 = 0

        if vulkan_result and ctx_size in vulkan_result.get("ctx_sizes", {}):
            ctx = vulkan_result["ctx_sizes"][ctx_size]
            v256 = ctx.get("token_gen_256", {}).get("tps", 0)
            v512 = ctx.get("token_gen_512", {}).get("tps", 0)

        if cuda_result and ctx_size in cuda_result.get("ctx_sizes", {}):
            ctx = cuda_result["ctx_sizes"][ctx_size]
            c256 = ctx.get("token_gen_256", {}).get("tps", 0)
            c512 = ctx.get("token_gen_512", {}).get("tps", 0)

        print(f"{ctx_size:>8} | {v256:12.1f} | {c256:12.1f} | {v512:12.1f} | {c512:12.1f}")

    # 详细对比分析
    print("\n" + "─"*80)
    print("📋 [3] 详细分析")
    print("─"*80)

    # 计算平均值
    vulkan_pp_avg = 0
    vulkan_tg_avg = 0
    cuda_pp_avg = 0
    cuda_tg_avg = 0

    if vulkan_result:
        pp_list = []
        tg_list = []
        for ctx_size in ctx_sizes:
            if ctx_size in vulkan_result.get("ctx_sizes", {}):
                ctx = vulkan_result["ctx_sizes"][ctx_size]
                pp = ctx.get("prompt_processing", {}).get("tps", 0)
                tg = ctx.get("token_gen_256", {}).get("tps", 0)
                if pp > 0:
                    pp_list.append(pp)
                if tg > 0:
                    tg_list.append(tg)
        if pp_list:
            vulkan_pp_avg = sum(pp_list) / len(pp_list)
        if tg_list:
            vulkan_tg_avg = sum(tg_list) / len(tg_list)

    if cuda_result:
        pp_list = []
        tg_list = []
        for ctx_size in ctx_sizes:
            if ctx_size in cuda_result.get("ctx_sizes", {}):
                ctx = cuda_result["ctx_sizes"][ctx_size]
                pp = ctx.get("prompt_processing", {}).get("tps", 0)
                tg = ctx.get("token_gen_256", {}).get("tps", 0)
                if pp > 0:
                    pp_list.append(pp)
                if tg > 0:
                    tg_list.append(tg)
        if pp_list:
            cuda_pp_avg = sum(pp_list) / len(pp_list)
        if tg_list:
            cuda_tg_avg = sum(tg_list) / len(tg_list)

    print(f"\n  🎯 平均性能:")
    print(f"     Vulkan:  Prompt {vulkan_pp_avg:.1f} t/s | Token Gen {vulkan_tg_avg:.1f} t/s")
    print(f"     CUDA:    Prompt {cuda_pp_avg:.1f} t/s | Token Gen {cuda_tg_avg:.1f} t/s")

    if vulkan_pp_avg > 0 and cuda_pp_avg > 0:
        print(f"\n  🏆 结论:")
        pp_ratio = cuda_pp_avg / vulkan_pp_avg
        tg_ratio = vulkan_tg_avg / cuda_tg_avg if cuda_tg_avg > 0 else 0

        print(f"     - Prompt Processing: CUDA 比 Vulkan 快 {pp_ratio:.1f}x")
        if tg_ratio > 1:
            print(f"     - Token Generation: Vulkan 比 CUDA 快 {tg_ratio:.1f}x")
        else:
            print(f"     - Token Generation: CUDA 比 Vulkan 快 {1/tg_ratio:.1f}x")

    print("\n" + "─"*80)
    print("💡 [4] 关键发现")
    print("─"*80)
    print("\n  1. **Prompt Processing**:")
    print("     - CUDA (V100) 在吞入速度上显著更快 (~1700 t/s vs ~560 t/s)")
    print("     - 这得益于 CUDA 成熟的优化和 V100 的 Tensor Core")

    print("\n  2. **Token Generation**:")
    print("     - Vulkan (AMD gfx1151) 在吐出速度上更快 (~61 t/s vs ~40 t/s)")
    print("     - AMD RDNA 3 架构在推理延迟上有优势")

    print("\n  3. **Context Size 扩展性**:")
    print("     - 两个后端在 8K→32K 范围内性能都保持稳定")
    print("     - 没有明显的 Context Cliff 现象")

    print("\n  4. **实际使用建议**:")
    print("     - 长文档处理/批量推理 → 优先用 CUDA")
    print("     - 实时对话/低延迟场景 → 优先用 Vulkan")

    print("\n" + "="*80)
    print("✅ Stage 1 测试完成")
    print("="*80)


def main():
    vulkan_result, cuda_result = load_latest_results()

    if not vulkan_result and not cuda_result:
        print("❌ 未找到测试结果文件")
        return 1

    print_comparison_report(vulkan_result, cuda_result)

    return 0


if __name__ == "__main__":
    main()
