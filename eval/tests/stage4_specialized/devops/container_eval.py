#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - 容器与编排 (200 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

CONTAINER_TEMPLATES = {
    "Docker 基础": [
        {"q": "Docker 镜像是？", "opts": ["只读模板", "运行中的容器", "数据卷", "网络配置"], "a": "A"},
        {"q": "Docker 容器是？", "opts": ["镜像的运行实例", "镜像本身", "数据卷", "配置文件"], "a": "A"},
        {"q": "Dockerfile 用于？", "opts": ["构建镜像", "运行容器", "管理网络", "存储数据"], "a": "A"},
        {"q": "FROM 指令用于？", "opts": ["指定基础镜像", "暴露端口", "复制文件", "运行命令"], "a": "A"},
        {"q": "RUN 指令用于？", "opts": ["执行命令", "暴露端口", "复制文件", "指定基础镜像"], "a": "A"},
        {"q": "CMD 指令用于？", "opts": ["容器启动时执行", "构建时执行", "暴露端口", "复制文件"], "a": "A"},
        {"q": "ENTRYPOINT 和 CMD 的区别是？", "opts": ["ENTRYPOINT 更固定", "CMD 更固定", "没有区别", "ENTRYPOINT 是命令"], "a": "A"},
        {"q": "COPY 和 ADD 的区别是？", "opts": ["ADD 支持 URL 和解压", "COPY 支持 URL", "没有区别", "ADD 更快"], "a": "A"},
        {"q": "EXPOSE 用于？", "opts": ["声明端口", "映射端口", "开放防火墙", "绑定地址"], "a": "A"},
        {"q": "VOLUME 用于？", "opts": ["创建挂载点", "复制文件", "暴露端口", "运行命令"], "a": "A"},
        {"q": "WORKDIR 用于？", "opts": ["设置工作目录", "复制文件", "暴露端口", "运行命令"], "a": "A"},
        {"q": "ENV 用于？", "opts": ["设置环境变量", "暴露端口", "复制文件", "运行命令"], "a": "A"},
        {"q": "ARG 和 ENV 的区别是？", "opts": ["ARG 只在构建时可用", "ENV 只在构建时可用", "没有区别", "ARG 是环境变量"], "a": "A"},
        {"q": "docker build -t 用于？", "opts": ["打标签", "指定 Dockerfile", "指定构建上下文", "指定网络"], "a": "A"},
        {"q": "docker run -d 表示？", "opts": ["后台运行", "交互模式", "删除容器", "指定端口"], "a": "A"},
        {"q": "docker run -p 8080:80 表示？", "opts": ["主机 8080 映射容器 80", "容器 8080 映射主机 80", "只开放 8080", "只开放 80"], "a": "A"},
        {"q": "docker run -v 用于？", "opts": ["挂载卷", "暴露端口", "设置环境变量", "指定网络"], "a": "A"},
        {"q": "docker run --rm 表示？", "opts": ["停止后自动删除", "后台运行", "交互模式", "只读模式"], "a": "A"},
        {"q": "docker ps -a 显示？", "opts": ["所有容器", "运行中的容器", "停止的容器", "镜像列表"], "a": "A"},
        {"q": "docker exec 用于？", "opts": ["在运行容器中执行命令", "启动新容器", "构建镜像", "查看日志"], "a": "A"},
    ],
    "Docker 网络": [
        {"q": "bridge 网络是？", "opts": ["默认桥接网络", "主机网络", "无网络", "覆盖网络"], "a": "A"},
        {"q": "host 网络模式的特点是？", "opts": ["共享主机网络", "隔离网络", "无网络", "自定义网络"], "a": "A"},
        {"q": "none 网络模式表示？", "opts": ["无网络", "默认网络", "主机网络", "桥接网络"], "a": "A"},
        {"q": "docker network create 用于？", "opts": ["创建自定义网络", "删除网络", "连接容器", "断开容器"], "a": "A"},
        {"q": "容器间通过什么通信？", "opts": ["容器名", "IP 地址", "MAC 地址", "端口号"], "a": "A"},
        {"q": "docker-compose 中 links 用于？", "opts": ["连接服务", "暴露端口", "挂载卷", "设置环境变量"], "a": "A"},
    ],
    "Docker 存储": [
        {"q": "bind mount 是？", "opts": ["挂载主机目录", "Docker 管理卷", "临时文件", "内存文件"], "a": "A"},
        {"q": "volume 是？", "opts": ["Docker 管理卷", "挂载主机目录", "临时文件", "内存文件"], "a": "A"},
        {"q": "tmpfs 是？", "opts": ["内存文件系统", "持久化存储", "网络存储", "对象存储"], "a": "A"},
        {"q": "docker volume create 用于？", "opts": ["创建卷", "删除卷", "列出卷", "查看卷"], "a": "A"},
        {"q": "数据卷容器用于？", "opts": ["共享数据", "隔离数据", "压缩数据", "加密数据"], "a": "A"},
    ],
    "Docker Compose": [
        {"q": "docker-compose.yml 用于？", "opts": ["定义多容器应用", "构建镜像", "管理网络", "存储数据"], "a": "A"},
        {"q": "services 在 docker-compose 中表示？", "opts": ["服务定义", "网络配置", "卷配置", "环境变量"], "a": "A"},
        {"q": "docker-compose up -d 表示？", "opts": ["后台启动", "前台启动", "停止服务", "删除服务"], "a": "A"},
        {"q": "docker-compose down 表示？", "opts": ["停止并删除", "只停止", "只删除", "重启"], "a": "A"},
        {"q": "depends_on 用于？", "opts": ["控制启动顺序", "网络连接", "卷挂载", "端口映射"], "a": "A"},
        {"q": "docker-compose scale 用于？", "opts": ["扩展服务实例数", "缩小服务", "删除服务", "更新服务"], "a": "A"},
    ],
    "Kubernetes 基础": [
        {"q": "Pod 是 K8s 的？", "opts": ["最小调度单元", "控制器", "服务", "存储"], "a": "A"},
        {"q": "Deployment 用于？", "opts": ["管理 Pod 副本", "暴露服务", "存储数据", "配置网络"], "a": "A"},
        {"q": "Service 用于？", "opts": ["暴露 Pod 访问", "管理副本", "存储数据", "配置资源"], "a": "A"},
        {"q": "ConfigMap 用于？", "opts": ["配置管理", "密钥管理", "存储管理", "网络管理"], "a": "A"},
        {"q": "Secret 用于？", "opts": ["敏感数据管理", "普通配置", "存储管理", "网络管理"], "a": "A"},
        {"q": "Namespace 用于？", "opts": ["资源隔离", "负载均衡", "存储管理", "网络管理"], "a": "A"},
        {"q": "kubectl apply 用于？", "opts": ["应用配置", "删除资源", "查看日志", "进入容器"], "a": "A"},
        {"q": "kubectl get pods 显示？", "opts": ["Pod 列表", "服务列表", "节点列表", "部署列表"], "a": "A"},
        {"q": "kubectl describe 用于？", "opts": ["查看详细信息", "删除资源", "编辑资源", "创建资源"], "a": "A"},
        {"q": "kubectl logs 用于？", "opts": ["查看日志", "进入容器", "删除 Pod", "重启 Pod"], "a": "A"},
        {"q": "kubectl exec 用于？", "opts": ["在容器中执行命令", "查看日志", "删除 Pod", "重启 Pod"], "a": "A"},
        {"q": "kubectl port-forward 用于？", "opts": ["端口转发", "暴露服务", "创建服务", "删除服务"], "a": "A"},
    ],
    "Kubernetes 进阶": [
        {"q": "StatefulSet 用于？", "opts": ["有状态应用", "无状态应用", "批处理", "定时任务"], "a": "A"},
        {"q": "DaemonSet 用于？", "opts": ["每个节点运行一个 Pod", "多副本", "批处理", "定时任务"], "a": "A"},
        {"q": "Job 用于？", "opts": ["批处理任务", "长期运行服务", "定时任务", "守护进程"], "a": "A"},
        {"q": "CronJob 用于？", "opts": ["定时任务", "批处理", "长期运行", "守护进程"], "a": "A"},
        {"q": "Ingress 用于？", "opts": ["HTTP/HTTPS 路由", "服务发现", "负载均衡", "存储"], "a": "A"},
        {"q": "PersistentVolume 用于？", "opts": ["持久化存储", "临时存储", "内存存储", "网络存储"], "a": "A"},
        {"q": "PersistentVolumeClaim 用于？", "opts": ["申请存储", "提供存储", "管理网络", "管理配置"], "a": "A"},
        {"q": "RBAC 用于？", "opts": ["权限控制", "网络控制", "存储控制", "资源控制"], "a": "A"},
        {"q": "Helm 是？", "opts": ["K8s 包管理器", "容器运行时", "镜像仓库", "监控工具"], "a": "A"},
        {"q": "Chart 在 Helm 中是？", "opts": ["应用包", "配置文件", "镜像", "密钥"], "a": "A"},
    ],
    "容器安全": [
        {"q": "容器以 root 运行的问题是？", "opts": ["安全风险高", "性能差", "无法运行", "无法联网"], "a": "A"},
        {"q": "Docker 的 --cap-drop 用于？", "opts": ["丢弃能力", "添加能力", "查看能力", "修改能力"], "a": "A"},
        {"q": "read-only root 文件系统用于？", "opts": ["防止写入攻击", "提高性能", "减少存储", "方便调试"], "a": "A"},
        {"q": "镜像扫描用于？", "opts": ["发现漏洞", "提高性能", "减少大小", "加速构建"], "a": "A"},
        {"q": "distroless 镜像的特点是？", "opts": ["最小化攻击面", "包含所有工具", "易于调试", "体积大"], "a": "A"},
    ],
}


def generate_container_questions(target_count=200):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["Docker 基础", "Docker 网络", "Docker 存储"]
    medium_cats = ["Docker Compose", "Kubernetes 基础", "容器安全"]
    hard_cats = ["Kubernetes 进阶", "Kubernetes 基础", "容器安全"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in CONTAINER_TEMPLATES and CONTAINER_TEMPLATES[cat]:
            template = random.choice(CONTAINER_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"容器-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["container"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in CONTAINER_TEMPLATES and CONTAINER_TEMPLATES[cat]:
            template = random.choice(CONTAINER_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"容器-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["container"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in CONTAINER_TEMPLATES and CONTAINER_TEMPLATES[cat]:
            template = random.choice(CONTAINER_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"容器-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["container"]
            })
            qid += 1

    return questions


class ContainerEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_container_questions(200)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "container")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_container_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = ContainerEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 容器测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_container_questions(200)
        print(f"生成了 {len(questions)} 道容器题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "container_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_container_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
