#!/usr/bin/env python3
"""
Stage 3 深度常识问答测试 (100 cases)
涵盖：物理、化学、生物、地理、历史、政治、经济、社会、生活常识等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 常识问答测试用例 (100个)
COMMONSENSE_TEST_CASES = [
    # ===== 物理常识 (15题) =====
    {"id": 1, "name": "光速", "category": "物理", "difficulty": "简单",
     "question": "光在真空中的传播速度约为多少米/秒？", "options": ["3×10⁶", "3×10⁸", "3×10¹⁰", "3×10¹²"], "answer": "B"},
    {"id": 2, "name": "牛顿定律", "category": "物理", "difficulty": "简单",
     "question": "牛顿第一定律又称为什么定律？", "options": ["加速度定律", "惯性定律", "作用力定律", "反作用力定律"], "answer": "B"},
    {"id": 3, "name": "能量守恒", "category": "物理", "difficulty": "中等",
     "question": "能量守恒定律指的是能量可以：", "options": ["创造", "消灭", "转化", "消失"], "answer": "C"},
    {"id": 4, "name": "电磁波谱", "category": "物理", "difficulty": "中等",
     "question": "以下哪种电磁波波长最短？", "options": ["无线电波", "微波", "X射线", "伽马射线"], "answer": "D"},
    {"id": 5, "name": "浮力原理", "category": "物理", "difficulty": "简单",
     "question": "阿基米德原理描述的是：", "options": ["浮力", "压强", "速度", "温度"], "answer": "A"},
    {"id": 6, "name": "绝对零度", "category": "物理", "difficulty": "中等",
     "question": "绝对零度是多少摄氏度？", "options": ["0°C", "-100°C", "-273.15°C", "-373°C"], "answer": "C"},
    {"id": 7, "name": "欧姆定律", "category": "物理", "difficulty": "简单",
     "question": "欧姆定律公式中，电流等于：", "options": ["电压×电阻", "电压÷电阻", "电压+电阻", "电压-电阻"], "answer": "B"},
    {"id": 8, "name": "核聚变", "category": "物理", "difficulty": "中等",
     "question": "太阳的能量来源于：", "options": ["核裂变", "核聚变", "化学燃烧", "引力收缩"], "answer": "B"},
    {"id": 9, "name": "相对论", "category": "物理", "difficulty": "困难",
     "question": "爱因斯坦狭义相对论的基本假设不包括：", "options": ["光速不变", "相对性原理", "以太存在", "同时相对性"], "answer": "C"},
    {"id": 10, "name": "量子力学", "category": "物理", "difficulty": "困难",
     "question": "海森堡不确定性原理指出不能同时精确测量：", "options": ["位置和速度", "质量和能量", "时间和空间", "电荷和质量"], "answer": "A"},
    {"id": 11, "name": "热力学", "category": "物理", "difficulty": "中等",
     "question": "热力学第二定律指出热量不能自发地从：", "options": ["高温传到低温", "低温传到高温", "固态到液态", "液态到气态"], "answer": "B"},
    {"id": 12, "name": "声波", "category": "物理", "difficulty": "简单",
     "question": "声音在哪种介质中传播最快？", "options": ["空气", "水", "钢铁", "真空"], "answer": "C"},
    {"id": 13, "name": "光的折射", "category": "物理", "difficulty": "中等",
     "question": "光从空气进入水中时传播方向会：", "options": ["不变", "偏折", "反射", "消失"], "answer": "B"},
    {"id": 14, "name": "重力加速度", "category": "物理", "difficulty": "简单",
     "question": "地球表面重力加速度约为多少m/s²？", "options": ["8.9", "9.8", "10.8", "11.8"], "answer": "B"},
    {"id": 15, "name": "原子结构", "category": "物理", "difficulty": "中等",
     "question": "原子核由什么组成？", "options": ["质子和电子", "质子和中子", "中子和电子", "光子和电子"], "answer": "B"},

    # ===== 化学常识 (15题) =====
    {"id": 16, "name": "水分子", "category": "化学", "difficulty": "简单",
     "question": "水的化学式是：", "options": ["HO", "H₂O", "H₂O₂", "HO₂"], "answer": "B"},
    {"id": 17, "name": "元素周期表", "category": "化学", "difficulty": "简单",
     "question": "元素周期表中原子序数为1的元素是：", "options": ["氦", "氢", "锂", "铍"], "answer": "B"},
    {"id": 18, "name": "氧化还原", "category": "化学", "difficulty": "中等",
     "question": "在氧化还原反应中，氧化剂会：", "options": ["得电子被氧化", "得电子被还原", "失电子被氧化", "失电子被还原"], "answer": "B"},
    {"id": 19, "name": "酸碱度", "category": "化学", "difficulty": "简单",
     "question": "pH=7表示溶液：", "options": ["酸性", "碱性", "中性", "强酸性"], "answer": "C"},
    {"id": 20, "name": "有机物", "category": "化学", "difficulty": "中等",
     "question": "有机物一定含有的元素是：", "options": ["碳", "氢", "氧", "氮"], "answer": "A"},
    {"id": 21, "name": "催化剂", "category": "化学", "difficulty": "中等",
     "question": "催化剂在化学反应中：", "options": ["被消耗", "改变反应速率", "改变产物", "提供能量"], "answer": "B"},
    {"id": 22, "name": "金属活动性", "category": "化学", "difficulty": "中等",
     "question": "以下金属活动性最强的是：", "options": ["铜", "铁", "锌", "钾"], "answer": "D"},
    {"id": 23, "name": "同位素", "category": "化学", "difficulty": "困难",
     "question": "同位素是指质子数相同但什么不同的原子？", "options": ["电子数", "中子数", "质子数", "核外电子排布"], "answer": "B"},
    {"id": 24, "name": "化学键", "category": "化学", "difficulty": "中等",
     "question": "氯化钠中的化学键类型是：", "options": ["共价键", "离子键", "金属键", "氢键"], "answer": "B"},
    {"id": 25, "name": "摩尔", "category": "化学", "difficulty": "中等",
     "question": "1摩尔物质包含的粒子数约为：", "options": ["6.02×10²³", "6.02×10²²", "6.02×10²⁴", "6.02×10²¹"], "answer": "A"},
    {"id": 26, "name": "温室气体", "category": "化学", "difficulty": "简单",
     "question": "最主要的温室气体是：", "options": ["氧气", "氮气", "二氧化碳", "氢气"], "answer": "C"},
    {"id": 27, "name": "电解", "category": "化学", "difficulty": "中等",
     "question": "电解水时阴极产生：", "options": ["氧气", "氢气", "氯气", "氮气"], "answer": "B"},
    {"id": 28, "name": "同分异构", "category": "化学", "difficulty": "困难",
     "question": "分子式相同但结构不同的化合物互称：", "options": ["同位素", "同素异形体", "同分异构体", "同系物"], "answer": "C"},
    {"id": 29, "name": "燃烧", "category": "化学", "difficulty": "简单",
     "question": "燃烧三要素不包括：", "options": ["可燃物", "氧气", "着火点", "催化剂"], "answer": "D"},
    {"id": 30, "name": "稀有气体", "category": "化学", "difficulty": "简单",
     "question": "以下哪种是稀有气体？", "options": ["氮气", "氧气", "氩气", "氯气"], "answer": "C"},

    # ===== 生物常识 (15题) =====
    {"id": 31, "name": "细胞", "category": "生物", "difficulty": "简单",
     "question": "细胞的基本结构不包括：", "options": ["细胞膜", "细胞核", "细胞壁", "叶绿体"], "answer": "C"},
    {"id": 32, "name": "DNA", "category": "生物", "difficulty": "简单",
     "question": "DNA的中文名称是：", "options": ["核糖核酸", "脱氧核糖核酸", "氨基酸", "蛋白质"], "answer": "B"},
    {"id": 33, "name": "光合作用", "category": "生物", "difficulty": "中等",
     "question": "光合作用的主要产物是：", "options": ["氧气和葡萄糖", "二氧化碳和水", "氮气和氧气", "甲烷和水"], "answer": "A"},
    {"id": 34, "name": "基因", "category": "生物", "difficulty": "中等",
     "question": "基因是控制生物性状的：", "options": ["DNA片段", "蛋白质", "RNA片段", "细胞膜"], "answer": "A"},
    {"id": 35, "name": "人体系统", "category": "生物", "difficulty": "简单",
     "question": "人体最大的器官是：", "options": ["肝脏", "大脑", "皮肤", "心脏"], "answer": "C"},
    {"id": 36, "name": "血液循环", "category": "生物", "difficulty": "中等",
     "question": "血液循环的动力器官是：", "options": ["肺", "心脏", "肝脏", "肾脏"], "answer": "B"},
    {"id": 37, "name": "免疫系统", "category": "生物", "difficulty": "中等",
     "question": "抗体是由什么细胞产生的？", "options": ["红细胞", "白细胞", "T细胞", "B细胞"], "answer": "D"},
    {"id": 38, "name": "进化论", "category": "生物", "difficulty": "中等",
     "question": "自然选择学说是谁提出的？", "options": ["拉马克", "达尔文", "孟德尔", "摩尔根"], "answer": "B"},
    {"id": 39, "name": "遗传", "category": "生物", "difficulty": "中等",
     "question": "孟德尔通过什么实验发现了遗传规律？", "options": ["豌豆杂交", "果蝇实验", "玉米实验", "细菌转化"], "answer": "A"},
    {"id": 40, "name": "生态系统", "category": "生物", "difficulty": "简单",
     "question": "生态系统中生产者是：", "options": ["动物", "植物", "细菌", "真菌"], "answer": "B"},
    {"id": 41, "name": "新陈代谢", "category": "生物", "difficulty": "中等",
     "question": "有氧呼吸的主要场所是：", "options": ["细胞核", "线粒体", "叶绿体", "核糖体"], "answer": "B"},
    {"id": 42, "name": "神经系统", "category": "生物", "difficulty": "简单",
     "question": "人体神经系统的基本单位是：", "options": ["神经元", "神经纤维", "突触", "神经节"], "answer": "A"},
    {"id": 43, "name": "血型", "category": "生物", "difficulty": "中等",
     "question": "AB型血的人可以接受什么血型的血液？", "options": ["只能AB型", "A型和B型", "A型、B型、AB型、O型", "只能O型"], "answer": "C"},
    {"id": 44, "name": "DNA复制", "category": "生物", "difficulty": "困难",
     "question": "DNA复制方式是：", "options": ["全保留", "半保留", "分散", "随机"], "answer": "B"},
    {"id": 45, "name": "食物链", "category": "生物", "difficulty": "简单",
     "question": "食物链中箭头的方向表示：", "options": ["能量流动", "物质循环", "信息传递", "捕食关系"], "answer": "A"},

    # ===== 地理常识 (15题) =====
    {"id": 46, "name": "地球", "category": "地理", "difficulty": "简单",
     "question": "地球表面积约多少亿平方公里？", "options": ["3.1", "4.1", "5.1", "6.1"], "answer": "C"},
    {"id": 47, "name": "大气层", "category": "地理", "difficulty": "中等",
     "question": "大气层中最靠近地面的一层是：", "options": ["平流层", "对流层", "中间层", "热层"], "answer": "B"},
    {"id": 48, "name": "板块构造", "category": "地理", "difficulty": "中等",
     "question": "板块构造学说认为地壳由什么组成？", "options": ["一整块", "若干板块", "无数小岛", "液态岩浆"], "answer": "B"},
    {"id": 49, "name": "洋流", "category": "地理", "difficulty": "中等",
     "question": "世界上最大的暖流是：", "options": ["千岛寒流", "墨西哥湾暖流", "秘鲁寒流", "西风漂流"], "answer": "B"},
    {"id": 50, "name": "气候", "category": "地理", "difficulty": "简单",
     "question": "赤道附近的气候类型主要是：", "options": ["热带沙漠", "热带雨林", "温带季风", "极地气候"], "answer": "B"},
    {"id": 51, "name": "地震", "category": "地理", "difficulty": "中等",
     "question": "地震震级相差1级，能量相差约多少倍？", "options": ["10", "30", "100", "1000"], "answer": "B"},
    {"id": 52, "name": "河流", "category": "地理", "difficulty": "简单",
     "question": "世界上最长的河流是：", "options": ["长江", "尼罗河", "亚马逊河", "密西西比河"], "answer": "B"},
    {"id": 53, "name": "山脉", "category": "地理", "difficulty": "简单",
     "question": "世界上最高的山峰是：", "options": ["K2", "珠穆朗玛峰", "富士山", "乞力马扎罗山"], "answer": "B"},
    {"id": 54, "name": "时区", "category": "地理", "difficulty": "简单",
     "question": "全球共分为多少个时区？", "options": ["12", "24", "36", "48"], "answer": "B"},
    {"id": 55, "name": "五带", "category": "地理", "difficulty": "中等",
     "question": "回归线是热带和什么的分界线？", "options": ["北温带和北寒带", "南温带和南寒带", "温带和寒带", "热带和温带"], "answer": "D"},
    {"id": 56, "name": "水循环", "category": "地理", "difficulty": "简单",
     "question": "水循环的主要动力是：", "options": ["重力", "太阳辐射", "地转偏向力", "风力"], "answer": "B"},
    {"id": 57, "name": "人口", "category": "地理", "difficulty": "简单",
     "question": "世界上人口最多的国家是：", "options": ["中国", "印度", "美国", "印度尼西亚"], "answer": "B"},
    {"id": 58, "name": "岩石", "category": "地理", "difficulty": "中等",
     "question": "三大类岩石不包括：", "options": ["岩浆岩", "沉积岩", "变质岩", "化石岩"], "answer": "D"},
    {"id": 59, "name": "季风", "category": "地理", "difficulty": "中等",
     "question": "东亚季风夏季吹什么方向的风？", "options": ["东北", "东南", "西北", "西南"], "answer": "B"},
    {"id": 60, "name": "自然资源", "category": "地理", "difficulty": "简单",
     "question": "以下哪种是可再生资源？", "options": ["石油", "煤炭", "天然气", "太阳能"], "answer": "D"},

    # ===== 历史常识 (15题) =====
    {"id": 61, "name": "四大文明", "category": "历史", "difficulty": "简单",
     "question": "四大文明古国不包括：", "options": ["古埃及", "古巴比伦", "古希腊", "古印度"], "answer": "C"},
    {"id": 62, "name": "工业革命", "category": "历史", "difficulty": "中等",
     "question": "第一次工业革命首先发生在哪个国家？", "options": ["法国", "德国", "英国", "美国"], "answer": "C"},
    {"id": 63, "name": "二战", "category": "历史", "difficulty": "简单",
     "question": "第二次世界大战结束于哪一年？", "options": ["1943", "1944", "1945", "1946"], "answer": "C"},
    {"id": 64, "name": "文艺复兴", "category": "历史", "difficulty": "中等",
     "question": "文艺复兴运动起源于哪个国家？", "options": ["法国", "英国", "德国", "意大利"], "answer": "D"},
    {"id": 65, "name": "法国大革命", "category": "历史", "difficulty": "中等",
     "question": "法国大革命爆发于哪一年？", "options": ["1787", "1788", "1789", "1790"], "answer": "C"},
    {"id": 66, "name": "冷战", "category": "历史", "difficulty": "简单",
     "question": "冷战时期两个超级大国是：", "options": ["美国和英国", "美国和苏联", "苏联和中国", "英国和法国"], "answer": "B"},
    {"id": 67, "name": "丝绸之路", "category": "历史", "difficulty": "中等",
     "question": "丝绸之路的起点是：", "options": ["洛阳", "西安", "北京", "南京"], "answer": "B"},
    {"id": 68, "name": "印刷术", "category": "历史", "difficulty": "简单",
     "question": "活字印刷术是谁发明的？", "options": ["蔡伦", "毕昇", "沈括", "宋应星"], "answer": "B"},
    {"id": 69, "name": "美国独立", "category": "历史", "difficulty": "中等",
     "question": "美国独立宣言发表于哪一年？", "options": ["1774", "1775", "1776", "1777"], "answer": "C"},
    {"id": 70, "name": "联合国的成立", "category": "历史", "difficulty": "中等",
     "question": "联合国成立于哪一年？", "options": ["1943", "1944", "1945", "1946"], "answer": "C"},
    {"id": 71, "name": "明治维新", "category": "历史", "difficulty": "中等",
     "question": "日本明治维新开始于哪一年？", "options": ["1865", "1866", "1867", "1868"], "answer": "D"},
    {"id": 72, "name": "辛亥革命", "category": "历史", "difficulty": "简单",
     "question": "辛亥革命爆发于哪一年？", "options": ["1909", "1910", "1911", "1912"], "answer": "C"},
    {"id": 73, "name": "大航海时代", "category": "历史", "difficulty": "中等",
     "question": "发现新大陆的航海家是：", "options": ["麦哲伦", "达·伽马", "哥伦布", "迪亚士"], "answer": "C"},
    {"id": 74, "name": "启蒙运动", "category": "历史", "difficulty": "困难",
     "question": "以下哪位不是启蒙思想家？", "options": ["伏尔泰", "卢梭", "孟德斯鸠", "达芬奇"], "answer": "D"},
    {"id": 75, "name": "柏林墙", "category": "历史", "difficulty": "中等",
     "question": "柏林墙倒塌于哪一年？", "options": ["1987", "1988", "1989", "1990"], "answer": "C"},

    # ===== 政治经济 (15题) =====
    {"id": 76, "name": "国家结构", "category": "政治", "difficulty": "简单",
     "question": "中国的国家结构形式是：", "options": ["单一制", "联邦制", "邦联制", "复合制"], "answer": "A"},
    {"id": 77, "name": "市场经济", "category": "经济", "difficulty": "中等",
     "question": '"看不见的手"是指：', "options": ["政府干预", "市场机制", "计划调控", "国际贸易"], "answer": "B"},
    {"id": 78, "name": "通货膨胀", "category": "经济", "difficulty": "中等",
     "question": "通货膨胀指的是：", "options": ["物价普遍下降", "物价普遍上涨", "货币升值", "经济增长"], "answer": "B"},
    {"id": 79, "name": "GDP", "category": "经济", "difficulty": "简单",
     "question": "GDP是指：", "options": ["国民生产总值", "国内生产总值", "国民收入", "人均收入"], "answer": "B"},
    {"id": 80, "name": "货币政策", "category": "经济", "difficulty": "中等",
     "question": "中央银行提高利率是为了：", "options": ["刺激经济", "抑制通胀", "增加就业", "扩大出口"], "answer": "B"},
    {"id": 81, "name": "比较优势", "category": "经济", "difficulty": "困难",
     "question": "国际贸易中的比较优势理论是谁提出的？", "options": ["亚当·斯密", "大卫·李嘉图", "凯恩斯", "弗里德曼"], "answer": "B"},
    {"id": 82, "name": "供给侧改革", "category": "经济", "difficulty": "中等",
     "question": "供给侧改革主要侧重于：", "options": ["刺激需求", "优化供给", "扩大出口", "增加投资"], "answer": "B"},
    {"id": 83, "name": "基尼系数", "category": "经济", "difficulty": "中等",
     "question": "基尼系数衡量的是：", "options": ["经济增长", "通货膨胀", "收入分配", "失业率"], "answer": "C"},
    {"id": 84, "name": "三权分立", "category": "政治", "difficulty": "中等",
     "question": "三权分立不包括：", "options": ["立法权", "行政权", "司法权", "军权"], "answer": "D"},
    {"id": 85, "name": "社会保障", "category": "政治", "difficulty": "简单",
     "question": "五险一金中的'一金'是指：", "options": ["养老保险", "医疗保险", "住房公积金", "失业保险"], "answer": "C"},
    {"id": 86, "name": "汇率", "category": "经济", "difficulty": "中等",
     "question": "本币贬值有利于：", "options": ["进口", "出口", "旅游出国", "购买外国资产"], "answer": "B"},
    {"id": 87, "name": "垄断", "category": "经济", "difficulty": "中等",
     "question": "反垄断法主要针对：", "options": ["小企业", "大企业", "垄断行为", "所有企业"], "answer": "C"},
    {"id": 88, "name": "一带一路", "category": "政治", "difficulty": "简单",
     "question": "'一带一路'中的'一路'是指：", "options": ["丝绸之路经济带", "21世纪海上丝绸之路", "长江经济带", "沿海开放带"], "answer": "B"},
    {"id": 89, "name": "WTO", "category": "经济", "difficulty": "简单",
     "question": "WTO是指：", "options": ["世界银行", "国际货币基金组织", "世界贸易组织", "世界卫生组织"], "answer": "C"},
    {"id": 90, "name": "恩格尔系数", "category": "经济", "difficulty": "中等",
     "question": "恩格尔系数越低说明：", "options": ["越贫穷", "越富裕", "食品越贵", "食品越便宜"], "answer": "B"},

    # ===== 生活常识 (10题) =====
    {"id": 91, "name": "食品安全", "category": "生活", "difficulty": "简单",
     "question": "食品保质期是指：", "options": ["生产日期", "最佳食用期", "必须丢弃日期", "销售截止日期"], "answer": "B"},
    {"id": 92, "name": "急救", "category": "生活", "difficulty": "中等",
     "question": "心肺复苏时按压与人工呼吸的比例是：", "options": ["15:1", "30:1", "30:2", "15:2"], "answer": "C"},
    {"id": 93, "name": "消防安全", "category": "生活", "difficulty": "简单",
     "question": "电器着火首先应该：", "options": ["用水扑灭", "切断电源", "用灭火器", "报警"], "answer": "B"},
    {"id": 94, "name": "营养", "category": "生活", "difficulty": "中等",
     "question": "人体必需的六大营养素不包括：", "options": ["蛋白质", "脂肪", "氧气", "维生素"], "answer": "C"},
    {"id": 95, "name": "垃圾分类", "category": "生活", "difficulty": "简单",
     "question": "废旧电池属于：", "options": ["可回收物", "有害垃圾", "厨余垃圾", "其他垃圾"], "answer": "B"},
    {"id": 96, "name": "交通", "category": "生活", "difficulty": "简单",
     "question": "高速公路最高时速一般限制为：", "options": ["100", "110", "120", "130"], "answer": "C"},
    {"id": 97, "name": "金融", "category": "生活", "difficulty": "中等",
     "question": "信用卡免息期内还款需要支付利息吗？", "options": ["需要", "不需要", "部分需要", "看银行"], "answer": "B"},
    {"id": 98, "name": "法律", "category": "生活", "difficulty": "简单",
     "question": "我国成年年龄是：", "options": ["16", "18", "20", "22"], "answer": "B"},
    {"id": 99, "name": "健康", "category": "生活", "difficulty": "中等",
     "question": "成年人正常血压范围是收缩压：", "options": ["60-90", "90-120", "120-140", "140-160"], "answer": "B"},
    {"id": 100, "name": "消费", "category": "生活", "difficulty": "简单",
     "question": "消费者权益保护法规定的退货期限是：", "options": ["3天", "7天", "15天", "30天"], "answer": "B"},
]


class CommonsenseEvaluator(BaseEvaluator):
    """常识问答能力评估器"""

    name = "commonsense"
    description = "常识问答测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-常识问答"

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
        """运行常识问答测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in COMMONSENSE_TEST_CASES:
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
        """测试单个常识问答用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        options_str = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case['options'])])
        prompt = f"回答以下常识问题，只输出选项字母(A/B/C/D)：\n\n{test_case['question']}\n\n{options_str}\n\n答案："

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个知识渊博的专家。只回答选项字母，不要解释。"},
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
            }, test_type="commonsense_stage3")

            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "difficulty": test_case['difficulty'],
                    "expected": expected,
                    "actual": answer
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


def run_commonsense_test(model_url: str, model_name: str) -> dict:
    """运行常识问答测试"""
    evaluator = CommonsenseEvaluator(model_url, model_name)
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
    result = run_commonsense_test("http://localhost:8400", "Qwen3VL-4B-Instruct-Q8_0")
    print(f"常识问答测试: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
