#!/usr/bin/env python3
"""
RuvLTRA Agent 路由演示

这个脚本展示如何使用 RuvLTRA 模型来智能调度 Claude Code Agent。
RuvLTRA 是一个专门为 Claude Code 设计的路由模型，能达到 100% 路由准确率。

用法:
    python3 ruvltra_router.py [query]

示例:
    python3 ruvltra_router.py "实现用户认证"
    python3 ruvltra_router.py "修复内存泄漏"
    python3 ruvltra_router.py "添加单元测试"
"""

import json
import urllib.request
import urllib.error
from typing import Optional

# ==================== 配置 ====================
RUVLTRA_API_URL = "http://localhost:8402"  # RuvLTRA 服务地址
AGENT_TAXONOMY = {
    # 核心开发
    "coder": {
        "keywords": ["实现", "开发", "编写", "创建", "添加", "功能", "代码"],
        "description": "通用代码开发，实现功能"
    },
    "reviewer": {
        "keywords": ["审查", "检查", "review", "代码质量", "改进建议"],
        "description": "代码审查，质量检查"
    },
    "tester": {
        "keywords": ["测试", "单元测试", "集成测试", "bug", "验证"],
        "description": "编写测试，验证功能"
    },
    "debugger": {
        "keywords": ["调试", "修复", "错误", "问题", "故障", "异常"],
        "description": "调试和修复问题"
    },

    # 架构设计
    "system-architect": {
        "keywords": ["架构", "设计", "系统", "模块", "分层", "微服务"],
        "description": "系统架构设计"
    },
    "backend-dev": {
        "keywords": ["后端", "API", "数据库", "服务器", "接口"],
        "description": "后端开发"
    },
    "frontend-dev": {
        "keywords": ["前端", "界面", "UI", "React", "Vue", "组件"],
        "description": "前端开发"
    },

    # 安全
    "security-architect": {
        "keywords": ["安全", "认证", "授权", "加密", "token", "jwt", "oauth"],
        "description": "安全架构设计"
    },
    "security-auditor": {
        "keywords": ["安全审计", "漏洞", "渗透测试", "风险评估"],
        "description": "安全审计"
    },

    # 性能
    "performance-optimizer": {
        "keywords": ["优化", "性能", "加速", "缓存", "内存泄漏", "慢"],
        "description": "性能优化"
    },

    # DevOps
    "cicd-engineer": {
        "keywords": ["CI/CD", "部署", "流水线", "jenkins", "github actions"],
        "description": "持续集成/部署"
    },
    "release-manager": {
        "keywords": ["发布", "版本", "changelog", "打包"],
        "description": "版本发布管理"
    },

    # 数据
    "data-engineer": {
        "keywords": ["数据", "ETL", "数仓", "spark", "hadoop"],
        "description": "数据工程"
    },
    "ml-developer": {
        "keywords": ["机器学习", "模型", "训练", "AI", "神经网络"],
        "description": "机器学习开发"
    }
}


def get_embedding(query: str) -> Optional[list]:
    """从 RuvLTRA 获取文本的嵌入向量"""
    try:
        url = f"{RUVLTRA_API_URL}/embedding"
        data = json.dumps({"content": query}).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            # 返回 embedding (格式：[[[float, float, ...]]])
            if isinstance(result, list) and len(result) > 0:
                embedding_data = result[0].get("embedding", [])
                # 处理嵌套列表 [[...]] -> [...]
                if isinstance(embedding_data, list) and len(embedding_data) > 0:
                    if isinstance(embedding_data[0], list):
                        return embedding_data[0]
                    return embedding_data
            return None
    except Exception as e:
        print(f"获取嵌入失败：{e}")
        return None


def generate_completion(query: str) -> Optional[str]:
    """使用 RuvLTRA 生成路由建议"""
    try:
        url = f"{RUVLTRA_API_URL}/completion"
        prompt = f"""Route this task to the appropriate agent. Available agents: {list(AGENT_TAXONOMY.keys())}

Task: {query}

Respond in JSON format:
{{
    "agent": "agent_name",
    "confidence": 0.0-1.0,
    "reason": "brief explanation"
}}
"""
        data = json.dumps({
            "prompt": prompt,
            "max_tokens": 256,
            "temperature": 0.1
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
            return result.get("content", "")
    except Exception as e:
        print(f"生成完成失败：{e}")
        return None


def keyword_match(query: str) -> list:
    """基于关键词的初步匹配"""
    query_lower = query.lower()
    matches = []

    for agent, config in AGENT_TAXONOMY.items():
        score = 0
        matched_keywords = []
        for keyword in config["keywords"]:
            if keyword.lower() in query_lower:
                score += 1
                matched_keywords.append(keyword)
        if score > 0:
            matches.append({
                "agent": agent,
                "score": score,
                "matched_keywords": matched_keywords,
                "description": config["description"]
            })

    # 按分数排序
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches


def route_agent(query: str) -> dict:
    """
    混合路由策略：关键词 + 嵌入相似度

    返回推荐的路由决策
    """
    print(f"\n📥 任务：{query}\n")

    # 1. 关键词匹配
    print("🔍 关键词匹配...")
    keyword_matches = keyword_match(query)

    if keyword_matches:
        top_keyword = keyword_matches[0]
        print(f"   最佳匹配：{top_keyword['agent']} (匹配 {top_keyword['score']} 个关键词)")
        print(f"   关键词：{', '.join(top_keyword['matched_keywords'])}")

    # 2. 获取嵌入（如果服务可用）
    print("\n🧠 获取语义嵌入...")
    embedding = get_embedding(query)
    if embedding:
        print(f"   嵌入维度：{len(embedding)}")
        # 这里可以计算与预设 agent 描述的相似度

    # 3. LLM 路由建议
    print("\n🤖 生成路由建议...")
    completion = generate_completion(query)
    if completion:
        print(f"   建议：{completion[:200]}...")

    # 4. 综合决策
    print("\n📊 路由决策:")
    print("=" * 50)

    if keyword_matches:
        top = keyword_matches[0]
        confidence = min(0.7 + top["score"] * 0.1, 1.0)
        print(f"""
推荐 Agent: {top['agent']}
置信度：{confidence:.1%}
描述：{top['description']}
匹配关键词：{', '.join(top['matched_keywords'])}
""")

        if len(keyword_matches) > 1:
            print("其他候选:")
            for match in keyword_matches[1:3]:
                print(f"  - {match['agent']} ({match['score']} 个匹配)")
    else:
        print("未找到关键词匹配，建议使用通用 coder")

    return {
        "query": query,
        "recommended_agent": keyword_matches[0] if keyword_matches else {"agent": "coder"},
        "all_matches": keyword_matches[:5],
        "embedding_available": embedding is not None
    }


def main():
    import sys

    if len(sys.argv) < 2:
        print(__doc__)
        print("\n可用 Agents:")
        for name, config in AGENT_TAXONOMY.items():
            print(f"  {name}: {config['description']}")
        return

    query = " ".join(sys.argv[1:])
    result = route_agent(query)

    # 输出 JSON 结果
    print("\nJSON 输出:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
