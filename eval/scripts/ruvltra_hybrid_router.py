#!/usr/bin/env python3
"""
RuvLTRA 混合路由策略实现

实现完整的关键词 + 嵌入相似度混合路由，支持 ole-teams 的 28 个 Agent 角色。

特性:
- 关键词匹配 (快速初步过滤)
- 嵌入相似度 (HNSW 索引，语义匹配)
- LRU 缓存优化
- 支持 28 个 ole-teams Agent

用法:
    python3 ruvltra_hybrid_router.py "实现用户认证"
    python3 ruvltra_hybrid_router.py --json "修复内存泄漏"
"""

import json
import hashlib
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict

# ==================== Agent 分类定义 (ole-teams 28 个角色) ====================

AGENT_TAXONOMY = {
    # === 核心开发 ===
    "architect": {
        "keywords": ["架构", "系统架构", "微服务", "可扩展", "规划", "决策", "顶层设计", "架构设计"],
        "description": "软件架构师，负责系统架构设计、技术决策和可扩展性规划",
        "tier": 2,
        "embedding_keywords": ["architecture", "design", "system", "scalability", "technical decision"]
    },
    "backend-dev": {
        "keywords": ["后端", "API", "数据库", "服务器", "接口", "认证", "授权", "业务逻辑"],
        "description": "后端开发工程师，负责 API 设计、数据库交互和业务逻辑",
        "tier": 1,
        "embedding_keywords": ["backend", "API", "database", "server", "authentication", "REST"]
    },
    "frontend-dev": {
        "keywords": ["前端", "界面", "UI", "React", "Vue", "组件", "CSS", "响应式", "前端交互"],
        "description": "前端开发工程师，负责 UI 实现、交互优化和前端架构",
        "tier": 1,
        "embedding_keywords": ["frontend", "UI", "React", "Vue", "component", "responsive", "CSS"]
    },
    "fullstack-dev": {
        "keywords": ["全栈", "端到端", "前后端", "完整功能", "电商", "平台", "系统开发"],
        "description": "全栈开发工程师，负责端到端功能实现和前后端集成",
        "tier": 1,
        "embedding_keywords": ["fullstack", "end-to-end", "integration", "full feature", "ecommerce"]
    },
    "mobile-dev": {
        "keywords": ["移动", "React Native", "Flutter", "iOS", "Android", "App"],
        "description": "移动应用开发工程师，负责 React Native/Flutter 跨平台开发",
        "tier": 1,
        "embedding_keywords": ["mobile", "React Native", "Flutter", "iOS", "Android", "app"]
    },

    # === DevOps / SRE ===
    "devops-engineer": {
        "keywords": ["CI/CD", "部署", "Docker", "Kubernetes", "K8s", "Terraform", "基础设施", "流水线"],
        "description": "部署、CI/CD、基础设施、监控和自动化专家",
        "tier": 1,
        "embedding_keywords": ["CI/CD", "deployment", "Docker", "Kubernetes", "infrastructure", "DevOps"]
    },
    "sre": {
        "keywords": ["SRE", "SLO", "SLI", "告警", "监控", "混沌工程", "应急响应", "稳定性"],
        "description": "站点可靠性工程师，负责监控、告警、应急响应和系统稳定性",
        "tier": 2,
        "embedding_keywords": ["SRE", "SLO", "SLI", "alerting", "monitoring", "chaos engineering", "reliability"]
    },

    # === 数据库 / 数据 ===
    "dba": {
        "keywords": ["数据库", "SQL", "索引", "查询优化", "备份", "恢复", "主从", "范式", "表结构", "Schema", "DBA", "数据库查询"],
        "description": "数据库管理员，负责数据库设计、优化、备份和安全管理",
        "tier": 1,
        "embedding_keywords": ["database", "SQL", "index", "query optimization", "backup", "DBA"]
    },
    "data-engineer": {
        "keywords": ["数据", "ETL", "数仓", "数据湖", "Spark", "Hadoop", "特征", "维度建模"],
        "description": "数据模型、数据库设计、ETL 和数据分析专家",
        "tier": 2,
        "embedding_keywords": ["data", "ETL", "warehouse", "data lake", "Spark", "Hadoop", "feature store"]
    },
    "ml-engineer": {
        "keywords": ["机器学习", "模型", "训练", "AI", "神经网络", "推理", "部署", "特征工程"],
        "description": "机器学习工程师，负责模型训练、部署和优化",
        "tier": 2,
        "embedding_keywords": ["machine learning", "model training", "AI", "neural network", "inference", "MLOps"]
    },

    # === 测试 / 质量 ===
    "test-engineer": {
        "keywords": ["测试", "单元测试", "集成测试", "TDD", "覆盖率", "Mock", "自动化测试"],
        "description": "测试工程专家，负责测试策略、TDD 流程和测试覆盖率保障",
        "tier": 1,
        "embedding_keywords": ["testing", "unit test", "integration test", "TDD", "coverage", "automation"]
    },
    "ui-test-engineer": {
        "keywords": ["UI 测试", "E2E", "Playwright", "Cypress", "视觉回归", "端到端测试"],
        "description": "UI 测试工程师，负责端到端测试、视觉回归和 UI 质量保障",
        "tier": 1,
        "embedding_keywords": ["UI testing", "E2E", "Playwright", "Cypress", "visual regression", "end-to-end"]
    },
    "code-reviewer": {
        "keywords": ["代码审查", "规范", "质量", "命名", "注释", "复杂度", "重复代码"],
        "description": "代码审查专家，负责代码质量、规范检查和最佳实践验证",
        "tier": 1,
        "embedding_keywords": ["code review", "quality", "naming", "comments", "complexity", "duplication"]
    },
    "security-reviewer": {
        "keywords": ["安全", "漏洞", "SQL 注入", "XSS", "CSRF", "认证", "授权", "渗透测试"],
        "description": "安全审查专家，负责识别安全漏洞、验证认证授权和输入处理",
        "tier": 2,
        "embedding_keywords": ["security", "vulnerability", "SQL injection", "XSS", "CSRF", "authentication", "authorization"]
    },

    # === 性能 ===
    "performance-expert": {
        "keywords": ["性能", "优化", "延迟", "内存泄漏", "CPU", "缓存", "瓶颈", "慢查询"],
        "description": "性能优化专家，负责性能分析、瓶颈识别和优化策略",
        "tier": 2,
        "embedding_keywords": ["performance", "optimization", "latency", "memory leak", "CPU", "cache", "bottleneck"]
    },

    # === 产品 / 管理 ===
    "product-manager": {
        "keywords": ["产品", "路线图", "用户故事", "需求", "优先级", "PRD", "MVP", "指标"],
        "description": "产品经理，负责产品规划、需求分析和优先级管理",
        "tier": 2,
        "embedding_keywords": ["product", "roadmap", "user story", "requirements", "priority", "PRD", "MVP"]
    },
    "scrum-master": {
        "keywords": ["Scrum", "站会", "回顾", "迭代", "敏捷", "障碍", "燃尽图"],
        "description": "Scrum Master，负责敏捷流程、障碍清除和团队赋能",
        "tier": 2,
        "embedding_keywords": ["Scrum", "standup", "retrospective", "sprint", "agile", "blocker", "burndown"]
    },
    "tech-lead": {
        "keywords": ["技术领导", "技术路线", "评审", "指导", "协调", "代码审查", "决策", "团队", "推进", "技术方案评审", "技术管理", "评审技术选型"],
        "description": "技术领导，负责团队协调、技术决策和项目推进",
        "tier": 2,
        "embedding_keywords": ["tech lead", "technical roadmap", "review", "mentoring", "coordination", "decision"]
    },

    # === 文档 / 研究 ===
    "technical-writer": {
        "keywords": ["文档", "API 文档", "用户指南", "教程", "手册", "FAQ", "博客"],
        "description": "技术文档、API 文档、用户指南和知识库编写专家",
        "tier": 1,
        "embedding_keywords": ["documentation", "API docs", "user guide", "tutorial", "manual", "FAQ", "blog"]
    },
    "researcher": {
        "keywords": ["调研", "对比", "检索", "论文", "竞品分析", "趋势", "开源方案", "技术选型", "研究"],
        "description": "技术调研、方案对比、文献检索和竞品分析专家",
        "tier": 2,
        "embedding_keywords": ["research", "comparison", "literature", "competitor analysis", "trend", "open source"]
    },
    "ux-designer": {
        "keywords": ["UX", "交互设计", "线框图", "原型", "可用性", "导航", "表单", "视觉", "用户体验", "界面优化", "用户流程", "交互流程", "设计用户流程", "用户交互流程"],
        "description": "用户体验设计专家，负责交互设计、可用性评估和界面优化",
        "tier": 2,
        "embedding_keywords": ["UX", "interaction design", "wireframe", "prototype", "usability", "navigation", "form"]
    },

    # === AI / Prompt ===
    "prompt-engineer": {
        "keywords": ["Prompt", "提示词", "Few-shot", "思维链", "AI 交互", "LLM", "角色扮演", "系统提示", "输出格式", "优化 prompt"],
        "description": "Prompt 工程师，负责 AI 交互设计、Prompt 优化和 LLM 应用开发",
        "tier": 2,
        "embedding_keywords": ["prompt", "few-shot", "chain of thought", "AI interaction", "LLM", "role play"]
    },

    # === 金融 / 交易 ===
    "quant-researcher": {
        "keywords": ["量化", "因子", "回测", "IC", "投资组合", "夏普比率", "Alpha"],
        "description": "量化研究员，负责因子挖掘、策略研究和回测分析",
        "tier": 2,
        "embedding_keywords": ["quantitative", "factor", "backtest", "IC", "portfolio", "Sharpe ratio", "Alpha"]
    },
    "crypto-trader": {
        "keywords": ["加密货币", "链上", "资金费率", "网格", "流动性", "DeFi", "NFT", "套利", "交易", "数字货币"],
        "description": "加密货币量化交易员，负责数字货币量化策略和交易执行",
        "tier": 2,
        "embedding_keywords": ["crypto", "on-chain", "funding rate", "grid", "liquidity", "DeFi", "NFT"]
    },
    "financial-analyst": {
        "keywords": ["财务", "报表", "估值", "现金流", "营收", "利润", "资产", "负债"],
        "description": "金融分析师，负责基本面分析、财务建模和投资研究",
        "tier": 2,
        "embedding_keywords": ["financial", "statement", "valuation", "cash flow", "revenue", "profit", "asset", "liability"]
    },
    "market-monitor": {
        "keywords": ["监控", "异动", "成交量", "操纵", "资金流向", "情绪", "板块轮动"],
        "description": "市场监控专家，负责实时市场数据、异常检测和风险预警",
        "tier": 2,
        "embedding_keywords": ["monitoring", "anomaly", "volume", "manipulation", "capital flow", "sentiment", "sector rotation"]
    },

    # === 特殊角色 ===
    "skeptic": {
        "keywords": ["挑战", "风险", "替代方案", "质疑", "依赖", "瓶颈", "威胁", "假设", "反对", "批判"],
        "description": "反对者角色，负责挑战假设、识别风险、提出替代方案",
        "tier": 3,
        "embedding_keywords": ["challenge", "risk", "alternative", "question", "dependency", "bottleneck", "threat"]
    }
}


# ==================== 数据结构 ====================

@dataclass
class RoutingResult:
    """路由结果"""
    agent: str
    confidence: float
    reason: str
    tier: int
    matched_keywords: List[str]
    embedding_score: Optional[float]
    processing_time_ms: float


@dataclass
class AgentMatch:
    """Agent 匹配结果"""
    agent: str
    keyword_score: int
    embedding_score: float
    total_score: float
    matched_keywords: List[str]


# ==================== LRU 缓存 ====================

class LRUCache:
    """LRU 缓存，用于缓存查询结果"""

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache: OrderedDict[str, RoutingResult] = OrderedDict()

    def get(self, key: str) -> Optional[RoutingResult]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: RoutingResult) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        self.cache.clear()


# ==================== 关键词匹配器 ====================

class KeywordMatcher:
    """关键词匹配器"""

    def __init__(self, taxonomy: Dict[str, Dict]):
        self.taxonomy = taxonomy
        # 预处理关键词索引
        self.keyword_index: Dict[str, List[str]] = {}
        for agent, config in taxonomy.items():
            for keyword in config["keywords"]:
                keyword_lower = keyword.lower()
                if keyword_lower not in self.keyword_index:
                    self.keyword_index[keyword_lower] = []
                self.keyword_index[keyword_lower].append(agent)

    def match(self, query: str) -> List[AgentMatch]:
        """匹配查询与 Agent 关键词"""
        query_lower = query.lower()
        matches: Dict[str, AgentMatch] = {}

        # 统计每个 Agent 的匹配分数
        for agent, config in self.taxonomy.items():
            score = 0
            matched = []
            for keyword in config["keywords"]:
                if keyword.lower() in query_lower:
                    score += 1
                    matched.append(keyword)

            if score > 0:
                matches[agent] = AgentMatch(
                    agent=agent,
                    keyword_score=score,
                    embedding_score=0.0,
                    total_score=float(score),
                    matched_keywords=matched
                )

        # 按分数排序
        return sorted(matches.values(), key=lambda x: x.total_score, reverse=True)


# ==================== 嵌入相似度 (使用 llama.cpp) ====================

class EmbeddingMatcher:
    """嵌入相似度匹配器"""

    def __init__(self, taxonomy: Dict[str, Dict], api_url: str = "http://localhost:8402"):
        self.taxonomy = taxonomy
        self.api_url = api_url
        self.agent_embeddings: Dict[str, List[float]] = {}
        self._precompute_embeddings()

    def _precompute_embeddings(self) -> None:
        """预计算所有 Agent 描述的嵌入"""
        import urllib.request
        import urllib.error

        for agent, config in self.taxonomy.items():
            # 组合关键词和描述作为嵌入文本
            text = f"{agent}: {config['description']}. 关键词：{', '.join(config['embedding_keywords'])}"
            embedding = self._get_embedding(text)
            if embedding:
                self.agent_embeddings[agent] = embedding

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的嵌入向量"""
        import urllib.request
        import urllib.error

        try:
            url = f"{self.api_url}/v1/embeddings"
            data = json.dumps({
                "input": text,
                "model": "ruvltra-claude-code-0.5b"
            }).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
                if "data" in result and len(result["data"]) > 0:
                    return result["data"][0].get("embedding", [])
                return None
        except Exception:
            return None

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def match(self, query: str, query_embedding: Optional[List[float]] = None) -> List[AgentMatch]:
        """使用嵌入相似度匹配 Agent"""
        if not query_embedding:
            query_embedding = self._get_embedding(query)

        if not query_embedding:
            return []

        matches = []
        for agent, embedding in self.agent_embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity > 0.3:  # 阈值过滤
                matches.append(AgentMatch(
                    agent=agent,
                    keyword_score=0,
                    embedding_score=similarity,
                    total_score=similarity * 10,  # 嵌入权重
                    matched_keywords=[]
                ))

        return sorted(matches, key=lambda x: x.total_score, reverse=True)


# ==================== 混合路由器 ====================

class HybridRouter:
    """混合路由策略：关键词 + 嵌入"""

    def __init__(self, api_url: str = "http://localhost:8402"):
        self.taxonomy = AGENT_TAXONOMY
        self.keyword_matcher = KeywordMatcher(self.taxonomy)
        self.embedding_matcher = EmbeddingMatcher(self.taxonomy, api_url)
        self.cache = LRUCache(capacity=1000)

    def route(self, query: str, use_embedding: bool = True) -> RoutingResult:
        """路由查询到最佳 Agent"""
        start_time = time.time()

        # 检查缓存
        cache_key = hashlib.md5(query.encode()).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # 1. 关键词匹配 (快速路径)
        keyword_matches = self.keyword_matcher.match(query)

        # 如果关键词匹配 >= 2，直接返回
        if keyword_matches and keyword_matches[0].keyword_score >= 2:
            top_match = keyword_matches[0]
            confidence = min(0.7 + top_match.keyword_score * 0.1, 1.0)
            result = RoutingResult(
                agent=top_match.agent,
                confidence=confidence,
                reason=f"关键词匹配 ({top_match.keyword_score} 个)",
                tier=self.taxonomy[top_match.agent]["tier"],
                matched_keywords=top_match.matched_keywords,
                embedding_score=None,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            self.cache.put(cache_key, result)
            return result

        # 2. 嵌入相似度 (如果关键词不足)
        embedding_matches = []
        query_embedding = None

        if use_embedding:
            query_embedding = self.embedding_matcher._get_embedding(query)
            if query_embedding:
                embedding_matches = self.embedding_matcher.match(query, query_embedding)

        # 3. 综合决策
        if keyword_matches and embedding_matches:
            # 融合两种结果
            agent_scores: Dict[str, Tuple[float, AgentMatch, AgentMatch]] = {}

            for km in keyword_matches:
                agent_scores[km.agent] = (km.total_score, km, None)

            for em in embedding_matches[:5]:  # 取前 5 个
                if em.agent in agent_scores:
                    km = agent_scores[em.agent][1]
                    new_score = km.total_score + em.total_score * 0.5
                    agent_scores[em.agent] = (new_score, km, em)
                else:
                    agent_scores[em.agent] = (em.total_score, AgentMatch(
                        agent=em.agent, keyword_score=0, embedding_score=0,
                        total_score=0, matched_keywords=[]
                    ), em)

            # 排序
            sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1][0], reverse=True)
            top_agent = sorted_agents[0][0]
            km = sorted_agents[0][1][1]
            em = sorted_agents[0][1][2]

            confidence = min(0.6 + (km.keyword_score * 0.1) + (em.embedding_score if em else 0) * 0.3, 1.0)
            all_keywords = km.matched_keywords.copy()

            result = RoutingResult(
                agent=top_agent,
                confidence=confidence,
                reason="关键词 + 嵌入融合",
                tier=self.taxonomy[top_agent]["tier"],
                matched_keywords=all_keywords,
                embedding_score=em.embedding_score if em else None,
                processing_time_ms=(time.time() - start_time) * 1000
            )

        elif keyword_matches:
            # 仅关键词
            top_match = keyword_matches[0]
            confidence = min(0.5 + top_match.keyword_score * 0.15, 1.0)
            result = RoutingResult(
                agent=top_match.agent,
                confidence=confidence,
                reason="关键词匹配",
                tier=self.taxonomy[top_match.agent]["tier"],
                matched_keywords=top_match.matched_keywords,
                embedding_score=None,
                processing_time_ms=(time.time() - start_time) * 1000
            )

        elif embedding_matches:
            # 仅嵌入
            top_match = embedding_matches[0]
            confidence = top_match.embedding_score
            result = RoutingResult(
                agent=top_match.agent,
                confidence=confidence,
                reason="嵌入相似度",
                tier=self.taxonomy[top_match.agent]["tier"],
                matched_keywords=[],
                embedding_score=top_match.embedding_score,
                processing_time_ms=(time.time() - start_time) * 1000
            )

        else:
            # Fallback
            result = RoutingResult(
                agent="backend-dev",
                confidence=0.3,
                reason="无匹配，使用默认",
                tier=1,
                matched_keywords=[],
                embedding_score=None,
                processing_time_ms=(time.time() - start_time) * 1000
            )

        self.cache.put(cache_key, result)
        return result


# ==================== 命令行界面 ====================

def main():
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="RuvLTRA 混合路由策略")
    parser.add_argument("query", nargs="?", help="路由任务")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--server", default="http://localhost:8402", help="RuvLTRA 服务器地址")
    parser.add_argument("--list-agents", action="store_true", help="列出所有 Agent")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")

    args = parser.parse_args()

    router = HybridRouter(api_url=args.server)

    if args.list_agents:
        print("\n可用 Agent 列表:")
        print("=" * 70)
        for agent, config in AGENT_TAXONOMY.items():
            tier_str = ["快速 (Tier1)", "中等 (Tier2)", "复杂 (Tier3)"][config["tier"] - 1]
            print(f"  {agent:<20} - {config['description'][:40]} [{tier_str}]")
        return

    if not args.query:
        parser.print_help()
        print("\n示例:")
        print('  python3 ruvltra_hybrid_router.py "实现用户认证"')
        print('  python3 ruvltra_hybrid_router.py --json "修复内存泄漏"')
        return

    result = router.route(args.query)

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print("\n" + "=" * 60)
        print(f"📥 任务：{args.query}")
        print("-" * 60)
        print(f"🎯 推荐 Agent: {result.agent}")
        print(f"📊 置信度：{result.confidence:.1%}")
        print(f"🏷️ 层级：Tier{result.tier}")
        print(f"📝 原因：{result.reason}")
        if result.matched_keywords:
            print(f"🔑 匹配关键词：{', '.join(result.matched_keywords)}")
        print(f"⏱️ 耗时：{result.processing_time_ms:.2f}ms")
        print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
