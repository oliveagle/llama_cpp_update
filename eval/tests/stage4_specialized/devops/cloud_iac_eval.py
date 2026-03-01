#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - 云服务与 IaC (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

CLOUD_IAC_TEMPLATES = {
    "AWS 基础": [
        {"q": "AWS EC2 是？", "opts": ["虚拟机服务", "对象存储", "数据库", "负载均衡"], "a": "A"},
        {"q": "AWS S3 是？", "opts": ["对象存储", "虚拟机", "数据库", "消息队列"], "a": "A"},
        {"q": "AWS RDS 是？", "opts": ["托管数据库", "对象存储", "虚拟机", "缓存"], "a": "A"},
        {"q": "AWS Lambda 是？", "opts": ["无服务器计算", "虚拟机", "容器", "数据库"], "a": "A"},
        {"q": "AWS VPC 是？", "opts": ["虚拟私有云", "对象存储", "数据库", "负载均衡"], "a": "A"},
        {"q": "AWS IAM 是？", "opts": ["身份和访问管理", "虚拟机管理", "网络管理", "存储管理"], "a": "A"},
        {"q": "AWS ELB 是？", "opts": ["负载均衡", "对象存储", "数据库", "缓存"], "a": "A"},
        {"q": "AWS CloudWatch 是？", "opts": ["监控服务", "存储服务", "计算服务", "网络服务"], "a": "A"},
        {"q": "AWS Route 53 是？", "opts": ["DNS 服务", "负载均衡", "CDN", "数据库"], "a": "A"},
        {"q": "AWS CloudFront 是？", "opts": ["CDN", "DNS", "负载均衡", "存储"], "a": "A"},
    ],
    "Terraform": [
        {"q": "Terraform 是？", "opts": ["基础设施即代码工具", "CI/CD 工具", "监控工具", "日志工具"], "a": "A"},
        {"q": "Terraform 使用？", "opts": ["HCL", "YAML", "JSON", "XML"], "a": "A"},
        {"q": "Provider 在 Terraform 中是？", "opts": ["云服务商", "资源", "模块", "变量"], "a": "A"},
        {"q": "Resource 在 Terraform 中是？", "opts": ["基础设施组件", "云服务商", "模块", "变量"], "a": "A"},
        {"q": "Module 在 Terraform 中是？", "opts": ["可复用配置", "资源", "提供者", "变量"], "a": "A"},
        {"q": "State 在 Terraform 中是？", "opts": ["基础设施状态", "配置文件", "变量", "输出"], "a": "A"},
        {"q": "terraform init 用于？", "opts": ["初始化", "应用", "计划", "销毁"], "a": "A"},
        {"q": "terraform plan 用于？", "opts": ["预览变更", "应用变更", "初始化", "销毁"], "a": "A"},
        {"q": "terraform apply 用于？", "opts": ["应用变更", "预览变更", "初始化", "销毁"], "a": "A"},
        {"q": "terraform destroy 用于？", "opts": ["销毁资源", "应用变更", "预览变更", "初始化"], "a": "A"},
    ],
    "云原生": [
        {"q": "云原生 (Cloud Native) 的核心是？", "opts": ["容器、微服务、DevOps", "虚拟机", "物理机", "传统架构"], "a": "A"},
        {"q": "CNCF 是？", "opts": ["云原生计算基金会", "云服务提供商", "容器运行时", "编排工具"], "a": "A"},
        {"q": "Service Mesh 用于？", "opts": ["服务间通信管理", "服务发现", "负载均衡", "数据存储"], "a": "A"},
        {"q": "Istio 是？", "opts": ["Service Mesh", "容器运行时", "CI/CD 工具", "监控工具"], "a": "A"},
        {"q": "Envoy 是？", "opts": ["代理", "容器运行时", "CI/CD 工具", "监控工具"], "a": "A"},
        {"q": "GitOps 是？", "opts": ["Git 作为单一事实来源", "Git 作为 CI/CD", "Git 作为存储", "Git 作为监控"], "a": "A"},
        {"q": "ArgoCD 是？", "opts": ["GitOps 工具", "CI 工具", "监控工具", "日志工具"], "a": "A"},
    ],
    "无服务器": [
        {"q": "Serverless 的特点是？", "opts": ["无需管理服务器", "自己管理服务器", "使用物理机", "使用虚拟机"], "a": "A"},
        {"q": "FaaS 是？", "opts": ["函数即服务", "平台即服务", "基础设施即服务", "软件即服务"], "a": "A"},
        {"q": "冷启动是指？", "opts": ["函数首次执行延迟", "函数执行中", "函数结束", "函数错误"], "a": "A"},
        {"q": "AWS Lambda 的计费方式是？", "opts": ["按调用次数和执行时间", "按服务器数量", "按存储大小", "按带宽"], "a": "A"},
    ],
    "云服务模型": [
        {"q": "IaaS 是？", "opts": ["基础设施即服务", "平台即服务", "软件即服务", "函数即服务"], "a": "A"},
        {"q": "PaaS 是？", "opts": ["平台即服务", "基础设施即服务", "软件即服务", "函数即服务"], "a": "A"},
        {"q": "SaaS 是？", "opts": ["软件即服务", "基础设施即服务", "平台即服务", "函数即服务"], "a": "A"},
        {"q": "AWS EC2 属于？", "opts": ["IaaS", "PaaS", "SaaS", "FaaS"], "a": "A"},
        {"q": "AWS RDS 属于？", "opts": ["PaaS", "IaaS", "SaaS", "FaaS"], "a": "A"},
        {"q": "Gmail 属于？", "opts": ["SaaS", "IaaS", "PaaS", "FaaS"], "a": "A"},
    ],
}


def generate_cloud_iac_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["云服务模型", "AWS 基础"]
    medium_cats = ["Terraform", "无服务器"]
    hard_cats = ["Terraform", "云原生"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in CLOUD_IAC_TEMPLATES and CLOUD_IAC_TEMPLATES[cat]:
            template = random.choice(CLOUD_IAC_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"云IaC-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cloud_iac"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in CLOUD_IAC_TEMPLATES and CLOUD_IAC_TEMPLATES[cat]:
            template = random.choice(CLOUD_IAC_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"云IaC-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cloud_iac"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in CLOUD_IAC_TEMPLATES and CLOUD_IAC_TEMPLATES[cat]:
            template = random.choice(CLOUD_IAC_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"云IaC-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cloud_iac"]
            })
            qid += 1

    return questions


class CloudIACEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_cloud_iac_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "cloud_iac")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_cloud_iac_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = CloudIACEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 云服务与 IaC 测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_cloud_iac_questions(150)
        print(f"生成了 {len(questions)} 道云服务与 IaC 题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "cloud_iac_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_cloud_iac_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
