#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - CI/CD 与自动化 (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

CICD_TEMPLATES = {
    "CI/CD 基础": [
        {"q": "CI 的含义是？", "opts": ["持续集成", "持续部署", "持续交付", "持续开发"], "a": "A"},
        {"q": "CD 的含义是？", "opts": ["持续部署/交付", "持续开发", "持续集成", "持续测试"], "a": "A"},
        {"q": "CI/CD 的主要目标是？", "opts": ["自动化软件交付", "手动部署", "代码编写", "需求分析"], "a": "A"},
        {"q": "构建 (Build) 阶段包括？", "opts": ["编译和打包", "部署", "测试", "监控"], "a": "A"},
        {"q": "测试阶段包括？", "opts": ["单元测试和集成测试", "只构建", "只部署", "只监控"], "a": "A"},
        {"q": "部署阶段包括？", "opts": ["发布到环境", "编译", "测试", "开发"], "a": "A"},
    ],
    "Jenkins": [
        {"q": "Jenkins 是？", "opts": ["CI/CD 工具", "代码编辑器", "数据库", "操作系统"], "a": "A"},
        {"q": "Jenkins Pipeline 用？", "opts": ["Jenkinsfile", "pipeline.yml", "ci.yaml", ".gitlab-ci.yml"], "a": "A"},
        {"q": "Jenkins 的默认端口是？", "opts": ["8080", "3000", "9090", "80"], "a": "A"},
        {"q": "Stage 在 Pipeline 中是？", "opts": ["阶段", "步骤", "节点", "代理"], "a": "A"},
        {"q": "Step 在 Pipeline 中是？", "opts": ["步骤", "阶段", "节点", "代理"], "a": "A"},
        {"q": "Agent 在 Pipeline 中是？", "opts": ["执行环境", "阶段", "步骤", "脚本"], "a": "A"},
    ],
    "GitHub Actions": [
        {"q": "GitHub Actions 配置文件？", "opts": [".github/workflows/*.yml", ".gitlab-ci.yml", "Jenkinsfile", "ci.yaml"], "a": "A"},
        {"q": "Workflow 是？", "opts": ["自动化流程", "单个任务", "配置文件", "环境变量"], "a": "A"},
        {"q": "Job 是？", "opts": ["一组步骤", "单个步骤", "整个工作流", "触发器"], "a": "A"},
        {"q": "Step 是？", "opts": ["单个任务", "一组任务", "整个工作流", "触发器"], "a": "A"},
        {"q": "Action 是？", "opts": ["可复用的步骤", "工作流", "任务", "触发器"], "a": "A"},
        {"q": "Runner 是？", "opts": ["执行环境", "配置文件", "触发器", "变量"], "a": "A"},
    ],
    "GitLab CI": [
        {"q": "GitLab CI 配置文件？", "opts": [".gitlab-ci.yml", ".github/workflows/*.yml", "Jenkinsfile", "ci.yaml"], "a": "A"},
        {"q": "Pipeline 在 GitLab 中是？", "opts": ["整个 CI/CD 流程", "单个任务", "阶段", "作业"], "a": "A"},
        {"q": "Stage 在 GitLab 中是？", "opts": ["阶段", "作业", "管道", "变量"], "a": "A"},
        {"q": "Job 在 GitLab 中是？", "opts": ["作业", "阶段", "管道", "变量"], "a": "A"},
        {"q": "Runner 在 GitLab 中是？", "opts": ["执行器", "配置文件", "触发器", "变量"], "a": "A"},
    ],
    "部署策略": [
        {"q": "蓝绿部署的特点是？", "opts": ["两套环境切换", "灰度发布", "滚动更新", "回滚"], "a": "A"},
        {"q": "金丝雀发布是？", "opts": ["逐步发布给部分用户", "全量发布", "回滚", "测试"], "a": "A"},
        {"q": "滚动更新是？", "opts": ["逐个替换实例", "同时替换所有", "两套环境", "停止服务"], "a": "A"},
        {"q": "特性开关 (Feature Flag) 用于？", "opts": ["动态启用功能", "代码分支", "版本控制", "回滚"], "a": "A"},
        {"q": "回滚 (Rollback) 是？", "opts": ["恢复到之前版本", "部署新版本", "测试版本", "删除版本"], "a": "A"},
    ],
    "自动化": [
        {"q": "Ansible 是？", "opts": ["配置管理工具", "CI/CD 工具", "监控工具", "日志工具"], "a": "A"},
        {"q": "Ansible 使用？", "opts": ["YAML", "JSON", "XML", "INI"], "a": "A"},
        {"q": "Playbook 在 Ansible 中是？", "opts": ["剧本/配置", "角色", "任务", "变量"], "a": "A"},
        {"q": "Role 在 Ansible 中是？", "opts": ["可复用的配置单元", "剧本", "任务", "变量"], "a": "A"},
        {"q": "Inventory 在 Ansible 中是？", "opts": ["主机清单", "剧本", "角色", "变量"], "a": "A"},
    ],
}


def generate_cicd_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["CI/CD 基础", "GitHub Actions"]
    medium_cats = ["Jenkins", "GitLab CI", "部署策略"]
    hard_cats = ["部署策略", "自动化"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in CICD_TEMPLATES and CICD_TEMPLATES[cat]:
            template = random.choice(CICD_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"CI/CD-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cicd"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in CICD_TEMPLATES and CICD_TEMPLATES[cat]:
            template = random.choice(CICD_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"CI/CD-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cicd"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in CICD_TEMPLATES and CICD_TEMPLATES[cat]:
            template = random.choice(CICD_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"CI/CD-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["cicd"]
            })
            qid += 1

    return questions


class CICDEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_cicd_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "cicd")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_cicd_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = CICDEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 CI/CD 测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_cicd_questions(150)
        print(f"生成了 {len(questions)} 道 CI/CD 题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "cicd_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_cicd_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
