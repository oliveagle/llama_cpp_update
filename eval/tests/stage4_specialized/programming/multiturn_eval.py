#!/usr/bin/env python3
"""
Stage 4 增强版多轮对话能力测试
测试复杂问题的多轮推理能力

包含 50+ 道测试题，覆盖：
- 指代消解
- 信息追踪
- 上下文计算
- 意图变化
- 否定理解
- 时间顺序
- 角色扮演
- 多条件约束
- 推理链
- 隐含信息
- 任务恢复
- 情感理解
- 逻辑推断
"""

import random
import json
import time
import os
import sys
from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import Counter


# 多轮对话测试用例模板
MULTITURN_TEMPLATES = {
    "指代消解": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "张三和李四是好朋友。"},
                {"role": "assistant", "content": "明白了，他们是好朋友。"},
                {"role": "user", "content": "他昨天结婚了。"}
            ],
            "question": "谁结婚了？",
            "expected_keywords": ["张三"],
            "category": "指代消解"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "我今天买了苹果和香蕉。"},
                {"role": "assistant", "content": "好的，水果收到了吗？"},
                {"role": "user", "content": "苹果不甜，我想退货。"}
            ],
            "question": "用户想退什么？",
            "expected_keywords": ["苹果"],
            "category": "指代消解"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "我有两个朋友，小明在北京，小红在上海。"},
                {"role": "assistant", "content": "好的，了解了。"},
                {"role": "user", "content": "小明今天去找小红玩了。"},
                {"role": "assistant", "content": "他们见面了吗？"},
                {"role": "user", "content": "对，他们一起去了长城。"}
            ],
            "question": "谁去了长城？",
            "expected_keywords": ["小明", "小红"],
            "category": "指代消解"
        },
    ],
    "信息追踪": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "我要订一张明天北京到上海的机票。"},
                {"role": "assistant", "content": "好的，已记录您的需求。"},
                {"role": "user", "content": "改成后天的吧。"}
            ],
            "question": "用户最终订的是哪天的机票？",
            "expected_keywords": ["后天"],
            "category": "信息追踪"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "我的手机号码是13812345678。"},
                {"role": "assistant", "content": "好的，已记录。"},
                {"role": "user", "content": "不对，我换号了，现在是13987654321。"}
            ],
            "question": "用户的手机号是多少？",
            "expected_keywords": ["139", "87654321"],
            "category": "信息追踪"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "帮我查下北京今天的天气。"},
                {"role": "assistant", "content": "北京今天晴，25度。"},
                {"role": "user", "content": "那上海呢？"},
                {"role": "assistant", "content": "上海多云，28度。"},
                {"role": "user", "content": "帮我订明天去上海的机票。"}
            ],
            "question": "用户要订哪里的机票？",
            "expected_keywords": ["上海"],
            "category": "信息追踪"
        },
    ],
    "上下文计算": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "我有100元钱。"},
                {"role": "assistant", "content": "好的，您有100元。"},
                {"role": "user", "content": "花了30元买了本书。"}
            ],
            "question": "现在还剩多少钱？",
            "expected_keywords": ["70"],
            "category": "上下文计算"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "我每天跑步5公里。"},
                {"role": "assistant", "content": "很好的运动习惯。"},
                {"role": "user", "content": "这周我跑了4天。"},
                {"role": "assistant", "content": "4天跑了20公里。"},
                {"role": "user", "content": "下周每天跑6公里，跑5天。"}
            ],
            "question": "下周总共跑多少公里？",
            "expected_keywords": ["30"],
            "category": "上下文计算"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "一个公司有100名员工。"},
                {"role": "assistant", "content": "好的，100人。"},
                {"role": "user", "content": "其中60%是男性。"},
                {"role": "assistant", "content": "男性60人，女性40人。"},
                {"role": "user", "content": "男性中有一半是工程师。"},
                {"role": "assistant", "content": "男性工程师30人。"},
                {"role": "user", "content": "女性中有20%是工程师。"}
            ],
            "question": "公司共有多少工程师？",
            "expected_keywords": ["38", "30", "8"],
            "category": "上下文计算"
        },
    ],
    "意图变化": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "我想吃意大利面。"},
                {"role": "assistant", "content": "好的，意大利面是不错的选择。"},
                {"role": "user", "content": "算了，还是吃寿司吧。"}
            ],
            "question": "用户最终想吃什么？",
            "expected_keywords": ["寿司"],
            "category": "意图变化"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "帮我买张去北京的火车票。"},
                {"role": "assistant", "content": "好的，几号的？"},
                {"role": "user", "content": "算了，改成飞机吧。"},
                {"role": "assistant", "content": "好的，飞机。"},
                {"role": "user", "content": "等等，还是火车吧。"}
            ],
            "question": "用户最终选择什么出行方式？",
            "expected_keywords": ["火车"],
            "category": "意图变化"
        },
    ],
    "否定理解": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "我喜欢红色。"},
                {"role": "assistant", "content": "红色很热情。"},
                {"role": "user", "content": "但我不喜欢穿红色的衣服。"}
            ],
            "question": "用户喜欢穿红色衣服吗？",
            "expected_keywords": ["不", "不喜欢", "否定"],
            "category": "否定理解"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "这家餐厅服务很好。"},
                {"role": "assistant", "content": "是的，服务不错。"},
                {"role": "user", "content": "但是菜品味道一般。"}
            ],
            "question": "用户对餐厅的菜品满意吗？",
            "expected_keywords": ["不", "一般", "否定"],
            "category": "否定理解"
        },
    ],
    "时间顺序": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "早上8点我吃了早餐。"},
                {"role": "assistant", "content": "好的，早餐在8点。"},
                {"role": "user", "content": "中午12点吃了午饭。"}
            ],
            "question": "午饭是几点吃的？",
            "expected_keywords": ["12"],
            "category": "时间顺序"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "早餐在8点。"},
                {"role": "assistant", "content": "好的，8点早餐。"},
                {"role": "user", "content": "午饭比早餐晚4个小时。"},
                {"role": "assistant", "content": "好的，午饭12点。"},
                {"role": "user", "content": "晚饭比午饭晚6个小时。"}
            ],
            "question": "晚饭是几点？",
            "expected_keywords": ["18", "6点", "下午6点"],
            "category": "时间顺序"
        },
    ],
    "角色扮演": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "假设你是一位历史老师，请用老师的身份和我对话。"},
                {"role": "assistant", "content": "好的同学，我是你的历史老师。"},
                {"role": "user", "content": "老师，请介绍一下秦始皇。"}
            ],
            "question": "模型是否保持了历史老师的角色？",
            "check_role_keywords": ["同学", "我们", "学习", "历史"],
            "category": "角色扮演"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "你现在是一位医生，我是你的病人。"},
                {"role": "assistant", "content": "好的，请坐，您哪里不舒服？"},
                {"role": "user", "content": "我头痛。"}
            ],
            "question": "模型是否保持了医生的角色？",
            "check_role_keywords": ["医生", "病人", "检查", "症状"],
            "category": "角色扮演"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "你是一位Linux终端。我输入命令，你执行并返回结果。"},
                {"role": "assistant", "content": "$ 好的，我现在是Linux终端。"},
                {"role": "user", "content": "ls -la /home"},
                {"role": "assistant", "content": "$ 执行 ls -la /home"},
                {"role": "user", "content": "cat /etc/passwd | head -3"}
            ],
            "question": "模型是否正确执行了命令？",
            "check_command": True,
            "category": "角色扮演"
        },
    ],
    "多条件约束": [
        {
            "difficulty": "简单",
            "turns": [
                {"role": "user", "content": "我要找一家餐厅。"},
                {"role": "assistant", "content": "好的，有什么要求吗？"},
                {"role": "user", "content": "要便宜的。"}
            ],
            "question": "用户有什么要求？",
            "expected_keywords": ["便宜"],
            "category": "多条件约束"
        },
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "我要找一家餐厅。"},
                {"role": "assistant", "content": "好的，有什么要求吗？"},
                {"role": "user", "content": "要便宜的。"},
                {"role": "assistant", "content": "好的，经济实惠的。"},
                {"role": "user", "content": "还要在市中心。"}
            ],
            "question": "用户有哪些要求？",
            "expected_keywords": ["便宜", "市中心"],
            "category": "多条件约束"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "帮我找一台电脑。"},
                {"role": "assistant", "content": "好的，什么配置要求？"},
                {"role": "user", "content": "内存至少16G。"},
                {"role": "assistant", "content": "16G以上。"},
                {"role": "user", "content": "显卡要好，能跑AI模型。"},
                {"role": "assistant", "content": "好的，显卡要求高。"},
                {"role": "user", "content": "预算8000以内。"}
            ],
            "question": "用户的完整需求是什么？",
            "expected_keywords": ["16G", "显卡", "8000"],
            "category": "多条件约束"
        },
    ],
    "推理链": [
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "所有猫都怕水。"},
                {"role": "assistant", "content": "明白了，猫怕水。"},
                {"role": "user", "content": "汤姆是一只猫。"},
                {"role": "assistant", "content": "汤姆是猫。"},
                {"role": "user", "content": "所以汤姆怕什么？"}
            ],
            "question": "汤姆怕什么？",
            "expected_keywords": ["水"],
            "category": "推理链"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "所有学生都要考试。"},
                {"role": "assistant", "content": "学生需要考试。"},
                {"role": "user", "content": "小明没有参加考试。"},
                {"role": "assistant", "content": "小明没考试。"},
                {"role": "user", "content": "所以小明是什么？"}
            ],
            "question": "小明可能是什么？",
            "expected_keywords": ["不是学生", "不是", "未参加"],
            "category": "推理链"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "苹果比梨贵。"},
                {"role": "assistant", "content": "苹果 > 梨。"},
                {"role": "user", "content": "梨比香蕉贵。"},
                {"role": "assistant", "content": "梨 > 香蕉。"},
                {"role": "user", "content": "香蕉3元一斤。"}
            ],
            "question": "苹果至少多少钱一斤？",
            "expected_keywords": ["4", "大于", "贵"],
            "category": "推理链"
        },
    ],
    "隐含信息": [
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "这件衣服多少钱？"},
                {"role": "assistant", "content": "这件衣服售价500元。"},
                {"role": "user", "content": "好贵啊，我预算只有300。"}
            ],
            "question": "用户的意思是什么？",
            "expected_keywords": ["买不起", "超预算", "太贵", "不想买"],
            "category": "隐含信息"
        },
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "今天是我女朋友生日。"},
                {"role": "assistant", "content": "生日快乐！"},
                {"role": "user", "content": "但是我忘了买礼物。"},
                {"role": "assistant", "content": "这有点尴尬。"},
                {"role": "user", "content": "附近有花店吗？"}
            ],
            "question": "用户想买什么？",
            "expected_keywords": ["花", "鲜花", "礼物"],
            "category": "隐含信息"
        },
    ],
    "任务恢复": [
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "帮我订明天上午的机票。"},
                {"role": "assistant", "content": "好的，请问从哪里出发？"},
                {"role": "user", "content": "对了，今天天气怎么样？"},
                {"role": "assistant", "content": "今天天气晴朗。"},
                {"role": "user", "content": "继续说机票的事。"}
            ],
            "question": "用户要订哪里的机票？",
            "expected_keywords": ["出发", "哪里", "目的地"],
            "category": "任务恢复"
        },
    ],
    "情感理解": [
        {
            "difficulty": "中等",
            "turns": [
                {"role": "user", "content": "我今天被领导骂了。"},
                {"role": "assistant", "content": "听起来不太好受。"},
                {"role": "user", "content": "其实是我做错了。"}
            ],
            "question": "用户现在的情绪状态？",
            "expected_keywords": ["自责", "承认", "难过", "后悔"],
            "category": "情感理解"
        },
    ],
    "逻辑推断": [
        {
            "difficulty": "困难",
            "turns": [
                {"role": "user", "content": "下雨天不带伞出门会被淋湿。"},
                {"role": "assistant", "content": "是的，会淋湿。"},
                {"role": "user", "content": "今天下雨了。"},
                {"role": "assistant", "content": "今天有雨。"},
                {"role": "user", "content": "小明没带伞出门了。"}
            ],
            "question": "小明会被淋湿吗？",
            "expected_keywords": ["会", "淋湿", "肯定"],
            "category": "逻辑推断"
        },
    ],
}


def generate_multiturn_questions(target_count=50):
    """生成多轮对话测试题目"""
    questions = []
    qid = 1

    # 难度分布：简单 30%, 中等 50%, 困难 20%
    easy_count = int(target_count * 0.3)
    medium_count = int(target_count * 0.5)
    hard_count = target_count - easy_count - medium_count

    difficulty_map = {
        "简单": easy_count,
        "中等": medium_count,
        "困难": hard_count,
    }

    # 按难度生成题目
    for difficulty, count in difficulty_map.items():
        for _ in range(count):
            # 随机选择一个类别
            category = random.choice(list(MULTITURN_TEMPLATES.keys()))
            templates = MULTITURN_TEMPLATES[category]

            # 筛选该难度下的模板
            suitable_templates = [t for t in templates if t.get("difficulty") == difficulty]

            if suitable_templates:
                template = random.choice(suitable_templates)
            else:
                template = random.choice(templates)

            # 创建题目
            question = {
                "id": qid,
                "name": f"多轮-{category}-{qid}",
                "category": category,
                "difficulty": template.get("difficulty", difficulty),
                "turns": template["turns"],
                "question": template.get("question", ""),
                "expected_keywords": template.get("expected_keywords", []),
                "check_role_keywords": template.get("check_role_keywords", []),
                "check_command": template.get("check_command", False),
            }
            questions.append(question)
            qid += 1

    # 打乱顺序
    random.shuffle(questions)

    return questions


class MultiTurnEvaluator:
    """增强版多轮对话评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        self.model_url = model_url
        self.model_name = model_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def evaluate_question(self, question: dict) -> dict:
        """评估单个多轮对话问题"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"

        # 构建消息历史
        messages = [{"role": "system", "content": "你是一个helpful助手。"}]

        # 添加对话历史
        for turn in question["turns"]:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # 添加最终问题
        if question.get("question"):
            messages.append({"role": "user", "content": question["question"]})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start

            if resp.status_code != 200:
                return {
                    "passed": False,
                    "error": f"HTTP {resp.status_code}",
                    "duration_ms": elapsed * 1000
                }

            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            if not content:
                content = message.get("reasoning_content", "")

            # 评估回答
            passed = self._check_response(content, question)

            return {
                "passed": passed,
                "response": content[:500],
                "duration_ms": elapsed * 1000,
                "raw_response": data
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "duration_ms": 0
            }

    def _check_response(self, response: str, question: dict) -> bool:
        """检查回答是否符合预期"""
        response_lower = response.lower()

        # 检查角色扮演关键词
        if question.get("check_role_keywords"):
            keywords = question["check_role_keywords"]
            matched = sum(1 for kw in keywords if kw.lower() in response_lower)
            return matched >= len(keywords) * 0.5

        # 检查命令执行
        if question.get("check_command"):
            # 检查是否包含命令输出格式
            return "$" in response or "root" in response or "drwxr-xr-x" in response

        # 检查预期关键词
        if question.get("expected_keywords"):
            keywords = question["expected_keywords"]
            matched = sum(1 for kw in keywords if kw.lower() in response_lower)
            # 需要匹配至少50%的关键词
            return matched >= len(keywords) * 0.5

        return False


def run_multiturn_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4",
                       question_count: int = 50, generate_only: bool = False):
    """运行多轮对话测试"""

    # 生成题目
    questions = generate_multiturn_questions(question_count)

    print(f"生成了 {len(questions)} 道多轮对话测试题")

    # 统计难度分布
    difficulty_dist = Counter(q["difficulty"] for q in questions)
    print(f"难度分布: {dict(difficulty_dist)}")

    # 统计类别分布
    category_dist = Counter(q["category"] for q in questions)
    print(f"类别分布: {dict(category_dist)}")

    # 保存题目
    output_file = os.path.join(output_dir, "multiturn_questions.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"题目已保存到: {output_file}")

    if generate_only:
        return None

    # 运行测试
    evaluator = MultiTurnEvaluator(model_url, model_name, output_dir)

    results = []
    passed = 0

    for i, q in enumerate(questions, 1):
        print(f"\r  进度: {i}/{len(questions)}", end="", flush=True)

        result = evaluator.evaluate_question(q)
        results.append({
            "question": q,
            "result": result
        })

        if result.get("passed"):
            passed += 1

    print(f"\n测试完成！通过率: {passed/len(results)*100:.1f}%")

    # 生成报告
    report = generate_report(questions, results, model_name, model_url)
    print(f"报告已保存到: {report}")

    return {
        "total": len(questions),
        "passed": passed,
        "pass_rate": passed / len(questions) if questions else 0,
        "report": report
    }


def generate_report(questions: List[dict], results: List[dict], model_name: str, model_url: str) -> str:
    """生成测试报告"""
    from datetime import datetime

    passed = sum(1 for r in results if r["result"].get("passed"))
    total = len(results)

    # 按难度统计
    difficulty_stats = {}
    for q, r in zip(questions, results):
        diff = q["difficulty"]
        if diff not in difficulty_stats:
            difficulty_stats[diff] = {"total": 0, "passed": 0}
        difficulty_stats[diff]["total"] += 1
        if r["result"].get("passed"):
            difficulty_stats[diff]["passed"] += 1

    # 按类别统计
    category_stats = {}
    for q, r in zip(questions, results):
        cat = q["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1
        if r["result"].get("passed"):
            category_stats[cat]["passed"] += 1

    # 生成报告
    report = f"""# Stage 4 多轮对话能力测试报告

> **模型**: {model_name}
> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **后端**: {"Vulkan" if "8400" in model_url else "CUDA V100"}

---

## 📊 总体表现

| 指标 | 数值 |
|------|------|
| 总题数 | {total} |
| 通过数 | {passed} |
| 失败数 | {total - passed} |
| 通过率 | **{passed/total*100:.1f}%** |

**评级**: {"✅ 优秀" if passed/total >= 0.8 else "✅ 良好" if passed/total >= 0.6 else "⚠️ 需改进"}

---

## 📈 按难度统计

| 难度 | 题数 | 通过 | 通过率 |
|------|------|------|--------|
"""

    for diff in ["简单", "中等", "困难"]:
        stats = difficulty_stats.get(diff, {"total": 0, "passed": 0})
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        report += f"| {diff} | {stats['total']} | {stats['passed']} | {rate:.1f}% |\n"

    report += f"""
## 📋 按类别统计

| 类别 | 题数 | 通过 | 通过率 |
|------|------|------|--------|
"""

    # 按通过率排序
    sorted_cats = sorted(category_stats.items(), key=lambda x: x[1]["passed"]/x[1]["total"] if x[1]["total"] > 0 else 0, reverse=True)
    for cat, stats in sorted_cats:
        rate = stats["passed"] / stats["total"] * 100 if stats["total"] > 0 else 0
        report += f"| {cat} | {stats['total']} | {stats['passed']} | {rate:.1f}% |\n"

    report += f"""
---

## 📝 错误分析

### 失败题目

| 题目 | 类别 | 难度 | 期望关键词 |
|------|------|------|------------|
"""

    failed = [(q, r) for q, r in zip(questions, results) if not r["result"].get("passed")]
    for q, r in failed[:20]:
        keywords = q.get("expected_keywords", q.get("check_role_keywords", []))
        report += f"| {q['name']} | {q['category']} | {q['difficulty']} | {', '.join(keywords[:3])} |\n"

    report += f"""
---

*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    # 保存报告
    output_file = os.path.join("eval_results/stage4", f"multiturn_{datetime.now().strftime('%Y%m%d_%H%M%S')}_report.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    return output_file


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 多轮对话能力测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--count", type=int, default=50, help="题目数量")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    run_multiturn_test(
        args.model_url,
        args.model_name,
        args.output_dir,
        args.count,
        args.generate_only
    )
