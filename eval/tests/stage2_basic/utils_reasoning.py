#!/usr/bin/env python3
"""
推理模型输出处理工具

用于处理包含 Thinking Process 的模型输出
"""

import re


def extract_after_think(text: str) -> str:
    """
    提取 </think> 标签后的内容

    Args:
        text: 模型输出文本

    Returns:
        </think> 后的内容，如果没有则返回原文本
    """
    # 匹配 </think> 标签及其后的内容
    patterns = [
        r'</think>\s*(.*)',  # 标准格式
        r'\*\*Final Answer:\*\*\s*(.*)',  # 某些模型的格式
        r'答案是\s*[:：]\s*(.*)',  # 中文格式
        r'答案[是为]\s*[:：]\s*(.*)',  # 中文格式变体
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return text


def extract_last_number(text: str) -> float:
    """
    从文本中提取最后一个数字

    Args:
        text: 模型输出文本

    Returns:
        最后一个数字，如果没有则返回 None
    """
    # 先清理推理过程
    text = clean_reasoning_output(text)

    # 先尝试找明确的答案标记
    patterns = [
        r'答案[是为:]+\s*([\d.]+)',
        r'结果[是为:]+\s*([\d.]+)',
        r'等于\s*([\d.]+)',
        r'([\d.]+)\s*元',
        r'([\d.]+)\s*天',
        r'([\d.]+)\s*人',
        r'([\d.]+)\s*公里',
        r'([\d.]+)\s*克',
        r'([\d.]+)\s*%',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            try:
                return float(matches[-1])  # 取最后一个匹配
            except:
                continue

    # 最后尝试：取文本中最后一个单独的数字
    all_numbers = re.findall(r'\b([\d.]+)\b', text)
    if all_numbers:
        try:
            return float(all_numbers[-1])
        except:
            pass

    return None


def extract_answer_letter(text: str) -> str:
    """
    从文本中提取答案字母 (A/B/C/D)

    策略：
    1. 先看 </think> 后的内容
    2. 查找最后一行的大写字母
    3. 查找明确标记的答案

    Args:
        text: 模型输出文本

    Returns:
        答案字母 A/B/C/D，如果没有则返回空字符串
    """
    text = text.upper().strip()

    # 1. 先看 </think> 后的内容
    after_think = extract_after_think(text)
    if after_think and after_think != text:
        # 在 </think> 后的内容中找答案
        lines = after_think.split('\n')
        for line in reversed(lines):
            line = line.strip()
            # 查找明确的答案格式
            match = re.search(r'(?:答案|选项|选择)[:：]?\s*([ABCD])', line)
            if match:
                return match.group(1)
            # 查找行首或行尾的字母
            match = re.search(r'^[\s\*\-]*([ABCD])[\.\)\s]', line)
            if match:
                return match.group(1)
            match = re.search(r'\b([ABCD])\b', line)
            if match:
                return match.group(1)

    # 2. 查找最后一行
    lines = text.split('\n')
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        # 查找明确标记的答案
        match = re.search(r'(?:答案|选项|选择)[:：]?\s*([ABCD])', line, re.IGNORECASE)
        if match:
            return match.group(1)
        # 查找独立的字母
        match = re.search(r'\b([ABCD])\b', line)
        if match:
            return match.group(1)

    # 3. 最后的兜底：找第一个 A/B/C/D (可能不准确)
    for char in ["A", "B", "C", "D"]:
        if char in text:
            return char

    return ""


def clean_reasoning_output(text: str) -> str:
    """
    清理推理模型的输出，去除 Thinking Process

    Args:
        text: 原始输出

    Returns:
        清理后的输出
    """
    if not text:
        return text

    # 1. 提取 </think> 后的内容
    after_think = extract_after_think(text)
    if after_think and after_think != text:
        return after_think

    # 2. 如果没有 </think>，尝试去掉 Thinking Process 部分
    # Qwen3.5 格式: "Thinking Process:" 后面跟着多行分析，然后是空行和最终答案
    patterns = [
        # 匹配 "Thinking Process:" 开头，直到遇到空行+大写字母开头（Final Answer 或数字）
        r'Thinking Process:.*?(?=\n\n(?:[A-Z\d]|$))',  # Thinking Process 部分
        r'<think>.*?</think>',  # think 标签
        # 匹配 "Thinking Process:" 到 "Final Answer:" 之间的内容
        r'Thinking Process:.*?(?=Final Answer:|$)',
    ]

    cleaned = text
    for pattern in patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    # 3. 移除常见的推理标记
    cleaned = re.sub(r'\*\*Thinking Process:\*\*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\*\*Final Answer:\*\*', '', cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


# 向后兼容的别名
_extract_number_fixed = extract_last_number
_extract_answer_fixed = extract_answer_letter
