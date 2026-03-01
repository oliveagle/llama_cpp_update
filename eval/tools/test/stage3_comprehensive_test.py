#!/usr/bin/env python3
"""
第三层综合能力测试 - 单模型深度评估
测试维度：数学推理、代码生成、逻辑推理、常识问答、文本理解、Linux Shell
每个模型生成独立报告
"""

import requests
import json
import time
import os
from datetime import datetime

BASE_URL = "http://localhost:8401/v1/completions"
TIMEOUT = 180

# 综合能力测试用例 (50 cases)
TEST_CASES = {
    "math_reasoning": [
        {"name": "数学-简单算术", "prompt": "计算: 125 + 367 = ?", "expected": ["492"], "weight": 1},
        {"name": "数学-分数计算", "prompt": "1/2 + 1/3 = ?", "expected": ["5/6", "0.833"], "weight": 2},
        {"name": "数学-百分比", "prompt": "200的15%是多少?", "expected": ["30"], "weight": 1},
        {"name": "数学-代数", "prompt": "解方程: 2x + 5 = 15, x = ?", "expected": ["5"], "weight": 2},
        {"name": "数学-应用题", "prompt": "一辆车以60km/h行驶2.5小时，行驶了多少公里?", "expected": ["150"], "weight": 2},
        {"name": "数学-比例", "prompt": "如果3个苹果6元，5个苹果多少钱?", "expected": ["10"], "weight": 2},
        {"name": "数学-面积", "prompt": "边长为5的正方形面积是多少?", "expected": ["25"], "weight": 1},
        {"name": "数学-速度", "prompt": "小明跑了400米用时80秒，平均速度是多少米/秒?", "expected": ["5"], "weight": 2},
        {"name": "数学-利润", "prompt": "进货价80元，售价100元，利润率是多少?", "expected": ["25%", "0.25"], "weight": 2},
        {"name": "数学-年龄", "prompt": "父亲40岁，儿子12岁，几年后父亲年龄是儿子的2倍?", "expected": ["16"], "weight": 3},
    ],
    "code_generation": [
        {"name": "代码-HelloWorld", "prompt": "写一个Python程序输出'Hello, World!'", "expected": ["print", "Hello"], "weight": 1},
        {"name": "代码-两数之和", "prompt": "写一个Python函数add(a, b)返回两数之和", "expected": ["def", "return", "a+b"], "weight": 1},
        {"name": "代码-列表反转", "prompt": "写一个Python函数反转列表，不使用reverse()", "expected": ["def", "return", "[::-1]"], "weight": 2},
        {"name": "代码-判断素数", "prompt": "写一个Python函数判断一个数是否为素数", "expected": ["def", "for", "range", "return"], "weight": 2},
        {"name": "代码-文件读取", "prompt": "写Python代码读取test.txt文件内容并打印", "expected": ["open", "read", "print"], "weight": 1},
        {"name": "代码-字典操作", "prompt": "创建一个字典存储学生姓名和分数，然后查询", "expected": ["{", "}", "dict"], "weight": 1},
        {"name": "代码-异常处理", "prompt": "写Python代码处理除以零异常", "expected": ["try", "except", "ZeroDivisionError"], "weight": 2},
        {"name": "代码-列表推导", "prompt": "用列表推导式生成1到10的平方列表", "expected": ["[", "]", "for", "in", "range"], "weight": 2},
        {"name": "代码-字符串处理", "prompt": "写一个Python函数统计字符串中单词数量", "expected": ["def", "split", "len"], "weight": 2},
        {"name": "代码-递归", "prompt": "用递归写阶乘函数", "expected": ["def", "if", "return", "n*"], "weight": 3},
    ],
    "logic_reasoning": [
        {"name": "逻辑-真假判断", "prompt": "所有的鸟都会飞。企鹅是鸟。企鹅会飞吗?", "expected": ["不会", "不能", "错误"], "weight": 2},
        {"name": "逻辑-顺序推理", "prompt": "A在B前面，B在C前面，谁在中间?", "expected": ["B"], "weight": 1},
        {"name": "逻辑-类比", "prompt": "医生对医院，就像教师对什么?", "expected": ["学校", "教室"], "weight": 1},
        {"name": "逻辑-排除法", "prompt": "有三个人：甲说真话，乙说假话，丙有时说真话。谁最可靠?", "expected": ["甲"], "weight": 2},
        {"name": "逻辑-必要条件", "prompt": "下雨是地面湿的必要条件吗?为什么?", "expected": ["不是", "洒水", "其他"], "weight": 2},
        {"name": "逻辑-归纳", "prompt": "观察到5只天鹅都是白色的，能否得出所有天鹅都是白色的结论?", "expected": ["不能", "样本", "不完全"], "weight": 3},
        {"name": "逻辑-演绎", "prompt": "所有人都会死，苏格拉底是人，所以?", "expected": ["苏格拉底会死"], "weight": 2},
        {"name": "逻辑-矛盾", "prompt": "一个人说他正在说谎，这句话可信吗?", "expected": ["悖论", "矛盾", "不可信"], "weight": 3},
        {"name": "逻辑-假设", "prompt": "如果地球自转反向，太阳会从西边升起吗?", "expected": ["会", "是的"], "weight": 2},
        {"name": "逻辑-最优解", "prompt": "过河问题：一人带狼羊菜过河，船只能载人和一件东西，狼吃羊、羊吃菜，如何安全过河?", "expected": ["先带羊", "羊先"], "weight": 3},
    ],
    "knowledge_qa": [
        {"name": "常识-地理", "prompt": "中国的首都是哪里?", "expected": ["北京"], "weight": 1},
        {"name": "常识-历史", "prompt": "中国四大发明是什么?", "expected": ["造纸", "印刷", "火药", "指南针"], "weight": 2},
        {"name": "常识-科学", "prompt": "光合作用的主要产物是什么?", "expected": ["氧气", "葡萄糖", "淀粉"], "weight": 2},
        {"name": "常识-生物", "prompt": "人体最大的器官是什么?", "expected": ["皮肤"], "weight": 1},
        {"name": "常识-物理", "prompt": "光在真空中的速度是多少?", "expected": ["3亿", "300000000", "3×10^8"], "weight": 2},
        {"name": "常识-化学", "prompt": "水的化学式是什么?", "expected": ["H2O", "H₂O"], "weight": 1},
        {"name": "常识-天文", "prompt": "太阳系中最大的行星是哪个?", "expected": ["木星"], "weight": 1},
        {"name": "常识-计算机", "prompt": "HTTP和HTTPS的区别是什么?", "expected": ["安全", "加密", "SSL", "TLS"], "weight": 2},
        {"name": "常识-经济", "prompt": "通货膨胀是什么意思?", "expected": ["物价", "上涨", "货币", "贬值"], "weight": 2},
        {"name": "常识-法律", "prompt": "宪法是一国的什么法?", "expected": ["根本", "最高", "基本"], "weight": 1},
    ],
    "text_comprehension": [
        {"name": "文本-主旨提取", "prompt": "阅读：'科技发展改变了人们的生活方式，从通信到交通都发生了巨大变化。'主旨是?", "expected": ["科技", "改变", "生活"], "weight": 1},
        {"name": "文本-情感分析", "prompt": "分析：'这部电影太精彩了，我强烈推荐!'的情感倾向?", "expected": ["正面", "积极", "好评"], "weight": 1},
        {"name": "文本-关键词", "prompt": "提取关键词：'人工智能在医疗诊断领域展现出巨大潜力'", "expected": ["人工智能", "医疗", "诊断"], "weight": 1},
        {"name": "文本-总结", "prompt": "用一句话总结：'春天来了，花儿开了，鸟儿叫了，人们都出去踏青了。'", "expected": ["春天", "来了"], "weight": 1},
        {"name": "文本-推理", "prompt": "'他很勤奋，每天工作到很晚，终于成功了。'说明什么?", "expected": ["勤奋", "努力", "成功"], "weight": 2},
        {"name": "文本-对比", "prompt": "比较：'传统教育注重记忆，现代教育注重创新。'两者区别?", "expected": ["记忆", "创新", "传统", "现代"], "weight": 2},
        {"name": "文本-因果关系", "prompt": "'因为下雨，所以运动会取消了。'原因和结果?", "expected": ["下雨", "取消"], "weight": 1},
        {"name": "文本-观点识别", "prompt": "'有人认为AI会取代人类工作，也有人认为AI会创造新工作。'观点?", "expected": ["取代", "创造"], "weight": 2},
        {"name": "文本-细节理解", "prompt": "'小明早上8点出门，坐公交车30分钟到达学校。'小明几点到学校?", "expected": ["8点30", "8:30"], "weight": 1},
        {"name": "文本-词义理解", "prompt": "'他工作一丝不苟'，'一丝不苟'是什么意思?", "expected": ["认真", "仔细", "不马虎"], "weight": 2},
    ],
}

# Linux Shell 测试用例 (15 cases)
LINUX_SHELL_TESTS = [
    {"name": "Shell-查看目录", "prompt": "如何查看当前目录下的所有文件?", "expected": ["ls", "dir", "list"], "weight": 1},
    {"name": "Shell-切换目录", "prompt": "如何切换到上一级目录?", "expected": ["cd ..", "cd.."], "weight": 1},
    {"name": "Shell-查看磁盘", "prompt": "如何查看磁盘空间使用情况?", "expected": ["df", "du", "disk"], "weight": 2},
    {"name": "Shell-查看内存", "prompt": "如何查看内存使用情况?", "expected": ["free", "top", "htop"], "weight": 2},
    {"name": "Shell-查看进程", "prompt": "如何查看当前运行的进程?", "expected": ["ps", "top", "htop"], "weight": 2},
    {"name": "Shell-查找文件", "prompt": "如何在当前目录下查找名为test.txt的文件?", "expected": ["find", "locate"], "weight": 2},
    {"name": "Shell-查看文件内容", "prompt": "如何查看文件内容但不编辑?", "expected": ["cat", "less", "more", "head", "tail"], "weight": 1},
    {"name": "Shell-创建目录", "prompt": "如何创建一个名为backup的新目录?", "expected": ["mkdir", "md"], "weight": 1},
    {"name": "Shell-复制文件", "prompt": "如何将file1.txt复制为file2.txt?", "expected": ["cp", "copy"], "weight": 1},
    {"name": "Shell-移动文件", "prompt": "如何将文件移动到另一个目录?", "expected": ["mv", "move"], "weight": 1},
    {"name": "Shell-删除文件", "prompt": "如何删除一个文件?", "expected": ["rm", "del", "delete"], "weight": 1},
    {"name": "Shell-压缩文件", "prompt": "如何将多个文件打包成tar.gz?", "expected": ["tar", "gzip", "zip"], "weight": 2},
    {"name": "Shell-查看网络", "prompt": "如何查看网络接口信息?", "expected": ["ifconfig", "ip", "netstat"], "weight": 2},
    {"name": "Shell-ping命令", "prompt": "如何测试与www.google.com的网络连通性?", "expected": ["ping", "curl", "wget"], "weight": 1},
    {"name": "Shell-权限设置", "prompt": "如何将文件设置为可执行权限?", "expected": ["chmod", "+x"], "weight": 2},
]

def call_model(prompt, max_tokens=512):
    """调用模型API"""
    payload = {
        "model": "test",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
    }
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        data = resp.json()
        choice = data["choices"][0]
        # 检查 content 和 reasoning_content
        content = choice.get("text", "") or choice.get("content", "")
        reasoning = choice.get("reasoning_content", "")
        # 合并内容（优先使用 content，如果为空则使用 reasoning）
        full_content = content if content else reasoning
        return {"success": True, "content": full_content}
    except Exception as e:
        return {"success": False, "error": str(e)}

def extract_answer(content):
    """
    从模型的"过度思考"输出中提取实际答案
    处理 GLM-4.7、MiniCPM 等模型的结构化输出
    """
    import re

    if not content:
        return ""

    # 1. 尝试提取 "最终答案：" 或 "答案：" 后的内容
    answer_patterns = [
        r'最终答案[：:]\s*([^\n]+)',
        r'答案[：:]\s*([^\n]+)',
        r'Answer[：:]\s*([^\n]+)',
        r'答案是[：:]?\s*([^\n]+)',
        r'所以答案是[：:]?\s*([^\n]+)',
    ]
    for pattern in answer_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # 2. 去除常见的思考过程标记
    # 去除 "1. **分析用户请求：**" 这类结构化标记
    content_clean = re.sub(r'^\s*\d+\.\s*\*\*[^*]+\*\*', '', content, flags=re.MULTILINE)
    # 去除 "- 分析："、"- 思考：" 等列表标记
    content_clean = re.sub(r'^\s*[-•]\s*\w+[：:]', '', content_clean, flags=re.MULTILINE)
    # 去除 "用户问的是..." 这类思考前缀
    content_clean = re.sub(r'^用户问的是[^。]+。', '', content_clean)
    # 去除 "我需要回忆..." 这类思考过程
    content_clean = re.sub(r'我需要回忆[^。]+。', '', content_clean)
    content_clean = re.sub(r'让我思考一下[^。]*。', '', content_clean)

    # 3. 提取最后一段非空文本（通常是答案）
    lines = [line.strip() for line in content_clean.split('\n') if line.strip()]
    if lines:
        # 过滤掉纯思考标记的行
        filtered_lines = []
        for line in lines:
            # 跳过纯元信息行
            if re.match(r'^\d+\.\s*\*+', line):
                continue
            if re.match(r'^\s*[-•]\s*\*+', line):
                continue
            if line.startswith('**') and line.endswith('：**'):
                continue
            # 保留有意义的行
            if len(line) > 2:
                filtered_lines.append(line)

        if filtered_lines:
            # 返回最后一段作为答案
            return filtered_lines[-1]

    return content.strip()


def check_response(content, expected_keywords):
    """检查响应是否包含预期关键词（使用提取后的答案）"""
    # 先提取实际答案
    extracted_answer = extract_answer(content)

    # 使用提取后的答案进行关键词匹配
    content_lower = extracted_answer.lower()
    matched = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
    return matched >= max(1, len(expected_keywords) // 2)

def run_test_case(test_case):
    """运行单个测试用例"""
    result = call_model(test_case["prompt"], max_tokens=256)
    if not result["success"]:
        return {"passed": False, "error": result["error"], "content": "", "extracted": "", "weight": test_case["weight"]}

    # 提取实际答案
    extracted_answer = extract_answer(result["content"])
    passed = check_response(result["content"], test_case["expected"])
    return {
        "passed": passed,
        "content": result["content"][:200],
        "extracted": extracted_answer[:100],
        "weight": test_case["weight"]
    }

def test_category(category_name, test_cases):
    """测试一个类别"""
    print(f"\n{'='*60}")
    print(f"📚 {category_name}")
    print(f"{'='*60}")

    results = []
    total_weight = 0
    passed_weight = 0

    for test in test_cases:
        print(f"  📝 {test['name']}...", end=" ", flush=True)
        result = run_test_case(test)
        results.append({"name": test["name"], **result})

        total_weight += test["weight"]
        if result["passed"]:
            passed_weight += test["weight"]

        status = "✅" if result["passed"] else "❌"
        print(f"{status}")
        time.sleep(0.2)

    score = (passed_weight / total_weight * 100) if total_weight > 0 else 0
    return results, score, passed_weight, total_weight

def generate_report(model_name, model_config, results_summary, output_dir):
    """生成详细报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON 结果
    json_file = os.path.join(output_dir, f"{model_name}_{date_str}_stage3.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)

    # Markdown 报告
    md_file = os.path.join(output_dir, f"{model_name}_{date_str}_stage3.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# 第三层综合能力测试报告 - {model_name}\n\n")
        f.write(f"> **测试时间**: {timestamp}\n")
        f.write(f"> **模型配置**: {model_config}\n")
        f.write(f"> **测试端点**: {BASE_URL}\n")
        f.write(f"> **Agent**: V100-CUDA\n\n")
        f.write("---\n\n")

        # 总览
        f.write("## 📊 测试概览\n\n")
        total_cases = sum(len(cases) for cases in TEST_CASES.values()) + len(LINUX_SHELL_TESTS)
        f.write(f"**总测试用例**: {total_cases}\n")
        f.write(f"**测试维度**: 6个 (数学推理、代码生成、逻辑推理、常识问答、文本理解、Linux Shell)\n\n")

        # 各维度得分
        f.write("| 维度 | 得分 | 权重 | 状态 |\n")
        f.write("|------|------|------|------|\n")

        overall_score = 0
        total_weights = 0

        for category, data in results_summary["categories"].items():
            score = data["score"]
            weight = data["weight"]
            total_weights += weight
            overall_score += score * weight
            status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
            f.write(f"| {category} | {score:.1f}% | {weight} | {status} |\n")

        final_score = overall_score / total_weights if total_weights > 0 else 0
        final_status = "✅ 优秀" if final_score >= 80 else "✅ 良好" if final_score >= 70 else "⚠️ 及格" if final_score >= 60 else "❌ 不及格"
        f.write(f"| **综合** | **{final_score:.1f}%** | - | {final_status} |\n\n")

        # 详细结果
        f.write("---\n\n")
        f.write("## 📋 详细测试结果\n\n")

        for category, data in results_summary["categories"].items():
            f.write(f"### {category} (得分: {data['score']:.1f}%)\n\n")
            f.write("| 测试项 | 结果 | 原始回答 | 提取答案 |\n")
            f.write("|--------|------|----------|----------|\n")
            for case in data["cases"]:
                status = "✅" if case["passed"] else "❌"
                content = case["content"][:40].replace("|", "\\|").replace("\n", " ")
                extracted = case.get("extracted", "")[:40].replace("|", "\\|").replace("\n", " ")
                f.write(f"| {case['name']} | {status} | {content}... | {extracted}... |\n")
            f.write("\n")

        # 结论
        f.write("---\n\n")
        f.write("## 💡 结论与建议\n\n")

        if final_score >= 80:
            f.write("**综合评价**: 模型在综合能力测试中表现优秀，各维度均衡发展。\n\n")
        elif final_score >= 70:
            f.write("**综合评价**: 模型综合能力良好，主要维度表现稳定。\n\n")
        elif final_score >= 60:
            f.write("**综合评价**: 模型综合能力及格，部分维度需要改进。\n\n")
        else:
            f.write("**综合评价**: 模型综合能力较弱，建议针对薄弱维度进行优化。\n\n")

        # 强项和弱项
        sorted_categories = sorted(results_summary["categories"].items(), key=lambda x: x[1]["score"], reverse=True)
        f.write(f"**最强维度**: {sorted_categories[0][0]} ({sorted_categories[0][1]['score']:.1f}%)\n")
        f.write(f"**最弱维度**: {sorted_categories[-1][0]} ({sorted_categories[-1][1]['score']:.1f}%)\n\n")

        f.write("---\n\n")
        f.write(f"*报告生成时间: {timestamp}*\n")

    return md_file, json_file

def run_stage3_test(model_name, model_config, output_dir="eval_results/stage3"):
    """运行第三层测试"""
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print(f"🧪 第三层综合能力测试 - {model_name}")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试端点: {BASE_URL}")
    print("=" * 80)

    results_summary = {
        "model": model_name,
        "config": model_config,
        "timestamp": datetime.now().isoformat(),
        "categories": {}
    }

    category_names = {
        "math_reasoning": "数学推理",
        "code_generation": "代码生成",
        "logic_reasoning": "逻辑推理",
        "knowledge_qa": "常识问答",
        "text_comprehension": "文本理解"
    }

    # 综合能力测试
    for category, test_cases in TEST_CASES.items():
        cases, score, passed_w, total_w = test_category(category_names[category], test_cases)
        results_summary["categories"][category_names[category]] = {
            "cases": cases,
            "score": score,
            "passed_weight": passed_w,
            "total_weight": total_w,
            "weight": 1
        }

    # Linux Shell 测试
    cases, score, passed_w, total_w = test_category("Linux Shell", LINUX_SHELL_TESTS)
    results_summary["categories"]["Linux Shell"] = {
        "cases": cases,
        "score": score,
        "passed_weight": passed_w,
        "total_weight": total_w,
        "weight": 1
    }

    # 生成报告
    md_file, json_file = generate_report(model_name, model_config, results_summary, output_dir)

    # 打印汇总
    print("\n" + "=" * 80)
    print("📊 测试汇总")
    print("=" * 80)

    for category, data in results_summary["categories"].items():
        status = "✅" if data["score"] >= 70 else "⚠️" if data["score"] >= 50 else "❌"
        print(f"  {status} {category}: {data['score']:.1f}%")

    # 计算综合得分
    overall = sum(d["score"] for d in results_summary["categories"].values()) / len(results_summary["categories"])
    final_status = "✅ 优秀" if overall >= 80 else "✅ 良好" if overall >= 70 else "⚠️ 及格" if overall >= 60 else "❌ 不及格"
    print(f"\n  📈 综合得分: {overall:.1f}% - {final_status}")

    print(f"\n  📄 Markdown报告: {md_file}")
    print(f"  💾 JSON数据: {json_file}")

    return results_summary, overall

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", required=True, help="模型显示名称")
    parser.add_argument("--model-config", default="", help="模型配置描述")
    parser.add_argument("--output-dir", default="eval_results/stage3", help="输出目录")
    args = parser.parse_args()

    run_stage3_test(args.model_name, args.model_config, args.output_dir)
