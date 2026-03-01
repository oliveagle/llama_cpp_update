#!/usr/bin/env python3
"""
Stage 3 深度数学推理测试 (100 cases)
涵盖：代数、几何、概率统计、微积分、数论、应用题等
"""

import time
import json
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 数学推理测试用例 (100个)
MATH_TEST_CASES = [
    # ===== 代数运算 (20题) =====
    {"id": 1, "name": "一元一次方程", "category": "代数", "difficulty": "简单",
     "problem": "解方程：3x + 7 = 22", "answer": 5, "type": "integer"},
    {"id": 2, "name": "二元一次方程组", "category": "代数", "difficulty": "简单",
     "problem": "解方程组：2x + y = 10, x - y = 2，求 x + y 的值", "answer": 8, "type": "integer"},
    {"id": 3, "name": "一元二次方程", "category": "代数", "difficulty": "中等",
     "problem": "解方程：x² - 5x + 6 = 0，求较大根", "answer": 3, "type": "integer"},
    {"id": 4, "name": "分式方程", "category": "代数", "difficulty": "中等",
     "problem": "解方程：(x+1)/(x-1) = 3，求 x", "answer": 2, "type": "integer"},
    {"id": 5, "name": "绝对值方程", "category": "代数", "difficulty": "中等",
     "problem": "解方程：|2x - 3| = 5，求正数解", "answer": 4, "type": "integer"},
    {"id": 6, "name": "不等式求解", "category": "代数", "difficulty": "简单",
     "problem": "解不等式：3x - 5 < 10，求最大整数解", "answer": 4, "type": "integer"},
    {"id": 7, "name": "多项式展开", "category": "代数", "difficulty": "中等",
     "problem": "展开 (a + b)³ 后，a²b 项的系数是多少", "answer": 3, "type": "integer"},
    {"id": 8, "name": "因式分解应用", "category": "代数", "difficulty": "中等",
     "problem": "若 x² + kx + 12 = (x+3)(x+4)，求 k", "answer": 7, "type": "integer"},
    {"id": 9, "name": "指数运算", "category": "代数", "difficulty": "简单",
     "problem": "计算：2³ × 2⁴ ÷ 2⁵", "answer": 4, "type": "integer"},
    {"id": 10, "name": "对数运算", "category": "代数", "difficulty": "中等",
     "problem": "计算：log₂(64)", "answer": 6, "type": "integer"},
    {"id": 11, "name": "复数运算", "category": "代数", "difficulty": "困难",
     "problem": "计算 i²⁰²⁴（i为虚数单位）", "answer": 1, "type": "integer"},
    {"id": 12, "name": "等差数列", "category": "代数", "difficulty": "简单",
     "problem": "等差数列 3, 7, 11... 的第10项是多少", "answer": 39, "type": "integer"},
    {"id": 13, "name": "等比数列求和", "category": "代数", "difficulty": "中等",
     "problem": "等比数列 2, 6, 18... 前4项和是多少", "answer": 80, "type": "integer"},
    {"id": 14, "name": "函数求值", "category": "代数", "difficulty": "简单",
     "problem": "f(x) = 2x² - 3x + 1，求 f(3)", "answer": 10, "type": "integer"},
    {"id": 15, "name": "反函数", "category": "代数", "difficulty": "中等",
     "problem": "f(x) = 2x + 1，求 f⁻¹(5)", "answer": 2, "type": "integer"},
    {"id": 16, "name": "方程根与系数", "category": "代数", "difficulty": "中等",
     "problem": "x² - 6x + 8 = 0 的两根之和是多少", "answer": 6, "type": "integer"},
    {"id": 17, "name": "分式化简", "category": "代数", "difficulty": "中等",
     "problem": "化简：(x²-9)/(x-3) 当x=4时的值", "answer": 7, "type": "integer"},
    {"id": 18, "name": "根式运算", "category": "代数", "difficulty": "简单",
     "problem": "计算：√81 + √16", "answer": 13, "type": "integer"},
    {"id": 19, "name": "配方求最值", "category": "代数", "difficulty": "中等",
     "problem": "y = x² - 4x + 5 的最小值是多少", "answer": 1, "type": "integer"},
    {"id": 20, "name": "韦达定理", "category": "代数", "difficulty": "中等",
     "problem": "x² + px + q = 0 的两根为2和3，求 p + q", "answer": 1, "type": "integer"},

    # ===== 几何 (20题) =====
    {"id": 21, "name": "三角形面积", "category": "几何", "difficulty": "简单",
     "problem": "三角形底为8，高为5，面积是多少", "answer": 20, "type": "integer"},
    {"id": 22, "name": "勾股定理", "category": "几何", "difficulty": "简单",
     "problem": "直角三角形两直角边为3和4，斜边是多少", "answer": 5, "type": "integer"},
    {"id": 23, "name": "圆周长", "category": "几何", "difficulty": "简单",
     "problem": "直径为10的圆，周长是多少（π取3.14，答案取整）", "answer": 31, "type": "integer"},
    {"id": 24, "name": "圆面积", "category": "几何", "difficulty": "简单",
     "problem": "半径为4的圆，面积是多少（π取3）", "answer": 48, "type": "integer"},
    {"id": 25, "name": "矩形对角线", "category": "几何", "difficulty": "简单",
     "problem": "矩形长6宽8，对角线长度是多少", "answer": 10, "type": "integer"},
    {"id": 26, "name": "正方形面积", "category": "几何", "difficulty": "简单",
     "problem": "正方形对角线为10，面积是多少", "answer": 50, "type": "integer"},
    {"id": 27, "name": "圆柱体积", "category": "几何", "difficulty": "中等",
     "problem": "圆柱半径3高4，体积是多少（π取3）", "answer": 108, "type": "integer"},
    {"id": 28, "name": "球体积", "category": "几何", "difficulty": "中等",
     "problem": "球半径为3，体积是多少（π取3，V=4/3πr³）", "answer": 108, "type": "integer"},
    {"id": 29, "name": "等边三角形高", "category": "几何", "difficulty": "中等",
     "problem": "边长为6的等边三角形，高是多少（√3取1.7）", "answer": 5, "type": "integer"},
    {"id": 30, "name": "梯形面积", "category": "几何", "difficulty": "简单",
     "problem": "梯形上底4下底6高5，面积是多少", "answer": 25, "type": "integer"},
    {"id": 31, "name": "正多边形内角", "category": "几何", "difficulty": "中等",
     "problem": "正五边形每个内角是多少度", "answer": 108, "type": "integer"},
    {"id": 32, "name": "相似三角形", "category": "几何", "difficulty": "中等",
     "problem": "两相似三角形对应边比为2:3，面积比是多少", "answer": 4, "type": "ratio"},
    {"id": 33, "name": "扇形面积", "category": "几何", "difficulty": "中等",
     "problem": "半径6，圆心角60度的扇形面积（π取3）", "answer": 18, "type": "integer"},
    {"id": 34, "name": "圆锥体积", "category": "几何", "difficulty": "中等",
     "problem": "圆锥底半径3高4，体积是多少（π取3）", "answer": 36, "type": "integer"},
    {"id": 35, "name": "立方体表面积", "category": "几何", "difficulty": "简单",
     "problem": "棱长为4的立方体表面积", "answer": 96, "type": "integer"},
    {"id": 36, "name": "立方体体积", "category": "几何", "difficulty": "简单",
     "problem": "棱长为5的立方体体积", "answer": 125, "type": "integer"},
    {"id": 37, "name": "圆周角定理", "category": "几何", "difficulty": "中等",
     "problem": "圆心角为80度，对应圆周角是多少度", "answer": 40, "type": "integer"},
    {"id": 38, "name": "直角三角形边角", "category": "几何", "difficulty": "中等",
     "problem": "直角三角形一锐角30度，对边为5，斜边是多少", "answer": 10, "type": "integer"},
    {"id": 39, "name": "菱形面积", "category": "几何", "difficulty": "中等",
     "problem": "菱形对角线为6和8，面积是多少", "answer": 24, "type": "integer"},
    {"id": 40, "name": "内切圆半径", "category": "几何", "difficulty": "困难",
     "problem": "直角边为6和8的直角三角形，内切圆半径是多少", "answer": 2, "type": "integer"},

    # ===== 概率统计 (20题) =====
    {"id": 41, "name": "平均数", "category": "概率统计", "difficulty": "简单",
     "problem": "数据 5, 8, 12, 15 的平均数是多少", "answer": 10, "type": "integer"},
    {"id": 42, "name": "中位数", "category": "概率统计", "difficulty": "简单",
     "problem": "数据 3, 7, 9, 12, 15 的中位数是多少", "answer": 9, "type": "integer"},
    {"id": 43, "name": "众数", "category": "概率统计", "difficulty": "简单",
     "problem": "数据 2, 3, 3, 5, 5, 5, 7 的众数是多少", "answer": 5, "type": "integer"},
    {"id": 44, "name": "方差", "category": "概率统计", "difficulty": "中等",
     "problem": "数据 2, 4, 6 的方差是多少", "answer": 4, "type": "integer"},
    {"id": 45, "name": "排列数", "category": "概率统计", "difficulty": "中等",
     "problem": "从5人中选3人排列，有多少种排法", "answer": 60, "type": "integer"},
    {"id": 46, "name": "组合数", "category": "概率统计", "difficulty": "中等",
     "problem": "从6人中选2人，有多少种选法", "answer": 15, "type": "integer"},
    {"id": 47, "name": "概率计算", "category": "概率统计", "difficulty": "简单",
     "problem": "掷骰子得偶数的概率是多少（分数，分子+分母）", "answer": 5, "type": "integer"},
    {"id": 48, "name": "独立事件", "category": "概率统计", "difficulty": "中等",
     "problem": "两独立事件概率各为0.5，同时发生的概率是多少（百分数）", "answer": 25, "type": "integer"},
    {"id": 49, "name": "互斥事件", "category": "概率统计", "difficulty": "中等",
     "problem": "P(A)=0.3, P(B)=0.4, A与B互斥，P(A∪B)是多少（百分数）", "answer": 70, "type": "integer"},
    {"id": 50, "name": "条件概率", "category": "概率统计", "difficulty": "困难",
     "problem": "袋中3红2蓝，不放回抽2个，已知第一个是红，第二个也是红的概率（分数，分子+分母）", "answer": 3, "type": "integer"},
    {"id": 51, "name": "二项分布期望", "category": "概率统计", "difficulty": "中等",
     "problem": "n=10, p=0.3的二项分布，期望是多少", "answer": 3, "type": "integer"},
    {"id": 52, "name": "百分位数", "category": "概率统计", "difficulty": "中等",
     "problem": "数据 1,2,3,4,5,6,7,8,9,10 的第75百分位数是多少", "answer": 8, "type": "integer"},
    {"id": 53, "name": "标准差", "category": "概率统计", "difficulty": "中等",
     "problem": "数据 4, 8, 12 的标准差是多少（√12取3.5）", "answer": 4, "type": "integer"},
    {"id": 54, "name": "全概率", "category": "概率统计", "difficulty": "困难",
     "problem": "袋A有2红1白，袋B有1红2白，随机选袋抽一球得红球概率（分数，分子+分母）", "answer": 3, "type": "integer"},
    {"id": 55, "name": "贝叶斯", "category": "概率统计", "difficulty": "困难",
     "problem": "疾病患病率1%，检测准确率95%，检测阳性实际患病概率约多少（百分数取整）", "answer": 16, "type": "integer"},
    {"id": 56, "name": "期望值", "category": "概率统计", "difficulty": "中等",
     "problem": "掷骰子，点数的期望值是多少", "answer": 3, "type": "integer"},
    {"id": 57, "name": "几何分布", "category": "概率统计", "difficulty": "困难",
     "problem": "每次成功概率0.2，首次成功期望试验次数是多少", "answer": 5, "type": "integer"},
    {"id": 58, "name": "相关系数", "category": "概率统计", "difficulty": "困难",
     "problem": "完全正相关的相关系数是多少", "answer": 1, "type": "integer"},
    {"id": 59, "name": "样本方差", "category": "概率统计", "difficulty": "中等",
     "problem": "样本 2, 4, 6, 8 的样本方差（分母n-1）是多少", "answer": 6, "type": "integer"},
    {"id": 60, "name": "置信区间", "category": "概率统计", "difficulty": "困难",
     "problem": "95%置信区间对应的Z值约是多少（取整）", "answer": 2, "type": "integer"},

    # ===== 应用题 (20题) =====
    {"id": 61, "name": "速度问题", "category": "应用题", "difficulty": "简单",
     "problem": "汽车时速60公里，3小时行驶多少公里", "answer": 180, "type": "integer"},
    {"id": 62, "name": "工程问题", "category": "应用题", "difficulty": "中等",
     "problem": "甲10天完成，乙15天完成，合作几天完成", "answer": 6, "type": "integer"},
    {"id": 63, "name": "利润问题", "category": "应用题", "difficulty": "中等",
     "problem": "成本80售价100，利润率是多少（百分数）", "answer": 25, "type": "integer"},
    {"id": 64, "name": "浓度问题", "category": "应用题", "difficulty": "中等",
     "problem": "100克10%盐水加多少克盐变为20%盐水", "answer": 12, "type": "integer"},
    {"id": 65, "name": "年龄问题", "category": "应用题", "difficulty": "简单",
     "problem": "父40子10，几年后父年龄是子3倍", "answer": 5, "type": "integer"},
    {"id": 66, "name": "鸡兔同笼", "category": "应用题", "difficulty": "中等",
     "problem": "头共35，脚共94，鸡多少只", "answer": 23, "type": "integer"},
    {"id": 67, "name": "追及问题", "category": "应用题", "difficulty": "中等",
     "problem": "甲速60，乙速80，甲先走1小时，乙几小时追上", "answer": 3, "type": "integer"},
    {"id": 68, "name": "相遇问题", "category": "应用题", "difficulty": "简单",
     "problem": "两地相距300公里，两车相向而行，时速各为50和70，几小时相遇", "answer": 2, "type": "integer"},
    {"id": 69, "name": "盈亏问题", "category": "应用题", "difficulty": "中等",
     "problem": "每人分3个多8个，每人分5个少12个，共有多少人", "answer": 10, "type": "integer"},
    {"id": 70, "name": "植树问题", "category": "应用题", "difficulty": "简单",
     "problem": "100米路每隔5米种树，两端都种，共多少棵", "answer": 21, "type": "integer"},
    {"id": 71, "name": "抽屉原理", "category": "应用题", "difficulty": "中等",
     "problem": "红蓝球各10个，至少取多少个保证有2个同色", "answer": 3, "type": "integer"},
    {"id": 72, "name": "牛吃草问题", "category": "应用题", "difficulty": "困难",
     "problem": "27牛6天吃完，23牛9天吃完，21牛几天吃完", "answer": 12, "type": "integer"},
    {"id": 73, "name": "时钟问题", "category": "应用题", "difficulty": "中等",
     "problem": "4点后，时针分针第一次重合约多少分（取整）", "answer": 21, "type": "integer"},
    {"id": 74, "name": "比例分配", "category": "应用题", "difficulty": "简单",
     "problem": "甲乙丙按2:3:5分100元，乙得多少", "answer": 30, "type": "integer"},
    {"id": 75, "name": "平均速度", "category": "应用题", "difficulty": "中等",
     "problem": "上坡速30，下坡速60，往返平均速度是多少", "answer": 40, "type": "integer"},
    {"id": 76, "name": "折扣问题", "category": "应用题", "difficulty": "简单",
     "problem": "原价200，先涨20%再打8折，现价多少", "answer": 192, "type": "integer"},
    {"id": 77, "name": "利息计算", "category": "应用题", "difficulty": "简单",
     "problem": "本金1000，年利率5%，2年后本息共多少", "answer": 1100, "type": "integer"},
    {"id": 78, "name": "溶液混合", "category": "应用题", "difficulty": "中等",
     "problem": "20%盐水100克与30%盐水200克混合，浓度是多少（百分数）", "answer": 26, "type": "integer"},
    {"id": 79, "name": "排列组合应用", "category": "应用题", "difficulty": "中等",
     "problem": "5人排队，甲乙必须相邻，多少种排法", "answer": 48, "type": "integer"},
    {"id": 80, "name": "最短路径", "category": "应用题", "difficulty": "中等",
     "problem": "长方形长8宽6，从一角到对角最短距离是多少", "answer": 10, "type": "integer"},

    # ===== 数论 (20题) =====
    {"id": 81, "name": "最大公约数", "category": "数论", "difficulty": "简单",
     "problem": "GCD(48, 18) 是多少", "answer": 6, "type": "integer"},
    {"id": 82, "name": "最小公倍数", "category": "数论", "difficulty": "简单",
     "problem": "LCM(12, 18) 是多少", "answer": 36, "type": "integer"},
    {"id": 83, "name": "质数判断", "category": "数论", "difficulty": "简单",
     "problem": "100以内最大的质数是多少", "answer": 97, "type": "integer"},
    {"id": 84, "name": "质因数分解", "category": "数论", "difficulty": "中等",
     "problem": "360 有多少个正因数", "answer": 24, "type": "integer"},
    {"id": 85, "name": "同余运算", "category": "数论", "difficulty": "中等",
     "problem": "17 mod 5 是多少", "answer": 2, "type": "integer"},
    {"id": 86, "name": "欧拉函数", "category": "数论", "difficulty": "困难",
     "problem": "φ(10) 是多少（1-10中与10互质的整数个数）", "answer": 4, "type": "integer"},
    {"id": 87, "name": "完全平方数", "category": "数论", "difficulty": "简单",
     "problem": "100-200之间有多少个完全平方数", "answer": 4, "type": "integer"},
    {"id": 88, "name": "阶乘末尾零", "category": "数论", "difficulty": "中等",
     "problem": "20! 末尾有多少个零", "answer": 4, "type": "integer"},
    {"id": 89, "name": "模幂运算", "category": "数论", "difficulty": "中等",
     "problem": "2¹⁰ mod 100 是多少", "answer": 24, "type": "integer"},
    {"id": 90, "name": "中国剩余定理", "category": "数论", "difficulty": "困难",
     "problem": "x ≡ 2(mod 3), x ≡ 3(mod 5), x ≡ 2(mod 7)，求最小正整数x", "answer": 23, "type": "integer"},
    {"id": 91, "name": "素数定理近似", "category": "数论", "difficulty": "中等",
     "problem": "100以内有多少个质数", "answer": 25, "type": "integer"},
    {"id": 92, "name": "数字和", "category": "数论", "difficulty": "简单",
     "problem": "1到100所有整数的数字和是多少（如123的数字和为6）", "answer": 901, "type": "integer"},
    {"id": 93, "name": "回文数", "category": "数论", "difficulty": "中等",
     "problem": "1000-2000之间有多少个回文数", "answer": 10, "type": "integer"},
    {"id": 94, "name": "梅森素数", "category": "数论", "difficulty": "困难",
     "problem": "2³-1 是素数吗？是则回答3，否则回答0", "answer": 3, "type": "integer"},
    {"id": 95, "name": "斐波那契", "category": "数论", "difficulty": "中等",
     "problem": "斐波那契数列第10项是多少（F₁=1, F₂=1）", "answer": 55, "type": "integer"},
    {"id": 96, "name": "杨辉三角", "category": "数论", "difficulty": "中等",
     "problem": "杨辉三角第6行第3个数是多少（从0行0列开始）", "answer": 10, "type": "integer"},
    {"id": 97, "name": "二进制转换", "category": "数论", "difficulty": "简单",
     "problem": "二进制 1101 转换为十进制是多少", "answer": 13, "type": "integer"},
    {"id": 98, "name": "位数计算", "category": "数论", "difficulty": "中等",
     "problem": "2¹⁰⁰ 有多少位数字（log₁₀2≈0.301，取整）", "answer": 31, "type": "integer"},
    {"id": 99, "name": "连续整数和", "category": "数论", "difficulty": "中等",
     "problem": "100可以表示为多少个连续正整数的和（至少2个）", "answer": 2, "type": "integer"},
    {"id": 100, "name": "约数和", "category": "数论", "difficulty": "困难",
     "problem": "28的所有正因数之和是多少", "answer": 56, "type": "integer"},
]


class MathEvaluator(BaseEvaluator):
    """数学推理能力评估器"""

    name = "math"
    description = "数学推理测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-数学推理"

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
        """运行数学推理测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in MATH_TEST_CASES:
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
        """测试单个数学用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        prompt = f"解决以下数学问题，只输出最终答案数字，不要解释。\n\n问题：{test_case['problem']}\n\n答案："

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个数学专家。只回答数字，不要解释。"},
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

            # 提取数字答案
            answer = self._extract_number(content)
            expected = test_case['answer']

            # 允许一定误差
            if test_case.get('type') == 'ratio':
                passed = answer == expected
            else:
                passed = abs(answer - expected) <= 0.01 * expected if expected != 0 else answer == expected

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case['name'],
                "problem": test_case['problem'],
                "expected": expected,
                "extracted_answer": answer,
                "model_response": content,
                "passed": passed
            }, test_type="math_stage3")

            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "difficulty": test_case['difficulty'],
                    "expected": expected,
                    "actual": answer,
                    "response": content[:200]
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

    def _extract_number(self, text: str) -> float:
        """从文本中提取数字 - 支持推理模型"""
        # 先提取 </think> 后的内容
        text = self._extract_after_think(text)

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
        all_numbers = re.findall(r'\b([\d.]+)\b', text.replace(',', ''))
        if all_numbers:
            try:
                return float(all_numbers[-1])
            except:
                pass
        return float('inf')


def run_math_test(model_url: str, model_name: str) -> dict:
    """运行数学推理测试"""
    evaluator = MathEvaluator(model_url, model_name)
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
    result = run_math_test("http://localhost:8400", "Qwen3VL-4B-Instruct-Q8_0")
    print(f"数学推理测试: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
