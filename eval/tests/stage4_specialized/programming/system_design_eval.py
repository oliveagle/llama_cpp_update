#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - 系统设计 (150 题生成器)
自动生成系统设计题目，包含选择题
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

# 系统设计题目模板
SYSTEM_DESIGN_TEMPLATES = {
    "微服务": [
        {"q": "微服务架构相比单体架构的优势是？", "opts": ["独立部署和扩展", "复杂度低", "通信简单", "部署容易"], "a": "A"},
        {"q": "微服务间通信最常用的协议是？", "opts": ["REST/HTTP", "TCP", "UDP", "SMTP"], "a": "A"},
        {"q": "服务发现的主要作用是？", "opts": ["找到服务实例", "注册服务", "负载均衡", "所有以上"], "a": "D"},
        {"q": "API 网关的作用是？", "opts": ["统一入口", "认证授权", "限流熔断", "所有以上"], "a": "D"},
        {"q": "熔断器模式用于？", "opts": ["防止级联故障", "提高性能", "缓存数据", "消息队列"], "a": "A"},
        {"q": "CAP 理论中的 C 表示？", "opts": ["一致性", "可用性", "分区容错性", "并发"], "a": "A"},
        {"q": "CAP 理论中网络分区发生时，需要在？", "opts": ["C 和 A 之间权衡", "C 和 P 之间权衡", "A 和 P 之间权衡", "无需权衡"], "a": "A"},
        {"q": "最终一致性比强一致性？", "opts": ["可用性更高", "一致性更高", "更简单", "更安全"], "a": "A"},
        {"q": "分布式事务常用的解决方案是？", "opts": ["Saga", "2PC", "3PC", "所有以上"], "a": "D"},
        {"q": "事件驱动架构的核心是？", "opts": ["消息队列", "同步调用", "数据库", "API 网关"], "a": "A"},
    ],
    "缓存": [
        {"q": "缓存的主要作用是？", "opts": ["减少数据库压力", "增加存储空间", "提高安全性", "持久化数据"], "a": "A"},
        {"q": "缓存穿透是指？", "opts": ["请求不存在的 Key", "同一 Key 大量请求", "缓存失效", "缓存过期"], "a": "A"},
        {"q": "缓存击穿是指？", "opts": ["热点 Key 失效", "请求不存在的 Key", "缓存和数据库不一致", "缓存溢出"], "a": "A"},
        {"q": "缓存雪崩是指？", "opts": ["大量 Key 同时失效", "单个 Key 失效", "缓存内存不足", "缓存服务器宕机"], "a": "A"},
        {"q": "解决缓存穿透常用？", "opts": ["布隆过滤器", "互斥锁", "过期时间随机化", "预热"], "a": "A"},
        {"q": "解决缓存击穿常用？", "opts": ["互斥锁", "布隆过滤器", "删除过期 Key", "压缩数据"], "a": "A"},
        {"q": "解决缓存雪崩常用？", "opts": ["过期时间随机化", "布隆过滤器", "单一锁", "禁用过期"], "a": "A"},
        {"q": "缓存更新策略 Write-Through 指？", "opts": ["先写缓存再写数据库", "先写数据库再写缓存", "只写数据库", "只写缓存"], "a": "A"},
        {"q": "LRU 缓存淘汰策略是？", "opts": ["最近最少使用", "最近不使用", "先进先出", "最少使用"], "a": "A"},
        {"q": "Redis 适合做缓存因为？", "opts": ["性能高", "持久化", "事务", "备份"], "a": "A"},
    ],
    "数据库": [
        {"q": "关系型数据库和 NoSQL 的主要区别？", "opts": ["Schema 严格 vs 灵活", "性能更高", "更安全", "更便宜"], "a": "A"},
        {"q": "分库分表的主要目的是？", "opts": ["应对数据量增长", "提高一致性", "简化查询", "减少服务器"], "a": "A"},
        {"q": "读写分离的主要目的是？", "opts": ["提高读性能", "提高写性能", "提高一致性", "减少服务器"], "a": "A"},
        {"q": "索引的主要作用是？", "opts": ["加速查询", "加速写入", "增加存储空间", "数据压缩"], "a": "A"},
        {"q": "B+ 树索引的优势是？", "opts": ["范围查询高效", "内存占用小", "写入快", "删除快"], "a": "A"},
        {"q": "事务 ACID 中的 I 是？", "opts": ["隔离性", "一致性", "持久性", "原子性"], "a": "A"},
        {"q": "MVCC 的主要作用是？", "opts": ["读写不阻塞", "提高写性能", "数据备份", "事务回滚"], "a": "A"},
        {"q": "乐观锁和悲观锁的区别是？", "opts": ["是否假设冲突", "性能高低", "安全性", "实现复杂度"], "a": "A"},
    ],
    "负载均衡": [
        {"q": "负载均衡的主要作用是？", "opts": ["分发请求", "增加带宽", "提高安全性", "数据备份"], "a": "A"},
        {"q": "轮询算法的特点是？", "opts": ["依次分配", "按权重分配", "随机分配", "最少连接"], "a": "A"},
        {"q": "加权轮询适合？", "opts": ["服务器性能不同", "服务器性能相同", "连接数差异大", "响应时间不同"], "a": "A"},
        {"q": "最少连接算法的特点是？", "opts": ["分配给连接数最少的", "依次分配", "随机分配", "按权重分配"], "a": "A"},
        {"q": "一致性哈希的主要优势是？", "opts": ["增减节点影响小", "负载更均衡", "实现简单", "性能更高"], "a": "A"},
        {"q": "七层负载均衡工作在？", "opts": ["应用层", "网络层", "传输层", "数据链路层"], "a": "A"},
        {"q": "四层负载均衡工作在？", "opts": ["传输层", "应用层", "网络层", "数据链路层"], "a": "A"},
        {"q": "Nginx 通常用作？", "opts": ["七层负载均衡", "四层负载均衡", "三层负载均衡", "二层负载均衡"], "a": "A"},
    ],
    "消息队列": [
        {"q": "消息队列的主要作用是？", "opts": ["解耦和异步", "同步通信", "数据持久化", "缓存"], "a": "A"},
        {"q": "Kafka 的存储特点是？", "opts": ["追加写入", "随机写入", "事务存储", "键值存储"], "a": "A"},
        {"q": "RabbitMQ 的特色是？", "opts": ["灵活的路由", "高吞吐", "持久化", "分片"], "a": "A"},
        {"q": "消息队列的确认机制用于？", "opts": ["保证消息不丢失", "提高速度", "减少内存", "负载均衡"], "a": "A"},
        {"q": "消费者组的作用是？", "opts": ["负载均衡消费", "提高生产者速度", "消息备份", "延迟消费"], "a": "A"},
        {"q": "死信队列用于？", "opts": ["处理失败的消息", "存储重要消息", "消息备份", "延迟消息"], "a": "A"},
        {"q": "幂等性是指？", "opts": ["多次执行结果相同", "一次执行", "执行失败回滚", "执行成功返回"], "a": "A"},
    ],
    "设计模式": [
        {"q": "单例模式保证？", "opts": ["一个类只有一个实例", "多个实例", "不可实例化", "延迟加载"], "a": "A"},
        {"q": "工厂模式用于？", "opts": ["创建对象", "单例", "组合", "代理"], "a": "A"},
        {"q": "观察者模式适合？", "opts": ["事件通知", "创建对象", "结构组合", "算法替换"], "a": "A"},
        {"q": "策略模式的特点是？", "opts": ["算法可替换", "创建对象", "结构组合", "事件通知"], "a": "A"},
        {"q": "装饰器模式用于？", "opts": ["动态添加功能", "创建对象", "结构组合", "算法替换"], "a": "A"},
        {"q": "适配器模式的作用是？", "opts": ["接口转换", "创建对象", "动态功能", "算法替换"], "a": "A"},
    ],
    "高可用": [
        {"q": "高可用的衡量指标是？", "opts": ["99.99% 等 uptime", "响应时间", "吞吐量", "并发数"], "a": "A"},
        {"q": "主从复制的主要目的是？", "opts": ["数据备份和读扩展", "写扩展", "提高一致性", "减少存储"], "a": "A"},
        {"q": "哨兵模式用于？", "opts": ["自动故障转移", "数据备份", "负载均衡", "缓存"], "a": "A"},
        {"q": "集群中节点数通常为奇数是为了？", "opts": ["避免脑裂", "提高性能", "减少成本", "负载均衡"], "a": "A"},
        {"q": "Raft 算法是？", "opts": ["共识算法", "加密算法", "压缩算法", "排序算法"], "a": "A"},
    ],
}


def generate_system_design_questions(target_count=150):
    """生成系统设计题目"""
    questions = []
    qid = 1

    # 难度分布：简单 30%, 中等 50%, 困难 20%
    easy_count = int(target_count * 0.3)
    medium_count = int(target_count * 0.5)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["缓存", "负载均衡", "设计模式"]
    medium_cats = ["微服务", "数据库", "消息队列"]
    hard_cats = ["微服务", "数据库", "高可用"]

    # 生成简单题
    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in SYSTEM_DESIGN_TEMPLATES and SYSTEM_DESIGN_TEMPLATES[cat]:
            template = random.choice(SYSTEM_DESIGN_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"系统设计-{cat}-{qid}",
                "category": cat,
                "difficulty": "简单",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["system_design"]
            })
            qid += 1

    # 生成中等题
    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in SYSTEM_DESIGN_TEMPLATES and SYSTEM_DESIGN_TEMPLATES[cat]:
            template = random.choice(SYSTEM_DESIGN_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"系统设计-{cat}-{qid}",
                "category": cat,
                "difficulty": "中等",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["system_design"]
            })
            qid += 1

    # 生成困难题
    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in SYSTEM_DESIGN_TEMPLATES and SYSTEM_DESIGN_TEMPLATES[cat]:
            template = random.choice(SYSTEM_DESIGN_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"系统设计-{cat}-{qid}",
                "category": cat,
                "difficulty": "困难",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["system_design"]
            })
            qid += 1

    return questions


class SystemDesignEvaluator:
    """系统设计评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_system_design_questions(150)

    def run_tests(self):
        """运行系统设计测试"""
        return self.base_eval.run_tests(self.test_cases, "system_design")

    def generate_report(self, result):
        """生成报告"""
        return self.base_eval.generate_report(result)


def run_system_design_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """便捷函数运行系统设计测试"""
    evaluator = SystemDesignEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {
        "result": result,
        "report_file": report_file
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 系统设计测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型地址")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M", help="模型名称")
    parser.add_argument("--output-dir", default="eval_results/stage4", help="输出目录")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_system_design_questions(150)
        print(f"生成了 {len(questions)} 道系统设计题目:")
        easy = sum(1 for q in questions if q["difficulty"] == "简单")
        medium = sum(1 for q in questions if q["difficulty"] == "中等")
        hard = sum(1 for q in questions if q["difficulty"] == "困难")
        print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

        # 保存题目
        output_file = os.path.join(args.output_dir, "system_design_questions.json")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到：{output_file}")
    else:
        print(f"开始运行系统设计测试...")
        test_result = run_system_design_test(args.model_url, args.model_name, args.output_dir)
        print(f"\n测试完成！通过率：{test_result['result'].pass_rate*100:.1f}%")
