#!/usr/bin/env python3
"""
Stage 4 运维能力测试 - 网络与安全 (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

NETWORK_SECURITY_TEMPLATES = {
    "TCP/IP": [
        {"q": "TCP 和 UDP 的主要区别是？", "opts": ["TCP 可靠 UDP 不可靠", "TCP 快 UDP 慢", "TCP 无连接 UDP 有连接", "没有区别"], "a": "A"},
        {"q": "TCP 三次握手用于？", "opts": ["建立连接", "关闭连接", "数据传输", "错误恢复"], "a": "A"},
        {"q": "TCP 四次挥手用于？", "opts": ["关闭连接", "建立连接", "数据传输", "错误恢复"], "a": "A"},
        {"q": "IP 地址的作用是？", "opts": ["网络层寻址", "传输层寻址", "应用层寻址", "物理层寻址"], "a": "A"},
        {"q": "子网掩码的作用是？", "opts": ["划分网络和主机", "加密数据", "压缩数据", "路由选择"], "a": "A"},
        {"q": "默认网关的作用是？", "opts": ["连接不同网络", "DNS 解析", "DHCP 分配", "NAT 转换"], "a": "A"},
        {"q": "MTU 是指？", "opts": ["最大传输单元", "最小传输单元", "传输速率", "传输延迟"], "a": "A"},
        {"q": "OSI 模型有？", "opts": ["7 层", "4 层", "5 层", "6 层"], "a": "A"},
        {"q": "TCP/IP 模型有？", "opts": ["4 层", "7 层", "5 层", "6 层"], "a": "A"},
        {"q": "HTTP 工作在？", "opts": ["应用层", "传输层", "网络层", "数据链路层"], "a": "A"},
        {"q": "TCP 工作在？", "opts": ["传输层", "应用层", "网络层", "数据链路层"], "a": "A"},
        {"q": "IP 工作在？", "opts": ["网络层", "应用层", "传输层", "数据链路层"], "a": "A"},
    ],
    "HTTP/HTTPS": [
        {"q": "HTTP 默认端口是？", "opts": ["80", "443", "8080", "22"], "a": "A"},
        {"q": "HTTPS 默认端口是？", "opts": ["443", "80", "8080", "22"], "a": "A"},
        {"q": "HTTP 状态码 200 表示？", "opts": ["成功", "重定向", "客户端错误", "服务器错误"], "a": "A"},
        {"q": "HTTP 状态码 404 表示？", "opts": ["未找到", "成功", "服务器错误", "重定向"], "a": "A"},
        {"q": "HTTP 状态码 500 表示？", "opts": ["服务器错误", "成功", "客户端错误", "重定向"], "a": "A"},
        {"q": "HTTP 状态码 301 表示？", "opts": ["永久重定向", "临时重定向", "成功", "未找到"], "a": "A"},
        {"q": "GET 和 POST 的区别是？", "opts": ["GET 获取 POST 提交", "GET 安全 POST 不安全", "GET 快 POST 慢", "没有区别"], "a": "A"},
        {"q": "HTTPS 比 HTTP 多了？", "opts": ["SSL/TLS 加密", "压缩", "缓存", "代理"], "a": "A"},
        {"q": "TLS 握手用于？", "opts": ["协商加密参数", "建立 TCP 连接", "传输数据", "关闭连接"], "a": "A"},
        {"q": "HTTP/2 相比 HTTP/1.1 的优势是？", "opts": ["多路复用", "更简单", "无状态", "明文传输"], "a": "A"},
        {"q": "WebSocket 用于？", "opts": ["全双工通信", "单向通信", "文件传输", "邮件发送"], "a": "A"},
    ],
    "DNS": [
        {"q": "DNS 的作用是？", "opts": ["域名解析", "IP 分配", "路由选择", "负载均衡"], "a": "A"},
        {"q": "A 记录用于？", "opts": ["域名到 IPv4", "域名到 IPv6", "邮件服务器", "别名"], "a": "A"},
        {"q": "AAAA 记录用于？", "opts": ["域名到 IPv6", "域名到 IPv4", "邮件服务器", "别名"], "a": "A"},
        {"q": "CNAME 记录用于？", "opts": ["别名", "IP 地址", "邮件服务器", "名称服务器"], "a": "A"},
        {"q": "MX 记录用于？", "opts": ["邮件服务器", "IP 地址", "别名", "名称服务器"], "a": "A"},
        {"q": "NS 记录用于？", "opts": ["名称服务器", "IP 地址", "别名", "邮件服务器"], "a": "A"},
        {"q": "TTL 在 DNS 中表示？", "opts": ["缓存时间", "生存时间", "传输时间", "响应时间"], "a": "A"},
        {"q": "DNS 递归查询是？", "opts": ["DNS 服务器代替客户端查询", "客户端自己查询", "不查询", "随机查询"], "a": "A"},
    ],
    "防火墙": [
        {"q": "防火墙的主要作用是？", "opts": ["控制网络访问", "加速网络", "压缩数据", "加密数据"], "a": "A"},
        {"q": "iptables 是？", "opts": ["Linux 防火墙工具", "网络监控", "VPN 工具", "代理服务器"], "a": "A"},
        {"q": "firewalld 是？", "opts": ["动态防火墙", "静态防火墙", "网络监控", "VPN 工具"], "a": "A"},
        {"q": "ufw 是？", "opts": ["简化的防火墙", "复杂的防火墙", "网络监控", "VPN 工具"], "a": "A"},
        {"q": "ACCEPT 在防火墙中表示？", "opts": ["允许", "拒绝", "丢弃", "记录"], "a": "A"},
        {"q": "DROP 在防火墙中表示？", "opts": ["丢弃", "允许", "拒绝", "记录"], "a": "A"},
        {"q": "REJECT 在防火墙中表示？", "opts": ["拒绝并通知", "丢弃", "允许", "记录"], "a": "A"},
        {"q": "状态防火墙的特点是？", "opts": ["跟踪连接状态", "不跟踪状态", "只过滤 IP", "只过滤端口"], "a": "A"},
    ],
    "安全基础": [
        {"q": "对称加密的特点是？", "opts": ["加密解密用相同密钥", "不同密钥", "无需密钥", "公钥加密"], "a": "A"},
        {"q": "非对称加密的特点是？", "opts": ["公钥加密私钥解密", "相同密钥", "无需密钥", "私钥加密公钥解密"], "a": "A"},
        {"q": "哈希函数的特点是？", "opts": ["单向不可逆", "可逆", "加密", "解密"], "a": "A"},
        {"q": "数字签名用于？", "opts": ["验证身份和完整性", "加密数据", "压缩数据", "传输数据"], "a": "A"},
        {"q": "CA 的作用是？", "opts": ["签发证书", "加密数据", "解密数据", "传输数据"], "a": "A"},
        {"q": "SSL/TLS 证书用于？", "opts": ["身份验证和加密", "压缩数据", "加速传输", "负载均衡"], "a": "A"},
        {"q": "中间人攻击是指？", "opts": ["攻击者截获通信", "直接攻击服务器", "DDoS 攻击", "SQL 注入"], "a": "A"},
        {"q": "XSS 攻击是指？", "opts": ["跨站脚本攻击", "SQL 注入", "跨站请求伪造", "DDoS"], "a": "A"},
        {"q": "CSRF 攻击是指？", "opts": ["跨站请求伪造", "SQL 注入", "跨站脚本", "DDoS"], "a": "A"},
        {"q": "SQL 注入是指？", "opts": ["注入恶意 SQL", "跨站脚本", "请求伪造", "DDoS"], "a": "A"},
    ],
    "认证授权": [
        {"q": "认证是？", "opts": ["验证身份", "授权访问", "加密数据", "审计日志"], "a": "A"},
        {"q": "授权是？", "opts": ["授予权限", "验证身份", "加密数据", "审计日志"], "a": "A"},
        {"q": "OAuth 2.0 用于？", "opts": ["第三方授权", "单点登录", "数据加密", "用户认证"], "a": "A"},
        {"q": "JWT 包含？", "opts": ["Header Payload Signature", "只有 Payload", "只有 Header", "只有 Signature"], "a": "A"},
        {"q": "SSO 是？", "opts": ["单点登录", "多点登录", "无需登录", "强制登录"], "a": "A"},
        {"q": "MFA 是？", "opts": ["多因素认证", "单因素认证", "无认证", "强制认证"], "a": "A"},
        {"q": "RBAC 是？", "opts": ["基于角色的访问控制", "基于属性的访问控制", "强制访问控制", "自主访问控制"], "a": "A"},
        {"q": "ACL 是？", "opts": ["访问控制列表", "访问控制日志", "访问控制层", "访问控制语言"], "a": "A"},
    ],
}


def generate_network_security_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["TCP/IP", "HTTP/HTTPS", "DNS"]
    medium_cats = ["防火墙", "安全基础"]
    hard_cats = ["安全基础", "认证授权"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in NETWORK_SECURITY_TEMPLATES and NETWORK_SECURITY_TEMPLATES[cat]:
            template = random.choice(NETWORK_SECURITY_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"网络安全-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["network_security"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in NETWORK_SECURITY_TEMPLATES and NETWORK_SECURITY_TEMPLATES[cat]:
            template = random.choice(NETWORK_SECURITY_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"网络安全-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["network_security"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in NETWORK_SECURITY_TEMPLATES and NETWORK_SECURITY_TEMPLATES[cat]:
            template = random.choice(NETWORK_SECURITY_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"网络安全-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["network_security"]
            })
            qid += 1

    return questions


class NetworkSecurityEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_network_security_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "network_security")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_network_security_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = NetworkSecurityEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 网络安全测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_network_security_questions(150)
        print(f"生成了 {len(questions)} 道网络安全题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "network_security_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_network_security_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
