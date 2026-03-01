#!/usr/bin/env python3
"""
RuvLTRA 混合路由策略 - 扩展测试 (50 个用例)

测试 28 个 ole-teams Agent 角色的路由准确率
"""

import subprocess
import json
import sys

# 扩展测试任务定义 (50 个用例)
TEST_TASKS = [
    # === 核心开发 (10) ===
    ("实现用户认证 API", "backend-dev"),
    ("设计系统架构", "architect"),
    ("开发响应式界面", "frontend-dev"),
    ("开发完整电商功能", "fullstack-dev"),
    ("开发 iOS 应用", "mobile-dev"),
    ("开发 Android 应用", "mobile-dev"),
    ("实现 RESTful API", "backend-dev"),
    ("设计微服务架构", "architect"),
    ("开发管理后台界面", "frontend-dev"),
    ("实现前后端分离架构", "fullstack-dev"),

    # === DevOps / SRE (4) ===
    ("配置 CI/CD 流水线", "devops-engineer"),
    ("设计 SLO 指标", "sre"),
    ("部署 Kubernetes 集群", "devops-engineer"),
    ("配置 Prometheus 监控", "sre"),

    # === 数据库 / 数据 (6) ===
    ("优化数据库查询", "dba"),
    ("构建 ETL 管道", "data-engineer"),
    ("训练文本分类模型", "ml-engineer"),
    ("设计数据库 Schema", "dba"),
    ("搭建数据仓库", "data-engineer"),
    ("部署机器学习模型", "ml-engineer"),

    # === 测试 / 质量 (6) ===
    ("编写单元测试", "test-engineer"),
    ("编写 Playwright E2E 测试", "ui-test-engineer"),
    ("审查代码规范", "code-reviewer"),
    ("检查 SQL 注入漏洞", "security-reviewer"),
    ("进行代码质量评估", "code-reviewer"),
    ("执行渗透测试", "security-reviewer"),

    # === 性能 (2) ===
    ("优化 API 响应延迟", "performance-expert"),
    ("排查内存泄漏问题", "performance-expert"),

    # === 产品 / 管理 (5) ===
    ("定义产品路线图", "product-manager"),
    ("组织每日站会", "scrum-master"),
    ("评审技术选型", "tech-lead"),
    ("制定迭代计划", "scrum-master"),
    ("评估技术债务", "tech-lead"),

    # === 文档 / 研究 / 设计 (5) ===
    ("编写 API 文档", "technical-writer"),
    ("调研技术选型方案", "researcher"),
    ("设计用户交互流程", "ux-designer"),
    ("编写用户手册", "technical-writer"),
    ("进行竞品分析", "researcher"),

    # === AI / Prompt (2) ===
    ("优化 Few-shot 提示词", "prompt-engineer"),
    ("设计 LLM 应用架构", "prompt-engineer"),

    # === 金融 / 交易 (6) ===
    ("回测交易策略", "quant-researcher"),
    ("执行套利交易", "crypto-trader"),
    ("分析公司财务报表", "financial-analyst"),
    ("监控成交量异动", "market-monitor"),
    ("开发量化因子", "quant-researcher"),
    ("分析链上数据", "crypto-trader"),

    # === 特殊角色 (2) ===
    ("挑战技术方案假设", "skeptic"),
    ("识别项目风险", "skeptic"),
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
    print("  RuvLTRA 混合路由策略 - 扩展测试报告 (50 用例)")
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
        category = expected.split("-")[0] if "-" in expected else expected
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
        if not r["matched"]:
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

    # 失败案例详细分析
    failures = [r for r in results if not r["matched"]]
    if failures:
        print("失败案例分析:")
        print("-" * 70)
        for r in failures:
            print(f"  • \"{r['query']}\"")
            print(f"    期望：{r['expected']}, 实际：{r['actual']}")
            print(f"    关键词：{r['keywords']}")
            print()

    print("=" * 70)

    return 0 if accuracy >= 90 else 1


if __name__ == "__main__":
    sys.exit(main())
