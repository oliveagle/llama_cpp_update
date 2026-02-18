#!/usr/bin/env python3
"""
Stage 3 深度知识问答测试 (100 cases)
涵盖：科学技术、历史文化、地理政治、艺术文学、经济金融、医学健康、法律政策等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 知识问答测试用例 (100个)
KNOWLEDGE_TEST_CASES = [
    # ===== 科学技术 (20题) =====
    {"id": 1, "name": "光速", "category": "科学技术", "difficulty": "简单",
     "question": "光在真空中的传播速度约为多少？",
     "options": ["3×10^6 m/s", "3×10^8 m/s", "3×10^10 m/s", "3×10^12 m/s"],
     "answer": "B", "explanation": "光速约为3×10^8 m/s"},
    {"id": 2, "name": "DNA结构", "category": "科学技术", "difficulty": "简单",
     "question": "DNA的双螺旋结构是由谁发现的？",
     "options": ["达尔文", "沃森和克里克", "孟德尔", "爱因斯坦"],
     "answer": "B", "explanation": "Watson和Crick于1953年发现"},
    {"id": 3, "name": "元素周期表", "category": "科学技术", "difficulty": "中等",
     "question": "元素周期表中，原子序数为1的元素是？",
     "options": ["氧", "氢", "氦", "碳"],
     "answer": "B", "explanation": "氢原子序数为1"},
    {"id": 4, "name": "牛顿定律", "category": "科学技术", "difficulty": "中等",
     "question": "牛顿第二定律的公式是？",
     "options": ["F=ma", "E=mc²", "F=G(m1m2)/r²", "p=mv"],
     "answer": "A", "explanation": "F=ma，力=质量×加速度"},
    {"id": 5, "name": "相对论", "category": "科学技术", "difficulty": "中等",
     "question": "质能方程E=mc²中的c代表什么？",
     "options": ["电荷", "光速", "比热容", "电容"],
     "answer": "B", "explanation": "c是光速"},
    {"id": 6, "name": "细胞结构", "category": "科学技术", "difficulty": "中等",
     "question": "植物细胞与动物细胞相比，特有的结构是？",
     "options": ["细胞核", "线粒体", "细胞壁和叶绿体", "细胞膜"],
     "answer": "C", "explanation": "植物细胞有细胞壁和叶绿体"},
    {"id": 7, "name": "量子力学", "category": "科学技术", "difficulty": "困难",
     "question": "海森堡不确定性原理指出不能同时精确测量？",
     "options": ["质量和能量", "位置和动量", "时间和空间", "电荷和质量"],
     "answer": "B", "explanation": "不能同时精确知道位置和动量"},
    {"id": 8, "name": "进化论", "category": "科学技术", "difficulty": "简单",
     "question": "自然选择学说是谁提出的？",
     "options": ["拉马克", "达尔文", "孟德尔", "摩尔根"],
     "answer": "B", "explanation": "达尔文提出自然选择"},
    {"id": 9, "name": "计算机基础", "category": "科学技术", "difficulty": "简单",
     "question": "计算机中最小的存储单位是？",
     "options": ["字节(Byte)", "位(Bit)", "千字节(KB)", "兆字节(MB)"],
     "answer": "B", "explanation": "位(bit)是最小单位"},
    {"id": 10, "name": "互联网协议", "category": "科学技术", "difficulty": "中等",
     "question": "IP地址192.168.1.1属于哪类地址？",
     "options": ["A类公网", "B类公网", "C类公网", "C类私网"],
     "answer": "D", "explanation": "192.168.x.x是C类私有地址"},
    {"id": 11, "name": "化学反应", "category": "科学技术", "difficulty": "中等",
     "question": "水的化学式是？",
     "options": ["CO2", "H2O", "O2", "NaCl"],
     "answer": "B", "explanation": "水H2O"},
    {"id": 12, "name": "天文学", "category": "科学技术", "difficulty": "中等",
     "question": "太阳系中最大的行星是？",
     "options": ["地球", "土星", "木星", "火星"],
     "answer": "C", "explanation": "木星最大"},
    {"id": 13, "name": "人工智能", "category": "科学技术", "difficulty": "中等",
     "question": "深度学习中的'深度'主要指什么？",
     "options": ["数据量大", "网络层数多", "训练时间长", "参数多"],
     "answer": "B", "explanation": "指神经网络层数深"},
    {"id": 14, "name": "半导体", "category": "科学技术", "difficulty": "困难",
     "question": "现代CPU主要使用什么材料制造？",
     "options": ["铜", "铝", "硅", "锗"],
     "answer": "C", "explanation": "硅是主要半导体材料"},
    {"id": 15, "name": "基因编辑", "category": "科学技术", "difficulty": "困难",
     "question": "CRISPR-Cas9技术用于？",
     "options": ["基因测序", "基因编辑", "蛋白质合成", "细胞培养"],
     "answer": "B", "explanation": "CRISPR是基因编辑技术"},
    {"id": 16, "name": "热力学", "category": "科学技术", "difficulty": "困难",
     "question": "热力学第二定律指出热量不能自发从？",
     "options": ["高温到低温", "低温到高温", "固体到液体", "气体到固体"],
     "answer": "B", "explanation": "不能自发从低温到高温"},
    {"id": 17, "name": "电磁波", "category": "科学技术", "difficulty": "中等",
     "question": "可见光在电磁波谱中位于？",
     "options": ["无线电波和微波之间", "微波和红外线之间", "红外线和紫外线之间", "紫外线和X射线之间"],
     "answer": "C", "explanation": "可见光在红光和紫外之间"},
    {"id": 18, "name": "操作系统", "category": "科学技术", "difficulty": "中等",
     "question": "Linux系统的内核创始人是？",
     "options": ["比尔盖茨", "乔布斯", "林纳斯·托瓦兹", "肯·汤普森"],
     "answer": "C", "explanation": "Linus Torvalds创建Linux"},
    {"id": 19, "name": "区块链技术", "category": "科学技术", "difficulty": "困难",
     "question": "区块链的核心技术不包括？",
     "options": ["分布式账本", "共识机制", "密码学", "中心化管理"],
     "answer": "D", "explanation": "区块链是去中心化"},
    {"id": 20, "name": "航天科技", "category": "科学技术", "difficulty": "中等",
     "question": "中国第一艘载人飞船是？",
     "options": ["神舟一号", "神舟三号", "神舟五号", "神舟七号"],
     "answer": "C", "explanation": "神舟五号，杨利伟首飞"},

    # ===== 历史文化 (20题) =====
    {"id": 21, "name": "四大发明", "category": "历史文化", "difficulty": "简单",
     "question": "中国古代四大发明不包括？",
     "options": ["造纸术", "指南针", "火药", "地动仪"],
     "answer": "D", "explanation": "四大发明：造纸、指南针、火药、印刷"},
    {"id": 22, "name": "文艺复兴", "category": "历史文化", "difficulty": "中等",
     "question": "文艺复兴运动起源于哪个国家？",
     "options": ["法国", "英国", "意大利", "德国"],
     "answer": "C", "explanation": "起源于意大利"},
    {"id": 23, "name": "秦朝统一", "category": "历史文化", "difficulty": "简单",
     "question": "秦始皇统一六国是在哪一年？",
     "options": ["公元前221年", "公元前210年", "公元221年", "公元210年"],
     "answer": "A", "explanation": "公元前221年统一"},
    {"id": 24, "name": "二战结束", "category": "历史文化", "difficulty": "中等",
     "question": "第二次世界大战结束于哪一年？",
     "options": ["1943年", "1944年", "1945年", "1946年"],
     "answer": "C", "explanation": "1945年结束"},
    {"id": 25, "name": "工业革命", "category": "历史文化", "difficulty": "中等",
     "question": "第一次工业革命首先发生在哪个国家？",
     "options": ["美国", "法国", "英国", "德国"],
     "answer": "C", "explanation": "英国率先工业化"},
    {"id": 26, "name": "丝绸之路", "category": "历史文化", "difficulty": "中等",
     "question": "古代丝绸之路的起点是？",
     "options": ["洛阳", "长安(西安)", "敦煌", "兰州"],
     "answer": "B", "explanation": "起点是长安"},
    {"id": 27, "name": "美国独立", "category": "历史文化", "difficulty": "中等",
     "question": "美国独立战争开始的标志是？",
     "options": ["波士顿倾茶事件", "莱克星顿枪声", "独立宣言发表", "约克镇战役"],
     "answer": "B", "explanation": "1775年莱克星顿枪声"},
    {"id": 28, "name": "法国大革命", "category": "历史文化", "difficulty": "中等",
     "question": "法国大革命爆发的年份是？",
     "options": ["1787年", "1788年", "1789年", "1790年"],
     "answer": "C", "explanation": "1789年攻占巴士底狱"},
    {"id": 29, "name": "唐朝盛世", "category": "历史文化", "difficulty": "中等",
     "question": "唐朝的鼎盛时期被称为什么？",
     "options": ["文景之治", "贞观之治", "开元盛世", "康乾盛世"],
     "answer": "C", "explanation": "唐玄宗开元盛世"},
    {"id": 30, "name": "冷战", "category": "历史文化", "difficulty": "中等",
     "question": "冷战期间两大对立阵营的领导国是？",
     "options": ["美国和英国", "美国和苏联", "苏联和中国", "英国和法国"],
     "answer": "B", "explanation": "美苏两极对立"},
    {"id": 31, "name": "明朝迁都", "category": "历史文化", "difficulty": "中等",
     "question": "明成祖朱棣将都城迁到哪里？",
     "options": ["南京", "北京", "西安", "开封"],
     "answer": "B", "explanation": "迁都北京"},
    {"id": 32, "name": "古希腊", "category": "历史文化", "difficulty": "中等",
     "question": "古代奥运会起源于哪个国家？",
     "options": ["罗马", "埃及", "希腊", "波斯"],
     "answer": "C", "explanation": "起源于古希腊"},
    {"id": 33, "name": "辛亥革命", "category": "历史文化", "difficulty": "简单",
     "question": "辛亥革命爆发于哪一年？",
     "options": ["1909年", "1910年", "1911年", "1912年"],
     "answer": "C", "explanation": "1911年武昌起义"},
    {"id": 34, "name": "罗马帝国的衰落", "category": "历史文化", "difficulty": "困难",
     "question": "西罗马帝国灭亡于哪一年？",
     "options": ["376年", "410年", "455年", "476年"],
     "answer": "D", "explanation": "476年被日耳曼人灭亡"},
    {"id": 35, "name": "郑和下西洋", "category": "历史文化", "difficulty": "中等",
     "question": "郑和下西洋发生在哪个朝代？",
     "options": ["唐朝", "宋朝", "元朝", "明朝"],
     "answer": "D", "explanation": "明成祖时期"},
    {"id": 36, "name": "启蒙运动", "category": "历史文化", "difficulty": "困难",
     "question": "启蒙运动的中心在哪个国家？",
     "options": ["英国", "德国", "法国", "美国"],
     "answer": "C", "explanation": "法国是启蒙运动中心"},
    {"id": 37, "name": "二战转折点", "category": "历史文化", "difficulty": "中等",
     "question": "第二次世界大战的转折点是？",
     "options": ["诺曼底登陆", "斯大林格勒战役", "珍珠港事件", "中途岛海战"],
     "answer": "B", "explanation": "斯大林格勒战役是苏德战场转折点"},
    {"id": 38, "name": "玛雅文明", "category": "历史文化", "difficulty": "困难",
     "question": "玛雅文明主要分布在现在的哪个地区？",
     "options": ["南美洲安第斯山区", "中美洲墨西哥和危地马拉", "北美洲", "加勒比海"],
     "answer": "B", "explanation": "中美洲地区"},
    {"id": 39, "name": "百家争鸣", "category": "历史文化", "difficulty": "中等",
     "question": "百家争鸣主要发生在哪个时期？",
     "options": ["春秋战国时期", "秦汉时期", "唐宋时期", "明清时期"],
     "answer": "A", "explanation": "春秋战国时期"},
    {"id": 40, "name": "欧盟成立", "category": "历史文化", "difficulty": "中等",
     "question": "欧盟正式成立于哪一年？",
     "options": ["1957年", "1991年", "1993年", "1999年"],
     "answer": "C", "explanation": "1993年马约生效"},

    # ===== 地理政治 (15题) =====
    {"id": 41, "name": "世界最高峰", "category": "地理政治", "difficulty": "简单",
     "question": "世界最高峰是？",
     "options": ["乔戈里峰", "珠穆朗玛峰", "干城章嘉峰", "洛子峰"],
     "answer": "B", "explanation": "珠穆朗玛峰"},
    {"id": 42, "name": "最长河流", "category": "地理政治", "difficulty": "中等",
     "question": "世界上最长的河流是？",
     "options": ["亚马逊河", "尼罗河", "长江", "密西西比河"],
     "answer": "B", "explanation": "尼罗河最长(传统观点)"},
    {"id": 43, "name": "联合国", "category": "地理政治", "difficulty": "简单",
     "question": "联合国总部位于哪个城市？",
     "options": ["华盛顿", "伦敦", "日内瓦", "纽约"],
     "answer": "D", "explanation": "纽约"},
    {"id": 44, "name": "最大海洋", "category": "地理政治", "difficulty": "简单",
     "question": "世界最大的海洋是？",
     "options": ["大西洋", "印度洋", "太平洋", "北冰洋"],
     "answer": "C", "explanation": "太平洋最大"},
    {"id": 45, "name": "金砖国家", "category": "地理政治", "difficulty": "中等",
     "question": "以下哪个国家不属于金砖国家(BRICS)？",
     "options": ["巴西", "俄罗斯", "日本", "中国"],
     "answer": "C", "explanation": "日本不属于金砖"},
    {"id": 46, "name": "撒哈拉沙漠", "category": "地理政治", "difficulty": "中等",
     "question": "撒哈拉沙漠位于哪个大洲？",
     "options": ["亚洲", "非洲", "南美洲", "澳洲"],
     "answer": "B", "explanation": "非洲北部"},
    {"id": 47, "name": "北约", "category": "地理政治", "difficulty": "中等",
     "question": "北约(NATO)总部设在哪个国家？",
     "options": ["美国", "英国", "法国", "比利时"],
     "answer": "D", "explanation": "比利时布鲁塞尔"},
    {"id": 48, "name": "亚马逊雨林", "category": "地理政治", "difficulty": "简单",
     "question": "亚马逊雨林主要分布在哪个国家？",
     "options": ["巴西", "秘鲁", "哥伦比亚", "厄瓜多尔"],
     "answer": "A", "explanation": "主要在巴西"},
    {"id": 49, "name": "G7峰会", "category": "地理政治", "difficulty": "困难",
     "question": "G7包括以下哪七个国家？",
     "options": ["美英德法日意加", "美中德法日意俄", "美英德法日中加", "美英德法日意澳"],
     "answer": "A", "explanation": "G7不含中俄澳"},
    {"id": 50, "name": "地中海", "category": "地理政治", "difficulty": "中等",
     "question": "地中海通过什么海峡与大西洋相连？",
     "options": ["英吉利海峡", "直布罗陀海峡", "马六甲海峡", "土耳其海峡"],
     "answer": "B", "explanation": "直布罗陀海峡"},
    {"id": 51, "name": "安理会", "category": "地理政治", "difficulty": "中等",
     "question": "联合国安理会常任理事国有几个？",
     "options": ["3个", "4个", "5个", "6个"],
     "answer": "C", "explanation": "中美俄英法五常"},
    {"id": 52, "name": "赤道穿过", "category": "地理政治", "difficulty": "中等",
     "question": "赤道穿过以下哪个国家？",
     "options": ["中国", "印度", "巴西", "澳大利亚"],
     "answer": "C", "explanation": "赤道穿过巴西"},
    {"id": 53, "name": "欧盟总部", "category": "地理政治", "difficulty": "中等",
     "question": "欧盟委员会总部位于哪个城市？",
     "options": ["巴黎", "柏林", "布鲁塞尔", "阿姆斯特丹"],
     "answer": "C", "explanation": "布鲁塞尔"},
    {"id": 54, "name": "死海", "category": "地理政治", "difficulty": "中等",
     "question": "死海位于哪个地区？",
     "options": ["非洲", "中东", "中亚", "欧洲"],
     "answer": "B", "explanation": "中东地区(以色列/约旦)"},
    {"id": 55, "name": "APEC", "category": "地理政治", "difficulty": "困难",
     "question": "APEC的全称是？",
     "options": ["亚太经合组织", "东盟", "上合组织", "非盟"],
     "answer": "A", "explanation": "Asia-Pacific Economic Cooperation"},

    # ===== 艺术文学 (15题) =====
    {"id": 56, "name": "莎士比亚", "category": "艺术文学", "difficulty": "简单",
     "question": "莎士比亚的四大悲剧不包括？",
     "options": ["哈姆雷特", "李尔王", "罗密欧与朱丽叶", "奥赛罗"],
     "answer": "C", "explanation": "罗密欧与朱丽叶不是四大悲剧"},
    {"id": 57, "name": "蒙娜丽莎", "category": "艺术文学", "difficulty": "简单",
     "question": "《蒙娜丽莎》的作者是谁？",
     "options": ["梵高", "毕加索", "达芬奇", "米开朗基罗"],
     "answer": "C", "explanation": "达芬奇作品"},
    {"id": 58, "name": "红楼梦", "category": "艺术文学", "difficulty": "中等",
     "question": "《红楼梦》的作者是谁？",
     "options": ["曹雪芹", "罗贯中", "施耐庵", "吴承恩"],
     "answer": "A", "explanation": "曹雪芹著"},
    {"id": 59, "name": "贝多芬", "category": "艺术文学", "difficulty": "中等",
     "question": "贝多芬的第五交响曲又称什么？",
     "options": ["田园", "命运", "英雄", "合唱"],
     "answer": "B", "explanation": "命运交响曲"},
    {"id": 60, "name": "李白", "category": "艺术文学", "difficulty": "简单",
     "question": "李白被称为什么？",
     "options": ["诗圣", "诗仙", "诗佛", "诗鬼"],
     "answer": "B", "explanation": "诗仙李白"},
    {"id": 61, "name": "印象派", "category": "艺术文学", "difficulty": "中等",
     "question": "印象派绘画的代表人物是？",
     "options": ["梵高", "莫奈", "毕加索", "达芬奇"],
     "answer": "B", "explanation": "莫奈是印象派代表"},
    {"id": 62, "name": "交响乐", "category": "艺术文学", "difficulty": "困难",
     "question": "标准交响乐队中，哪个乐器组人数最多？",
     "options": ["铜管", "木管", "弦乐", "打击乐"],
     "answer": "C", "explanation": "弦乐组人数最多"},
    {"id": 63, "name": "鲁迅", "category": "艺术文学", "difficulty": "中等",
     "question": "鲁迅的第一篇白话小说是？",
     "options": ["阿Q正传", "狂人日记", "药", "祝福"],
     "answer": "B", "explanation": "狂人日记"},
    {"id": 64, "name": "芭蕾", "category": "艺术文学", "difficulty": "中等",
     "question": "芭蕾舞起源于哪个国家？",
     "options": ["法国", "俄罗斯", "意大利", "奥地利"],
     "answer": "C", "explanation": "起源于意大利文艺复兴时期"},
    {"id": 65, "name": "唐诗宋词", "category": "艺术文学", "difficulty": "中等",
     "question": "宋词分为哪两大流派？",
     "options": ["豪放派和婉约派", "写实派和浪漫派", "山水派和田园派", "边塞派和闺怨派"],
     "answer": "A", "explanation": "豪放与婉约"},
    {"id": 66, "name": "毕加索", "category": "艺术文学", "difficulty": "中等",
     "question": "毕加索是哪个艺术流派的代表？",
     "options": ["印象派", "立体主义", "超现实主义", "抽象派"],
     "answer": "B", "explanation": "立体主义创始人"},
    {"id": 67, "name": "宫崎骏", "category": "艺术文学", "difficulty": "简单",
     "question": "宫崎骏是哪家动画工作室的创始人之一？",
     "options": ["东映", "吉卜力", "京都动画", "骨头社"],
     "answer": "B", "explanation": "吉卜力工作室"},
    {"id": 68, "name": "古希腊悲剧", "category": "艺术文学", "difficulty": "困难",
     "question": "古希腊三大悲剧家不包括？",
     "options": ["埃斯库罗斯", "索福克勒斯", "欧里庇得斯", "阿里斯托芬"],
     "answer": "D", "explanation": "阿里斯托芬是喜剧家"},
    {"id": 69, "name": "书法", "category": "艺术文学", "difficulty": "中等",
     "question": "中国书法五体不包括？",
     "options": ["楷书", "行书", "草书", "美术字"],
     "answer": "D", "explanation": "五体：篆隶楷行草"},
    {"id": 70, "name": "交响乐之父", "category": "艺术文学", "difficulty": "困难",
     "question": "被称为'交响乐之父'的是？",
     "options": ["莫扎特", "贝多芬", "海顿", "巴赫"],
     "answer": "C", "explanation": "海顿被称为交响乐之父"},

    # ===== 经济金融 (15题) =====
    {"id": 71, "name": "GDP", "category": "经济金融", "difficulty": "简单",
     "question": "GDP的中文全称是？",
     "options": ["国内生产总值", "国民生产总值", "国民收入", "国内收入"],
     "answer": "A", "explanation": "国内生产总值"},
    {"id": 72, "name": "通货膨胀", "category": "经济金融", "difficulty": "中等",
     "question": "通货膨胀是指？",
     "options": ["物价普遍持续上涨", "物价普遍持续下跌", "经济增长", "货币升值"],
     "answer": "A", "explanation": "物价普遍持续上涨"},
    {"id": 73, "name": "中央银行", "category": "经济金融", "difficulty": "中等",
     "question": "中国的中央银行是？",
     "options": ["中国银行", "工商银行", "中国人民银行", "建设银行"],
     "answer": "C", "explanation": "中国人民银行"},
    {"id": 74, "name": "股票市场", "category": "经济金融", "difficulty": "中等",
     "question": "股票市场中'牛市'指？",
     "options": ["股市上涨", "股市下跌", "股市平稳", "股市关闭"],
     "answer": "A", "explanation": "牛市=上涨"},
    {"id": 75, "name": "利率", "category": "经济金融", "difficulty": "中等",
     "question": "央行提高基准利率通常是为了？",
     "options": ["刺激经济", "抑制通胀", "增加就业", "贬值货币"],
     "answer": "B", "explanation": "加息抑制通胀"},
    {"id": 76, "name": "复利", "category": "经济金融", "difficulty": "中等",
     "question": "复利与单利的区别在于？",
     "options": ["利率不同", "利息是否再生息", "期限不同", "本金不同"],
     "answer": "B", "explanation": "复利利滚利"},
    {"id": 77, "name": "汇率", "category": "经济金融", "difficulty": "中等",
     "question": "本币贬值有利于？",
     "options": ["进口", "出口", "旅游", "留学"],
     "answer": "B", "explanation": "贬值促进出口"},
    {"id": 78, "name": "股票指数", "category": "经济金融", "difficulty": "简单",
     "question": "美国道琼斯指数属于？",
     "options": ["债券指数", "股票指数", "商品指数", "汇率指数"],
     "answer": "B", "explanation": "股票指数"},
    {"id": 79, "name": "次贷危机", "category": "经济金融", "difficulty": "中等",
     "question": "2008年金融危机又称什么危机？",
     "options": ["互联网泡沫", "次贷危机", "石油危机", "欧债危机"],
     "answer": "B", "explanation": "次贷危机"},
    {"id": 80, "name": "供给侧改革", "category": "经济金融", "difficulty": "困难",
     "question": "供给侧改革主要侧重？",
     "options": ["刺激需求", "提高供给质量", "增加货币供应", "扩大出口"],
     "answer": "B", "explanation": "提高供给体系质量"},
    {"id": 81, "name": " cryptocurrency", "category": "经济金融", "difficulty": "中等",
     "question": "比特币基于什么技术？",
     "options": ["云计算", "区块链", "人工智能", "大数据"],
     "answer": "B", "explanation": "区块链技术"},
    {"id": 82, "name": "美联储", "category": "经济金融", "difficulty": "中等",
     "question": "美联储是美国的？",
     "options": ["商业银行", "中央银行", "投资银行", "政策性银行"],
     "answer": "B", "explanation": "美国中央银行"},
    {"id": 83, "name": "财务报表", "category": "经济金融", "difficulty": "困难",
     "question": "企业三大财务报表不包括？",
     "options": ["资产负债表", "利润表", "现金流量表", "税务报表"],
     "answer": "D", "explanation": "三大报表：资产负债、利润、现金流"},
    {"id": 84, "name": "货币政策", "category": "经济金融", "difficulty": "困难",
     "question": "量化宽松(QE)属于？",
     "options": ["财政政策", "货币政策", "产业政策", "贸易政策"],
     "answer": "B", "explanation": "非常规货币政策"},
    {"id": 85, "name": "IPO", "category": "经济金融", "difficulty": "简单",
     "question": "IPO的中文意思是？",
     "options": ["首次公开发行", "并购", "重组", "退市"],
     "answer": "A", "explanation": "Initial Public Offering"},

    # ===== 医学健康 (15题) =====
    {"id": 86, "name": "血液循环", "category": "医学健康", "difficulty": "简单",
     "question": "人体血液循环的主要动力器官是？",
     "options": ["肺", "心脏", "肝脏", "肾脏"],
     "answer": "B", "explanation": "心脏是血泵"},
    {"id": 87, "name": "免疫系统", "category": "医学健康", "difficulty": "中等",
     "question": "人体最大的免疫器官是？",
     "options": ["胸腺", "脾脏", "扁桃体", "淋巴结"],
     "answer": "B", "explanation": "脾脏是最大免疫器官"},
    {"id": 88, "name": "维生素", "category": "医学健康", "difficulty": "简单",
     "question": "缺乏维生素C会导致？",
     "options": ["夜盲症", "坏血病", "佝偻病", "脚气病"],
     "answer": "B", "explanation": "坏血病"},
    {"id": 89, "name": "血压", "category": "医学健康", "difficulty": "中等",
     "question": "正常成人的理想血压约为？",
     "options": ["90/60 mmHg", "120/80 mmHg", "140/90 mmHg", "160/100 mmHg"],
     "answer": "B", "explanation": "120/80左右"},
    {"id": 90, "name": "传染病", "category": "医学健康", "difficulty": "中等",
     "question": "以下哪种属于乙类传染病？",
     "options": ["流感", "鼠疫", "新冠肺炎", "手足口病"],
     "answer": "C", "explanation": "新冠属于乙类(按甲类管理)"},
    {"id": 91, "name": "糖尿病", "category": "医学健康", "difficulty": "中等",
     "question": "1型糖尿病主要是由于？",
     "options": ["胰岛素抵抗", "胰岛素分泌不足", "饮食不当", "肥胖"],
     "answer": "B", "explanation": "胰岛β细胞破坏"},
    {"id": 92, "name": "急救", "category": "医学健康", "difficulty": "简单",
     "question": "心肺复苏(CPR)的黄金时间是？",
     "options": ["1分钟内", "4-6分钟", "10分钟", "30分钟"],
     "answer": "B", "explanation": "4-6分钟内"},
    {"id": 93, "name": "疫苗", "category": "医学健康", "difficulty": "中等",
     "question": "疫苗的主要作用是？",
     "options": ["治疗疾病", "预防疾病", "缓解症状", "替代药物"],
     "answer": "B", "explanation": "预防性免疫"},
    {"id": 94, "name": "DNA", "category": "医学健康", "difficulty": "中等",
     "question": "DNA是主要的遗传物质，其全称是？",
     "options": ["核糖核酸", "脱氧核糖核酸", "蛋白质", "氨基酸"],
     "answer": "B", "explanation": "Deoxyribonucleic acid"},
    {"id": 95, "name": "抗生素", "category": "医学健康", "difficulty": "中等",
     "question": "抗生素对以下哪种疾病无效？",
     "options": ["肺炎", "流感", "肺结核", "尿路感染"],
     "answer": "B", "explanation": "流感是病毒，抗生素对病毒无效"},
    {"id": 96, "name": "癌症", "category": "医学健康", "difficulty": "困难",
     "question": "恶性肿瘤的主要特征是？",
     "options": ["生长缓慢", "有包膜", "浸润转移", "不会复发"],
     "answer": "C", "explanation": "浸润和转移"},
    {"id": 97, "name": "血型", "category": "医学健康", "difficulty": "简单",
     "question": "AB型血的人可以接受哪种血型？",
     "options": ["只能AB型", "A型和B型", "O型", "任何血型"],
     "answer": "D", "explanation": "AB型是万能受血者"},
    {"id": 98, "name": "脑卒中", "category": "医学健康", "difficulty": "中等",
     "question": "脑卒中又称？",
     "options": ["心脏病", "中风", "癫痫", "帕金森"],
     "answer": "B", "explanation": "俗称中风"},
    {"id": 99, "name": "睡眠质量", "category": "医学健康", "difficulty": "简单",
     "question": "成年人每天建议睡眠时间为？",
     "options": ["4-5小时", "6-7小时", "7-9小时", "10小时以上"],
     "answer": "C", "explanation": "7-9小时"},
    {"id": 100, "name": "病毒结构", "category": "医学健康", "difficulty": "困难",
     "question": "病毒的基本结构包括？",
     "options": ["细胞核和细胞质", "蛋白质外壳和核酸", "细胞膜和细胞壁", "线粒体和内质网"],
     "answer": "B", "explanation": "蛋白质衣壳+核酸核心"},
]


class KnowledgeEvaluator(BaseEvaluator):
    """知识问答能力评估器"""
    name = "knowledge"
    description = "深度知识问答测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-知识问答"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.6

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        self.raw_logger = RawDataLogger("stage3", "knowledge")

    def run_tests(self) -> StageResult:
        """运行知识问答测试"""
        passed = 0
        failed = 0
        results = []
        start_time = time.time()

        for test_case in KNOWLEDGE_TEST_CASES:
            result = self._test_single_case(test_case)
            results.append(result)

            if result.passed:
                passed += 1
            else:
                failed += 1

        duration = time.time() - start_time
        total = len(KNOWLEDGE_TEST_CASES)
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
        """测试单个知识用例"""
        import requests
        start_time = time.time()

        try:
            # 构建提示
            options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(test_case["options"])])
            prompt = f"""问题：{test_case['question']}

选项：
{options_text}

请直接回答选项字母(A/B/C/D)，不要解释。"""

            url = f"{self.model_url}/v1/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是一个知识问答专家。只回答选项字母，不要解释。"},
                    {"role": "user", "content": prompt}
                ],
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

            answer = self._extract_answer(content)
            correct = answer == test_case["answer"]

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "prompt": prompt,
                "expected": test_case["answer"],
                "actual": answer,
                "response": content,
                "passed": correct
            }, test_type="knowledge_stage3")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=correct,
                duration_ms=elapsed * 1000,
                details={"difficulty": test_case["difficulty"]},
                error_message=None if correct else f"期望: {test_case['answer']}, 实际: {answer}"
            )

        except Exception as e:
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_case_id": test_case["id"],
                "test_case_name": test_case["name"],
                "category": test_case["category"],
                "difficulty": test_case["difficulty"],
                "expected": test_case["answer"],
                "actual": "ERROR",
                "error": str(e)
            }, test_type="knowledge_stage3")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=False,
                duration_ms=(time.time() - start_time) * 1000,
                details={},
                error_message=str(e)
            )

    def _extract_answer(self, response: str) -> str:
        """从响应中提取答案字母，支持多种格式"""
        if not response:
            return ""
        text_upper = response.upper()

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
            match = re.search(pattern, text_upper)
            if match:
                return match.group(1)

        # 如果都没匹配到，找最后一个独立的 A-D 字母（通常在回答末尾）
        matches = re.findall(r'\b([A-D])\b', text_upper)
        if matches:
            return matches[-1]  # 返回最后一个匹配

        # 最后的备选：找第一个 A-D 字符
        match = re.search(r'[A-D]', text_upper)
        return match.group(0) if match else ""


def run_knowledge_test(model_url: str, model_name: str, **kwargs) -> StageResult:
    """运行知识问答测试的便捷函数"""
    evaluator = KnowledgeEvaluator(model_url, model_name, **kwargs)
    return evaluator.run_tests()


__all__ = [
    'KnowledgeEvaluator', 'run_knowledge_test',
    'KNOWLEDGE_TEST_CASES'
]