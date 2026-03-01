#!/usr/bin/env python3
"""
Stage 3 深度逻辑推理测试 (100 cases)
涵盖：演绎推理、归纳推理、类比推理、逻辑谜题、条件推理等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 逻辑推理测试用例 (100个)
LOGIC_TEST_CASES = [
    # ===== 演绎推理 (20题) =====
    {"id": 1, "name": "三段论基础", "category": "演绎推理", "difficulty": "简单",
     "question": "所有A都是B，所有B都是C，那么：", "options": ["所有A都是C", "所有C都是A", "有些A不是C", "无法确定"],
     "answer": "A", "explanation": "三段论传递性"},
    {"id": 2, "name": "充分必要条件", "category": "演绎推理", "difficulty": "中等",
     "question": "如果下雨那么地湿，地湿了说明：", "options": ["一定下雨了", "可能下雨了", "一定没下雨", "无法确定是否下雨"],
     "answer": "D", "explanation": "地湿可能有其他原因"},
    {"id": 3, "name": "否定后件", "category": "演绎推理", "difficulty": "中等",
     "question": "如果是鸟就会飞，企鹅不会飞，那么：", "options": ["企鹅是鸟", "企鹅不是鸟", "有些鸟不会飞", "所有鸟都会飞"],
     "answer": "B", "explanation": "否定后件推出否定前件"},
    {"id": 4, "name": "逆否命题", "category": "演绎推理", "difficulty": "中等",
     "question": "原命题：如果学习好那么考试好。其逆否命题是：", "options": ["如果考试好那么学习好", "如果考试不好那么学习不好", "如果学习不好那么考试不好", "如果考试不好那么学习好"],
     "answer": "B", "explanation": "逆否命题与原命题等价"},
    {"id": 5, "name": "选言推理", "category": "演绎推理", "difficulty": "简单",
     "question": "要么A要么B，不是A，那么：", "options": ["一定是B", "一定不是B", "可能是A", "无法确定"],
     "answer": "A", "explanation": "不相容选言推理"},
    {"id": 6, "name": "假言连锁", "category": "演绎推理", "difficulty": "中等",
     "question": "如果A则B，如果B则C，如果C则D，那么如果A则：", "options": ["B", "C", "D", "无法确定"],
     "answer": "C", "explanation": "假言连锁推理"},
    {"id": 7, "name": "直言命题对当", "category": "演绎推理", "difficulty": "困难",
     "question": "所有S都是P为真，那么有些S不是P：", "options": ["为真", "为假", "真假不定", "无法判断"],
     "answer": "B", "explanation": "矛盾关系"},
    {"id": 8, "name": "假言易位", "category": "演绎推理", "difficulty": "困难",
     "question": "只有P才Q，等价于：", "options": ["如果P那么Q", "如果Q那么P", "如果非P那么非Q", "如果非Q那么非P"],
     "answer": "B", "explanation": "必要条件假言命题"},
    {"id": 9, "name": "二难推理", "category": "演绎推理", "difficulty": "困难",
     "question": "如果A则C，如果B则C，A或B，那么：", "options": ["非C", "C", "非A且非B", "无法确定"],
     "answer": "B", "explanation": "简单构成式二难推理"},
    {"id": 10, "name": "归谬法", "category": "演绎推理", "difficulty": "中等",
     "question": "假设P为真推出矛盾，那么：", "options": ["P为真", "P为假", "P真假不定", "需要更多条件"],
     "answer": "B", "explanation": "归谬法否定假设"},
    {"id": 11, "name": "直言命题变形", "category": "演绎推理", "difficulty": "中等",
     "question": "所有S都不是P，可以推出：", "options": ["所有P都是S", "所有P都不是S", "有些P不是S", "无法推出"],
     "answer": "B", "explanation": "换质位推理"},
    {"id": 12, "name": "联言推理", "category": "演绎推理", "difficulty": "简单",
     "question": "A且B为真，那么：", "options": ["A真B假", "A假B真", "A真B真", "A假B假"],
     "answer": "C", "explanation": "联言命题为真则各支为真"},
    {"id": 13, "name": "选言支推理", "category": "演绎推理", "difficulty": "简单",
     "question": "A或B或C为真，且A假B假，那么：", "options": ["A真", "B真", "C真", "无法确定"],
     "answer": "C", "explanation": "否定肯定式"},
    {"id": 14, "name": "反三段论", "category": "演绎推理", "difficulty": "困难",
     "question": "如果A且B则C，A且非C，那么：", "options": ["B真", "非B", "A假", "C真"],
     "answer": "B", "explanation": "反三段论推理"},
    {"id": 15, "name": "模态命题", "category": "演绎推理", "difficulty": "困难",
     "question": "必然P的矛盾命题是：", "options": ["必然非P", "可能P", "可能非P", "不可能P"],
     "answer": "C", "explanation": "必然P与可能非P矛盾"},
    {"id": 16, "name": "复合命题", "category": "演绎推理", "difficulty": "中等",
     "question": "如果A则(B且C)，非B，那么：", "options": ["A真", "非A", "C真", "无法确定"],
     "answer": "B", "explanation": "否定后件式"},
    {"id": 17, "name": "条件转换", "category": "演绎推理", "difficulty": "中等",
     "question": "除非P否则Q，等价于：", "options": ["如果P则Q", "如果非P则Q", "P且Q", "P或Q"],
     "answer": "B", "explanation": "除非P否则Q = 非P→Q"},
    {"id": 18, "name": "等价关系", "category": "演绎推理", "difficulty": "困难",
     "question": "当且仅当P则Q，P为真，那么：", "options": ["Q真假不定", "Q为假", "Q为真", "无法判断"],
     "answer": "C", "explanation": "充要条件双向推出"},
    {"id": 19, "name": "推理有效性", "category": "演绎推理", "difficulty": "中等",
     "question": "前提：所有M是P，所有S是M。结论：所有S是P。该推理：", "options": ["有效", "无效", "前提不足", "结论错误"],
     "answer": "A", "explanation": "标准三段论Barbara式"},
    {"id": 20, "name": "逻辑谬误识别", "category": "演绎推理", "difficulty": "中等",
     "question": "因为A是B，C是B，所以A是C。这是：", "options": ["有效推理", "中项不周延", "大项不当周延", "小项不当周延"],
     "answer": "B", "explanation": "中项必须周延一次"},

    # ===== 归纳推理 (20题) =====
    {"id": 21, "name": "简单枚举", "category": "归纳推理", "difficulty": "简单",
     "question": "观察到的天鹅都是白色的，推断所有天鹅都是白色，这是：", "options": ["演绎推理", "完全归纳", "不完全归纳", "类比推理"],
     "answer": "C", "explanation": "基于部分样本的归纳"},
    {"id": 22, "name": "因果归纳", "category": "归纳推理", "difficulty": "中等",
     "question": "每次吃这种食物都过敏，推断这种食物导致过敏，这是：", "options": ["求同法", "求异法", "共变法", "剩余法"],
     "answer": "A", "explanation": "穆勒五法之求同法"},
    {"id": 23, "name": "统计归纳", "category": "归纳推理", "difficulty": "中等",
     "question": "抽样调查显示60%人喜欢A品牌，推断总体约60%喜欢，这是：", "options": ["完全归纳", "统计归纳", "演绎推理", "类比推理"],
     "answer": "B", "explanation": "基于样本统计的归纳"},
    {"id": 24, "name": "科学归纳", "category": "归纳推理", "difficulty": "中等",
     "question": "通过实验发现金属受热膨胀与分子运动有关，这是：", "options": ["简单枚举", "科学归纳", "完全归纳", "演绎推理"],
     "answer": "B", "explanation": "分析因果联系的归纳"},
    {"id": 25, "name": "完全归纳", "category": "归纳推理", "difficulty": "简单",
     "question": "检查了所有学生的作业都完成了，推断全班作业都完成，这是：", "options": ["不完全归纳", "完全归纳", "类比推理", "演绎推理"],
     "answer": "B", "explanation": "穷尽所有情况的归纳"},
    {"id": 26, "name": "求异法", "category": "归纳推理", "difficulty": "中等",
     "question": "实验组和对照组仅一个因素不同导致结果不同，这是：", "options": ["求同法", "求异法", "共变法", "剩余法"],
     "answer": "B", "explanation": "穆勒五法之求异法"},
    {"id": 27, "name": "共变法", "category": "归纳推理", "difficulty": "中等",
     "question": "温度升高金属膨胀越多，推断温度与膨胀相关，这是：", "options": ["求同法", "求异法", "共变法", "剩余法"],
     "answer": "C", "explanation": "穆勒五法之共变法"},
    {"id": 28, "name": "剩余法", "category": "归纳推理", "difficulty": "困难",
     "question": "复合现象中减去已知原因部分，剩余部分另有原因，这是：", "options": ["求同法", "求异法", "共变法", "剩余法"],
     "answer": "D", "explanation": "穆勒五法之剩余法"},
    {"id": 29, "name": "归纳强度", "category": "归纳推理", "difficulty": "中等",
     "question": "观察1000只天鹅都是白色，比观察10只的归纳结论：", "options": ["更弱", "一样", "更强", "无法比较"],
     "answer": "C", "explanation": "样本量越大归纳强度越高"},
    {"id": 30, "name": "反例否定", "category": "归纳推理", "difficulty": "简单",
     "question": "发现一只黑天鹅，对所有天鹅都是白色的结论是：", "options": ["证实", "否定", "无关", "加强"],
     "answer": "B", "explanation": "一个反例可否定全称命题"},
    {"id": 31, "name": "概率归纳", "category": "归纳推理", "difficulty": "中等",
     "question": "根据历史数据，某股票上涨概率70%，这是：", "options": ["演绎推理", "统计归纳", "因果推理", "类比推理"],
     "answer": "B", "explanation": "基于频率的概率归纳"},
    {"id": 32, "name": "典型抽样", "category": "归纳推理", "difficulty": "中等",
     "question": "选择代表性样本进行归纳，目的是：", "options": ["增加样本量", "提高归纳可靠性", "简化计算", "减少时间"],
     "answer": "B", "explanation": "代表性样本提高归纳质量"},
    {"id": 33, "name": "归纳跳跃", "category": "归纳推理", "difficulty": "困难",
     "question": "从有限样本到全称结论的逻辑跳跃称为：", "options": ["演绎跳跃", "归纳跳跃", "类比跳跃", "逻辑错误"],
     "answer": "B", "explanation": "归纳推理的本质特征"},
    {"id": 34, "name": "因果方向", "category": "归纳推理", "difficulty": "困难",
     "question": "A和B总是同时出现，能确定：", "options": ["A导致B", "B导致A", "有因果关系", "无法确定因果方向"],
     "answer": "D", "explanation": "相关不等于因果"},
    {"id": 35, "name": "归纳确证", "category": "归纳推理", "difficulty": "中等",
     "question": "新证据与归纳结论一致，对结论是：", "options": ["证实", "证伪", "确证", "无关"],
     "answer": "C", "explanation": "确证增加可信度但不等于证实"},
    {"id": 36, "name": "预测归纳", "category": "归纳推理", "difficulty": "简单",
     "question": "根据过去趋势预测未来，属于：", "options": ["演绎推理", "归纳推理", "类比推理", "假说演绎"],
     "answer": "B", "explanation": "基于历史模式的归纳预测"},
    {"id": 37, "name": "归纳问题", "category": "归纳推理", "difficulty": "困难",
     "question": "休谟提出的归纳问题是质疑：", "options": ["归纳的有效性", "演绎的有效性", "逻辑的有效性", "数学的有效性"],
     "answer": "A", "explanation": "休谟质疑归纳的合理性基础"},
    {"id": 38, "name": "自然齐一", "category": "归纳推理", "difficulty": "困难",
     "question": "归纳推理依赖的基本假设是：", "options": ["自然的齐一性", "神的存在", "人的理性", "经验可靠性"],
     "answer": "A", "explanation": "自然是齐一的才能从过去推未来"},
    {"id": 39, "name": "排除归纳", "category": "归纳推理", "difficulty": "中等",
     "question": "通过排除不可能选项确定原因，这是：", "options": ["求同法", "排除归纳", "共变法", "剩余法"],
     "answer": "B", "explanation": "排除法确定因果"},
    {"id": 40, "name": "归纳类比", "category": "归纳推理", "difficulty": "中等",
     "question": "从个体到总体的推理与从样本到总体的推理都是：", "options": ["演绎", "归纳", "类比", "综合"],
     "answer": "B", "explanation": "都属于归纳推理"},

    # ===== 类比推理 (20题) =====
    {"id": 41, "name": "类比基础", "category": "类比推理", "difficulty": "简单",
     "question": "A有属性a、b、c、d，B有属性a、b、c，那么B可能有：", "options": ["a", "b", "c", "d"],
     "answer": "D", "explanation": "类比推理推出共同属性"},
    {"id": 42, "name": "类比强度", "category": "类比推理", "difficulty": "中等",
     "question": "两类事物相似属性越多，类比结论：", "options": ["越弱", "越强", "不变", "不确定"],
     "answer": "B", "explanation": "相似性越多类比越可靠"},
    {"id": 43, "name": "类比相关", "category": "类比推理", "difficulty": "中等",
     "question": "类比推理中相似属性与推出属性越相关，结论：", "options": ["越弱", "越强", "无关", "错误"],
     "answer": "B", "explanation": "相关性提高类比可靠性"},
    {"id": 44, "name": "功能类比", "category": "类比推理", "difficulty": "简单",
     "question": "鸟翼:飞翔 = 鱼鳍:？", "options": ["游泳", "呼吸", "捕食", "繁殖"],
     "answer": "A", "explanation": "功能类比"},
    {"id": 45, "name": "因果类比", "category": "类比推理", "difficulty": "中等",
     "question": "地球有大气、有水、有生命，火星有大气、有水，那么火星：", "options": ["一定有生命", "可能有生命", "一定无生命", "无法判断"],
     "answer": "B", "explanation": "类比推理推出可能性"},
    {"id": 46, "name": "结构类比", "category": "类比推理", "difficulty": "中等",
     "question": "原子结构类似太阳系结构，这是：", "options": ["功能类比", "结构类比", "因果类比", "综合类比"],
     "answer": "B", "explanation": "基于结构相似的类比"},
    {"id": 47, "name": "类比失效", "category": "类比推理", "difficulty": "困难",
     "question": "两种事物有表面相似但本质不同，类比会：", "options": ["更有效", "失效", "不确定", "更强"],
     "answer": "B", "explanation": "本质差异导致类比失效"},
    {"id": 48, "name": "数学类比", "category": "类比推理", "difficulty": "中等",
     "question": "(a+b)²=a²+2ab+b²，类比(a+b)³=？", "options": ["a³+b³", "a³+3ab+b³", "a³+3a²b+3ab²+b³", "a³+a²b+ab²+b³"],
     "answer": "C", "explanation": "二项式定理类比"},
    {"id": 49, "name": "类比反驳", "category": "类比推理", "difficulty": "困难",
     "question": "有人用A类比B论证，反驳该论证可指出：", "options": ["A和B相似", "A和B有本质差异", "A是假的", "B是假的"],
     "answer": "B", "explanation": "指出差异削弱类比"},
    {"id": 50, "name": "模型类比", "category": "类比推理", "difficulty": "中等",
     "question": "用地图类比实际地理，地图是：", "options": ["原物", "模型", "本质", "整体"],
     "answer": "B", "explanation": "模型是原型的类比"},
    {"id": 51, "name": "类比限度", "category": "类比推理", "difficulty": "中等",
     "question": "类比的结论是：", "options": ["必然真", "必然假", "或然真", "不确定"],
     "answer": "C", "explanation": "类比推出可能性而非必然性"},
    {"id": 52, "name": "类比谬误", "category": "类比推理", "difficulty": "中等",
     "question": "强行类比不相关事物属于：", "options": ["有效推理", "类比谬误", "归纳错误", "演绎错误"],
     "answer": "B", "explanation": "不当类比是逻辑谬误"},
    {"id": 53, "name": "仿生学类比", "category": "类比推理", "difficulty": "简单",
     "question": "根据蝙蝠超声波发明雷达，这是：", "options": ["功能类比应用", "因果类比应用", "结构类比应用", "随机发明"],
     "answer": "A", "explanation": "功能类比的应用"},
    {"id": 54, "name": "比例类比", "category": "类比推理", "difficulty": "简单",
     "question": "2:4 = 3:？", "options": ["5", "6", "7", "8"],
     "answer": "B", "explanation": "比例关系类比"},
    {"id": 55, "name": "类比推理方向", "category": "类比推理", "difficulty": "中等",
     "question": "从个别到个别的推理是：", "options": ["演绎", "归纳", "类比", "综合"],
     "answer": "C", "explanation": "类比的推理方向"},
    {"id": 56, "name": "类比与比喻", "category": "类比推理", "difficulty": "中等",
     "question": "类比推理与修辞比喻的区别在于：", "options": ["无区别", "类比是推理，比喻是修辞", "比喻更精确", "类比更生动"],
     "answer": "B", "explanation": "功能不同"},
    {"id": 57, "name": "负类比", "category": "类比推理", "difficulty": "困难",
     "question": "指出类比对象的不同点是为了：", "options": ["支持类比", "削弱类比", "无关", "加强类比"],
     "answer": "B", "explanation": "负类比削弱论证"},
    {"id": 58, "name": "正类比", "category": "类比推理", "difficulty": "困难",
     "question": "强调类比对象的相似点是为了：", "options": ["支持类比", "削弱类比", "无关", "反驳类比"],
     "answer": "A", "explanation": "正类比支持论证"},
    {"id": 59, "name": "类比重构", "category": "类比推理", "difficulty": "困难",
     "question": "科学发现中常用类比来：", "options": ["证明定理", "提出假说", "逻辑演绎", "数学计算"],
     "answer": "B", "explanation": "类比用于假说发现"},
    {"id": 60, "name": "隐喻理解", "category": "类比推理", "difficulty": "中等",
     "question": "理解'时间就是金钱'需要：", "options": ["演绎推理", "类比推理", "归纳推理", "数学计算"],
     "answer": "B", "explanation": "隐喻基于类比"},

    # ===== 逻辑谜题 (20题) =====
    {"id": 61, "name": "骑士与无赖", "category": "逻辑谜题", "difficulty": "中等",
     "question": "骑士总说真话，无赖总说假话。A说'我是无赖'，A是：", "options": ["骑士", "无赖", "无法确定", "既是又是"],
     "answer": "B", "explanation": "骑士不会说自己是无赖"},
    {"id": 62, "name": "三扇门问题", "category": "逻辑谜题", "difficulty": "中等",
     "question": "蒙提霍尔问题中，换门赢得汽车的概率是：", "options": ["1/3", "1/2", "2/3", "无法确定"],
     "answer": "C", "explanation": "换门胜率2/3"},
    {"id": 63, "name": "囚徒困境", "category": "逻辑谜题", "difficulty": "中等",
     "question": "囚徒困境中，双方理性的选择导致：", "options": ["最优结果", "最差结果", "纳什均衡", "合作结果"],
     "answer": "C", "explanation": "个体理性导致集体次优"},
    {"id": 64, "name": "渡河问题", "category": "逻辑谜题", "difficulty": "简单",
     "question": "农夫带狼羊菜过河，船只能载农夫和一样，狼吃羊、羊吃菜，最少几次：", "options": ["3", "5", "7", "9"],
     "answer": "C", "explanation": "经典过河问题需7步"},
    {"id": 65, "name": "称重问题", "category": "逻辑谜题", "difficulty": "中等",
     "question": "12个球中1个假球（不知轻重），用天平最少几次找出：", "options": ["2", "3", "4", "5"],
     "answer": "B", "explanation": "信息论下限为3次"},
    {"id": 66, "name": "爱因斯坦谜题", "category": "逻辑谜题", "difficulty": "困难",
     "question": "五房子五人五饮料五烟五宠物，谁养鱼？这类问题用：", "options": ["排除法", "假设法", "排除法和假设法", "无法解决"],
     "answer": "C", "explanation": "复杂约束用系统方法"},
    {"id": 67, "name": "说谎者悖论", "category": "逻辑谜题", "difficulty": "困难",
     "question": "'这句话是假的'是：", "options": ["真", "假", "悖论", "无意义"],
     "answer": "C", "explanation": "经典自指悖论"},
    {"id": 68, "name": "理发师悖论", "category": "逻辑谜题", "difficulty": "困难",
     "question": "理发师给且只给不给自己刮脸的人刮脸，他给自己刮脸吗？这是：", "options": ["可解", "罗素悖论", "真命题", "假命题"],
     "answer": "B", "explanation": "集合论悖论"},
    {"id": 69, "name": "Unexpected Hanging", "category": "逻辑谜题", "difficulty": "困难",
     "question": "'你将在下周某天被绞死，但执行当天早上你不知今天执行'，这句话：", "options": ["自洽", "悖论", "真", "假"],
     "answer": "B", "explanation": "知识悖论"},
    {"id": 70, "name": "斑马谜题", "category": "逻辑谜题", "difficulty": "困难",
     "question": "五个人五国家五房子五颜色五饮料五香烟五宠物，用：", "options": ["逻辑矩阵", "暴力搜索", "逻辑矩阵或搜索", "无法解决"],
     "answer": "C", "explanation": "系统逻辑方法可解"},
    {"id": 71, "name": " muddy children", "category": "逻辑谜题", "difficulty": "困难",
     "question": "n个泥孩子，父亲说'至少一人有泥'，重复n次'知道自己有泥的举手'，第n次：", "options": ["无人举手", "都举手", "部分举手", "无法确定"],
     "answer": "B", "explanation": "公共知识推理"},
    {"id": 72, "name": "真假话", "category": "逻辑谜题", "difficulty": "中等",
     "question": "三人中一人总说真，一人总说假，一人随机。问A'你是随机吗？'回答'是'，A是：", "options": ["真话", "假话", "随机", "无法确定"],
     "answer": "C", "explanation": "真话和假话者都不会说自己是随机"},
    {"id": 73, "name": "海盗分金", "category": "逻辑谜题", "difficulty": "困难",
     "question": "5海盗分100金，从老五开始提议，半数通过，老五最优策略：", "options": ["全拿", "分部分", "拿0", "无法确定"],
     "answer": "B", "explanation": "逆向归纳法"},
    {"id": 74, "name": "生日问题", "category": "逻辑谜题", "difficulty": "中等",
     "question": "23人中至少两人生日相同的概率超过：", "options": ["25%", "50%", "75%", "90%"],
     "answer": "B", "explanation": "生日悖论，23人概率>50%"},
    {"id": 75, "name": "两个信封", "category": "逻辑谜题", "difficulty": "中等",
     "question": "一个信封钱是另一个两倍，打开一个后应：", "options": ["肯定换", "肯定不换", "换不换期望相同", "无法确定"],
     "answer": "C", "explanation": "两信封悖论"},
    {"id": 76, "name": "纽科姆问题", "category": "逻辑谜题", "difficulty": "困难",
     "question": "预测者已预测你选择，选B盒(可能有100万)或两盒都选，理性选择：", "options": ["只选B", "选两盒", "无差异", "悖论"],
     "answer": "B", "explanation": "占优策略选择"},
    {"id": 77, "name": "睡美人问题", "category": "逻辑谜题", "difficulty": "困难",
     "question": "硬币正面醒1次，反面醒2次，睡美人醒来认为正面概率：", "options": ["1/2", "1/3", "2/3", "无法确定"],
     "answer": "B", "explanation": "自我定位概率争议"},
    {"id": 78, "name": "男孩女孩悖论", "category": "逻辑谜题", "difficulty": "中等",
     "question": "两个孩子，已知至少一个是男孩，两个都是男孩的概率：", "options": ["1/2", "1/3", "1/4", "2/3"],
     "answer": "B", "explanation": "条件概率问题"},
    {"id": 79, "name": "三门问题变体", "category": "逻辑谜题", "difficulty": "中等",
     "question": "主持人随机开门而非必开羊门，换门胜率：", "options": ["1/2", "2/3", "1/3", "不确定"],
     "answer": "A", "explanation": "条件改变导致概率变1/2"},
    {"id": 80, "name": "蓝眼睛岛", "category": "逻辑谜题", "difficulty": "困难",
     "question": "100蓝眼人，公告'至少一人蓝眼'，100天后：", "options": ["无人离开", "全离开", "部分离开", "无法确定"],
     "answer": "B", "explanation": "归纳公共知识"},

    # ===== 条件推理 (20题) =====
    {"id": 81, "name": "充分条件", "category": "条件推理", "difficulty": "简单",
     "question": "'如果下雨地就湿'，下雨是地湿的：", "options": ["充分条件", "必要条件", "充要条件", "无关条件"],
     "answer": "A", "explanation": "下雨足以使地湿"},
    {"id": 82, "name": "必要条件", "category": "条件推理", "difficulty": "简单",
     "question": "'只有年满18才能投票'，年满18是投票的：", "options": ["充分条件", "必要条件", "充要条件", "无关条件"],
     "answer": "B", "explanation": "必须满足的条件"},
    {"id": 83, "name": "充要条件", "category": "条件推理", "difficulty": "中等",
     "question": "三角形三边相等与三角相等的条件是：", "options": ["充分", "必要", "充要", "无关"],
     "answer": "C", "explanation": "两者等价"},
    {"id": 84, "name": "条件否定", "category": "条件推理", "difficulty": "中等",
     "question": "'如果P则Q'为真，那么'如果非P则非Q'：", "options": ["为真", "为假", "真假不定", "等价"],
     "answer": "C", "explanation": "否定前件谬误"},
    {"id": 85, "name": "条件逆否", "category": "条件推理", "difficulty": "中等",
     "question": "'如果P则Q'等价于：", "options": ["如果Q则P", "如果非P则非Q", "如果非Q则非P", "Q则P"],
     "answer": "C", "explanation": "逆否命题等价"},
    {"id": 86, "name": "多条件推理", "category": "条件推理", "difficulty": "中等",
     "question": "P→Q, Q→R, R→S，已知P，可推出：", "options": ["仅Q", "仅R", "S", "无法推出"],
     "answer": "C", "explanation": "假言连锁"},
    {"id": 87, "name": "除非否则", "category": "条件推理", "difficulty": "中等",
     "question": "'除非P否则Q'等价于：", "options": ["P→Q", "非P→Q", "Q→P", "P∧Q"],
     "answer": "B", "explanation": "除非P = 如果不P"},
    {"id": 88, "name": "只要就", "category": "条件推理", "difficulty": "简单",
     "question": "'只要P就Q'，P是Q的：", "options": ["充分条件", "必要条件", "充要条件", "无关"],
     "answer": "A", "explanation": "P足以导致Q"},
    {"id": 89, "name": "当且仅当", "category": "条件推理", "difficulty": "中等",
     "question": "'当且仅当P则Q'意味着：", "options": ["P→Q", "Q→P", "P↔Q", "以上都对"],
     "answer": "D", "explanation": "双向推出"},
    {"id": 90, "name": "除非才", "category": "条件推理", "difficulty": "困难",
     "question": "'除非P才Q'等价于：", "options": ["P→Q", "Q→P", "非P→非Q", "非Q→P"],
     "answer": "B", "explanation": "除非P才Q = 只有P才Q"},
    {"id": 91, "name": "条件组合", "category": "条件推理", "difficulty": "中等",
     "question": "(P→Q)∧(R→S)，P∨R，可推出：", "options": ["Q∧S", "Q∨S", "P∧R", "无法推出"],
     "answer": "B", "explanation": "二难推理"},
    {"id": 92, "name": "双条件否定", "category": "条件推理", "difficulty": "困难",
     "question": "否定(P↔Q)等价于：", "options": ["P∧非Q", "非P∧Q", "(P∧非Q)∨(非P∧Q)", "P∨Q"],
     "answer": "C", "explanation": "只有一个为真"},
    {"id": 93, "name": "条件概率", "category": "条件推理", "difficulty": "困难",
     "question": "P(A|B)与P(B|A)的关系：", "options": ["相等", "互为倒数", "通过贝叶斯联系", "无关"],
     "answer": "C", "explanation": "贝叶斯定理"},
    {"id": 94, "name": "实质蕴涵", "category": "条件推理", "difficulty": "困难",
     "question": "'如果P则Q'在P假Q真时为：", "options": ["真", "假", "不定", "悖论"],
     "answer": "A", "explanation": "实质蕴涵怪论"},
    {"id": 95, "name": "严格蕴涵", "category": "条件推理", "difficulty": "困难",
     "question": "模态逻辑中的严格蕴涵是指：", "options": ["P→Q为真", "必然(P→Q)", "P∧Q", "可能(P→Q)"],
     "answer": "B", "explanation": "必然联系"},
    {"id": 96, "name": "反事实条件", "category": "条件推理", "difficulty": "困难",
     "question": "'如果明天下雨我就带伞'，今天说这句话，明天下雨是：", "options": ["真", "假", "不确定", "假设"],
     "answer": "D", "explanation": "反事实条件句"},
    {"id": 97, "name": "条件独立性", "category": "条件推理", "difficulty": "困难",
     "question": "A和B在给定C条件下独立意味着：", "options": ["P(A|B)=P(A)", "P(A|B,C)=P(A|C)", "P(A,B)=P(A)P(B)", "P(A)=P(B)"],
     "answer": "B", "explanation": "条件独立性定义"},
    {"id": 98, "name": "Monotonicity", "category": "条件推理", "difficulty": "困难",
     "question": "经典逻辑是单调的，指增加前提：", "options": ["结论减少", "结论不变或增加", "结论变假", "系统崩溃"],
     "answer": "B", "explanation": "单调性特征"},
    {"id": 99, "name": "非单调推理", "category": "条件推理", "difficulty": "困难",
     "question": "增加前提可能撤回先前结论的推理是：", "options": ["单调", "非单调", "演绎", "无效"],
     "answer": "B", "explanation": "常识推理特点"},
    {"id": 100, "name": "默认推理", "category": "条件推理", "difficulty": "困难",
     "question": "'鸟会飞'作为默认规则，遇到企鹅时：", "options": ["坚持原结论", "撤回结论", "修改规则", "无法处理"],
     "answer": "B", "explanation": "非单调默认推理"},
]


class LogicEvaluator(BaseEvaluator):
    """逻辑推理能力评估器"""

    name = "logic"
    description = "逻辑推理测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-逻辑推理"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.6  # 60% 通过门槛

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行逻辑推理测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in LOGIC_TEST_CASES:
            result = self._test_single_case(test_case)
            test_results.append(result)

        elapsed = time.time() - start_time

        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        return StageResult(
            stage_name=self.stage_name,
            stage_number=self.stage_number,
            total_tests=total,
            passed_tests=passed,
            failed_tests=total - passed,
            duration_seconds=elapsed,
            test_results=test_results,
            passed_threshold=(passed / total >= self.threshold_percentage) if total > 0 else False,
            threshold_percentage=self.threshold_percentage
        )

    def _test_single_case(self, test_case: dict) -> TestResult:
        """测试单个逻辑推理用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case['options'])])
        prompt = f"回答以下逻辑推理问题，只输出选项字母(A/B/C/D)：\n\n{test_case['question']}\n\n{options_str}\n\n答案："

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个逻辑推理专家。只回答选项字母，不要解释。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=60)
            elapsed = time.time() - start

            if resp.status_code != 200:
                return TestResult(
                    name=test_case['name'],
                    category=test_case['category'],
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            content = data["choices"][0]["message"].get("content", "")
            if not content:
                content = data["choices"][0]["message"].get("reasoning_content", "")

            # 提取答案字母
            answer = self._extract_answer(content)
            expected = test_case['answer']
            passed = answer == expected

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case['name'],
                "question": test_case['question'],
                "expected": expected,
                "actual": answer,
                "passed": passed
            }, test_type="logic_stage3")

            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "difficulty": test_case['difficulty'],
                    "expected": expected,
                    "actual": answer,
                    "explanation": test_case.get('explanation', '')
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )

    def _extract_after_think(self, text: str) -> str:
        """提取 </think> 标签后的内容"""
        if not text:
            return text
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

    def _extract_answer(self, text: str) -> str:
        """从文本中提取答案字母 - 支持推理模型"""
        # 先提取 </think> 后的内容
        text = self._extract_after_think(text).upper()

        # 尝试匹配 "答案: A" 或 "答案是 B" 格式
        patterns = [
            r'答案[:：]\s*([A-D])',  # 答案: A
            r'答案(?:是|为)[:：]?\s*([A-D])',  # 答案是 A / 答案为A
            r'[\(\[\{]([A-D])[\)\]\}]',  # (A) [A] {A}
            r'\b([A-D])[\.、\)]',  # A. A、 A)
            r'选项[:：]?\s*([A-D])',  # 选项: A
            r'[选|答][择|案][:：]?\s*([A-D])',  # 选择: A / 答案: A
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)

        # 在 </think> 后的内容中找最后一个独立的 A-D 字母
        matches = re.findall(r'\b([A-D])\b', text)
        if matches:
            return matches[-1]  # 返回最后一个匹配

        # 最后的备选：找第一个 A-D 字符
        match = re.search(r'[A-D]', text)
        return match.group(0) if match else ""


def run_logic_test(model_url: str, model_name: str) -> dict:
    """运行逻辑推理测试"""
    evaluator = LogicEvaluator(model_url, model_name)
    stage_result = evaluator.run_tests()

    return {
        "model": model_name,
        "url": model_url,
        "stage": stage_result.stage_number,
        "stage_name": stage_result.stage_name,
        "total_tests": stage_result.total_tests,
        "passed_tests": stage_result.passed_tests,
        "failed_tests": stage_result.failed_tests,
        "pass_rate": stage_result.pass_rate,
        "duration_seconds": stage_result.duration_seconds,
        "passed_threshold": stage_result.passed_threshold,
        "tests": [
            {
                "name": r.name,
                "category": r.category,
                "passed": r.passed,
                "duration_ms": r.duration_ms,
                "details": r.details,
                "error": r.error_message
            }
            for r in stage_result.test_results
        ]
    }


if __name__ == "__main__":
    result = run_logic_test("http://localhost:8400", "Qwen3VL-4B-Instruct-Q8_0")
    print(f"逻辑推理测试: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
