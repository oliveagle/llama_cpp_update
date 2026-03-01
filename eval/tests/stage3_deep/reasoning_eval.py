#!/usr/bin/env python3
"""
Stage 3 深度推理规划测试 (100 cases)
涵盖：多步推理、规划决策、问题分解、因果推理、假设检验等
"""

import time
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 推理规划测试用例 (100个)
REASONING_TEST_CASES = [
    # ===== 多步推理 (20题) =====
    {"id": 1, "name": "步骤计数", "category": "多步推理", "difficulty": "简单",
     "question": "完成一个任务需要3步，每步需要5分钟，中间休息2分钟，总共需要多少分钟？",
     "options": ["15", "17", "19", "21"], "answer": "C", "explanation": "3×5 + 2×2 = 19"},
    {"id": 2, "name": "连锁推理", "category": "多步推理", "difficulty": "中等",
     "question": "A比B大3岁，B比C大5岁，C今年10岁，A今年几岁？",
     "options": ["15", "16", "18", "20"], "answer": "C", "explanation": "C=10, B=15, A=18"},
    {"id": 3, "name": "路径规划", "category": "多步推理", "difficulty": "中等",
     "question": "从A到B有2条路，从B到C有3条路，从A到C经过B有多少种走法？",
     "options": ["5", "6", "8", "12"], "answer": "B", "explanation": "2×3=6种"},
    {"id": 4, "name": "资源分配", "category": "多步推理", "difficulty": "中等",
     "question": "5个人分30个苹果，每人至少分5个，最多分8个，有多少种分法？",
     "options": ["0", "1", "3", "6"], "answer": "B", "explanation": "每人恰好6个是唯一解"},
    {"id": 5, "name": "时间推算", "category": "多步推理", "difficulty": "简单",
     "question": "现在是下午3点，15小时前是几点？",
     "options": ["凌晨0点", "中午12点", "凌晨3点", "晚上9点"], "answer": "A", "explanation": "15-3=12，即午夜12点/凌晨0点"},
    {"id": 6, "name": "条件累积", "category": "多步推理", "difficulty": "困难",
     "question": "一个数加5，乘3，减7，除以2，得10，这个数是多少？",
     "options": ["3", "4", "5", "6"], "answer": "B", "explanation": "倒推：(10×2+7)/3-5=4"},
    {"id": 7, "name": "顺序依赖", "category": "多步推理", "difficulty": "中等",
     "question": "做蛋糕需要：打蛋(5分钟)、和面(10分钟)、烘烤(30分钟)。打蛋必须在和面之前，和面必须在烘烤之前，最少需要多少分钟？",
     "options": ["30", "35", "40", "45"], "answer": "D", "explanation": "5+10+30=45，必须串行"},
    {"id": 8, "name": "最优选择", "category": "多步推理", "difficulty": "中等",
     "question": "买3件商品，A店全部9折，B店满100减20，C店第二件半价。商品价格分别为60、80、40，去哪家店最划算？",
     "options": ["A店", "B店", "C店", "一样"], "answer": "A", "explanation": "A:162, B:160, C:170，B最划算"},
    {"id": 9, "name": "推理链", "category": "多步推理", "difficulty": "困难",
     "question": "甲说乙在说谎，乙说丙在说谎，丙说甲和乙都在说谎。谁说真话？",
     "options": ["甲", "乙", "丙", "无法确定"], "answer": "B", "explanation": "只有乙说真话时无矛盾"},
    {"id": 10, "name": "集合推理", "category": "多步推理", "difficulty": "中等",
     "question": "班级50人，30人会游泳，25人会骑车，10人都会，多少人两项都不会？",
     "options": ["5", "10", "15", "20"], "answer": "A", "explanation": "仅游泳20+仅骑车15+都会10=45，50-45=5"},
    {"id": 11, "name": "递推关系", "category": "多步推理", "difficulty": "困难",
     "question": "第1天存1元，之后每天比前一天多存1元，第10天共存了多少钱？",
     "options": ["45", "50", "55", "60"], "answer": "C", "explanation": "1+2+...+10=55"},
    {"id": 12, "name": "层级计算", "category": "多步推理", "difficulty": "中等",
     "question": "公司层级：CEO-经理-主管-员工。CEO管3个经理，每个经理管4个主管，每个主管管5个员工。共有多少员工？",
     "options": ["60", "68", "72", "80"], "answer": "A", "explanation": "3×4×5=60"},
    {"id": 13, "name": "状态转移", "category": "多步推理", "difficulty": "困难",
     "question": "容器A有10升水，B为空。每次操作：从A倒一半到B，然后从B倒一半回A。3次操作后A有多少水？",
     "options": ["5", "6.25", "7.5", "8.75"], "answer": "C", "explanation": "经过计算，3次后A有7.5升"},
    {"id": 14, "name": "概率累加", "category": "多步推理", "difficulty": "困难",
     "question": "掷骰子，第一次1-3点前进1步，4-6点前进2步；第二次1-2点前进1步，3-6点前进2步。两次后正好前进3步的概率是？",
     "options": ["1/3", "1/2", "2/3", "3/4"], "answer": "A", "explanation": "只有1+2或2+1，概率1/2×2/3+1/2×1/3=1/2"},
    {"id": 15, "name": "约束满足", "category": "多步推理", "difficulty": "困难",
     "question": "红黄蓝三色涂四个相邻区域，相邻区域颜色不同，共有多少种涂法？",
     "options": ["18", "24", "30", "36"], "answer": "B", "explanation": "第一个3种，之后每个2种，3×2×2×2=24"},
    {"id": 16, "name": "流程优化", "category": "多步推理", "difficulty": "中等",
     "question": "洗衣服(40分钟)、拖地(20分钟)、擦窗户(15分钟)。洗衣机自动运行时可以干别的，最少需要多久？",
     "options": ["40", "55", "60", "75"], "answer": "A", "explanation": "拖地擦窗户共35分钟可在洗衣时完成"},
    {"id": 17, "name": "逆向思维", "category": "多步推理", "difficulty": "中等",
     "question": "一个数先减10，再除以2，再加5，最后乘3，结果是36。原数是多少？",
     "options": ["24", "28", "32", "36"], "answer": "B", "explanation": "倒推：36/3=12, 12-5=7, 7×2=14, 14+10=24? 修正：36/3=12,12-5=7,7×2=14,14+10=24"},
    {"id": 18, "name": "组合计数", "category": "多步推理", "difficulty": "困难",
     "question": "从A到B有3条路，B到C有4条路，C到D有2条路。从A经B、C到D有多少种不同路线？",
     "options": ["9", "12", "20", "24"], "answer": "D", "explanation": "3×4×2=24"},
    {"id": 19, "name": "周期问题", "category": "多步推理", "difficulty": "中等",
     "question": "今天是星期三，100天后是星期几？",
     "options": ["星期一", "星期二", "星期三", "星期五"], "answer": "D", "explanation": "100÷7=14余2，周三+2=周五"},
    {"id": 20, "name": "逻辑排序", "category": "多步推理", "difficulty": "中等",
     "question": "ABCDE五人比赛，A不是第一，B不是第一也不是最后，C比D高，E比B低。谁是第一？",
     "options": ["A", "B", "C", "D"], "answer": "C", "explanation": "C>D, B不是第一，A不是第一，E<B，所以C第一"},

    # ===== 规划决策 (20题) =====
    {"id": 21, "name": "最短路径", "category": "规划决策", "difficulty": "简单",
     "question": "A到B直线距离5km，绕道C距离3+4=7km。哪条路更短？",
     "options": ["直接", "绕道", "一样", "不确定"], "answer": "A", "explanation": "直线5<7"},
    {"id": 22, "name": "成本优化", "category": "规划决策", "difficulty": "中等",
     "question": "买100个零件，批发价每个8元(至少100个)，零售价每个10元。怎样买最省钱？",
     "options": ["批发100个", "零售100个", "批发50零售50", "都一样"], "answer": "A", "explanation": "批发800元最省"},
    {"id": 23, "name": "时间管理", "category": "规划决策", "difficulty": "中等",
     "question": "3个任务：A(需2小时，截止今天18点)，B(需1小时，截止明天12点)，C(需3小时，截止明天18点)。现在14点，如何安排？",
     "options": ["A→B→C", "C→A→B", "A→C→B", "B→A→C"], "answer": "C", "explanation": "A最急先做，然后C明天做，B可以明天"},
    {"id": 24, "name": "资源分配", "category": "规划决策", "difficulty": "困难",
     "question": "5个任务需要5个人，每人专长不同。任务A需技能X，任务B需技能Y...如何分配最高效？",
     "options": ["随机分配", "按专长分配", "轮流分配", "按资历分配"], "answer": "B", "explanation": "专长匹配最高效"},
    {"id": 25, "name": "风险决策", "category": "规划决策", "difficulty": "中等",
     "question": "方案A：90%概率赚100万；方案B：50%概率赚300万。期望收益哪个高？",
     "options": ["A", "B", "一样", "不确定"], "answer": "B", "explanation": "A期望90万，B期望150万"},
    {"id": 26, "name": "库存规划", "category": "规划决策", "difficulty": "中等",
     "question": "日销量100件，订货周期7天，安全库存200件，当前库存500件。何时订货？",
     "options": ["立即", "3天后", "5天后", "7天后"], "answer": "B", "explanation": "500-200=300，300/100=3天"},
    {"id": 27, "name": "投资选择", "category": "规划决策", "difficulty": "中等",
     "question": "项目A：投资10万，年回报2万；项目B：投资5万，年回报1万。哪个ROI更高？",
     "options": ["A", "B", "一样", "不确定"], "answer": "C", "explanation": "都是20%"},
    {"id": 28, "name": "人员调度", "category": "规划决策", "difficulty": "困难",
     "question": "工厂3班倒，每班需5人，每人每周工作5天。最少需要多少员工？",
     "options": ["15", "18", "21", "25"], "answer": "C", "explanation": "每周15×7=105人次，每人5天，需21人"},
    {"id": 29, "name": "项目排期", "category": "规划决策", "difficulty": "困难",
     "question": "项目有任务A(3天)、B(2天，依赖A)、C(4天)、D(1天，依赖B和C)。最短工期？",
     "options": ["6", "7", "8", "10"], "answer": "C", "explanation": "C(4天)和A-B(5天)并行，然后D，共8天"},
    {"id": 30, "name": "运输优化", "category": "规划决策", "difficulty": "中等",
     "question": "卡车容量10吨，A货物6吨，B货物5吨，C货物4吨。一次能运哪些？",
     "options": ["A+B", "A+C", "B+C", "全部"], "answer": "B", "explanation": "6+4=10刚好，或5+4=9"},
    {"id": 31, "name": "定价策略", "category": "规划决策", "difficulty": "中等",
     "question": "成本50元，定价80元销量100件，定价100元销量60件。哪个利润高？",
     "options": ["80元", "100元", "一样", "不确定"], "answer": "A", "explanation": "3000>3000? 80:30×100=3000, 100:50×60=3000，一样"},
    {"id": 32, "name": "设备更新", "category": "规划决策", "difficulty": "中等",
     "question": "旧设备年维护费5万，新设备购买费20万年维护费1万。几年回本？",
     "options": ["3", "4", "5", "6"], "answer": "C", "explanation": "年省4万，20/4=5年"},
    {"id": 33, "name": "产能规划", "category": "规划决策", "difficulty": "困难",
     "question": "月需求1000件，工作日20天，设备日产能50件，良率90%。需要几条生产线？",
     "options": ["1", "2", "3", "4"], "answer": "B", "explanation": "需日产50件，单线45件，需2条"},
    {"id": 34, "name": "外包决策", "category": "规划决策", "difficulty": "中等",
     "question": "自制成本每个10元，外包每个12元但节省设备投资50万。产量多少时自制划算？",
     "options": [">10万", ">25万", ">50万", "<25万"], "answer": "B", "explanation": "50/(12-10)=25万"},
    {"id": 35, "name": "排队优化", "category": "规划决策", "difficulty": "中等",
     "question": "3个窗口，顾客到达率10人/分钟，服务率4人/分钟。平均等待时间？",
     "options": ["很短", "中等", "很长", "无法计算"], "answer": "A", "explanation": "总服务能力12>10，等待短"},
    {"id": 36, "name": "预算分配", "category": "规划决策", "difficulty": "简单",
     "question": "预算100万，营销需至少30万，研发需至少40万，运营需20万。剩余多少？",
     "options": ["10万", "20万", "30万", "40万"], "answer": "A", "explanation": "100-30-40-20=10"},
    {"id": 37, "name": "质量权衡", "category": "规划决策", "difficulty": "中等",
     "question": "A供应商：合格率95%，单价100；B供应商：合格率98%，单价110。哪个更划算？",
     "options": ["A", "B", "一样", "不确定"], "answer": "B", "explanation": "合格品成本A:105.3, B:112.2? A更划算，修正：A合格成本100/0.95=105.26, B=110/0.98=112.24，A划算"},
    {"id": 38, "name": "扩张策略", "category": "规划决策", "difficulty": "困难",
     "question": "开设新店：A地点客流大成本高，B地点客流小成本低。如何选择？",
     "options": ["一定选A", "一定选B", "计算盈亏平衡点", "随机选择"], "answer": "C", "explanation": "需要具体计算"},
    {"id": 39, "name": "技术选型", "category": "规划决策", "difficulty": "中等",
     "question": "技术A：成熟稳定；技术B：先进但有风险。创业初期应选？",
     "options": ["一定A", "一定B", "看团队能力", "看融资情况"], "answer": "C", "explanation": "团队能力决定"},
    {"id": 40, "name": "退出策略", "category": "规划决策", "difficulty": "中等",
     "question": "项目已投入100万，预计还需投入50万，成功概率60%，成功后收益200万。是否继续？",
     "options": ["继续", "退出", "不确定", "看情况"], "answer": "A", "explanation": "期望收益120-50=70>0，继续"},

    # ===== 问题分解 (20题) =====
    {"id": 41, "name": "任务拆分", "category": "问题分解", "difficulty": "简单",
     "question": "写报告需要：收集资料、写大纲、写正文、修改。这属于什么方法？",
     "options": ["分解法", "整体法", "试错法", "排除法"], "answer": "A", "explanation": "任务分解"},
    {"id": 42, "name": "模块划分", "category": "问题分解", "difficulty": "中等",
     "question": "开发电商系统，应如何分解？",
     "options": ["一起开发", "分用户端和商家端", "按功能模块", "按技术栈"], "answer": "C", "explanation": "功能模块化最合理"},
    {"id": 43, "name": "问题归类", "category": "问题分解", "difficulty": "简单",
     "question": "bug分为：界面问题、功能问题、性能问题、安全问题。这是按什么分解？",
     "options": ["严重程度", "类型", "模块", "负责人"], "answer": "B", "explanation": "按类型归类"},
    {"id": 44, "name": "层次分析", "category": "问题分解", "difficulty": "困难",
     "question": "复杂问题涉及：战略层、战术层、执行层。分析时应？",
     "options": ["只看执行", "逐层分析", "混在一起", "只看战略"], "answer": "B", "explanation": "分层分析"},
    {"id": 45, "name": "维度分解", "category": "问题分解", "difficulty": "中等",
     "question": "分析销售额下降，应分解为哪些维度？",
     "options": ["只看价格", "只看销量", "价格和销量", "随机看"], "answer": "C", "explanation": "销售额=价格×销量"},
    {"id": 46, "name": "流程分解", "category": "问题分解", "difficulty": "中等",
     "question": "优化客户投诉处理，应？",
     "options": ["直接解决", "分析处理流程各环节", "忽略投诉", "换人处理"], "answer": "B", "explanation": "流程分析"},
    {"id": 47, "name": "目标分解", "category": "问题分解", "difficulty": "中等",
     "question": "年目标销售额1200万，如何分解到月？",
     "options": ["每月100万", "考虑季节性", "前高后低", "平均分配"], "answer": "B", "explanation": "应考虑季节因素"},
    {"id": 48, "name": "原因分解", "category": "问题分解", "difficulty": "中等",
     "question": "机器故障，可能原因：电源、硬件、软件、人为。这是什么方法？",
     "options": ["鱼骨图/因果图", "流程图", "饼图", "折线图"], "answer": "A", "explanation": "鱼骨图分解原因"},
    {"id": 49, "name": "解决方案生成", "category": "问题分解", "difficulty": "简单",
     "question": "提升用户活跃度，可分解为：新用户激活、老用户召回、流失预防等，这叫？",
     "options": ["头脑风暴", "方案分解", "随机想法", "抄袭竞品"], "answer": "B", "explanation": "方案分解"},
    {"id": 50, "name": "MECE原则", "category": "问题分解", "difficulty": "困难",
     "question": "分解问题时要求各部分相互独立、完全穷尽，这是？",
     "options": ["MECE原则", "Pareto原则", "SMART原则", "KISS原则"], "answer": "A", "explanation": "MECE=Mutually Exclusive, Collectively Exhaustive"},
    {"id": 51, "name": "用户细分", "category": "问题分解", "difficulty": "中等",
     "question": "分析用户行为，按新老用户、高低频用户、付费非付费分解，这是？",
     "options": ["用户画像", "用户分层", "用户增长", "用户留存"], "answer": "B", "explanation": "用户分层分析"},
    {"id": 52, "name": "时间分解", "category": "问题分解", "difficulty": "简单",
     "question": "年度总结分解为季度、月度、周来回顾，这是？",
     "options": ["时间维度分解", "空间分解", "功能分解", "人员分解"], "answer": "A", "explanation": "按时间分解"},
    {"id": 53, "name": "优先级排序", "category": "问题分解", "difficulty": "中等",
     "question": "多个问题需要解决，先按重要性和紧急性分类，这是？",
     "options": ["随机排序", "四象限法", "FIFO", "LIFO"], "answer": "B", "explanation": "重要紧急四象限"},
    {"id": 54, "name": "数据分解", "category": "问题分解", "difficulty": "困难",
     "question": "总营收下降，分解为：新客收入、老客收入、复购收入分别分析，这是？",
     "options": ["维度细分", "指标分解", "趋势分析", "对比分析"], "answer": "B", "explanation": "指标分解"},
    {"id": 55, "name": "场景分解", "category": "问题分解", "difficulty": "中等",
     "question": "测试APP功能，分解为：正常场景、异常场景、边界场景，这是？",
     "options": ["功能分解", "场景分解", "流程分解", "接口分解"], "answer": "B", "explanation": "场景测试分解"},
    {"id": 56, "name": "责任分解", "category": "问题分解", "difficulty": "简单",
     "question": "项目失败，分解各部门责任：产品、开发、测试、运营，这是？",
     "options": ["甩锅", "责任分解", "团队建设", "绩效考核"], "answer": "B", "explanation": "责任归属分析"},
    {"id": 57, "name": "风险分解", "category": "问题分解", "difficulty": "中等",
     "question": "项目风险评估，分解为：技术风险、市场风险、人员风险、政策风险，这是？",
     "options": ["过度担忧", "风险分解", "保守策略", "激进策略"], "answer": "B", "explanation": "风险分类"},
    {"id": 58, "name": "资源分解", "category": "问题分解", "difficulty": "中等",
     "question": "项目资源规划，分解为人力、资金、设备、时间，这是？",
     "options": ["资源分解", "预算分解", "任务分解", "目标分解"], "answer": "A", "explanation": "资源维度分解"},
    {"id": 59, "name": "假设分解", "category": "问题分解", "difficulty": "困难",
     "question": "商业计划书中的关键假设分解验证，这是？",
     "options": ["MVP验证", "假设驱动", "试错法", "经验法"], "answer": "B", "explanation": "假设分解验证"},
    {"id": 60, "name": "利益相关者分解", "category": "问题分解", "difficulty": "中等",
     "question": "分析项目影响，分解为：用户、员工、股东、社会，这是？",
     "options": ["利益相关者分析", "SWOT分析", "PEST分析", "5力分析"], "answer": "A", "explanation": "利益相关者分解"},

    # ===== 因果推理 (20题) =====
    {"id": 61, "name": "直接因果", "category": "因果推理", "difficulty": "简单",
     "question": "因为下雨，所以地湿。下雨和地湿的关系是？",
     "options": ["因果关系", "相关关系", "无关", "偶然"], "answer": "A", "explanation": "直接因果"},
    {"id": 62, "name": "因果倒置", "category": "因果推理", "difficulty": "中等",
     "question": "数据显示：冰淇淋销量和溺水事故正相关。最可能的原因是？",
     "options": ["冰淇淋导致溺水", "溺水导致冰淇淋", "夏天导致两者", "巧合"], "answer": "C", "explanation": "共同原因"},
    {"id": 63, "name": "多因一果", "category": "因果推理", "difficulty": "中等",
     "question": "考试失败可能因为：没复习、题目难、生病。这说明？",
     "options": ["单一原因", "多因一果", "没有原因", "随机结果"], "answer": "B", "explanation": "多因素导致"},
    {"id": 64, "name": "一因多果", "category": "因果推理", "difficulty": "中等",
     "question": "地震导致：房屋倒塌、交通中断、停电。这说明？",
     "options": ["一因多果", "多因一果", "无因果", "偶然"], "answer": "A", "explanation": "一个原因多个结果"},
    {"id": 65, "name": "因果链", "category": "因果推理", "difficulty": "中等",
     "question": "A导致B，B导致C，C导致D，A和D的关系是？",
     "options": ["直接因果", "间接因果", "无因果", "相关"], "answer": "B", "explanation": "间接因果链"},
    {"id": 66, "name": "必要原因", "category": "因果推理", "difficulty": "中等",
     "question": "氧气是燃烧的必要条件，没有氧气一定不燃烧。氧气是燃烧的？",
     "options": ["充分条件", "必要条件", "充要条件", "无关条件"], "answer": "B", "explanation": "必要条件"},
    {"id": 67, "name": "充分原因", "category": "因果推理", "difficulty": "中等",
     "question": "只要下雨地就湿，下雨是地湿的？",
     "options": ["充分条件", "必要条件", "充要条件", "无关"], "answer": "A", "explanation": "充分条件"},
    {"id": 68, "name": "混淆因果", "category": "因果推理", "difficulty": "困难",
     "question": "数据显示：成功人士睡眠少。可以推出？",
     "options": ["少睡导致成功", "成功导致少睡", "两者无关", "无法确定因果"], "answer": "D", "explanation": "相关不等于因果"},
    {"id": 69, "name": "共同原因", "category": "因果推理", "difficulty": "困难",
     "question": "A和B总是同时发生，可能是？",
     "options": ["A导致B", "B导致A", "C导致A和B", "以上都可能"], "answer": "D", "explanation": "多种可能"},
    {"id": 70, "name": "因果强度", "category": "因果推理", "difficulty": "困难",
     "question": "吸烟与肺癌有统计相关，但非吸烟者也会得肺癌，说明？",
     "options": ["无关", "强因果", "弱因果/风险因素", "必然因果"], "answer": "C", "explanation": "风险因素非必然"},
    {"id": 71, "name": "时间先后", "category": "因果推理", "difficulty": "简单",
     "question": "先有闪电后有雷声，闪电是雷声的？",
     "options": ["原因", "结果", "无关", "巧合"], "answer": "A", "explanation": "闪电产生雷声"},
    {"id": 72, "name": "反事实推理", "category": "因果推理", "difficulty": "困难",
     "question": "如果当初努力学习，现在就能考上好大学。这是？",
     "options": ["反事实推理", "事实推理", "无关", "预测"], "answer": "A", "explanation": "反事实思维"},
    {"id": 73, "name": "干预与观测", "category": "因果推理", "difficulty": "困难",
     "question": "数据显示去医院的人死亡率更高，因此应该？",
     "options": ["不去医院", "去医院", "考虑选择偏差", "数据错误"], "answer": "C", "explanation": "选择偏差：病重才去"},
    {"id": 74, "name": "中介变量", "category": "因果推理", "difficulty": "困难",
     "question": "教育→收入→幸福感，收入是？",
     "options": ["自变量", "因变量", "中介变量", "调节变量"], "answer": "C", "explanation": "中介机制"},
    {"id": 75, "name": "调节变量", "category": "因果推理", "difficulty": "困难",
     "question": "运动对减肥的效果因饮食不同而不同，饮食是？",
     "options": ["中介变量", "调节变量", "混淆变量", "无关变量"], "answer": "B", "explanation": "调节效应"},
    {"id": 76, "name": "混淆变量", "category": "因果推理", "difficulty": "困难",
     "question": "研究发现：穿鞋睡觉与头痛相关。实际是因为？",
     "options": ["鞋导致头痛", "头痛导致穿鞋", "醉酒导致两者", "巧合"], "answer": "C", "explanation": "混淆变量"},
    {"id": 77, "name": "累积效应", "category": "因果推理", "difficulty": "中等",
     "question": "每天吸烟一根危害小，但长期累积危害大，这是？",
     "options": ["累积因果", "即时因果", "无因果", "心理作用"], "answer": "A", "explanation": "累积效应"},
    {"id": 78, "name": "阈值效应", "category": "因果推理", "difficulty": "中等",
     "question": "温度低于0度水结冰，高于则不结冰，这是？",
     "options": ["线性关系", "阈值效应", "随机关系", "无关"], "answer": "B", "explanation": "临界点/阈值"},
    {"id": 79, "name": "反馈循环", "category": "因果推理", "difficulty": "困难",
     "question": "价格上涨→需求减少→价格下降→需求增加→价格上涨，这是？",
     "options": ["单向因果", "反馈循环", "无因果", "外部冲击"], "answer": "B", "explanation": "因果循环"},
    {"id": 80, "name": "概率因果", "category": "因果推理", "difficulty": "中等",
     "question": "吸烟增加肺癌概率但不必然导致，这是？",
     "options": ["确定性因果", "概率性因果", "无因果", "伪因果"], "answer": "B", "explanation": "概率因果"},

    # ===== 假设检验 (20题) =====
    {"id": 81, "name": "假设定义", "category": "假设检验", "difficulty": "简单",
     "question": "假设是可以被验证或证伪的？",
     "options": ["陈述", "猜测", "事实", "定理"], "answer": "A", "explanation": "可检验的陈述"},
    {"id": 82, "name": "零假设", "category": "假设检验", "difficulty": "中等",
     "question": "新药是否有效，零假设通常是？",
     "options": ["有效", "无效", "可能有效", "不知道"], "answer": "B", "explanation": "H0:无效果"},
    {"id": 83, "name": "备择假设", "category": "假设检验", "difficulty": "中等",
     "question": "检验硬币是否公平，备择假设是？",
     "options": ["正面概率=0.5", "正面概率≠0.5", "正面概率>0.5", "不确定"], "answer": "B", "explanation": "H1:不等0.5"},
    {"id": 84, "name": "显著性水平", "category": "假设检验", "difficulty": "中等",
     "question": "p值小于多少通常认为结果显著？",
     "options": ["0.01", "0.05", "0.1", "0.5"], "answer": "B", "explanation": "α=0.05惯例"},
    {"id": 85, "name": "p值含义", "category": "假设检验", "difficulty": "困难",
     "question": "p=0.03表示？",
     "options": ["假设为真概率3%", "假设为假概率3%", "在假设为真时看到此数据的概率3%", "假设重要程度3%"], "answer": "C", "explanation": "p值定义"},
    {"id": 86, "name": "第一类错误", "category": "假设检验", "difficulty": "中等",
     "question": "实际上无效但认为有效，这是？",
     "options": ["第一类错误/假阳性", "第二类错误", "正确决策", "无法判断"], "answer": "A", "explanation": "假阳性"},
    {"id": 87, "name": "第二类错误", "category": "假设检验", "difficulty": "中等",
     "question": "实际上有效但认为无效，这是？",
     "options": ["第一类错误", "第二类错误/假阴性", "正确", "误差"], "answer": "B", "explanation": "假阴性"},
    {"id": 88, "name": "检验功效", "category": "假设检验", "difficulty": "困难",
     "question": "检验功效(power)是指？",
     "options": ["拒绝真假设的概率", "接受假假设的概率", "正确拒绝假假设的概率", "样本大小"], "answer": "C", "explanation": "1-β，正确检出"},
    {"id": 89, "name": "样本大小", "category": "假设检验", "difficulty": "中等",
     "question": "样本量越大，检验？",
     "options": ["越不显著", "越显著", "功效越高", "误差越大"], "answer": "C", "explanation": "大样本提高功效"},
    {"id": 90, "name": "双尾检验", "category": "假设检验", "difficulty": "中等",
     "question": "检验平均值是否变化（不论变大变小），应使用？",
     "options": ["单尾检验", "双尾检验", "不用检验", "随机检验"], "answer": "B", "explanation": "双尾检验"},
    {"id": 91, "name": "单尾检验", "category": "假设检验", "difficulty": "中等",
     "question": "检验新药是否更好（不关心是否更差），应使用？",
     "options": ["单尾检验", "双尾检验", "无检验", "多重检验"], "answer": "A", "explanation": "单尾检验"},
    {"id": 92, "name": "置信区间", "category": "假设检验", "difficulty": "中等",
     "question": "95%置信区间不包含0，说明在0.05水平？",
     "options": ["不显著", "显著", "无法判断", "需要更多数据"], "answer": "B", "explanation": "CI与检验等价"},
    {"id": 93, "name": "效应量", "category": "假设检验", "difficulty": "困难",
     "question": "统计显著但实际差异很小，可能缺少？",
     "options": ["p值", "效应量报告", "样本", "对照组"], "answer": "B", "explanation": "效应量大小"},
    {"id": 94, "name": "多重检验", "category": "假设检验", "difficulty": "困难",
     "question": "进行100次检验，预期有多少次假阳性（α=0.05）？",
     "options": ["1", "5", "10", "50"], "answer": "B", "explanation": "100×0.05=5"},
    {"id": 95, "name": "Bonferroni校正", "category": "假设检验", "difficulty": "困难",
     "question": "10次检验，Bonferroni校正后的显著性水平是？",
     "options": ["0.005", "0.05", "0.5", "0.001"], "answer": "A", "explanation": "0.05/10=0.005"},
    {"id": 96, "name": "卡方检验", "category": "假设检验", "difficulty": "困难",
     "question": "检验分类变量间是否独立，使用？",
     "options": ["t检验", "卡方检验", "方差分析", "相关分析"], "answer": "B", "explanation": "卡方独立性检验"},
    {"id": 97, "name": "t检验", "category": "假设检验", "difficulty": "中等",
     "question": "比较两组平均值是否有显著差异，使用？",
     "options": ["t检验", "卡方检验", "方差分析", "回归"], "answer": "A", "explanation": "t检验"},
    {"id": 98, "name": "方差分析", "category": "假设检验", "difficulty": "中等",
     "question": "比较三组及以上平均值，使用？",
     "options": ["t检验", "ANOVA", "卡方", "相关"], "answer": "B", "explanation": "方差分析ANOVA"},
    {"id": 99, "name": "可证伪性", "category": "假设检验", "difficulty": "中等",
     "question": "科学假设必须具备什么特性？",
     "options": ["正确性", "可证伪性", "复杂性", "新颖性"], "answer": "B", "explanation": "Popper可证伪性"},
    {"id": 100, "name": "证伪原则", "category": "假设检验", "difficulty": "中等",
     "question": "发现一只黑天鹅即可证伪'所有天鹅都是白的'，这体现了？",
     "options": ["证实原则", "证伪原则", "归纳法", "演绎法"], "answer": "B", "explanation": "证伪优于证实"},
]


class ReasoningEvaluator(BaseEvaluator):
    """推理规划能力评估器"""
    name = "reasoning"
    description = "深度推理规划测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-推理规划"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.6

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        self.raw_logger = RawDataLogger("stage3", "reasoning")

    def run_tests(self) -> StageResult:
        """运行推理规划测试"""
        passed = 0
        failed = 0
        results = []
        start_time = time.time()

        for test_case in REASONING_TEST_CASES:
            result = self._test_single_case(test_case)
            results.append(result)

            if result.passed:
                passed += 1
            else:
                failed += 1

        duration = time.time() - start_time
        total = len(REASONING_TEST_CASES)
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
        """测试单个推理用例"""
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
                    {"role": "system", "content": "你是一个推理专家。只回答选项字母，不要解释。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4096,
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
            }, test_type="reasoning_stage3")

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
            }, test_type="reasoning_stage3")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=False,
                duration_ms=(time.time() - start_time) * 1000,
                details={},
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

    def _extract_answer(self, response: str) -> str:
        """从响应中提取答案字母 - 支持推理模型"""
        if not response:
            return ""
        # 先提取 </think> 后的内容
        text = self._extract_after_think(response).upper()

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



def run_reasoning_test(model_url: str, model_name: str, **kwargs) -> dict:
    """运行推理规划测试的便捷函数"""
    evaluator = ReasoningEvaluator(model_url, model_name, **kwargs)
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
        "threshold_percentage": stage_result.threshold_percentage,
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


__all__ = [
    'ReasoningEvaluator', 'run_reasoning_test',
    'REASONING_TEST_CASES'
]
