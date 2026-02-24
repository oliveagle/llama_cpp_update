#!/usr/bin/env python3
"""
JoyAI-LLM-Flash Stage 3 深度能力评估
基于项目 Stage 3 框架的完整评测 (10 个维度，1000 个测试用例精选版)
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
import statistics

# 配置
BASE_URL = "http://localhost:8400/v1/chat/completions"
MODEL_NAME = "JoyAI-LLM-Flash-Q4_K_M"
TIMEOUT = 120
OUTPUT_DIR = "eval_results/stage3_joyai_flash"

# Stage 3 精选测试用例 (每个维度 20 题，共 200 题)
# 从完整的 1000 题中精选代表性题目

STAGE3_TEST_CASES = {
    "math_reasoning": [
        {"id": 1, "name": "数学 - 代数方程", "category": "代数", "difficulty": "简单", "prompt": "解方程 3x + 7 = 22，求 x 的值", "expected_keywords": ["5"], "weight": 1},
        {"id": 2, "name": "数学 - 百分比计算", "category": "代数", "difficulty": "简单", "prompt": "一件商品原价 200 元，打 8 折后的价格是多少？", "expected_keywords": ["160"], "weight": 1},
        {"id": 3, "name": "数学 - 比例问题", "category": "代数", "difficulty": "中等", "prompt": "甲乙两人年龄比是 3:5，年龄和是 40 岁，问甲多少岁？", "expected_keywords": ["15"], "weight": 2},
        {"id": 4, "name": "数学 - 行程问题", "category": "应用题", "difficulty": "中等", "prompt": "AB 两地相距 300 公里，甲车从 A 出发时速 60 公里，乙车从 B 出发时速 40 公里，相向而行几小时后相遇？", "expected_keywords": ["3", "小时"], "weight": 2},
        {"id": 5, "name": "数学 - 工程问题", "category": "应用题", "difficulty": "中等", "prompt": "一项工程，甲单独做需要 10 天完成，乙单独做需要 15 天完成，两人合作需要几天完成？", "expected_keywords": ["6"], "weight": 2},
        {"id": 6, "name": "数学 - 几何面积", "category": "几何", "difficulty": "简单", "prompt": "一个圆的半径是 5 厘米，求面积（π取 3.14）", "expected_keywords": ["78.5"], "weight": 1},
        {"id": 7, "name": "数学 - 概率计算", "category": "概率", "difficulty": "中等", "prompt": "掷一枚骰子，出现偶数点的概率是多少？", "expected_keywords": ["1/2", "0.5", "50%"], "weight": 2},
        {"id": 8, "name": "数学 - 平均数", "category": "统计", "difficulty": "简单", "prompt": "5 个数的平均数是 20，其中 4 个数分别是 15、18、22、25，求第 5 个数", "expected_keywords": ["20"], "weight": 2},
        {"id": 9, "name": "数学 - 利润计算", "category": "应用题", "difficulty": "中等", "prompt": "某商品进价 80 元，标价 120 元，打 9 折出售，利润率是多少？", "expected_keywords": ["35%", "0.35"], "weight": 2},
        {"id": 10, "name": "数学 - 数列求和", "category": "代数", "difficulty": "中等", "prompt": "求等差数列 2,5,8,11,...的前 20 项和", "expected_keywords": ["610"], "weight": 2},
        {"id": 11, "name": "数学 - 鸡兔同笼", "category": "应用题", "difficulty": "中等", "prompt": "鸡兔同笼，共有头 35 个，脚 94 只，问鸡兔各多少只？", "expected_keywords": ["23", "12"], "weight": 2},
        {"id": 12, "name": "数学 - 追及问题", "category": "应用题", "difficulty": "中等", "prompt": "甲每小时行 15 公里，乙每小时行 10 公里，乙先走 2 小时后甲出发，甲几小时能追上乙？", "expected_keywords": ["4"], "weight": 2},
        {"id": 13, "name": "数学 - 浓度问题", "category": "应用题", "difficulty": "困难", "prompt": "有含盐 10% 的盐水 100 克，要变成含盐 20% 的盐水，需要加盐多少克？", "expected_keywords": ["12.5"], "weight": 3},
        {"id": 14, "name": "数学 - 二次方程", "category": "代数", "difficulty": "困难", "prompt": "解方程 x² - 5x + 6 = 0", "expected_keywords": ["2", "3"], "weight": 3},
        {"id": 15, "name": "数学 - 勾股定理", "category": "几何", "difficulty": "简单", "prompt": "直角三角形两直角边分别是 3 和 4，斜边长是多少？", "expected_keywords": ["5"], "weight": 1},
        {"id": 16, "name": "数学 - 排列组合", "category": "概率", "difficulty": "困难", "prompt": "从 5 个人中选 3 个人排队，有多少种不同的排法？", "expected_keywords": ["60"], "weight": 3},
        {"id": 17, "name": "数学 - 牛吃草问题", "category": "应用题", "difficulty": "困难", "prompt": "一片草地，10 头牛可以吃 20 天，15 头牛可以吃 10 天，问 25 头牛可以吃多少天？", "expected_keywords": ["5"], "weight": 3},
        {"id": 18, "name": "数学 - 分数运算", "category": "代数", "difficulty": "简单", "prompt": "计算 1/2 + 1/3 + 1/6", "expected_keywords": ["1"], "weight": 1},
        {"id": 19, "name": "数学 - 最大公约数", "category": "数论", "difficulty": "中等", "prompt": "求 48 和 60 的最大公约数", "expected_keywords": ["12"], "weight": 2},
        {"id": 20, "name": "数学 - 最小公倍数", "category": "数论", "difficulty": "中等", "prompt": "求 12 和 18 的最小公倍数", "expected_keywords": ["36"], "weight": 2},
    ],
    "logic_reasoning": [
        {"id": 1, "name": "逻辑 - 三段论", "category": "演绎推理", "difficulty": "简单", "prompt": "所有人都会死，苏格拉底是人，所以？", "expected_keywords": ["苏格拉底会死", "死"], "weight": 1},
        {"id": 2, "name": "逻辑 - 类比推理", "category": "类比推理", "difficulty": "简单", "prompt": "医生对医院，就像教师对什么？", "expected_keywords": ["学校"], "weight": 1},
        {"id": 3, "name": "逻辑 - 真假判断", "category": "演绎推理", "difficulty": "中等", "prompt": "如果'所有天鹅都是白色的'是假的，那么下面哪个一定是真的？A.所有天鹅都不是白色的 B.有些天鹅不是白色的 C.有些天鹅是白色的", "expected_keywords": ["B", "有些"], "weight": 2},
        {"id": 4, "name": "逻辑 - 必要条件", "category": "条件推理", "difficulty": "中等", "prompt": "年满 18 岁是拥有选举权的什么条件？", "expected_keywords": ["必要"], "weight": 2},
        {"id": 5, "name": "逻辑 - 排序推理", "category": "归纳推理", "difficulty": "简单", "prompt": "A 比 B 高，B 比 C 高，谁最高？", "expected_keywords": ["A"], "weight": 1},
        {"id": 6, "name": "逻辑 - 矛盾律", "category": "演绎推理", "difficulty": "困难", "prompt": "有人说'我现在说的这句话是谎话'，这句话是否构成悖论？", "expected_keywords": ["是", "悖论"], "weight": 3},
        {"id": 7, "name": "逻辑 - 选言推理", "category": "演绎推理", "difficulty": "中等", "prompt": "要么 A 去，要么 B 去。已知 A 没去，那么？", "expected_keywords": ["B 去"], "weight": 2},
        {"id": 8, "name": "逻辑 - 充分条件", "category": "条件推理", "difficulty": "中等", "prompt": "如果下雨，地就会湿。现在地湿了，能推出下雨了吗？", "expected_keywords": ["不能"], "weight": 2},
        {"id": 9, "name": "逻辑 - 归纳推理", "category": "归纳推理", "difficulty": "中等", "prompt": "观察了 1000 只天鹅都是白色的，能得出什么结论？这个结论可靠吗？", "expected_keywords": ["不可靠", "不完全"], "weight": 2},
        {"id": 10, "name": "逻辑 - 过河问题", "category": "逻辑谜题", "difficulty": "困难", "prompt": "一人带狼、羊、菜过河，船只能载一人一物，狼吃羊、羊吃菜，如何安全过河？", "expected_keywords": ["羊", "先"], "weight": 3},
        {"id": 11, "name": "逻辑 - 真假话", "category": "逻辑谜题", "difficulty": "困难", "prompt": "甲说乙说谎，乙说丙说谎，丙说甲乙都说谎。谁说的是真话？", "expected_keywords": ["乙"], "weight": 3},
        {"id": 12, "name": "逻辑 - 匹配问题", "category": "逻辑谜题", "difficulty": "中等", "prompt": "张三李四王五三人，分别是医生、教师、警察。已知张三不是医生，李四不是教师，王五不是警察。如果张三是教师，那么李四是？", "expected_keywords": ["警察"], "weight": 2},
        {"id": 13, "name": "逻辑 - 反向推理", "category": "演绎推理", "difficulty": "中等", "prompt": "如果 p 则 q，现在 q 不成立，能推出什么？", "expected_keywords": ["p 不成立"], "weight": 2},
        {"id": 14, "name": "逻辑 - 德摩根定律", "category": "演绎推理", "difficulty": "困难", "prompt": "非 (A 或 B) 等于什么？", "expected_keywords": ["非 A", "非 B"], "weight": 3},
        {"id": 15, "name": "逻辑 - 量词否定", "category": "演绎推理", "difficulty": "中等", "prompt": "'所有人都喜欢数学'的否定是什么？", "expected_keywords": ["有些人", "不喜欢"], "weight": 2},
        {"id": 16, "name": "逻辑 - 传递性", "category": "归纳推理", "difficulty": "简单", "prompt": "A>B, B>C, C>D，那么 A 和 D 的关系是？", "expected_keywords": ["A>D"], "weight": 1},
        {"id": 17, "name": "逻辑 - 充要条件", "category": "条件推理", "difficulty": "困难", "prompt": "一个三角形是等边三角形，是它是等角三角形的什么条件？", "expected_keywords": ["充要"], "weight": 3},
        {"id": 18, "name": "逻辑 - 排除法", "category": "逻辑谜题", "difficulty": "中等", "prompt": "有 ABCD 四个选项，已知 A 和 B 都不对，C 和 D 中只有一个对，如果 C 对则 D 也对，那么正确答案是？", "expected_keywords": ["D"], "weight": 2},
        {"id": 19, "name": "逻辑 - 假设推理", "category": "假设检验", "difficulty": "中等", "prompt": "假设地球停止自转，会发生什么现象？", "expected_keywords": ["昼夜", "一半"], "weight": 2},
        {"id": 20, "name": "逻辑 - 最优策略", "category": "逻辑谜题", "difficulty": "困难", "prompt": "囚徒困境中，两个理性囚徒的最优策略是什么？", "expected_keywords": ["都", "坦白", "背叛"], "weight": 3},
    ],
    "code_generation": [
        {"id": 1, "name": "代码 - 两数之和", "category": "基础算法", "difficulty": "简单", "prompt": "写一个 Python 函数 add(a, b) 返回两数之和", "expected_keywords": ["def", "return", "+", "a", "b"], "weight": 1},
        {"id": 2, "name": "代码 - 列表反转", "category": "数据结构", "difficulty": "简单", "prompt": "写一个 Python 函数反转列表，不使用 reverse()", "expected_keywords": ["def", "return", "[", "]", "::-1"], "weight": 1},
        {"id": 3, "name": "代码 - 判断素数", "category": "基础算法", "difficulty": "中等", "prompt": "写一个 Python 函数判断一个数是否为素数", "expected_keywords": ["def", "for", "return", "素数", "质数"], "weight": 2},
        {"id": 4, "name": "代码 - 斐波那契", "category": "基础算法", "difficulty": "中等", "prompt": "用 Python 写一个函数计算斐波那契数列的第 n 项", "expected_keywords": ["def", "fibonacci", "return"], "weight": 2},
        {"id": 5, "name": "代码 - 冒泡排序", "category": "排序算法", "difficulty": "中等", "prompt": "用 Python 实现冒泡排序", "expected_keywords": ["def", "for", "if", "swap"], "weight": 2},
        {"id": 6, "name": "代码 - 二分查找", "category": "基础算法", "difficulty": "中等", "prompt": "用 Python 实现二分查找算法", "expected_keywords": ["def", "left", "right", "mid"], "weight": 2},
        {"id": 7, "name": "代码 - 字符串反转", "category": "字符串处理", "difficulty": "简单", "prompt": "写一个 Python 函数反转字符串", "expected_keywords": ["def", "return", "[", "::-1", "]"], "weight": 1},
        {"id": 8, "name": "代码 - 统计词频", "category": "字符串处理", "difficulty": "中等", "prompt": "写一个 Python 函数统计字符串中每个单词出现的次数", "expected_keywords": ["def", "dict", "for", "in"], "weight": 2},
        {"id": 9, "name": "代码 - 最大公约数", "category": "基础算法", "difficulty": "中等", "prompt": "用 Python 写一个函数求两个数的最大公约数", "expected_keywords": ["def", "return", "gcd"], "weight": 2},
        {"id": 10, "name": "代码 - 文件读取", "category": "文件操作", "difficulty": "简单", "prompt": "写 Python 代码读取文件 test.txt 的内容并打印", "expected_keywords": ["open", "read", "print"], "weight": 1},
        {"id": 11, "name": "代码 - 异常处理", "category": "基础语法", "difficulty": "中等", "prompt": "写 Python 代码处理除以零异常", "expected_keywords": ["try", "except", "ZeroDivisionError"], "weight": 2},
        {"id": 12, "name": "代码 - 列表推导式", "category": "基础语法", "difficulty": "简单", "prompt": "用列表推导式生成 1 到 10 的平方的列表", "expected_keywords": ["[", "for", "in", "range"], "weight": 1},
        {"id": 13, "name": "代码 - 判断回文", "category": "字符串处理", "difficulty": "简单", "prompt": "写一个 Python 函数判断字符串是否是回文", "expected_keywords": ["def", "return", "=="], "weight": 1},
        {"id": 14, "name": "代码 - 快速排序", "category": "排序算法", "difficulty": "困难", "prompt": "用 Python 实现快速排序算法", "expected_keywords": ["def", "quick", "sort", "partition"], "weight": 3},
        {"id": 15, "name": "代码 - 链表节点", "category": "数据结构", "difficulty": "中等", "prompt": "用 Python 定义一个链表节点类", "expected_keywords": ["class", "Node", "next"], "weight": 2},
        {"id": 16, "name": "代码 - 栈的实现", "category": "数据结构", "difficulty": "中等", "prompt": "用 Python 实现一个栈数据结构，包含 push 和 pop 方法", "expected_keywords": ["class", "Stack", "push", "pop"], "weight": 2},
        {"id": 17, "name": "代码 - 递归阶乘", "category": "基础算法", "difficulty": "简单", "prompt": "用递归写一个计算阶乘的 Python 函数", "expected_keywords": ["def", "return", "n*", "factorial"], "weight": 1},
        {"id": 18, "name": "代码 - 字典操作", "category": "数据结构", "difficulty": "简单", "prompt": "创建一个字典存储学生姓名和分数，然后查询指定学生的分数", "expected_keywords": ["dict", "{", "}"], "weight": 1},
        {"id": 19, "name": "代码 - 冒泡排序优化", "category": "排序算法", "difficulty": "困难", "prompt": "写一个优化版的冒泡排序，如果某一轮没有交换就提前结束", "expected_keywords": ["def", "swap", "flag", "break"], "weight": 3},
        {"id": 20, "name": "代码 - 装饰器", "category": "高级语法", "difficulty": "困难", "prompt": "写一个 Python 装饰器，用于计算函数执行时间", "expected_keywords": ["def", "decorator", "wrapper", "time"], "weight": 3},
    ],
    "knowledge_qa": [
        {"id": 1, "name": "知识 - 中国首都", "category": "地理", "difficulty": "简单", "prompt": "中国的首都是哪里？", "expected_keywords": ["北京"], "weight": 1},
        {"id": 2, "name": "知识 - 四大发明", "category": "历史", "difficulty": "简单", "prompt": "中国古代四大发明是什么？", "expected_keywords": ["造纸", "印刷", "火药", "指南针"], "weight": 2},
        {"id": 3, "name": "知识 - 光速", "category": "物理", "difficulty": "中等", "prompt": "光在真空中的速度大约是多少？", "expected_keywords": ["3亿", "300000000", "3×10^8"], "weight": 2},
        {"id": 4, "name": "知识 - 人体器官", "category": "生物", "difficulty": "简单", "prompt": "人体最大的器官是什么？", "expected_keywords": ["皮肤"], "weight": 1},
        {"id": 5, "name": "知识 - 水化学式", "category": "化学", "difficulty": "简单", "prompt": "水的化学式是什么？", "expected_keywords": ["H2O", "H₂O"], "weight": 1},
        {"id": 6, "name": "知识 - 太阳系最大行星", "category": "天文", "difficulty": "简单", "prompt": "太阳系中体积最大的行星是哪颗？", "expected_keywords": ["木星"], "weight": 1},
        {"id": 7, "name": "知识 - HTTP 协议", "category": "计算机", "difficulty": "中等", "prompt": "HTTP 和 HTTPS 的主要区别是什么？", "expected_keywords": ["安全", "加密", "SSL"], "weight": 2},
        {"id": 8, "name": "知识 - 通货膨胀", "category": "经济", "difficulty": "中等", "prompt": "请解释什么是通货膨胀", "expected_keywords": ["物价", "上涨", "货币"], "weight": 2},
        {"id": 9, "name": "知识 - 宪法", "category": "法律", "difficulty": "简单", "prompt": "宪法是一国的什么法？", "expected_keywords": ["根本", "最高", "基本"], "weight": 1},
        {"id": 10, "name": "知识 - 光合作用", "category": "生物", "difficulty": "中等", "prompt": "光合作用的主要产物是什么？", "expected_keywords": ["氧气", "葡萄糖"], "weight": 2},
        {"id": 11, "name": "知识 - 长江长度", "category": "地理", "difficulty": "中等", "prompt": "中国最长的河流是哪条？长度大约多少？", "expected_keywords": ["长江", "6300"], "weight": 2},
        {"id": 12, "name": "知识 - 红楼梦作者", "category": "文学", "difficulty": "简单", "prompt": "《红楼梦》的作者是谁？", "expected_keywords": ["曹雪芹"], "weight": 1},
        {"id": 13, "name": "知识 - DNA 结构", "category": "生物", "difficulty": "中等", "prompt": "DNA 的结构是什么形状？", "expected_keywords": ["双螺旋"], "weight": 2},
        {"id": 14, "name": "知识 - 相对论", "category": "物理", "difficulty": "中等", "prompt": "谁提出了相对论？", "expected_keywords": ["爱因斯坦"], "weight": 1},
        {"id": 15, "name": "知识 - 元素周期表", "category": "化学", "difficulty": "中等", "prompt": "元素周期表中第一号元素是什么？", "expected_keywords": ["氢", "H"], "weight": 1},
        {"id": 16, "name": "知识 - 二战时间", "category": "历史", "difficulty": "中等", "prompt": "第二次世界大战爆发的年份是？", "expected_keywords": ["1939"], "weight": 1},
        {"id": 17, "name": "知识 - 世界杯", "category": "体育", "difficulty": "简单", "prompt": "足球世界杯几年举办一次？", "expected_keywords": ["4"], "weight": 1},
        {"id": 18, "name": "知识 - 珠穆朗玛峰", "category": "地理", "difficulty": "简单", "prompt": "世界最高峰珠穆朗玛峰的海拔高度大约是多少？", "expected_keywords": ["8848", "8849"], "weight": 1},
        {"id": 19, "name": "知识 - 牛顿定律", "category": "物理", "difficulty": "中等", "prompt": "牛顿第一定律又被称为什么？", "expected_keywords": ["惯性"], "weight": 2},
        {"id": 20, "name": "知识 - 人工智能", "category": "计算机", "difficulty": "中等", "prompt": "什么是图灵测试？", "expected_keywords": ["机器", "智能", "人"], "weight": 2},
    ],
    "commonsense": [
        {"id": 1, "name": "常识 - 水的沸点", "category": "物理", "difficulty": "简单", "prompt": "在标准大气压下，水的沸点是多少摄氏度？", "expected_keywords": ["100"], "weight": 1},
        {"id": 2, "name": "常识 - 一周几天", "category": "生活", "difficulty": "简单", "prompt": "一周有多少天？", "expected_keywords": ["7", "七"], "weight": 1},
        {"id": 3, "name": "常识 - 国旗颜色", "category": "地理", "difficulty": "简单", "prompt": "中国国旗是什么颜色？", "expected_keywords": ["红", "黄"], "weight": 1},
        {"id": 4, "name": "常识 - 火警电话", "category": "生活", "difficulty": "简单", "prompt": "中国的火警电话号码是多少？", "expected_keywords": ["119"], "weight": 1},
        {"id": 5, "name": "常识 - 一天几小时", "category": "生活", "difficulty": "简单", "prompt": "一天有多少小时？", "expected_keywords": ["24"], "weight": 1},
        {"id": 6, "name": "常识 - 水的密度", "category": "物理", "difficulty": "中等", "prompt": "水的密度大约是多少克/立方厘米？", "expected_keywords": ["1"], "weight": 1},
        {"id": 7, "name": "常识 - 哺乳动物", "category": "生物", "difficulty": "简单", "prompt": "鲸鱼是哺乳动物吗？", "expected_keywords": ["是"], "weight": 1},
        {"id": 8, "name": "常识 - 地球自转", "category": "地理", "difficulty": "简单", "prompt": "地球自转一圈需要多长时间？", "expected_keywords": ["一天", "24 小时"], "weight": 1},
        {"id": 9, "name": "常识 - 金属导电", "category": "物理", "difficulty": "简单", "prompt": "金属能导电吗？", "expected_keywords": ["能", "可以"], "weight": 1},
        {"id": 10, "name": "常识 - 植物光合作用", "category": "生物", "difficulty": "简单", "prompt": "植物在阳光下会进行什么作用产生氧气？", "expected_keywords": ["光合"], "weight": 1},
        {"id": 11, "name": "常识 - 急救电话", "category": "生活", "difficulty": "简单", "prompt": "中国的医疗急救电话号码是多少？", "expected_keywords": ["120"], "weight": 1},
        {"id": 12, "name": "常识 - 人体体温", "category": "生物", "difficulty": "简单", "prompt": "人的正常体温大约是多少摄氏度？", "expected_keywords": ["36", "37"], "weight": 1},
        {"id": 13, "name": "常识 - 闰年", "category": "生活", "difficulty": "中等", "prompt": "闰年有多少天？", "expected_keywords": ["366"], "weight": 1},
        {"id": 14, "name": "常识 - 交通信号", "category": "生活", "difficulty": "简单", "prompt": "红灯表示什么意思？", "expected_keywords": ["停", "禁止"], "weight": 1},
        {"id": 15, "name": "常识 - 大气成分", "category": "化学", "difficulty": "中等", "prompt": "空气中含量最多的气体是什么？", "expected_keywords": ["氮", "N2"], "weight": 2},
        {"id": 16, "name": "常识 - 地震逃生", "category": "安全", "difficulty": "中等", "prompt": "地震发生时，在室内应该躲在哪里比较安全？", "expected_keywords": ["桌子", "墙角"], "weight": 2},
        {"id": 17, "name": "常识 - 灭火器", "category": "安全", "difficulty": "中等", "prompt": "使用灭火器时应该对准火焰的哪个部位喷射？", "expected_keywords": ["根部", "底部"], "weight": 2},
        {"id": 18, "name": "常识 - 食物中毒", "category": "健康", "difficulty": "中等", "prompt": "发现食物中毒后应该怎么做？", "expected_keywords": ["医院", "就医", "催吐"], "weight": 2},
        {"id": 19, "name": "常识 - 溺水急救", "category": "安全", "difficulty": "中等", "prompt": "发现有人溺水，首先应该做什么？", "expected_keywords": ["呼救", "报警", "110"], "weight": 2},
        {"id": 20, "name": "常识 - 触电急救", "category": "安全", "difficulty": "中等", "prompt": "发现有人触电，首先应该做什么？", "expected_keywords": ["断电", "电源"], "weight": 2},
    ],
}


def call_model(prompt: str, max_tokens: int = 512) -> Dict:
    """调用模型 API"""
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "top_p": 0.9,
    }
    try:
        resp = requests.post(BASE_URL, json=payload, timeout=TIMEOUT)
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}"}
        data = resp.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        return {
            "success": True,
            "content": content,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_response(content: str, expected_keywords: List[str]) -> bool:
    """检查响应是否包含预期关键词"""
    if not content:
        return False
    content_lower = content.lower()
    matched = sum(1 for kw in expected_keywords if kw.lower() in content_lower)
    return matched >= max(1, len(expected_keywords) // 2)


def run_test_case(test_case: Dict) -> Dict:
    """运行单个测试用例"""
    start_time = time.time()
    result = call_model(test_case["prompt"], max_tokens=512)
    duration = (time.time() - start_time) * 1000  # ms

    if not result["success"]:
        return {
            "passed": False,
            "error": result["error"],
            "content": "",
            "duration_ms": duration,
            "weight": test_case["weight"],
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    passed = check_response(result["content"], test_case["expected_keywords"])
    return {
        "passed": passed,
        "content": result["content"][:300],
        "duration_ms": duration,
        "weight": test_case["weight"],
        "prompt_tokens": result.get("prompt_tokens", 0),
        "completion_tokens": result.get("completion_tokens", 0),
    }


def test_category(category_name: str, test_cases: List[Dict]) -> tuple:
    """测试一个类别"""
    print(f"\n{'='*60}")
    print(f"📚 {category_name}")
    print(f"{'='*60}")

    results = []
    total_weight = 0
    passed_weight = 0
    total_duration = 0
    total_tokens = 0

    for test in test_cases:
        print(f"  📝 {test['name']}...", end=" ", flush=True)
        result = run_test_case(test)
        results.append({"name": test["name"], "category": test.get("category", ""), "difficulty": test.get("difficulty", ""), **result})

        total_weight += test["weight"]
        if result["passed"]:
            passed_weight += test["weight"]

        total_duration += result["duration_ms"]
        total_tokens += result.get("completion_tokens", 0)

        status = "✅" if result["passed"] else "❌"
        print(f"{status}")

    score = (passed_weight / total_weight * 100) if total_weight > 0 else 0
    avg_duration = total_duration / len(test_cases) if test_cases else 0
    tokens_per_sec = (total_tokens / (total_duration / 1000)) if total_duration > 0 else 0

    return results, score, passed_weight, total_weight, avg_duration, tokens_per_sec


def generate_report(model_name: str, results_summary: Dict, output_dir: str):
    """生成详细报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)

    # JSON 结果
    json_file = os.path.join(output_dir, f"{model_name}_stage3_raw.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)

    # Markdown 报告
    md_file = os.path.join(output_dir, f"{model_name}_stage3_report.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# JoyAI-LLM-Flash Stage 3 深度能力评估报告\n\n")
        f.write(f"> **评测时间**: {timestamp}\n")
        f.write(f"> **模型名称**: {model_name}\n")
        f.write(f"> **评测服务**: {BASE_URL}\n")
        f.write(f"> **测试框架**: llama.cpp Stage 3 评估框架 (精选版)\n\n")
        f.write("---\n\n")

        # 总览
        f.write("## 📊 评估概览\n\n")
        total_cases = sum(len(cases) for cases in STAGE3_TEST_CASES.values())
        f.write(f"**总测试用例**: {total_cases}\n")
        f.write(f"**测试维度**: {len(STAGE3_TEST_CASES)} 个\n\n")

        # 计算综合得分
        overall_score = 0
        for cat_data in results_summary["categories"].values():
            overall_score += cat_data["score"]
        overall_score /= len(results_summary["categories"])

        final_status = "✅ 优秀" if overall_score >= 80 else "✅ 良好" if overall_score >= 70 else "⚠️ 及格" if overall_score >= 60 else "❌ 需改进"

        f.write(f"| 指标 | 数值 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 综合得分 | **{overall_score:.1f}%** |\n")
        f.write(f"| 评级 | {final_status} |\n")
        f.write(f"| 平均响应时间 | {results_summary['avg_response_ms']:.0f} ms |\n")
        f.write(f"| 生成速度 | {results_summary['tokens_per_sec']:.1f} tokens/s |\n\n")

        # 分项得分
        f.write("## 📈 分项能力\n\n")
        f.write("| 维度 | 得分 | 测试数 | 状态 |\n")
        f.write("|------|------|--------|------|\n")

        sorted_cats = sorted(results_summary["categories"].items(), key=lambda x: x[1]["score"], reverse=True)
        for cat_name, cat_data in sorted_cats:
            status = "✅" if cat_data["score"] >= 70 else "⚠️" if cat_data["score"] >= 50 else "❌"
            f.write(f"| {cat_data['display_name']} | {cat_data['score']:.1f}% | {cat_data['total_cases']} | {status} |\n")

        # 详细结果
        f.write("\n---\n\n")
        f.write("## 📋 详细测试结果\n\n")

        for cat_key, cat_data in results_summary["categories"].items():
            f.write(f"### {cat_data['display_name']} (得分：{cat_data['score']:.1f}%)\n\n")
            f.write("| 测试项 | 难度 | 结果 | 响应时间 |\n")
            f.write("|--------|------|------|----------|\n")
            for case in cat_data["cases"]:
                status = "✅" if case["passed"] else "❌"
                difficulty = case.get("difficulty", "")
                duration = f"{case.get('duration_ms', 0):.0f}ms"
                f.write(f"| {case['name']} | {difficulty} | {status} | {duration} |\n")
            f.write(f"\n**平均响应时间**: {cat_data['avg_duration_ms']:.0f}ms\n\n")

        # 能力雷达图数据
        f.write("\n---\n\n")
        f.write("## 🎯 能力雷达图数据\n\n")
        f.write("```json\n")
        radar_data = {cat_data['display_name']: round(cat_data['score']/100, 2) for cat_data in results_summary["categories"].values()}
        f.write(json.dumps(radar_data, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")

        # 结论
        f.write("---\n\n")
        f.write("## 💡 评估结论\n\n")

        # 强项和弱项
        strongest = sorted_cats[0]
        weakest = sorted_cats[-1]

        f.write(f"**最强维度**: {strongest[1]['display_name']} ({strongest[1]['score']:.1f}%)\n\n")
        f.write(f"**最弱维度**: {weakest[1]['display_name']} ({weakest[1]['score']:.1f}%)\n\n")

        if overall_score >= 80:
            f.write("**综合评价**: 模型在 Stage 3 深度能力测试中表现优秀，各维度均衡发展，具备较强的综合应用能力。\n\n")
        elif overall_score >= 70:
            f.write("**综合评价**: 模型综合能力良好，大部分维度表现稳定，部分维度有提升空间。\n\n")
        elif overall_score >= 60:
            f.write("**综合评价**: 模型综合能力达到及格水平，建议在薄弱维度进行针对性优化。\n\n")
        else:
            f.write("**综合评价**: 模型综合能力有待提升，建议针对各维度进行系统性改进。\n\n")

        f.write("---\n\n")
        f.write(f"*报告生成时间：{timestamp}*\n")

    return md_file, json_file


def run_stage3_evaluation():
    """运行 Stage 3 评估"""
    model_name = MODEL_NAME.replace(".gguf", "").replace("-", "_")
    output_dir = OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 80)
    print(f"🧪 JoyAI-LLM-Flash Stage 3 深度能力评估")
    print("=" * 80)
    print(f"模型：{MODEL_NAME}")
    print(f"评测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    results_summary = {
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
        "categories": {},
        "avg_response_ms": 0,
        "tokens_per_sec": 0,
    }

    category_names = {
        "math_reasoning": "数学推理",
        "logic_reasoning": "逻辑推理",
        "code_generation": "代码生成",
        "knowledge_qa": "知识问答",
        "commonsense": "常识判断",
    }

    total_duration = 0
    total_tokens = 0
    total_cases = 0

    # 运行各维度测试
    for category_key, test_cases in STAGE3_TEST_CASES.items():
        cases, score, passed_w, total_w, avg_duration, tokens_per_sec = test_category(
            category_names[category_key], test_cases
        )
        results_summary["categories"][category_key] = {
            "display_name": category_names[category_key],
            "cases": cases,
            "score": score,
            "passed_weight": passed_w,
            "total_weight": total_w,
            "total_cases": len(test_cases),
            "avg_duration_ms": avg_duration,
        }

        total_duration += avg_duration * len(test_cases)
        total_tokens += tokens_per_sec * len(test_cases) * (avg_duration / 1000)
        total_cases += len(test_cases)

    results_summary["avg_response_ms"] = total_duration / total_cases if total_cases > 0 else 0
    results_summary["tokens_per_sec"] = total_tokens / (total_duration / 1000) if total_duration > 0 else 0

    # 生成报告
    md_file, json_file = generate_report(model_name, results_summary, output_dir)

    # 打印汇总
    print("\n" + "=" * 80)
    print("📊 评估汇总")
    print("=" * 80)

    for cat_key, cat_data in results_summary["categories"].items():
        status = "✅" if cat_data["score"] >= 70 else "⚠️" if cat_data["score"] >= 50 else "❌"
        print(f"  {status} {cat_data['display_name']}: {cat_data['score']:.1f}%")

    overall = sum(d["score"] for d in results_summary["categories"].values()) / len(results_summary["categories"])
    final_status = "✅ 优秀" if overall >= 80 else "✅ 良好" if overall >= 70 else "⚠️ 及格" if overall >= 60 else "❌ 需改进"
    print(f"\n  📈 综合得分：{overall:.1f}% - {final_status}")
    print(f"  ⏱️ 平均响应：{results_summary['avg_response_ms']:.0f}ms")
    print(f"  ⚡ 生成速度：{results_summary['tokens_per_sec']:.1f} tokens/s")
    print(f"\n  📄 Markdown 报告：{md_file}")
    print(f"  💾 JSON 数据：{json_file}")

    return results_summary


if __name__ == "__main__":
    run_stage3_evaluation()
