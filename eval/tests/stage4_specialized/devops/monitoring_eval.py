#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - 监控与日志 (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

MONITORING_TEMPLATES = {
    "Prometheus": [
        {"q": "Prometheus 的数据模型是？", "opts": ["时间序列", "关系型", "文档型", "键值型"], "a": "A"},
        {"q": "PromQL 是？", "opts": ["Prometheus 查询语言", "SQL 方言", "Python API", "配置语言"], "a": "A"},
        {"q": "Gauge 指标类型是？", "opts": ["可上可下的数值", "只增不减", "直方图", "摘要"], "a": "A"},
        {"q": "Counter 指标类型是？", "opts": ["只增不减", "可上可下", "直方图", "摘要"], "a": "A"},
        {"q": "Histogram 用于？", "opts": ["分布统计", "计数", "当前值", "采样"], "a": "A"},
        {"q": "Summary 用于？", "opts": ["分位数统计", "计数", "当前值", "采样"], "a": "A"},
        {"q": "Prometheus 存储是？", "opts": ["本地时序数据库", "远程存储", "内存数据库", "关系数据库"], "a": "A"},
        {"q": "Prometheus AlertManager 用于？", "opts": ["告警路由和聚合", "数据存储", "查询", "可视化"], "a": "A"},
        {"q": "Prometheus 的默认端口是？", "opts": ["9090", "3000", "9100", "8080"], "a": "A"},
    ],
    "Grafana": [
        {"q": "Grafana 用于？", "opts": ["数据可视化", "数据存储", "数据采集", "告警"], "a": "A"},
        {"q": "Grafana 的默认端口是？", "opts": ["3000", "9090", "9100", "8080"], "a": "A"},
        {"q": "Panel 在 Grafana 中是？", "opts": ["单个图表", "整个仪表板", "数据源", "变量"], "a": "A"},
        {"q": "Dashboard 在 Grafana 中是？", "opts": ["Panel 的集合", "单个图表", "数据源", "变量"], "a": "A"},
        {"q": "Grafana 变量用于？", "opts": ["动态切换数据", "固定数据", "存储数据", "告警"], "a": "A"},
    ],
    "ELK 栈": [
        {"q": "Elasticsearch 是？", "opts": ["搜索引擎", "日志收集", "可视化", "消息队列"], "a": "A"},
        {"q": "Logstash 是？", "opts": ["日志处理", "日志存储", "日志可视化", "日志采集"], "a": "A"},
        {"q": "Kibana 是？", "opts": ["可视化", "日志收集", "日志存储", "消息队列"], "a": "A"},
        {"q": "Filebeat 是？", "opts": ["轻量级日志采集", "日志存储", "日志处理", "可视化"], "a": "A"},
        {"q": "Index 在 Elasticsearch 中是？", "opts": ["文档集合", "单个文档", "字段", "类型"], "a": "A"},
    ],
    "系统监控": [
        {"q": "CPU 使用率的查看命令是？", "opts": ["top", "df", "free", "netstat"], "a": "A"},
        {"q": "内存使用的查看命令是？", "opts": ["free -h", "top", "df", "netstat"], "a": "A"},
        {"q": "磁盘使用的查看命令是？", "opts": ["df -h", "top", "free", "netstat"], "a": "A"},
        {"q": "进程查看的命令是？", "opts": ["ps aux", "df", "free", "netstat"], "a": "A"},
        {"q": "网络连接的查看命令是？", "opts": ["ss -tuln", "top", "free", "df"], "a": "A"},
        {"q": "uptime 显示的负载是？", "opts": ["平均进程数", "CPU 使用率", "内存使用率", "磁盘使用率"], "a": "A"},
    ],
}


def generate_monitoring_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["系统监控", "Grafana"]
    medium_cats = ["Prometheus", "ELK 栈"]
    hard_cats = ["Prometheus", "ELK 栈"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in MONITORING_TEMPLATES and MONITORING_TEMPLATES[cat]:
            template = random.choice(MONITORING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"监控-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["monitoring"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in MONITORING_TEMPLATES and MONITORING_TEMPLATES[cat]:
            template = random.choice(MONITORING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"监控-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["monitoring"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in MONITORING_TEMPLATES and MONITORING_TEMPLATES[cat]:
            template = random.choice(MONITORING_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"监控-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["monitoring"]
            })
            qid += 1

    return questions


class MonitoringEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_monitoring_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "monitoring")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_monitoring_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = MonitoringEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 监控测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_monitoring_questions(150)
        print(f"生成了 {len(questions)} 道监控题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "monitoring_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_monitoring_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
