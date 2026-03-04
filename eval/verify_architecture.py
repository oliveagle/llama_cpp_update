#!/usr/bin/env python3
"""
验证测试脚本 - 检查架构是否正确配置
"""

import os
import sys
from pathlib import Path

EVAL_ROOT = Path(__file__).parent


def check_directory_structure():
    """检查目录结构"""
    print("="*60)
    print("检查评估系统架构")
    print("="*60)

    errors = []
    warnings = []

    # 检查关键目录
    required_dirs = [
        "results/stage1",
        "results/stage2",
        "results/stage3",
        "results/capabilities",
        "results/capabilities/knowledge",
        "results/capabilities/multiturn",
        "results/capabilities/reasoning",
        "results/capabilities/safety",
        "tests/stage1",
        "tests/stage2",
        "tests/stage3",
        "framework",
        "model_configs",
        "docs",
        "tools",
    ]

    print("\n📁 目录检查:")
    for d in required_dirs:
        path = EVAL_ROOT / d
        if path.exists():
            print(f"  ✅ {d}")
        else:
            print(f"  ❌ {d} - 不存在")
            errors.append(f"目录缺失：{d}")

    # 检查关键文件
    print("\n📄 文件检查:")
    required_files = [
        "run.py",
        "config.py",
        "framework/base.py",
        "framework/runner.py",
        "framework/report.py",
        "framework/__init__.py",
        "golden_benchmarks.py",
        "docs/eval-architecture.md",
    ]

    for f in required_files:
        path = EVAL_ROOT / f
        if path.exists():
            print(f"  ✅ {f}")
        else:
            print(f"  ❌ {f} - 不存在")
            errors.append(f"文件缺失：{f}")

    # 检查测试脚本
    print("\n🧪 测试脚本检查:")
    test_scripts = [
        "tests/stage1/performance_test.py",
        "tests/stage2/capability_test_v2.py",
        "tests/stage3/eval_tools_capability.py",
    ]

    for f in test_scripts:
        path = EVAL_ROOT / f
        if path.exists():
            print(f"  ✅ {f}")
        else:
            print(f"  ⚠️ {f} - 不存在")
            warnings.append(f"测试脚本缺失：{f}")

    # 检查 __init__.py
    print("\n📦 包检查:")
    init_files = [
        "tests/__init__.py",
        "tests/stage1/__init__.py",
        "tests/stage2/__init__.py",
        "tests/stage3/__init__.py",
        "framework/__init__.py",
        "model_configs/__init__.py",
    ]

    for f in init_files:
        path = EVAL_ROOT / f
        if path.exists():
            print(f"  ✅ {f}")
        else:
            print(f"  ⚠️ {f} - 不存在")
            warnings.append(f"包初始化文件缺失：{f}")

    # 汇总
    print("\n" + "="*60)
    print(f"检查结果：{len(errors)} 错误，{len(warnings)} 警告")

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ 所有检查通过!")

    return len(errors) == 0


def check_imports():
    """检查模块导入"""
    print("\n" + "="*60)
    print("检查模块导入")
    print("="*60)

    os.chdir(EVAL_ROOT)

    try:
        print("\n导入 framework...")
        from framework import BaseEvaluator, StageResult, EvaluationRunner
        print("  ✅ framework 导入成功")

        print("\n导入 config...")
        from config import DEFAULT_API_URL, STAGE2_THRESHOLD
        print(f"  ✅ config 导入成功 (API: {DEFAULT_API_URL})")

        print("\n所有导入测试通过!")
        return True

    except ImportError as e:
        print(f"  ❌ 导入失败：{e}")
        return False


if __name__ == "__main__":
    ok1 = check_directory_structure()
    ok2 = check_imports()

    print("\n" + "="*60)
    if ok1 and ok2:
        print("✅ 架构验证完成 - 一切正常!")
        sys.exit(0)
    else:
        print("❌ 架构验证失败 - 请检查上述错误")
        sys.exit(1)
