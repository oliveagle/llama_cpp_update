#!/usr/bin/env python3
"""
Stage 4 通用评估工具
提供通用的选项打乱、题目生成等工具函数
"""

import random


def shuffle_options(template):
    """
    打乱选择题选项顺序，返回新选项和对应答案

    Args:
        template: 题目模板，包含 "opts" (选项列表) 和 "a" (正确答案 A/B/C/D)

    Returns:
        tuple: (打乱后的选项列表, 新答案字母)

    示例:
        template = {"opts": ["正确", "错误 1", "错误 2", "错误 3"], "a": "A"}
        shuffled_opts, new_answer = shuffle_options(template)
        # 可能返回：(["错误 2", "正确", "错误 3", "错误 1"], "B")
    """
    opts = template["opts"].copy()
    correct_answer = template["a"]
    correct_idx = ord(correct_answer) - ord("A")
    correct_text = opts[correct_idx]

    # 随机打乱选项
    shuffled = opts.copy()
    random.shuffle(shuffled)

    # 找到正确答案的新位置
    new_idx = shuffled.index(correct_text)
    new_answer = chr(ord("A") + new_idx)

    return shuffled, new_answer


def generate_questions_from_templates(templates, target_count=100, difficulty_weights=None):
    """
    从模板生成选择题，自动打乱选项

    Args:
        templates: 题目模板字典 {category: [template1, template2, ...]}
        target_count: 目标题目数量
        difficulty_weights: 难度权重字典 {"简单": 0.4, "中等": 0.45, "困难": 0.15}

    Returns:
        list: 生成的题目列表
    """
    if difficulty_weights is None:
        difficulty_weights = {"简单": 0.4, "中等": 0.45, "困难": 0.15}

    questions = []
    qid = 1

    # 计算各难度题目数量
    difficulty_counts = {
        diff: int(target_count * weight)
        for diff, weight in difficulty_weights.items()
    }

    # 调整总数（由于取整可能导致差异）
    total = sum(difficulty_counts.values())
    if total < target_count:
        difficulty_counts["中等"] += target_count - total

    # 按难度生成题目
    for difficulty, count in difficulty_counts.items():
        for _ in range(count):
            # 随机选择类别和模板
            category = random.choice(list(templates.keys()))
            if templates[category]:
                template = random.choice(templates[category])

                # 打乱选项
                shuffled_opts, new_answer = shuffle_options(template)

                questions.append({
                    "id": qid,
                    "name": f"{category}-{qid}",
                    "category": category,
                    "difficulty": difficulty,
                    "question": template["q"],
                    "options": shuffled_opts,
                    "answer": new_answer,
                    "keywords": [category.lower()]
                })
                qid += 1

    return questions


def verify_answer_distribution(questions):
    """
    验证答案分布是否均匀

    Args:
        questions: 题目列表

    Returns:
        dict: 答案分布统计
    """
    from collections import Counter
    dist = Counter(q["answer"] for q in questions)
    return dict(dist)


def verify_shuffle_effectiveness(template, iterations=1000):
    """
    验证打乱函数的有效性

    Args:
        template: 题目模板
        iterations: 测试次数

    Returns:
        dict: 答案分布统计
    """
    from collections import Counter
    answers = []

    for _ in range(iterations):
        _, new_answer = shuffle_options(template)
        answers.append(new_answer)

    return Counter(answers)
