#!/usr/bin/env python3
"""
RuvLTRA 混合路由策略测试脚本

测试 28 个 ole-teams Agent 角色的路由准确率
"""

import subprocess
import json
import sys

# 测试任务定义
TEST_TASKS = [
    # 核心开发 (5)
    ("实现用户认证 API", "backend-dev"),
    ("设计系统架构", "architect"),
    ("开发响应式界面", "frontend-dev"),
    ("开发完整电商功能", "fullstack-dev"),
    ("开发 iOS 应用", "mobile-dev"),

    # DevOps / SRE (2)
    ("配置 CI/CD 流水线", "devops-engineer"),
    ("设计 SLO 指标", "sre"),

    # 数据库 / 数据 (3)
    ("优化数据库查询", "dba"),
    ("构建 ETL 管道", "data-engineer"),
    ("训练文本分类模型", "ml-engineer"),

    # 测试 / 质量 (4)
    ("编写单元测试", "test-engineer"),
    ("编写 Playwright E2E 测试", "ui-test-engineer"),
    ("审查代码规范", "code-reviewer"),
    ("检查 SQL 注入漏洞", "security-reviewer"),

    # 性能 (1)
    ("优化 API 响应延迟", "performance-expert"),

    # 产品 / 管理 (3)
    ("定义产品路线图", "product-manager"),
    ("组织每日站会", "scrum-master"),
    ("评审技术选型", "tech-lead"),

    # 文档 / 研究 / 设计 (3)
    ("编写 API 文档", "technical-writer"),
    ("调研技术选型方案", "researcher"),
    ("设计用户交互流程", "ux-designer"),

    # AI / Prompt (1)
    ("优化 Few-shot 提示词", "prompt-engineer"),

    # 金融 / 交易 (3)
    ("回测交易策略", "quant-researcher"),
    ("执行套利交易", "crypto-trader"),
    ("分析公司财务报表", "financial-analyst"),
    ("监控成交量异动", "market-monitor"),

    # 特殊角色 (1)
    ("挑战技术方案假设", "skeptic"),
]


def run_router(query: str) -> dict:
    """运行路由脚本"""
    result = subprocess.run(
        ["python3", "ruvltra_hybrid_router.py", "--json", query],
        capture_output=True,
        text=True,
        cwd="/mnt/volume3/llama_cpp/scripts"
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"agent": "error", "confidence": 0, "reason": result.stdout}


def main():
    print("=" * 70)
    print("  RuvLTRA 混合路由策略 - 测试报告")
    print("=" * 70)
    print()

    results = []
    category_stats = {}

    for query, expected in TEST_TASKS:
        result = run_router(query)
        actual = result.get("agent", "unknown")
        confidence = result.get("confidence", 0)
        matched = actual == expected

        results.append({
            "query": query,
            "expected": expected,
            "actual": actual,
            "confidence": confidence,
            "matched": matched,
            "keywords": result.get("matched_keywords", [])
        })

        # 分类统计
        category = expected.split("-")[0]
        if category not in category_stats:
            category_stats[category] = {"total": 0, "success": 0}
        category_stats[category]["total"] += 1
        if matched:
            category_stats[category]["success"] += 1

    # 输出详细结果
    print("详细结果:")
    print("-" * 70)
    for i, r in enumerate(results):
        status = "✓" if r["matched"] else "✗"
        print(f"{i+1:2}. {status} {r['query']}")
        print(f"       期望：{r['expected']}, 实际：{r['actual']} (置信度：{r['confidence']:.0%})")
        if r["keywords"]:
            print(f"       关键词：{', '.join(r['keywords'])}")

    # 总体统计
    total = len(results)
    success = sum(1 for r in results if r["matched"])
    accuracy = success / total * 100 if total > 0 else 0

    print()
    print("=" * 70)
    print("  总体统计")
    print("=" * 70)
    print(f"  测试任务：{total}")
    print(f"  成功：{success}")
    print(f"  失败：{total - success}")
    print(f"  准确率：{accuracy:.1f}%")
    print()

    # 分类统计
    print("分类统计:")
    print("-" * 70)
    for category, stats in sorted(category_stats.items()):
        cat_accuracy = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
        print(f"  {category:<20} {stats['success']}/{stats['total']} ({cat_accuracy:.0f}%)")

    print()
    print("=" * 70)

    return 0 if accuracy >= 80 else 1


if __name__ == "__main__":
    sys.exit(main())
