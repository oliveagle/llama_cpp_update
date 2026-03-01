#!/usr/bin/env python3
"""
Stage 4 专项能力测试 - 多轮对话推理能力测试
测试复杂问题的多轮推理能力，包含指代消解、信息追踪、推理链等
"""

import random
import json
import os
import time

# 多轮对话测试用例模板
MULTITURN_TEMPLATES = {
    # 简单级别 - 基本指代和追踪
    "指代消解_简单": {
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
    "信息追踪_简单": {
        "difficulty": "简单",
        "turns": [
            {"role": "user", "content": "我的名字是小明。"},
            {"role": "assistant", "content": "好的，小明。"},
            {"role": "user", "content": "我今天买了本书。"}
        ],
        "question": "谁买了书？",
        "expected_keywords": ["小明", "你"],
        "category": "信息追踪"
    },
    "意图变化_简单": {
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
    # 中等级别 - 多步推理
    "多步计算_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "我有100元钱。"},
            {"role": "assistant", "content": "好的，您有100元。"},
            {"role": "user", "content": "花了30元买了本书。"},
            {"role": "assistant", "content": "还剩70元。"},
            {"role": "user", "content": "又花了25元吃午饭。"}
        ],
        "question": "现在还剩多少钱？",
        "expected_keywords": ["45"],
        "category": "多步计算"
    },
    "否定理解_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "我喜欢红色。"},
            {"role": "assistant", "content": "红色很热情。"},
            {"role": "user", "content": "但我不喜欢穿红色的衣服。"}
        ],
        "question": "用户喜欢穿红色衣服吗？",
        "expected_keywords": ["不喜欢", "不"],
        "category": "否定理解"
    },
    "时间顺序_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "早上8点我吃了早餐。"},
            {"role": "assistant", "content": "好的，早餐在8点。"},
            {"role": "user", "content": "中午12点吃了午饭。"},
            {"role": "assistant", "content": "午餐在12点。"},
            {"role": "user", "content": "晚餐比午餐晚6个小时。"}
        ],
        "question": "晚餐是几点？",
        "expected_keywords": ["18", "下午6"],
        "category": "时间顺序"
    },
    "多条件约束_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "我要找一家餐厅。"},
            {"role": "assistant", "content": "好的，有什么要求吗？"},
            {"role": "user", "content": "要便宜的。"},
            {"role": "assistant", "content": "好的，经济实惠的。"},
            {"role": "user", "content": "还要在市中心。"},
            {"role": "assistant", "content": "好的，市中心的位置。"},
            {"role": "user", "content": "最好有包间。"}
        ],
        "question": "用户有哪些要求？",
        "expected_keywords": ["便宜", "市中心", "包间"],
        "category": "多条件约束"
    },
    # 困难级别 - 复杂推理链
    "推理链_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "如果明天下雨，球赛就会取消。"},
            {"role": "assistant", "content": "明白了。"},
            {"role": "user", "content": "明天下雨了。"},
            {"role": "assistant", "content": "所以球赛取消了。"},
            {"role": "user", "content": "但是体育馆有屋顶，所以比赛照常进行。"}
        ],
        "question": "球赛最终进行了吗？",
        "expected_keywords": ["进行", "照常", "是"],
        "category": "推理链"
    },
    "隐含信息_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "这件衣服多少钱？"},
            {"role": "assistant", "content": "这件衣服售价500元。"},
            {"role": "user", "content": "好贵啊，我预算只有300。"}
        ],
        "question": "用户的意思是什么？",
        "expected_keywords": ["买不起", "超预算", "太贵", "不想买", "便宜"],
        "category": "隐含信息"
    },
    "任务恢复_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "帮我订明天上午的机票。"},
            {"role": "assistant", "content": "好的，请问从哪里出发？"},
            {"role": "user", "content": "对了，今天天气怎么样？"},
            {"role": "assistant", "content": "今天天气晴朗。"},
            {"role": "user", "content": "继续说机票的事。"}
        ],
        "question": "客服需要继续问什么信息才能订票？",
        "expected_keywords": ["出发", "目的地", "城市", "地点"],
        "category": "任务恢复"
    },
    # 额外场景
    "角色扮演_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "假设你是一位历史老师，请用老师的身份和我对话。"},
            {"role": "assistant", "content": "好的同学，我是你的历史老师。"},
            {"role": "user", "content": "老师，请介绍一下秦始皇。"}
        ],
        "question": "老师的回答应该体现什么身份特征？",
        "expected_keywords": ["同学", "我们", "学习", "历史", "老师"],
        "category": "角色一致"
    },
    "逻辑陷阱_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "所有猫都是动物。"},
            {"role": "assistant", "content": "是的。"},
            {"role": "user", "content": "所有狗都是动物。"},
            {"role": "assistant", "content": "是的。"},
            {"role": "user", "content": "所以猫是狗吗？"}
        ],
        "question": "正确的回答应该是什么？",
        "expected_keywords": ["不是", "不能", "不"],
        "category": "逻辑推理"
    },
    "因果关系_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "因为今天下雨，所以地面湿了。"},
            {"role": "assistant", "content": "明白了。"},
            {"role": "user", "content": "现在地面是干的。"}
        ],
        "question": "可以推断出什么？",
        "expected_keywords": ["没下雨", "不下雨", "雨停了", "不可能"],
        "category": "因果推理"
    },
    "比较推理_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "A比B高。"},
            {"role": "assistant", "content": "好的，A更高。"},
            {"role": "user", "content": "B比C高。"}
        ],
        "question": "三个人中谁最高？",
        "expected_keywords": ["A"],
        "category": "比较推理"
    },
    "序列推理_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "第一天我读了10页书。"},
            {"role": "assistant", "content": "好的，第一天10页。"},
            {"role": "user", "content": "第二天读的页数是第一天的2倍。"},
            {"role": "assistant", "content": "第二天20页。"},
            {"role": "user", "content": "第三天读的页数比第二天少5页。"}
        ],
        "question": "第三天读了多少页？",
        "expected_keywords": ["15"],
        "category": "序列推理"
    },
    "反事实推理_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "如果昨天带了伞，我就不会被淋湿。"},
            {"role": "assistant", "content": "明白了。"},
            {"role": "user", "content": "但是我昨天确实被淋湿了。"}
        ],
        "question": "可以推断出什么？",
        "expected_keywords": ["没带伞", "没有带", "忘记带"],
        "category": "反事实推理"
    },
    "情感理解_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "我今天考试没考好，只得了60分。"},
            {"role": "assistant", "content": "60分刚好及格，别太灰心。"},
            {"role": "user", "content": "可是我同桌考了95分。"}
        ],
        "question": "用户的情绪可能是什么？",
        "expected_keywords": ["难过", "失落", "羡慕", "沮丧", "不甘"],
        "category": "情感理解"
    },
    "意图识别_中等": {
        "difficulty": "中等",
        "turns": [
            {"role": "user", "content": "现在几点？"},
            {"role": "assistant", "content": "现在的时间是..."},
            {"role": "user", "content": "我不是问时间，我是问今天星期几。"}
        ],
        "question": "用户真正的意图是什么？",
        "expected_keywords": ["星期", "周几", "礼拜"],
        "category": "意图识别"
    },
    "知识推理_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "水的化学式是H2O。"},
            {"role": "assistant", "content": "是的。"},
            {"role": "user", "content": "氧气有两个氧原子。"}
        ],
        "question": "氧气的化学式是什么？",
        "expected_keywords": ["O2"],
        "category": "知识推理"
    },
    "归纳总结_困难": {
        "difficulty": "困难",
        "turns": [
            {"role": "user", "content": "昨天气温是20度。"},
            {"role": "assistant", "content": "昨天20度。"},
            {"role": "user", "content": "今天气温是22度。"},
            {"role": "assistant", "content": "今天22度。"},
            {"role": "user", "content": "明天预计25度。"}
        ],
        "question": "气温的趋势是什么？",
        "expected_keywords": ["上升", "升高", "变暖", "回暖", "升温"],
        "category": "归纳总结"
    },
}


def generate_multiturn_questions(target_count=50):
    """生成多轮对话题目，难度分布：简单30%/中等50%/困难20%"""
    questions = []
    qid = 1

    easy_count = int(target_count * 0.3)
    medium_count = int(target_count * 0.5)
    hard_count = target_count - easy_count - medium_count

    # 按难度分类模板
    easy_templates = [k for k, v in MULTITURN_TEMPLATES.items() if v["difficulty"] == "简单"]
    medium_templates = [k for k, v in MULTITURN_TEMPLATES.items() if v["difficulty"] == "中等"]
    hard_templates = [k for k, v in MULTITURN_TEMPLATES.items() if v["difficulty"] == "困难"]

    def create_question(template_key):
        template = MULTITURN_TEMPLATES[template_key]
        return {
            "id": qid,
            "name": f"多轮-{template['category']}-{qid}",
            "category": template["category"],
            "difficulty": template["difficulty"],
            "turns": template["turns"],
            "question": template["question"],
            "expected_keywords": template["expected_keywords"],
            "min_keyword_match": max(1, len(template["expected_keywords"]) // 2),  # 至少匹配50%
            "keywords": ["multiturn", "conversation", "reasoning"]
        }

    # 生成简单题
    for _ in range(easy_count):
        if easy_templates:
            template_key = random.choice(easy_templates)
            questions.append(create_question(template_key))
            qid += 1

    # 生成中等题
    for _ in range(medium_count):
        if medium_templates:
            template_key = random.choice(medium_templates)
            questions.append(create_question(template_key))
            qid += 1

    # 生成困难题
    for _ in range(hard_count):
        if hard_templates:
            template_key = random.choice(hard_templates)
            questions.append(create_question(template_key))
            qid += 1

    # 如果数量不够，循环使用模板
    while len(questions) < target_count:
        template_key = random.choice(list(MULTITURN_TEMPLATES.keys()))
        questions.append(create_question(template_key))
        qid += 1

    return questions


class MultiTurnReasoningEvaluator:
    """多轮对话推理能力评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.model_url = model_url
        self.model_name = model_name
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_multiturn_questions(50)

    def _test_single_case(self, test_case):
        """测试单个多轮对话场景"""
        import requests
        url = f"{self.model_url}/v1/chat/completions"

        # 构建消息历史
        messages = [{"role": "system", "content": "你是一个 helpful 助手。"}]

        # 执行多轮对话
        for turn in test_case["turns"]:
            messages.append({"role": turn["role"], "content": turn["content"]})

        # 最终问题
        messages.append({"role": "user", "content": test_case["question"]})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 256,
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

            # 检查关键词匹配
            keywords = test_case["expected_keywords"]
            min_match = test_case["min_keyword_match"]
            matched = sum(1 for kw in keywords if kw in content)
            passed = matched >= min_match

            return {
                "passed": passed,
                "content": content[:200],
                "matched_keywords": matched,
                "total_keywords": len(keywords),
                "duration_ms": elapsed * 1000
            }

        except Exception as e:
            return {
                "passed": False,
                "error": str(e),
                "duration_ms": 0
            }

    def run_tests(self):
        """运行多轮对话推理测试"""
        test_results = []
        start_time = time.time()

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\r  进度：{i}/{len(self.test_cases)}", end="", flush=True)

            result = self._test_single_case(test_case)

            # 构建 TestResult
            from base import TestResult
            test_result = TestResult(
                name=test_case["name"],
                category=test_case["category"],
                difficulty=test_case["difficulty"],
                passed=result.get("passed", False),
                duration_ms=result.get("duration_ms", 0),
                details={
                    "question": test_case["question"],
                    "response": result.get("content", ""),
                    "matched_keywords": result.get("matched_keywords", 0),
                    "total_keywords": result.get("total_keywords", 0)
                },
                error_message=result.get("error")
            )
            test_results.append(test_result)

        elapsed = time.time() - start_time
        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        from base import StageResult
        stats = self.base_eval._calculate_stats(test_results)

        return StageResult(
            stage_name="专项能力测试-多轮对话",
            stage_number=4,
            category="multiturn_reasoning",
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            duration_seconds=elapsed,
            test_results=test_results,
            passed_threshold=(passed / total >= 0.6) if total > 0 else False,
            threshold_percentage=0.6,
            by_difficulty=stats["by_difficulty"],
            by_subcategory=stats["by_subcategory"]
        )


def run_multiturn_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """便捷函数运行多轮对话推理测试"""
    evaluator = MultiTurnReasoningEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.base_eval.generate_report(result)
    return {
        "result": result,
        "report_file": report_file
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 多轮对话推理测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型地址")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M", help="模型名称")
    parser.add_argument("--output-dir", default="eval_results/stage4", help="输出目录")
    parser.add_argument("--count", type=int, default=50, help="题目数量")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_multiturn_questions(args.count)
        print(f"生成了 {len(questions)} 道多轮对话推理题:")
        easy = sum(1 for q in questions if q["difficulty"] == "简单")
        medium = sum(1 for q in questions if q["difficulty"] == "中等")
        hard = sum(1 for q in questions if q["difficulty"] == "困难")
        print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

        # 保存题目
        output_file = os.path.join(args.output_dir, "multiturn_reasoning_questions.json")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到：{output_file}")
    else:
        print(f"开始运行多轮对话推理测试...")
        test_result = run_multiturn_test(args.model_url, args.model_name, args.output_dir)
        print(f"\n测试完成！通过率：{test_result['result'].pass_rate*100:.1f}%")
