#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - 算法与数据结构 (250 题生成器)
自动生成算法题目，包含选择题和代码生成题
"""

import random
import json
import os

# 算法题目模板
ALGORITHM_TEMPLATES = {
    "数组简单": [
        {"q": "数组 [1,2,3,4,5] 反转后的结果是？", "opts": ["[5,4,3,2,1]", "[1,2,3,4,5]", "[2,1,4,3,5]", "[5,1,2,3,4]"], "a": "A"},
        {"q": "Python 中 arr[::-1] 的作用是？", "opts": ["反转数组", "排序数组", "复制数组", "清空数组"], "a": "A"},
        {"q": "数组长度用哪个函数获取？", "opts": ["len(arr)", "arr.length", "arr.size", "sizeof(arr)"], "a": "A"},
        {"q": "arr[0] 访问的是？", "opts": ["第一个元素", "最后一个元素", "中间元素", "随机元素"], "a": "A"},
        {"q": "双指针法常用于？", "opts": ["有序数组查找", "无序数组排序", "图遍历", "树搜索"], "a": "A"},
    ],
    "数组中等": [
        {"q": "Kadane 算法用于解决？", "opts": ["最大子数组和", "数组排序", "数组去重", "数组合并"], "a": "A"},
        {"q": "滑动窗口最大值用？", "opts": ["单调双端队列", "普通队列", "栈", "哈希表"], "a": "A"},
        {"q": "旋转排序数组搜索复杂度？", "opts": ["O(log n)", "O(n)", "O(n log n)", "O(1)"], "a": "A"},
        {"q": "接雨水问题用？", "opts": ["单调栈", "贪心", "回溯", "位运算"], "a": "A"},
        {"q": "合并区间前先？", "opts": ["排序", "去重", "反转", "二分"], "a": "A"},
    ],
    "数组困难": [
        {"q": "中位数维护用？", "opts": ["双堆", "单堆", "栈", "队列"], "a": "A"},
        {"q": "第 K 大元素 O(n) 用？", "opts": ["快速选择", "排序", "暴力", "DP"], "a": "A"},
        {"q": "最长连续序列 O(n) 用？", "opts": ["哈希集合", "排序", "DP", "贪心"], "a": "A"},
    ],
    "链表": [
        {"q": "反转链表的时间复杂度？", "opts": ["O(n)", "O(1)", "O(log n)", "O(n²)"], "a": "A"},
        {"q": "检测链表环用？", "opts": ["快慢指针", "哈希表", "递归", "栈"], "a": "A"},
        {"q": "合并两个有序链表用？", "opts": ["双指针", "递归", "都可以", "都不行"], "a": "C"},
        {"q": "删除链表倒数第 N 个节点用？", "opts": ["双指针", "单指针", "递归", "栈"], "a": "A"},
        {"q": "LRU 缓存用？", "opts": ["哈希 + 双向链表", "数组", "栈", "队列"], "a": "A"},
    ],
    "栈和队列": [
        {"q": "栈的特性是？", "opts": ["后进先出", "先进先出", "随机访问", "有序"], "a": "A"},
        {"q": "队列的特性是？", "opts": ["先进先出", "后进先出", "随机访问", "有序"], "a": "A"},
        {"q": "有效的括号用？", "opts": ["栈", "队列", "哈希表", "堆"], "a": "A"},
        {"q": "单调栈用于？", "opts": ["找下一个更大元素", "排序", "查找", "去重"], "a": "A"},
        {"q": "最小栈需要？", "opts": ["辅助栈", "单栈", "队列", "哈希"], "a": "A"},
    ],
    "树": [
        {"q": "二叉树前序遍历顺序？", "opts": ["根左右", "左根右", "左右根", "右左根"], "a": "A"},
        {"q": "二叉树中序遍历顺序？", "opts": ["左根右", "根左右", "左右根", "右左根"], "a": "A"},
        {"q": "二叉树后序遍历顺序？", "opts": ["左右根", "根左右", "左根右", "右左根"], "a": "A"},
        {"q": "二叉树层序遍历用？", "opts": ["BFS 队列", "DFS 栈", "递归", "迭代"], "a": "A"},
        {"q": "BST 的中序遍历是？", "opts": ["升序", "降序", "无序", "随机"], "a": "A"},
        {"q": "平衡二叉树 AVL 要求？", "opts": ["左右子树高度差<=1", "完全二叉树", "满二叉树", "任意"], "a": "A"},
        {"q": "最近公共祖先用？", "opts": ["递归", "迭代", "BFS", "DFS"], "a": "A"},
        {"q": "二叉树最大深度用？", "opts": ["DFS 或 BFS", "只 DFS", "只 BFS", "贪心"], "a": "A"},
    ],
    "动态规划": [
        {"q": "DP 的核心是？", "opts": ["状态转移方程", "贪心策略", "回溯搜索", "分治"], "a": "A"},
        {"q": "斐波那契 DP 时间复杂度？", "opts": ["O(n)", "O(2^n)", "O(n²)", "O(log n)"], "a": "A"},
        {"q": "0-1 背包问题用？", "opts": ["DP", "贪心", "回溯", "分治"], "a": "A"},
        {"q": "最长递增子序列用？", "opts": ["DP 或贪心 + 二分", "只贪心", "只回溯", "只分治"], "a": "A"},
        {"q": "编辑距离用？", "opts": ["DP", "贪心", "BFS", "DFS"], "a": "A"},
        {"q": "最大子数组和用？", "opts": ["Kadane(DP)", "贪心", "回溯", "分治"], "a": "A"},
        {"q": "DP 空间优化常用？", "opts": ["滚动数组", "哈希表", "栈", "队列"], "a": "A"},
    ],
    "图": [
        {"q": "图的 DFS 用？", "opts": ["栈或递归", "队列", "哈希表", "堆"], "a": "A"},
        {"q": "图的 BFS 用？", "opts": ["队列", "栈", "哈希表", "堆"], "a": "A"},
        {"q": "拓扑排序用于？", "opts": ["DAG", "无向图", "完全图", "二分图"], "a": "A"},
        {"q": "Dijkstra 算法求？", "opts": ["单源最短路径", "多源最短路径", "最小生成树", "最大流"], "a": "A"},
        {"q": "最小生成树用？", "opts": ["Prim 或 Kruskal", "Dijkstra", "BFS", "DFS"], "a": "A"},
        {"q": "并查集用于？", "opts": ["连通分量", "最短路径", "拓扑排序", "关键路径"], "a": "A"},
        {"q": "Bellman-Ford 可以处理？", "opts": ["负权边", "只能正权", "无向图", "DAG"], "a": "A"},
    ],
    "排序": [
        {"q": "快速排序平均复杂度？", "opts": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], "a": "A"},
        {"q": "归并排序复杂度？", "opts": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], "a": "A"},
        {"q": "堆排序复杂度？", "opts": ["O(n log n)", "O(n²)", "O(n)", "O(log n)"], "a": "A"},
        {"q": "计数排序适用于？", "opts": ["小范围整数", "任意数据", "浮点数", "字符串"], "a": "A"},
        {"q": "稳定排序是？", "opts": ["归并排序", "快速排序", "堆排序", "选择排序"], "a": "A"},
    ],
    "二分查找": [
        {"q": "二分查找要求数组？", "opts": ["有序", "无序", "任意", "随机"], "a": "A"},
        {"q": "二分查找复杂度？", "opts": ["O(log n)", "O(n)", "O(1)", "O(n log n)"], "a": "A"},
        {"q": "寻找旋转数组最小值用？", "opts": ["二分", "线性", "贪心", "DP"], "a": "A"},
        {"q": "二分查找边界处理？", "opts": ["left<=right", "left<right", "left=right", "任意"], "a": "A"},
    ],
    "回溯": [
        {"q": "全排列用？", "opts": ["回溯", "贪心", "DP", "分治"], "a": "A"},
        {"q": "N 皇后用？", "opts": ["回溯", "贪心", "DP", "分治"], "a": "A"},
        {"q": "子集问题用？", "opts": ["回溯", "贪心", "DP", "分治"], "a": "A"},
        {"q": "括号生成用？", "opts": ["回溯", "贪心", "DP", "分治"], "a": "A"},
    ],
    "贪心": [
        {"q": "贪心算法的核心是？", "opts": ["局部最优", "全局最优", "回溯", "DP"], "a": "A"},
        {"q": "区间调度用？", "opts": ["贪心", "DP", "回溯", "分治"], "a": "A"},
        {"q": "霍夫曼编码用？", "opts": ["贪心", "DP", "回溯", "分治"], "a": "A"},
        {"q": "最小生成树 Prim 是？", "opts": ["贪心", "DP", "回溯", "分治"], "a": "A"},
    ],
}

def generate_algorithm_questions(target_count=250):
    """生成算法题目，答案随机分布在 A/B/C/D"""
    questions = []
    qid = 1

    # 难度分布：简单 30%, 中等 50%, 困难 20%
    easy_count = int(target_count * 0.3)
    medium_count = int(target_count * 0.5)
    hard_count = target_count - easy_count - medium_count

    categories = {
        "简单": ["数组简单", "链表", "栈和队列", "树", "排序", "二分查找"],
        "中等": ["数组中等", "动态规划", "图", "回溯", "贪心"],
        "困难": ["数组困难", "动态规划", "图"],
    }

    def shuffle_options(template):
        """打乱选项顺序，返回新选项和对应答案"""
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

    # 生成简单题
    for _ in range(easy_count):
        cat = random.choice(categories["简单"])
        if cat in ALGORITHM_TEMPLATES and ALGORITHM_TEMPLATES[cat]:
            template = random.choice(ALGORITHM_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"算法-{cat}-{qid}",
                "category": cat,
                "difficulty": "简单",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["algorithm"]
            })
            qid += 1

    # 生成中等题
    for _ in range(medium_count):
        cat = random.choice(categories["中等"])
        if cat in ALGORITHM_TEMPLATES and ALGORITHM_TEMPLATES[cat]:
            template = random.choice(ALGORITHM_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"算法-{cat}-{qid}",
                "category": cat,
                "difficulty": "中等",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["algorithm"]
            })
            qid += 1

    # 生成困难题
    for _ in range(hard_count):
        cat = random.choice(categories["困难"])
        if cat in ALGORITHM_TEMPLATES and ALGORITHM_TEMPLATES[cat]:
            template = random.choice(ALGORITHM_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid,
                "name": f"算法-{cat}-{qid}",
                "category": cat,
                "difficulty": "困难",
                "question": template["q"],
                "options": shuffled_opts,
                "answer": new_answer,
                "keywords": ["algorithm"]
            })
            qid += 1

    return questions


class AlgorithmEvaluator:
    """算法评估器"""

    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_algorithm_questions(250)

    def run_tests(self):
        """运行算法测试"""
        return self.base_eval.run_tests(self.test_cases, "algorithm")

    def generate_report(self, result):
        """生成报告"""
        return self.base_eval.generate_report(result)


def run_algorithm_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    """便捷函数运行算法测试"""
    evaluator = AlgorithmEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {
        "result": result,
        "report_file": report_file
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 算法测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型地址")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M", help="模型名称")
    parser.add_argument("--output-dir", default="eval_results/stage4", help="输出目录")
    parser.add_argument("--generate-only", action="store_true", help="只生成题目不运行")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_algorithm_questions(250)
        print(f"生成了 {len(questions)} 道算法题目:")
        easy = sum(1 for q in questions if q["difficulty"] == "简单")
        medium = sum(1 for q in questions if q["difficulty"] == "中等")
        hard = sum(1 for q in questions if q["difficulty"] == "困难")
        print(f"  简单：{easy}, 中等：{medium}, 困难：{hard}")

        # 保存题目
        output_file = os.path.join(args.output_dir, "algorithm_questions.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
        print(f"题目已保存到：{output_file}")
    else:
        print(f"开始运行算法测试...")
        test_result = run_algorithm_test(args.model_url, args.model_name, args.output_dir)
        print(f"\n测试完成！通过率：{test_result['result'].pass_rate*100:.1f}%")
