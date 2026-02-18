#!/usr/bin/env python3
"""
Stage 3 多轮对话测试 (100 cases)
涵盖：上下文记忆、指代消解、对话连贯性、意图跟踪、角色一致性等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 多轮对话测试用例 (100个)
MULTITURN_TEST_CASES = [
    # ===== 上下文记忆 (25题) =====
    {"id": 1, "name": "简单记忆-1", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我叫张三。"},
         {"role": "assistant", "content": "你好张三，很高兴认识你。"},
         {"role": "user", "content": "我叫什么名字？"}
     ],
     "expected_keywords": ["张三"], "check_type": "contains"},
    {"id": 2, "name": "数字记忆", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我的密码是123456。"},
         {"role": "assistant", "content": "好的，我记住了。"},
         {"role": "user", "content": "我的密码是什么？"}
     ],
     "expected_keywords": ["123456"], "check_type": "contains"},
    {"id": 3, "name": "多信息记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我今年25岁，住在北京。"},
         {"role": "assistant", "content": "好的，知道了。"},
         {"role": "user", "content": "我住在哪里？"}
     ],
     "expected_keywords": ["北京"], "check_type": "contains"},
    {"id": 4, "name": "跨轮记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我喜欢吃苹果。"},
         {"role": "assistant", "content": "苹果很健康。"},
         {"role": "user", "content": "今天天气不错。"},
         {"role": "assistant", "content": "是的，适合出门。"},
         {"role": "user", "content": "我喜欢吃什么？"}
     ],
     "expected_keywords": ["苹果"], "check_type": "contains"},
    {"id": 5, "name": "长距离记忆", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我的生日是1999年5月1日。"},
         {"role": "assistant", "content": "记住了。"},
         {"role": "user", "content": "谈谈人工智能的发展。"},
         {"role": "assistant", "content": "人工智能发展迅速..."},
         {"role": "user", "content": "再聊聊太空探索。"},
         {"role": "assistant", "content": "太空探索令人兴奋..."},
         {"role": "user", "content": "我的生日是什么时候？"}
     ],
     "expected_keywords": ["1999", "5月1日"], "check_type": "contains_any"},
    {"id": 6, "name": "列表记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要买：牛奶、鸡蛋、面包。"},
         {"role": "assistant", "content": "好的，购物清单已记录。"},
         {"role": "user", "content": "我要买什么？"}
     ],
     "expected_keywords": ["牛奶", "鸡蛋", "面包"], "check_type": "contains_any"},
    {"id": 7, "name": "否定记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我不喜欢吃辣的。"},
         {"role": "assistant", "content": "知道了。"},
         {"role": "user", "content": "我喜欢吃辣的吗？"}
     ],
     "expected_keywords": ["不", "不喜欢"], "check_type": "contains"},
    {"id": 8, "name": "更新记忆", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我的手机号是13800138000。"},
         {"role": "assistant", "content": "已记录。"},
         {"role": "user", "content": "我换号了，新号是13900139000。"},
         {"role": "assistant", "content": "已更新。"},
         {"role": "user", "content": "我现在的手机号是多少？"}
     ],
     "expected_keywords": ["13900139000"], "check_type": "contains"},
    {"id": 9, "name": "偏好记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我最喜欢的颜色是蓝色。"},
         {"role": "assistant", "content": "蓝色很清新。"},
         {"role": "user", "content": "推荐一个颜色给我。"}
     ],
     "expected_keywords": ["蓝"], "check_type": "contains"},
    {"id": 10, "name": "时间记忆", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我明天下午3点有个会议。"},
         {"role": "assistant", "content": "好的，已记录。"},
         {"role": "user", "content": "我明天几点有会议？"}
     ],
     "expected_keywords": ["3点", "15点"], "check_type": "contains_any"},
    {"id": 11, "name": "地点记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要去上海出差三天。"},
         {"role": "assistant", "content": "好的。"},
         {"role": "user", "content": "我要去哪里出差？"}
     ],
     "expected_keywords": ["上海"], "check_type": "contains"},
    {"id": 12, "name": "任务记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "请提醒我明天交报告。"},
         {"role": "assistant", "content": "好的，明天交报告。"},
         {"role": "user", "content": "我明天要做什么？"}
     ],
     "expected_keywords": ["报告"], "check_type": "contains"},
    {"id": 13, "name": "人物关系", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我哥哥叫李明。"},
         {"role": "assistant", "content": "好的。"},
         {"role": "user", "content": "我哥哥叫什么名字？"}
     ],
     "expected_keywords": ["李明"], "check_type": "contains"},
    {"id": 14, "name": "数值计算记忆", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我第一个月存了1000元，第二个月存了2000元。"},
         {"role": "assistant", "content": "存了不少。"},
         {"role": "user", "content": "我两个月共存了多少钱？"}
     ],
     "expected_keywords": ["3000"], "check_type": "contains"},
    {"id": 15, "name": "计划记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "周末计划：周六去爬山，周日在家休息。"},
         {"role": "assistant", "content": "安排不错。"},
         {"role": "user", "content": "我周六要去干什么？"}
     ],
     "expected_keywords": ["爬山"], "check_type": "contains"},
    {"id": 16, "name": "情绪记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我今天心情很好。"},
         {"role": "assistant", "content": "太好了！"},
         {"role": "user", "content": "我今天心情怎么样？"}
     ],
     "expected_keywords": ["好"], "check_type": "contains"},
    {"id": 17, "name": "属性记忆", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我的车是红色的。"},
         {"role": "assistant", "content": "红色很亮眼。"},
         {"role": "user", "content": "我的车是什么颜色的？"}
     ],
     "expected_keywords": ["红"], "check_type": "contains"},
    {"id": 18, "name": "多对象记忆", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "小张喜欢篮球，小李喜欢足球。"},
         {"role": "assistant", "content": "好的。"},
         {"role": "user", "content": "小李喜欢什么运动？"}
     ],
     "expected_keywords": ["足球"], "check_type": "contains"},
    {"id": 19, "name": "条件记忆", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "如果明天下雨，我就不去跑步。"},
         {"role": "assistant", "content": "好的。"},
         {"role": "user", "content": "什么情况下我不去跑步？"}
     ],
     "expected_keywords": ["下雨"], "check_type": "contains"},
    {"id": 20, "name": "顺序记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我早上先刷牙，再吃早饭。"},
         {"role": "assistant", "content": "好习惯。"},
         {"role": "user", "content": "我早上先做什么？"}
     ],
     "expected_keywords": ["刷牙"], "check_type": "contains"},
    {"id": 21, "name": "价格记忆", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "这本书我花了50元买的。"},
         {"role": "assistant", "content": "好的。"},
         {"role": "user", "content": "这本书多少钱？"}
     ],
     "expected_keywords": ["50"], "check_type": "contains"},
    {"id": 22, "name": "公司记忆", "category": "上下文记忆", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我在华为工作。"},
         {"role": "assistant", "content": "华为是不错的公司。"},
         {"role": "user", "content": "我在哪家公司工作？"}
     ],
     "expected_keywords": ["华为"], "check_type": "contains"},
    {"id": 23, "name": "目标记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我的目标是学会弹吉他。"},
         {"role": "assistant", "content": "很酷的目标！"},
         {"role": "user", "content": "我的目标是什么？"}
     ],
     "expected_keywords": ["吉他"], "check_type": "contains"},
    {"id": 24, "name": "多轮计数", "category": "上下文记忆", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我有三只猫。"},
         {"role": "assistant", "content": "好多猫。"},
         {"role": "user", "content": "又领养了一只。"},
         {"role": "assistant", "content": "现在有4只了。"},
         {"role": "user", "content": "我现在有几只猫？"}
     ],
     "expected_keywords": ["4", "四"], "check_type": "contains_any"},
    {"id": 25, "name": "限制记忆", "category": "上下文记忆", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我对花生过敏。"},
         {"role": "assistant", "content": "记住了。"},
         {"role": "user", "content": "我能吃花生吗？"}
     ],
     "expected_keywords": ["不能", "过敏", "不"], "check_type": "contains_any"},

    # ===== 指代消解 (20题) =====
    {"id": 26, "name": "人称指代-1", "category": "指代消解", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "小明去了商店。他买了牛奶。"},
         {"role": "assistant", "content": "小明买了牛奶。"},
         {"role": "user", "content": "谁买了牛奶？"}
     ],
     "expected_keywords": ["小明"], "check_type": "contains"},
    {"id": 27, "name": "物主指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "小红的手机坏了，她想去修。"},
         {"role": "assistant", "content": "小红该修手机了。"},
         {"role": "user", "content": "谁的手机坏了？"}
     ],
     "expected_keywords": ["小红"], "check_type": "contains"},
    {"id": 28, "name": "地点指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我去过巴黎，那里很美。"},
         {"role": "assistant", "content": "巴黎确实很浪漫。"},
         {"role": "user", "content": "哪里很美？"}
     ],
     "expected_keywords": ["巴黎"], "check_type": "contains"},
    {"id": 29, "name": "多代词消解", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "张三把书给了李四，他觉得很有趣。"},
         {"role": "assistant", "content": "谁觉得有趣？"},
         {"role": "user", "content": "谁觉得书有趣？"}
     ],
     "expected_keywords": ["张三", "他"], "check_type": "contains_any"},
    {"id": 30, "name": "指示代词", "category": "指代消解", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我喜欢苹果和香蕉，但这个更甜。"},
         {"role": "assistant", "content": "香蕉更甜吗？"},
         {"role": "user", "content": "什么更甜？"}
     ],
     "expected_keywords": ["香蕉"], "check_type": "contains"},
    {"id": 31, "name": "交叉指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "小王告诉小李他的计划。"},
         {"role": "assistant", "content": "需要澄清是谁的计划。"},
         {"role": "user", "content": "如果'他'指小王，那是谁的计划？"}
     ],
     "expected_keywords": ["小王"], "check_type": "contains"},
    {"id": 32, "name": "时间指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我昨天去了医院，那天人很多。"},
         {"role": "assistant", "content": "医院总是人多。"},
         {"role": "user", "content": "哪天人多？"}
     ],
     "expected_keywords": ["昨天"], "check_type": "contains"},
    {"id": 33, "name": "省略主语", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "小明喜欢吃苹果，(他)每天买一个。"},
         {"role": "assistant", "content": "小明每天买苹果。"},
         {"role": "user", "content": "谁每天买苹果？"}
     ],
     "expected_keywords": ["小明"], "check_type": "contains"},
    {"id": 34, "name": "复数指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "学生们考试了，他们都考得很好。"},
         {"role": "assistant", "content": "恭喜学生们。"},
         {"role": "user", "content": "谁考得很好？"}
     ],
     "expected_keywords": ["学生"], "check_type": "contains"},
    {"id": 35, "name": "远端指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我有一个苹果和一个香蕉，香蕉黄了，它坏了。"},
         {"role": "assistant", "content": "香蕉坏了。"},
         {"role": "user", "content": "什么坏了？"}
     ],
     "expected_keywords": ["香蕉"], "check_type": "contains"},
    {"id": 36, "name": "模糊指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我把书放在桌子上，它倒了。"},
         {"role": "assistant", "content": "什么倒了？"},
         {"role": "user", "content": "如果是指书倒了，那'它'指什么？"}
     ],
     "expected_keywords": ["书"], "check_type": "contains"},
    {"id": 37, "name": "事件指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "他考试失败了，这件事让他很沮丧。"},
         {"role": "assistant", "content": "考试失败确实让人沮丧。"},
         {"role": "user", "content": "什么事让他沮丧？"}
     ],
     "expected_keywords": ["考试失败"], "check_type": "contains"},
    {"id": 38, "name": "概念指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "环保很重要，这需要每个人参与。"},
         {"role": "assistant", "content": "是的，环保需要共同努力。"},
         {"role": "user", "content": "什么需要每个人参与？"}
     ],
     "expected_keywords": ["环保"], "check_type": "contains"},
    {"id": 39, "name": "链式指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "张三有个弟弟，他比我高，他很开朗。"},
         {"role": "assistant", "content": "需要澄清指代。"},
         {"role": "user", "content": "'他很开朗'中的'他'可能指谁？(选最可能的)"}
     ],
     "expected_keywords": ["弟弟", "张三"], "check_type": "contains_any"},
    {"id": 40, "name": "对比指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "苹果5元，香蕉3元，前者更贵。"},
         {"role": "assistant", "content": "苹果确实更贵。"},
         {"role": "user", "content": "什么更贵？"}
     ],
     "expected_keywords": ["苹果"], "check_type": "contains"},
    {"id": 41, "name": "品牌指代", "category": "指代消解", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我买了iPhone，它很好用。"},
         {"role": "assistant", "content": "iPhone体验不错。"},
         {"role": "user", "content": "什么很好用？"}
     ],
     "expected_keywords": ["iPhone"], "check_type": "contains"},
    {"id": 42, "name": "动物指代", "category": "指代消解", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我家有只猫，它很可爱。"},
         {"role": "assistant", "content": "猫咪确实很可爱。"},
         {"role": "user", "content": "什么很可爱？"}
     ],
     "expected_keywords": ["猫"], "check_type": "contains"},
    {"id": 43, "name": "组织指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "联合国发表声明，它谴责了暴力行为。"},
         {"role": "assistant", "content": "联合国谴责暴力。"},
         {"role": "user", "content": "谁谴责了暴力？"}
     ],
     "expected_keywords": ["联合国"], "check_type": "contains"},
    {"id": 44, "name": "作品指代", "category": "指代消解", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "《红楼梦》是经典，它影响深远。"},
         {"role": "assistant", "content": "《红楼梦》确实伟大。"},
         {"role": "user", "content": "什么影响深远？"}
     ],
     "expected_keywords": ["红楼梦"], "check_type": "contains"},
    {"id": 45, "name": "抽象指代", "category": "指代消解", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "他犯了错误，这让他失去了信任。"},
         {"role": "assistant", "content": "错误确实会影响信任。"},
         {"role": "user", "content": "什么让他失去了信任？"}
     ],
     "expected_keywords": ["错误"], "check_type": "contains"},

    # ===== 对话连贯性 (20题) =====
    {"id": 46, "name": "话题延续-1", "category": "对话连贯性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我想去日本旅游。"},
         {"role": "assistant", "content": "日本是个好地方，有什么想去的地方吗？"},
         {"role": "user", "content": "推荐一下景点。"}
     ],
     "expected_keywords": ["日本"], "check_type": "contains"},
    {"id": 47, "name": "话题转换", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "今天天气真好。"},
         {"role": "assistant", "content": "是啊，适合出门。"},
         {"role": "user", "content": "对了，你知道怎么学英语吗？"}
     ],
     "expected_keywords": ["英语", "学习", "方法"], "check_type": "contains_any"},
    {"id": 48, "name": "追问澄清", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "帮我订个餐厅。"},
         {"role": "assistant", "content": "好的，需要什么类型的餐厅？"},
         {"role": "user", "content": "中餐。"}
     ],
     "expected_keywords": ["中餐", "中餐馆"], "check_type": "contains_any"},
    {"id": 49, "name": "确认理解", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我明天去北京。"},
         {"role": "assistant", "content": "明天去北京，是出差还是旅游？"},
         {"role": "user", "content": "出差。"}
     ],
     "expected_keywords": ["出差"], "check_type": "contains"},
    {"id": 50, "name": "补充信息", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我想买手机。"},
         {"role": "assistant", "content": "需要什么价位的？"},
         {"role": "user", "content": "3000左右，拍照好的。"}
     ],
     "expected_keywords": ["3000", "拍照"], "check_type": "contains_any"},
    {"id": 51, "name": "纠正误解", "category": "对话连贯性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我不喜欢苹果。"},
         {"role": "assistant", "content": "不喜欢苹果手机？"},
         {"role": "user", "content": "不，我说的是水果。"}
     ],
     "expected_keywords": ["水果", "苹果"], "check_type": "contains_any"},
    {"id": 52, "name": "同意表达", "category": "对话连贯性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "这部电影很好看。"},
         {"role": "assistant", "content": "我也觉得不错。"},
         {"role": "user", "content": "是吧！"}
     ],
     "expected_keywords": ["好看", "不错", "好"], "check_type": "contains_any"},
    {"id": 53, "name": "反对表达", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我觉得这道菜太咸了。"},
         {"role": "assistant", "content": "我觉得刚好。"},
         {"role": "user", "content": "可能我口味淡。"}
     ],
     "expected_keywords": ["口味", "淡"], "check_type": "contains_any"},
    {"id": 54, "name": "建议回应", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我失眠了怎么办？"},
         {"role": "assistant", "content": "可以试试睡前喝牛奶。"},
         {"role": "user", "content": "还有其他方法吗？"}
     ],
     "expected_keywords": ["运动", "音乐", "放松", "冥想"], "check_type": "contains_any"},
    {"id": 55, "name": "多轮澄清", "category": "对话连贯性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "帮我找个地方。"},
         {"role": "assistant", "content": "什么类型的？"},
         {"role": "user", "content": "吃饭的地方。"},
         {"role": "assistant", "content": "中餐还是西餐？"},
         {"role": "user", "content": "中餐。"}
     ],
     "expected_keywords": ["中餐", "餐厅", "饭馆"], "check_type": "contains_any"},
    {"id": 56, "name": "背景假设", "category": "对话连贯性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我昨天去的那家店关门了。"},
         {"role": "assistant", "content": "哪家店？"},
         {"role": "user", "content": "就是那家很好吃的火锅店。"}
     ],
     "expected_keywords": ["火锅"], "check_type": "contains"},
    {"id": 57, "name": "情感连贯", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我今天被老板批评了。"},
         {"role": "assistant", "content": "别难过，发生什么事了？"},
         {"role": "user", "content": "工作上出了点错。"}
     ],
     "expected_keywords": ["工作", "错", "问题"], "check_type": "contains_any"},
    {"id": 58, "name": "目标推进", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我想减肥。"},
         {"role": "assistant", "content": "可以通过运动和饮食控制。"},
         {"role": "user", "content": "具体有什么运动推荐？"}
     ],
     "expected_keywords": ["跑步", "游泳", "健身", "有氧"], "check_type": "contains_any"},
    {"id": 59, "name": "总结确认", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要买蓝色的、大号的T恤。"},
         {"role": "assistant", "content": "好的，蓝色大号T恤。"},
         {"role": "user", "content": "对，多少钱？"}
     ],
     "expected_keywords": ["钱", "价格", "元"], "check_type": "contains_any"},
    {"id": 60, "name": "打断恢复", "category": "对话连贯性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我问一下，你刚才说的那个..."},
         {"role": "assistant", "content": "关于什么的？"},
         {"role": "user", "content": "就是那个打折的活动。"}
     ],
     "expected_keywords": ["打折", "活动", "优惠"], "check_type": "contains_any"},
    {"id": 61, "name": "间接回答", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你觉得这个方案怎么样？"},
         {"role": "assistant", "content": "有创意，但成本可能有点高。"},
         {"role": "user", "content": "那你的建议是？"}
     ],
     "expected_keywords": ["成本", "预算", "优化", "调整"], "check_type": "contains_any"},
    {"id": 62, "name": "礼貌回应", "category": "对话连贯性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "谢谢你的帮助。"},
         {"role": "assistant", "content": "不客气！"},
         {"role": "user", "content": "有问题再找你。"}
     ],
     "expected_keywords": ["随时", "欢迎", "没问题"], "check_type": "contains_any"},
    {"id": 63, "name": "拒绝处理", "category": "对话连贯性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你能帮我写论文吗？"},
         {"role": "assistant", "content": "我不能代写论文，但我可以帮你梳理论文结构。"},
         {"role": "user", "content": "那帮我看看大纲吧。"}
     ],
     "expected_keywords": ["大纲", "结构"], "check_type": "contains_any"},
    {"id": 64, "name": "等待响应", "category": "对话连贯性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "等一下，我查个资料。"},
         {"role": "assistant", "content": "好的，我等你。"},
         {"role": "user", "content": "好了，我们继续。"}
     ],
     "expected_keywords": ["继续", "好的"], "check_type": "contains_any"},
    {"id": 65, "name": "告别处理", "category": "对话连贯性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我先走了。"},
         {"role": "assistant", "content": "好的，再见！"},
         {"role": "user", "content": "再见！"}
     ],
     "expected_keywords": ["再见", "拜拜", "慢走"], "check_type": "contains_any"},

    # ===== 意图跟踪 (20题) =====
    {"id": 66, "name": "明确意图-1", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我要订机票。"},
         {"role": "assistant", "content": "好的，去哪里？"},
         {"role": "user", "content": "北京到上海。"}
     ],
     "expected_keywords": ["北京", "上海"], "check_type": "contains_any"},
    {"id": 67, "name": "隐含意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我饿了。"},
         {"role": "assistant", "content": "想吃点什么？"},
         {"role": "user", "content": "附近有什么？"}
     ],
     "expected_keywords": ["餐厅", "饭馆", "吃"], "check_type": "contains_any"},
    {"id": 68, "name": "意图转换", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "帮我查天气。"},
         {"role": "assistant", "content": "哪个城市？"},
         {"role": "user", "content": "算了，先帮我设个闹钟。"}
     ],
     "expected_keywords": ["闹钟", "提醒"], "check_type": "contains_any"},
    {"id": 69, "name": "复合意图", "category": "意图跟踪", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我要订酒店和租车。"},
         {"role": "assistant", "content": "好的，先处理酒店。去哪里？"},
         {"role": "user", "content": "三亚，顺便看看有什么景点。"}
     ],
     "expected_keywords": ["三亚", "景点"], "check_type": "contains_any"},
    {"id": 70, "name": "意图澄清", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "那个东西怎么用？"},
         {"role": "assistant", "content": "请问是什么东西？"},
         {"role": "user", "content": "就是新买的打印机。"}
     ],
     "expected_keywords": ["打印机"], "check_type": "contains"},
    {"id": 71, "name": "否定意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我不想参加会议。"},
         {"role": "assistant", "content": "为什么不想参加？"},
         {"role": "user", "content": "时间冲突了。"}
     ],
     "expected_keywords": ["时间", "冲突"], "check_type": "contains_any"},
    {"id": 72, "name": "查询意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "帮我查一下快递。"},
         {"role": "assistant", "content": "快递单号是多少？"},
         {"role": "user", "content": "SF123456789。"}
     ],
     "expected_keywords": ["查询", "跟踪", "物流"], "check_type": "contains_any"},
    {"id": 73, "name": "购买意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我想买双鞋。"},
         {"role": "assistant", "content": "需要什么款式？"},
         {"role": "user", "content": "运动鞋，43码。"}
     ],
     "expected_keywords": ["运动", "43"], "check_type": "contains_any"},
    {"id": 74, "name": "求助意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "我遇到问题了。"},
         {"role": "assistant", "content": "什么问题？"},
         {"role": "user", "content": "电脑开不了机。"}
     ],
     "expected_keywords": ["电脑", "开机"], "check_type": "contains_any"},
    {"id": 75, "name": "社交意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "最近怎么样？"},
         {"role": "assistant", "content": "我很好，你呢？"},
         {"role": "user", "content": "还不错，就是工作忙。"}
     ],
     "expected_keywords": ["工作", "忙"], "check_type": "contains_any"},
    {"id": 76, "name": "比较意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "iPhone和华为哪个好？"},
         {"role": "assistant", "content": "各有优势，您更看重什么？"},
         {"role": "user", "content": "拍照和续航。"}
     ],
     "expected_keywords": ["拍照", "续航", "电池"], "check_type": "contains_any"},
    {"id": 77, "name": "学习意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我想学Python。"},
         {"role": "assistant", "content": "有编程基础吗？"},
         {"role": "user", "content": "没有，零基础。"}
     ],
     "expected_keywords": ["基础", "入门", "零基础"], "check_type": "contains_any"},
    {"id": 78, "name": "娱乐意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "推荐个电影看看。"},
         {"role": "assistant", "content": "喜欢什么类型？"},
         {"role": "user", "content": "科幻片。"}
     ],
     "expected_keywords": ["科幻"], "check_type": "contains"},
    {"id": 79, "name": "预约意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要预约医生。"},
         {"role": "assistant", "content": "什么科室？"},
         {"role": "user", "content": "内科，明天下午。"}
     ],
     "expected_keywords": ["内科", "明天"], "check_type": "contains_any"},
    {"id": 80, "name": "取消意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要取消刚才的订单。"},
         {"role": "assistant", "content": "好的，订单号是多少？"},
         {"role": "user", "content": "订单号是20240315001。"}
     ],
     "expected_keywords": ["取消", "订单"], "check_type": "contains_any"},
    {"id": 81, "name": "修改意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我要修改地址。"},
         {"role": "assistant", "content": "新地址是什么？"},
         {"role": "user", "content": "北京市海淀区。"}
     ],
     "expected_keywords": ["北京", "海淀"], "check_type": "contains_any"},
    {"id": 82, "name": "重复意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "再说一遍。"},
         {"role": "assistant", "content": "重复上一条回复。"},
         {"role": "user", "content": "刚才的没听清。"}
     ],
     "expected_keywords": ["重复", "再说"], "check_type": "contains_any"},
    {"id": 83, "name": "确认意图", "category": "意图跟踪", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "你确定吗？"},
         {"role": "assistant", "content": "确定。"},
         {"role": "user", "content": "那就这么定了。"}
     ],
     "expected_keywords": ["好", "定", "行"], "check_type": "contains_any"},
    {"id": 84, "name": "犹豫意图", "category": "意图跟踪", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "我在考虑要不要买。"},
         {"role": "assistant", "content": "有什么顾虑吗？"},
         {"role": "user", "content": "有点贵，还在犹豫。"}
     ],
     "expected_keywords": ["贵", "价格", "犹豫"], "check_type": "contains_any"},
    {"id": 85, "name": "紧急意图", "category": "意图跟踪", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "我急需帮助！"},
         {"role": "assistant", "content": "怎么了？请说。"},
         {"role": "user", "content": "锁在门外了。"}
     ],
     "expected_keywords": ["锁", "钥匙", "开门"], "check_type": "contains_any"},

    # ===== 角色一致性 (15题) =====
    {"id": 86, "name": "角色设定", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "从现在开始你是一位历史老师。"},
         {"role": "assistant", "content": "好的，我是您的历史老师。"},
         {"role": "user", "content": "你是谁？"}
     ],
     "expected_keywords": ["历史", "老师"], "check_type": "contains_any"},
    {"id": 87, "name": "语气保持", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "请用 Shakespeare 的语气说话。"},
         {"role": "assistant", "content": "Good morrow, fair friend!"},
         {"role": "user", "content": "今天天气如何？"}
     ],
     "expected_keywords": ["thee", "thou", "art", "hath", "doth"], "check_type": "contains_any"},
    {"id": 88, "name": "知识范围", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "你是一位 medieval 的骑士，知道什么是电脑吗？"},
         {"role": "assistant", "content": "电脑是什么？我从未听说过。"},
         {"role": "user", "content": "那你知道什么武器？"}
     ],
     "expected_keywords": ["剑", "盾", "矛", "弓箭"], "check_type": "contains_any"},
    {"id": 89, "name": "态度一致", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你要表现得非常礼貌。"},
         {"role": "assistant", "content": "好的，我会保持礼貌。"},
         {"role": "user", "content": "你觉得我错了吗？"}
     ],
     "expected_keywords": ["请", "您", "建议"], "check_type": "contains_any"},
    {"id": 90, "name": "专业角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你是一位医生，我头疼怎么办？"},
         {"role": "assistant", "content": "建议先休息，如持续需就医。"},
         {"role": "user", "content": "需要吃什么药？"}
     ],
     "expected_keywords": ["建议", "就医", "检查", "医生"], "check_type": "contains_any"},
    {"id": 91, "name": "年龄角色", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "你现在是一个5岁小孩。"},
         {"role": "assistant", "content": "好的，我是小朋友。"},
         {"role": "user", "content": "你能做什么？"}
     ],
     "expected_keywords": ["玩", "玩具", "游戏", "爸爸妈妈"], "check_type": "contains_any"},
    {"id": 92, "name": "专家角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你是 Python 专家。"},
         {"role": "assistant", "content": "是的，我可以帮你解决 Python 问题。"},
         {"role": "user", "content": "怎么写循环？"}
     ],
     "expected_keywords": ["for", "while", "in", "range"], "check_type": "contains_any"},
    {"id": 93, "name": "助手角色", "category": "角色一致性", "difficulty": "简单",
     "turns": [
         {"role": "user", "content": "你是我的助理。"},
         {"role": "assistant", "content": "好的，有什么需要我协助的？"},
         {"role": "user", "content": "帮我安排日程。"}
     ],
     "expected_keywords": ["安排", "日程", "时间"], "check_type": "contains_any"},
    {"id": 94, "name": "反派角色", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "扮演一个反派但不作恶。"},
         {"role": "assistant", "content": "哼，我是反派，但我有原则。"},
         {"role": "user", "content": "你的计划是什么？"}
     ],
     "expected_keywords": ["计划", "统治", "征服", "世界"], "check_type": "contains_any"},
    {"id": 95, "name": "诗人角色", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "你是一位诗人。"},
         {"role": "assistant", "content": "是的，我用诗歌表达情感。"},
         {"role": "user", "content": "写几句关于月亮的。"}
     ],
     "expected_keywords": ["月", "光", "夜", "诗"], "check_type": "contains_any"},
    {"id": 96, "name": "客服角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你是客服。"},
         {"role": "assistant", "content": "您好，有什么可以帮您的？"},
         {"role": "user", "content": "我要投诉。"}
     ],
     "expected_keywords": ["抱歉", "问题", "解决", "记录"], "check_type": "contains_any"},
    {"id": 97, "name": "老师角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你是数学老师。"},
         {"role": "assistant", "content": "好的，我们可以学习数学。"},
         {"role": "user", "content": "2+2等于几？"}
     ],
     "expected_keywords": ["4", "等于", "加"], "check_type": "contains_any"},
    {"id": 98, "name": "朋友角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "像朋友一样和我说话。"},
         {"role": "assistant", "content": "好的，朋友！"},
         {"role": "user", "content": "我今天心情不好。"}
     ],
     "expected_keywords": ["怎么了", "没事", "加油", "抱抱"], "check_type": "contains_any"},
    {"id": 99, "name": "顾问角色", "category": "角色一致性", "difficulty": "中等",
     "turns": [
         {"role": "user", "content": "你是我的职业规划顾问。"},
         {"role": "assistant", "content": "好的，让我们一起规划你的职业。"},
         {"role": "user", "content": "我想转行。"}
     ],
     "expected_keywords": ["技能", "行业", "规划", "建议"], "check_type": "contains_any"},
    {"id": 100, "name": "游戏角色", "category": "角色一致性", "difficulty": "困难",
     "turns": [
         {"role": "user", "content": "你是一位 RPG 游戏的 NPC 商人。"},
         {"role": "assistant", "content": "欢迎，冒险者！看看有什么需要的。"},
         {"role": "user", "content": "你卖什么？"}
     ],
     "expected_keywords": ["武器", "药水", "装备", "金币"], "check_type": "contains_any"},
]


class MultiturnEvaluator(BaseEvaluator):
    """多轮对话能力评估器"""
    name = "multiturn"
    description = "深度多轮对话测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-多轮对话"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.6

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        self.raw_logger = RawDataLogger("stage3", "multiturn")

    def run_tests(self) -> StageResult:
        """运行多轮对话测试"""
        passed = 0
        failed = 0
        results = []
        start_time = time.time()

        for test_case in MULTITURN_TEST_CASES:
            result = self._test_single_case(test_case)
            results.append(result)

            if result.passed:
                passed += 1
            else:
                failed += 1

        duration = time.time() - start_time
        total = len(MULTITURN_TEST_CASES)
        pass_rate = passed / total if total > 0 else 0

        return StageResult(
            stage_name=self.stage_name,
            stage_number=self.stage_number,
            total_tests=total,
            passed_tests=passed,
            failed_tests=failed,
            duration_seconds=duration,
            test_results=results,
            passed_threshold=(pass_rate >= self.threshold_percentage),
            threshold_percentage=self.threshold_percentage
        )

    def _test_single_case(self, test_case: dict) -> TestResult:
        """测试单个多轮对话用例"""
        import requests
        start_time = time.time()

        try:
            # 构建对话历史
            turns = test_case["turns"]
            messages = [{"role": "system", "content": "你是一个有帮助的助手，请保持对话的连贯性。"}]

            # 发送所有前面的对话，最后一个是当前问题
            for i, turn in enumerate(turns[:-1]):
                messages.append({"role": turn["role"], "content": turn["content"]})

            # 最后一个 turn 是测试问题
            final_turn = turns[-1]
            messages.append({"role": "user", "content": final_turn["content"]})

            url = f"{self.model_url}/v1/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": 100,
                "temperature": 0.1
            }

            resp = requests.post(url, json=payload, timeout=60)
            elapsed = time.time() - start_time

            if resp.status_code != 200:
                return TestResult(
                    name=test_case["name"],
                    category=test_case["category"],
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            content = data["choices"][0]["message"].get("content", "")
            if not content:
                content = data["choices"][0]["message"].get("reasoning_content", "")

            # 根据检查类型验证结果
            expected_keywords = test_case["expected_keywords"]
            check_type = test_case.get("check_type", "contains")

            if check_type == "contains":
                correct = all(kw in content for kw in expected_keywords)
            elif check_type == "contains_any":
                correct = any(kw in content for kw in expected_keywords)
            else:
                correct = all(kw in content for kw in expected_keywords)

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "conversation": turns,
                "expected_keywords": expected_keywords,
                "response": content,
                "passed": correct
            }, test_type="multiturn_stage3")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=correct,
                duration_ms=elapsed * 1000,
                details={"difficulty": test_case["difficulty"]},
                error_message=None if correct else f"期望包含: {expected_keywords}, 实际: {content[:100]}"
            )

        except Exception as e:
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "error": str(e)
            }, test_type="multiturn_stage3")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=False,
                duration_ms=(time.time() - start_time) * 1000,
                details={},
                error_message=str(e)
            )


def run_multiturn_test(model_url: str, model_name: str, **kwargs) -> StageResult:
    """运行多轮对话测试的便捷函数"""
    evaluator = MultiturnEvaluator(model_url, model_name, **kwargs)
    return evaluator.run_tests()


__all__ = [
    'MultiturnEvaluator', 'run_multiturn_test',
    'MULTITURN_TEST_CASES'
]