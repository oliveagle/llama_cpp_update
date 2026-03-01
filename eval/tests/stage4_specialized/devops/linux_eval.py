#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - Linux/DevOps (200 题生成器)
自动生成运维题目，包含选择题和命令编写题
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

# Linux/DevOps 题目模板
DEVOPS_TEMPLATES = {
    "Linux 基础": [
        {"q": "查看当前目录用哪个命令？", "opts": ["pwd", "cd", "ls", "dir"], "a": "A"},
        {"q": "列出所有文件包括隐藏文件用？", "opts": ["ls -a", "ls -l", "ls -h", "ll"], "a": "A"},
        {"q": "切换到上一级目录用？", "opts": ["cd ..", "cd /", "cd ~", "cd -"], "a": "A"},
        {"q": "创建目录用？", "opts": ["mkdir", "touch", "cd", "mkfile"], "a": "A"},
        {"q": "删除非空目录用？", "opts": ["rm -rf", "rm -f", "rmdir", "rm"], "a": "A"},
        {"q": "复制文件用？", "opts": ["cp", "mv", "rm", "tar"], "a": "A"},
        {"q": "移动文件用？", "opts": ["mv", "cp", "rm", "ln"], "a": "A"},
        {"q": "查看文件内容用？", "opts": ["cat", "cp", "cd", "cr"], "a": "A"},
        {"q": "分页查看文件用？", "opts": ["less", "cat", "head", "tail"], "a": "A"},
        {"q": "查看文件前 10 行用？", "opts": ["head", "tail", "less", "more"], "a": "A"},
    ],
    "文本处理": [
        {"q": "搜索文件内容用？", "opts": ["grep", "find", "locate", "whereis"], "a": "A"},
        {"q": "统计文件行数用？", "opts": ["wc -l", "wc -w", "wc -c", "count"], "a": "A"},
        {"q": "替换文本用？", "opts": ["sed", "grep", "awk", "find"], "a": "A"},
        {"q": "格式化文本处理用？", "opts": ["awk", "grep", "sed", "cut"], "a": "A"},
        {"q": "提取列用？", "opts": ["cut", "awk", "都可以", "都不行"], "a": "C"},
        {"q": "排序文件内容用？", "opts": ["sort", "order", "rank", "arrange"], "a": "A"},
        {"q": "去重用？", "opts": ["uniq", "rm", "del", "distinct"], "a": "A"},
        {"q": "比较两个文件用？", "opts": ["diff", "comp", "cmp", "compare"], "a": "A"},
    ],
    "进程管理": [
        {"q": "查看进程用？", "opts": ["ps aux", "ls -l", "top", "htop"], "a": "A"},
        {"q": "动态查看进程用？", "opts": ["top", "ps", "ls", "pstree"], "a": "A"},
        {"q": "杀死进程用？", "opts": ["kill", "stop", "end", "rm"], "a": "A"},
        {"q": "后台运行用？", "opts": ["&", "#", "%", "$"], "a": "A"},
        {"q": "前台任务用？", "opts": ["fg", "bg", "jobs", "nohup"], "a": "A"},
        {"q": "查看端口占用用？", "opts": ["netstat -tulpn", "ps aux", "top", "ifconfig"], "a": "A"},
        {"q": "终止进程的信号是？", "opts": ["SIGKILL", "SIGTERM", "SIGHUP", "SIGINT"], "a": "A"},
    ],
    "权限管理": [
        {"q": "修改文件权限用？", "opts": ["chmod", "chown", "chgrp", "umask"], "a": "A"},
        {"q": "修改文件所有者用？", "opts": ["chown", "chmod", "chgrp", "umask"], "a": "A"},
        {"q": "755 权限表示？", "opts": ["rwxr-xr-x", "rwxrwxrwx", "rw-r--r--", "rwx------"], "a": "A"},
        {"q": "设置可执行权限用？", "opts": ["chmod +x", "chmod 777", "chown +x", "umask +x"], "a": "A"},
        {"q": "查看文件权限用？", "opts": ["ls -l", "ls -a", "ls -h", "ls -t"], "a": "A"},
    ],
    "网络命令": [
        {"q": "测试网络连通性用？", "opts": ["ping", "pong", "curl", "wget"], "a": "A"},
        {"q": "下载文件用？", "opts": ["wget", "download", "curl", "fetch"], "a": "A"},
        {"q": "发送 HTTP 请求用？", "opts": ["curl", "wget", "ping", "ssh"], "a": "A"},
        {"q": "SSH 登录用？", "opts": ["ssh", "sftp", "scp", "telnet"], "a": "A"},
        {"q": "查看 IP 地址用？", "opts": ["ip addr", "ifconfig", "都可以", "都不行"], "a": "C"},
        {"q": "查看路由表用？", "opts": ["ip route", "route", "都可以", "都不行"], "a": "C"},
        {"q": "DNS 解析用？", "opts": ["nslookup", "dig", "都可以", "都不行"], "a": "C"},
        {"q": "查看开放端口用？", "opts": ["ss -tuln", "netstat -tuln", "都可以", "都不行"], "a": "C"},
    ],
    "系统信息": [
        {"q": "查看磁盘空间用？", "opts": ["df -h", "du -h", "ls -lh", "free -h"], "a": "A"},
        {"q": "查看目录大小用？", "opts": ["du -sh", "df -h", "ls -lh", "free -h"], "a": "A"},
        {"q": "查看内存用？", "opts": ["free -h", "df -h", "top", "ps"], "a": "A"},
        {"q": "查看系统信息用？", "opts": ["uname -a", "hostname", "whoami", "pwd"], "a": "A"},
        {"q": "查看 Linux 版本用？", "opts": ["cat /etc/os-release", "uname -a", "version", "os-ver"], "a": "A"},
        {"q": "查看 CPU 信息用？", "opts": ["cat /proc/cpuinfo", "cpuinfo", "lscpu", "都可以"], "a": "D"},
    ],
    "Docker 基础": [
        {"q": "运行容器用？", "opts": ["docker run", "docker start", "docker create", "docker exec"], "a": "A"},
        {"q": "查看容器用？", "opts": ["docker ps", "docker images", "docker run", "docker start"], "a": "A"},
        {"q": "停止容器用？", "opts": ["docker stop", "docker kill", "docker rm", "docker pause"], "a": "A"},
        {"q": "删除容器用？", "opts": ["docker rm", "docker stop", "docker kill", "docker rmi"], "a": "A"},
        {"q": "查看镜像用？", "opts": ["docker images", "docker ps", "docker run", "docker pull"], "a": "A"},
        {"q": "拉取镜像用？", "opts": ["docker pull", "docker push", "docker run", "docker build"], "a": "A"},
        {"q": "构建镜像用？", "opts": ["docker build", "docker create", "docker run", "docker push"], "a": "A"},
        {"q": "进入容器用？", "opts": ["docker exec -it", "docker run -it", "docker attach", "都可以"], "a": "D"},
        {"q": "查看容器日志用？", "opts": ["docker logs", "docker inspect", "docker events", "docker history"], "a": "A"},
        {"q": "容器导出用？", "opts": ["docker export", "docker save", "docker push", "docker commit"], "a": "A"},
    ],
    "Kubernetes": [
        {"q": "kubectl 查看 Pod 用？", "opts": ["kubectl get pods", "kubectl list pods", "kubectl show pods", "kubectl desc pods"], "a": "A"},
        {"q": "创建资源用？", "opts": ["kubectl apply", "kubectl create", "都可以", "都不行"], "a": "C"},
        {"q": "删除资源用？", "opts": ["kubectl delete", "kubectl remove", "kubectl rm", "kubectl drop"], "a": "A"},
        {"q": "查看日志用？", "opts": ["kubectl logs", "kubectl log", "kubectl logview", "kubectl showlogs"], "a": "A"},
        {"q": "进入 Pod 用？", "opts": ["kubectl exec -it", "kubectl run -it", "kubectl attach", "kubectl enter"], "a": "A"},
        {"q": "滚动更新用？", "opts": ["kubectl rollout", "kubectl update", "kubectl upgrade", "kubectl refresh"], "a": "A"},
        {"q": "Service 类型不包括？", "opts": ["Service", "Deployment", "NodePort", "LoadBalancer"], "a": "B"},
        {"q": "ConfigMap 用于？", "opts": ["配置管理", "存储", "网络", "计算"], "a": "A"},
    ],
    "CI/CD": [
        {"q": "Jenkins Pipeline 用？", "opts": ["Jenkinsfile", "pipeline.yml", "ci.yaml", ".gitlab-ci.yml"], "a": "A"},
        {"q": "GitHub Actions 配置文件？", "opts": [".github/workflows/*.yml", ".gitlab-ci.yml", "Jenkinsfile", "ci.yaml"], "a": "A"},
        {"q": "GitLab CI 配置文件？", "opts": [".gitlab-ci.yml", ".github/workflows/*.yml", "Jenkinsfile", "ci.yaml"], "a": "A"},
        {"q": "ArgoCD 用于？", "opts": ["GitOps", "CI", "测试", "监控"], "a": "A"},
        {"q": "持续集成是？", "opts": ["CI", "CD", "CT", "CM"], "a": "A"},
    ],
    "监控": [
        {"q": "Prometheus 用于？", "opts": ["监控", "日志", "CI", "CD"], "a": "A"},
        {"q": "Grafana 用于？", "opts": ["可视化", "监控", "日志", "CI"], "a": "A"},
        {"q": "ELK 不包含？", "opts": ["Elasticsearch", "Logstash", "Kibana", "Prometheus"], "a": "D"},
        {"q": "收集日志用？", "opts": ["Filebeat", "Prometheus", "Grafana", "AlertManager"], "a": "A"},
    ],
    "Shell 脚本": [
        {"q": "Shell 脚本开头？", "opts": ["#!/bin/bash", "#!/bin/sh", "//bin/bash", "<bash>"], "a": "A"},
        {"q": "定义变量？", "opts": ["VAR=value", "var = value", "$VAR=value", "@VAR=value"], "a": "A"},
        {"q": "条件判断？", "opts": ["if [ ]; then", "if ( ) {", "if < > then", "when [ ]"], "a": "A"},
        {"q": "循环用？", "opts": ["for", "loop", "while", "foreach"], "a": "A"},
        {"q": "函数定义？", "opts": ["func() {}", "function func {}", "都可以", "def func()"], "a": "C"},
        {"q": "获取参数？", "opts": ["$1", "%1", "#1", "@1"], "a": "A"},
        {"q": "退出码？", "opts": ["$?", "$#", "$!", "$$"], "a": "A"},
    ],
    "Nginx": [
        {"q": "Nginx 配置文件？", "opts": ["nginx.conf", "httpd.conf", "apache.conf", "web.conf"], "a": "A"},
        {"q": "重启 Nginx 用？", "opts": ["systemctl restart nginx", "service nginx restart", "都可以", "都不行"], "a": "C"},
        {"q": "反向代理用？", "opts": ["proxy_pass", "redirect", "forward", "rewrite"], "a": "A"},
        {"q": "负载均衡用？", "opts": ["upstream", "backend", "server", "balance"], "a": "A"},
    ],
}

def generate_devops_questions(target_count=200):
    """生成运维题目"""
    questions = []
    qid = 1

    # 难度分布：简单 35%, 中等 45%, 困难 20%
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["Linux 基础", "文本处理", "权限管理", "Docker 基础", "Shell 脚本"]
    medium_cats = ["进程管理", "网络命令", "系统信息", "Kubernetes", "CI/CD", "监控", "Nginx"]
    hard_cats = ["Kubernetes", "CI/CD", "监控", "Docker 基础"]

    # 生成简单题
    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in DEVOPS_TEMPLATES and DEVOPS_TEMPLATES[cat]:
            template = random.choice(DEVOPS_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"运维-{cat}-{qid}",
                "category": cat,
                "difficulty": "简单",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["devops"]
            })
            qid += 1

    # 生成中等题
    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in DEVOPS_TEMPLATES and DEVOPS_TEMPLATES[cat]:
            template = random.choice(DEVOPS_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"运维-{cat}-{qid}",
                "category": cat,
                "difficulty": "中等",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["devops"]
            })
            qid += 1

    # 生成困难题
    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in DEVOPS_TEMPLATES and DEVOPS_TEMPLATES[cat]:
            template = random.choice(DEVOPS_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"运维-{cat}-{qid}",
                "category": cat,
                "difficulty": "困难",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["devops"]
            })
            qid += 1

    return questions


class DevOpsEvaluator:
    """运维评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_devops_questions(200)

    def run_tests(self):
        """运行运维测试"""
        return self.base_eval.run_tests(self.test_cases, "devops")

    def generate_report(self, result):
        """生成报告"""
        return self.base_eval.generate_report(result)


def run_devops_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """便捷函数运行运维测试"""
    evaluator = DevOpsEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {
        "result": result,
        "report_file": report_file
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 运维测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型地址")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M", help="模型名称")
    parser.add_argument("--output-dir", default="eval_results/stage4", help="输出目录")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_devops_questions(200)
        print(f"生成了 {len(questions)} 道运维题目:")
        easy = sum(1 for q in questions if q["difficulty"] == "简单")
        medium = sum(1 for q in questions if q["difficulty"] == "中等")
        hard = sum(1 for q in questions if q["difficulty"] == "困难")
        print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

        # 保存题目
        output_file = os.path.join(args.output_dir, "devops_questions.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到：{output_file}")
    else:
        print(f"开始运行运维测试...")
        test_result = run_devops_test(args.model_url, args.model_name, args.output_dir)
        print(f"\n测试完成！通过率：{test_result['result'].pass_rate*100:.1f}%")
