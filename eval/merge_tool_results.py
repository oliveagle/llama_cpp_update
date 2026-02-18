#!/usr/bin/env python3
"""
合并工具测试结果到现有 Stage 2 结果中
将 tool_result.json 的数据合并到对应的 _result.json 文件中
"""

import json
import os
import glob
from pathlib import Path

def get_model_name_from_file(filename):
    """从文件名提取模型名称"""
    basename = os.path.basename(filename)
    # 移除时间戳和hash部分 (格式: modelname_YYYYMMDD_HHMMSS_hash_result.json)
    parts = basename.split('_')
    # 找到日期部分 (8位数字)
    for i, part in enumerate(parts):
        if len(part) == 8 and part.isdigit():
            return '_'.join(parts[:i])
    return None

def load_tool_results():
    """加载工具测试结果"""
    results_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    tool_files = glob.glob(f"{results_dir}/*_tool_result.json")

    tool_results = {}
    for f in tool_files:
        data = json.load(open(f))
        model = data.get('model')
        if model:
            tool_results[model] = data

    return tool_results

def find_latest_result_file(model_name):
    """找到模型的最新 _result.json 文件"""
    results_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    pattern = f"{results_dir}/{model_name}_*_result.json"
    files = glob.glob(pattern)

    # 排除 tool_result 文件
    files = [f for f in files if '_tool_result' not in f]

    if not files:
        return None

    # 返回最新的文件
    return max(files, key=os.path.getmtime)

def merge_tool_into_result(model_name, tool_data):
    """将工具数据合并到结果文件"""
    result_file = find_latest_result_file(model_name)

    if not result_file:
        print(f"⚠️ {model_name}: 未找到结果文件")
        return False

    try:
        with open(result_file, 'r') as f:
            result_data = json.load(f)

        # 检查是否已有 tool 数据
        if 'tool' in result_data:
            print(f"✓ {model_name}: 已有 tool 数据，跳过")
            return True

        # 添加 tool 数据
        tool_info = tool_data.get('tool', {})
        result_data['tool'] = tool_info

        # 更新 summary
        if 'summary' in result_data:
            code = result_data.get('code', {})
            math = result_data.get('math', {})
            text = result_data.get('text', {})

            code_total = code.get('total', 0)
            math_total = math.get('total', 0)
            text_total = text.get('total', 0)
            tool_total = tool_info.get('total', 0)

            code_passed = code.get('passed', 0)
            math_passed = math.get('passed', 0)
            text_passed = text.get('passed', 0)
            tool_passed = tool_info.get('passed', 0)

            total_tests = code_total + math_total + text_total + tool_total
            total_passed = code_passed + math_passed + text_passed + tool_passed

            result_data['summary'] = {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_pass_rate': total_passed / total_tests if total_tests > 0 else 0,
                'total_duration': result_data['summary'].get('total_duration', 0) + tool_info.get('duration', 0)
            }

        # 保存更新后的文件
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        print(f"✓ {model_name}: 已合并 tool 数据 ({tool_passed}/{tool_total}) -> {result_file}")
        return True

    except Exception as e:
        print(f"❌ {model_name}: 合并失败 - {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("合并工具测试结果到 Stage 2 数据")
    print("=" * 70)

    tool_results = load_tool_results()
    print(f"\n找到 {len(tool_results)} 个模型的工具测试结果\n")

    success_count = 0
    for model, tool_data in sorted(tool_results.items()):
        if merge_tool_into_result(model, tool_data):
            success_count += 1

    print("\n" + "=" * 70)
    print(f"合并完成: {success_count}/{len(tool_results)} 个模型成功")
    print("=" * 70)
