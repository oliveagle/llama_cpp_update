#!/usr/bin/env python3
"""
Stage 3 深度代码生成测试 (100 cases)
涵盖：算法、数据结构、字符串处理、数学计算、文件操作等
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult


# 代码生成测试用例 (100个)
CODE_TEST_CASES = [
    # ===== 基础算法 (20题) =====
    {"id": 1, "name": "两数之和", "category": "基础算法", "difficulty": "简单",
     "prompt": "def two_sum(nums: list[int], target: int) -> list[int]:\n    '''找到数组中两数之和等于target的索引，假设每个输入只有一个答案'''\n    # 示例: two_sum([2,7,11,15], 9) -> [0,1]",
     "test_cases": [{"input": [[2,7,11,15], 9], "expected": [0,1]}, {"input": [[3,2,4], 6], "expected": [1,2]}]},

    {"id": 2, "name": "反转链表", "category": "基础算法", "difficulty": "中等",
     "prompt": "class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_list(head: ListNode) -> ListNode:\n    '''反转单链表'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 3, "name": "合并有序数组", "category": "基础算法", "difficulty": "简单",
     "prompt": "def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:\n    '''合并两个有序数组到nums1，假设nums1有足够的空间，原地修改'''",
     "test_cases": [{"input": [[1,2,3,0,0,0], 3, [2,5,6], 3], "expected": [1,2,2,3,5,6]}]},

    {"id": 4, "name": "最大子数组和", "category": "基础算法", "difficulty": "中等",
     "prompt": "def max_sub_array(nums: list[int]) -> int:\n    '''使用Kadane算法找出具有最大和的连续子数组的和'''\n    # 示例: max_sub_array([-2,1,-3,4,-1,2,1,-5,4]) -> 6",
     "test_cases": [{"input": [[-2,1,-3,4,-1,2,1,-5,4]], "expected": 6}, {"input": [[1]], "expected": 1}]},

    {"id": 5, "name": "爬楼梯", "category": "基础算法", "difficulty": "简单",
     "prompt": "def climb_stairs(n: int) -> int:\n    '''n阶楼梯，每次爬1或2阶，求到达顶部的不同方法数'''\n    # 斐波那契数列",
     "test_cases": [{"input": [2], "expected": 2}, {"input": [3], "expected": 3}, {"input": [4], "expected": 5}]},

    {"id": 6, "name": "二进制中1的个数", "category": "基础算法", "difficulty": "简单",
     "prompt": "def hamming_weight(n: int) -> int:\n    '''返回无符号整数二进制表示中1的个数（汉明重量）'''",
     "test_cases": [{"input": [11], "expected": 3}, {"input": [128], "expected": 1}]},

    {"id": 7, "name": "只出现一次的数字", "category": "基础算法", "difficulty": "中等",
     "prompt": "def single_number(nums: list[int]) -> int:\n    '''数组中每个元素都出现两次，只有一个出现一次，找出它（使用异或）'''",
     "test_cases": [{"input": [[2,2,1]], "expected": 1}, {"input": [[4,1,2,1,2]], "expected": 4}]},

    {"id": 8, "name": "环形链表检测", "category": "基础算法", "difficulty": "中等",
     "prompt": "def has_cycle(head) -> bool:\n    '''检测链表中是否有环（使用快慢指针）'''",
     "test_cases": [{"input": [[]], "expected": False}]},

    {"id": 9, "name": "有效括号", "category": "基础算法", "difficulty": "简单",
     "prompt": "def is_valid(s: str) -> bool:\n    '''判断字符串中的括号是否有效，包括(), {}, []'''\n    # 示例: is_valid('()[]{}') -> True, is_valid('([)]') -> False",
     "test_cases": [{"input": ["()"], "expected": True}, {"input": ["()[]{}"], "expected": True}, {"input": ["([)]"], "expected": False}]},

    {"id": 10, "name": "最小栈", "category": "基础算法", "difficulty": "中等",
     "prompt": "class MinStack:\n    '''设计一个栈，支持push、pop、top操作，并能在常数时间内检索最小元素'''\n    def __init__(self):\n        pass\n    def push(self, val: int) -> None:\n        pass\n    def pop(self) -> None:\n        pass\n    def top(self) -> int:\n        pass\n    def get_min(self) -> int:\n        pass",
     "test_cases": []},

    {"id": 11, "name": "移动零", "category": "基础算法", "difficulty": "简单",
     "prompt": "def move_zeroes(nums: list[int]) -> None:\n    '''将所有0移动到数组末尾，保持非零元素相对顺序，原地修改'''\n    # 示例: [0,1,0,3,12] -> [1,3,12,0,0]",
     "test_cases": [{"input": [[0,1,0,3,12]], "expected": [1,3,12,0,0]}]},

    {"id": 12, "name": "多数元素", "category": "基础算法", "difficulty": "中等",
     "prompt": "def majority_element(nums: list[int]) -> int:\n    '''找出数组中出现次数超过n/2的元素（摩尔投票法）'''",
     "test_cases": [{"input": [[3,2,3]], "expected": 3}, {"input": [[2,2,1,1,1,2,2]], "expected": 2}]},

    {"id": 13, "name": "买卖股票的最佳时机", "category": "基础算法", "difficulty": "简单",
     "prompt": "def max_profit(prices: list[int]) -> int:\n    '''给定股票价格数组，找出最大利润（只能买卖一次）'''\n    # 示例: [7,1,5,3,6,4] -> 5 (在1买6卖)",
     "test_cases": [{"input": [[7,1,5,3,6,4]], "expected": 5}, {"input": [[7,6,4,3,1]], "expected": 0}]},

    {"id": 14, "name": "反转字符串", "category": "基础算法", "difficulty": "简单",
     "prompt": "def reverse_string(s: list[str]) -> None:\n    '''原地反转字符串数组'''",
     "test_cases": [{"input": [["h","e","l","l","o"]], "expected": ["o","l","l","e","h"]}]},

    {"id": 15, "name": "斐波那契数", "category": "基础算法", "difficulty": "简单",
     "prompt": "def fib(n: int) -> int:\n    '''返回斐波那契数列第n项（F(0)=0, F(1)=1）'''",
     "test_cases": [{"input": [2], "expected": 1}, {"input": [3], "expected": 2}, {"input": [4], "expected": 3}]},

    {"id": 16, "name": "位1的个数", "category": "基础算法", "difficulty": "简单",
     "prompt": "def count_bits(n: int) -> int:\n    '''计算0到n每个数的二进制中1的个数，返回列表'''",
     "test_cases": [{"input": [2], "expected": [0,1,1]}, {"input": [5], "expected": [0,1,1,2,1,2]}]},

    {"id": 17, "name": "3的幂", "category": "基础算法", "difficulty": "简单",
     "prompt": "def is_power_of_three(n: int) -> bool:\n    '''判断n是否为3的幂'''",
     "test_cases": [{"input": [27], "expected": True}, {"input": [0], "expected": False}, {"input": [9], "expected": True}]},

    {"id": 18, "name": "第一个错误版本", "category": "基础算法", "difficulty": "简单",
     "prompt": "def first_bad_version(n: int) -> int:\n    '''使用二分查找找出第一个错误版本，isBadVersion(api)已定义'''",
     "test_cases": [{"input": [5], "expected": 4}]},

    {"id": 19, "name": "完全平方数", "category": "基础算法", "difficulty": "中等",
     "prompt": "def is_perfect_square(num: int) -> bool:\n    '''判断正整数是否为完全平方数，不使用内置平方根函数'''",
     "test_cases": [{"input": [16], "expected": True}, {"input": [14], "expected": False}]},

    {"id": 20, "name": "猜数字游戏", "category": "基础算法", "difficulty": "简单",
     "prompt": "def guess_number(n: int) -> int:\n    '''二分查找猜1到n之间的数字，guess(num)返回-1,0,1'''",
     "test_cases": [{"input": [10], "expected": 6}]},

    # ===== 数据结构 (20题) =====
    {"id": 21, "name": "实现队列使用栈", "category": "数据结构", "difficulty": "中等",
     "prompt": "class MyQueue:\n    '''用栈实现队列，支持push、pop、peek、empty操作'''\n    def __init__(self):\n        pass\n    def push(self, x: int) -> None:\n        pass\n    def pop(self) -> int:\n        pass\n    def peek(self) -> int:\n        pass\n    def empty(self) -> bool:\n        pass",
     "test_cases": []},

    {"id": 22, "name": "实现栈使用队列", "category": "数据结构", "difficulty": "中等",
     "prompt": "class MyStack:\n    '''用队列实现栈，支持push、pop、top、empty操作'''",
     "test_cases": []},

    {"id": 23, "name": "LRU缓存", "category": "数据结构", "difficulty": "困难",
     "prompt": "class LRUCache:\n    '''设计LRU缓存，容量为capacity，get和put都是O(1)'''\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        pass\n    def put(self, key: int, value: int) -> None:\n        pass",
     "test_cases": []},

    {"id": 24, "name": "二叉树前序遍历", "category": "数据结构", "difficulty": "中等",
     "prompt": "class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\ndef preorder_traversal(root: TreeNode) -> list[int]:\n    '''二叉树前序遍历（迭代实现）'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 25, "name": "二叉树层次遍历", "category": "数据结构", "difficulty": "中等",
     "prompt": "def level_order(root) -> list[list[int]]:\n    '''二叉树按层次遍历，返回每层节点值的列表'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 26, "name": "验证二叉搜索树", "category": "数据结构", "difficulty": "中等",
     "prompt": "def is_valid_bst(root) -> bool:\n    '''验证二叉树是否为有效的二叉搜索树'''",
     "test_cases": [{"input": [[]], "expected": True}]},

    {"id": 27, "name": "对称二叉树", "category": "数据结构", "difficulty": "简单",
     "prompt": "def is_symmetric(root) -> bool:\n    '''检查二叉树是否轴对称'''",
     "test_cases": [{"input": [[]], "expected": True}]},

    {"id": 28, "name": "二叉树最大深度", "category": "数据结构", "difficulty": "简单",
     "prompt": "def max_depth(root) -> int:\n    '''返回二叉树的最大深度'''",
     "test_cases": [{"input": [[]], "expected": 0}, {"input": [[1]], "expected": 1}]},

    {"id": 29, "name": "相同的树", "category": "数据结构", "difficulty": "简单",
     "prompt": "def is_same_tree(p, q) -> bool:\n    '''判断两棵二叉树是否相同'''",
     "test_cases": [{"input": [[], []], "expected": True}]},

    {"id": 30, "name": "路径总和", "category": "数据结构", "difficulty": "简单",
     "prompt": "def has_path_sum(root, targetSum: int) -> bool:\n    '''判断二叉树中是否存在根到叶的路径和等于targetSum'''",
     "test_cases": [{"input": [[], 0], "expected": False}]},

    {"id": 31, "name": "二叉树中序遍历", "category": "数据结构", "difficulty": "中等",
     "prompt": "def inorder_traversal(root) -> list[int]:\n    '''二叉树中序遍历（迭代实现）'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 32, "name": "二叉树后序遍历", "category": "数据结构", "difficulty": "中等",
     "prompt": "def postorder_traversal(root) -> list[int]:\n    '''二叉树后序遍历（迭代实现）'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 33, "name": "翻转二叉树", "category": "数据结构", "difficulty": "简单",
     "prompt": "def invert_tree(root):\n    '''翻转二叉树（镜像）'''",
     "test_cases": [{"input": [[]], "expected": []}]},

    {"id": 34, "name": "合并二叉树", "category": "数据结构", "difficulty": "简单",
     "prompt": "def merge_trees(root1, root2):\n    '''合并两棵二叉树，重叠节点值相加'''",
     "test_cases": [{"input": [[], []], "expected": []}]},

    {"id": 35, "name": "最小堆实现", "category": "数据结构", "difficulty": "中等",
     "prompt": "class MinHeap:\n    '''实现最小堆，支持push、pop、peek'''\n    def __init__(self):\n        pass\n    def push(self, val: int):\n        pass\n    def pop(self) -> int:\n        pass\n    def peek(self) -> int:\n        pass",
     "test_cases": []},

    {"id": 36, "name": "并查集", "category": "数据结构", "difficulty": "中等",
     "prompt": "class UnionFind:\n    '''实现并查集，支持find和union操作'''\n    def __init__(self, n: int):\n        pass\n    def find(self, x: int) -> int:\n        pass\n    def union(self, x: int, y: int) -> None:\n        pass",
     "test_cases": []},

    {"id": 37, "name": "Trie树", "category": "数据结构", "difficulty": "中等",
     "prompt": "class Trie:\n    '''实现前缀树，支持insert、search、startsWith'''\n    def __init__(self):\n        pass\n    def insert(self, word: str) -> None:\n        pass\n    def search(self, word: str) -> bool:\n        pass\n    def starts_with(self, prefix: str) -> bool:\n        pass",
     "test_cases": []},

    {"id": 38, "name": "二叉搜索树迭代器", "category": "数据结构", "difficulty": "中等",
     "prompt": "class BSTIterator:\n    '''实现二叉搜索树迭代器，支持next和hasNext，平均O(1)时间'''\n    def __init__(self, root):\n        pass\n    def next(self) -> int:\n        pass\n    def has_next(self) -> bool:\n        pass",
     "test_cases": []},

    {"id": 39, "name": "线段树", "category": "数据结构", "difficulty": "困难",
     "prompt": "class SegmentTree:\n    '''实现线段树，支持区间查询和单点更新'''\n    def __init__(self, nums: list[int]):\n        pass\n    def update(self, index: int, val: int) -> None:\n        pass\n    def query(self, left: int, right: int) -> int:\n        pass",
     "test_cases": []},

    {"id": 40, "name": "红黑树简化版", "category": "数据结构", "difficulty": "困难",
     "prompt": "class MyMap:\n    '''使用哈希表实现类似TreeMap的功能，支持put、get、remove'''\n    def __init__(self):\n        pass\n    def put(self, key: int, value: int) -> None:\n        pass\n    def get(self, key: int) -> int:\n        pass\n    def remove(self, key: int) -> None:\n        pass",
     "test_cases": []},

    # ===== 字符串处理 (20题) =====
    {"id": 41, "name": "反转字符串中的单词", "category": "字符串", "difficulty": "中等",
     "prompt": "def reverse_words(s: str) -> str:\n    '''反转字符串中每个单词的字符顺序，同时反转单词顺序，去除多余空格'''\n    # 示例: \"the sky is blue\" -> \"blue is sky the\"",
     "test_cases": [{"input": ["the sky is blue"], "expected": "blue is sky the"}]},

    {"id": 42, "name": "最长无重复子串", "category": "字符串", "difficulty": "中等",
     "prompt": "def length_of_longest_substring(s: str) -> int:\n    '''找出最长的不含重复字符的子串长度（滑动窗口）'''",
     "test_cases": [{"input": ["abcabcbb"], "expected": 3}, {"input": ["bbbbb"], "expected": 1}]},

    {"id": 43, "name": "最长公共前缀", "category": "字符串", "difficulty": "简单",
     "prompt": "def longest_common_prefix(strs: list[str]) -> str:\n    '''找出字符串数组的最长公共前缀'''",
     "test_cases": [{"input": [["flower","flow","flight"]], "expected": "fl"}, {"input": [["dog","racecar","car"]], "expected": ""}]},

    {"id": 44, "name": "实现strStr", "category": "字符串", "difficulty": "简单",
     "prompt": "def str_str(haystack: str, needle: str) -> int:\n    '''返回needle在haystack中首次出现的索引，使用KMP算法'''",
     "test_cases": [{"input": ["hello", "ll"], "expected": 2}, {"input": ["aaaaa", "bba"], "expected": -1}]},

    {"id": 45, "name": "字符串转整数", "category": "字符串", "difficulty": "中等",
     "prompt": "def my_atoi(s: str) -> int:\n    '''将字符串转换为32位有符号整数，处理各种边界情况'''",
     "test_cases": [{"input": ["42"], "expected": 42}, {"input": ["   -42"], "expected": -42}]},

    {"id": 46, "name": "回文数判断", "category": "字符串", "difficulty": "简单",
     "prompt": "def is_palindrome(x: int) -> bool:\n    '''判断整数是否为回文数，不转换为字符串'''",
     "test_cases": [{"input": [121], "expected": True}, {"input": [-121], "expected": False}]},

    {"id": 47, "name": "计数并说", "category": "字符串", "difficulty": "中等",
     "prompt": "def count_and_say(n: int) -> str:\n    '''外观数列第n项，递归描述前一项'''",
     "test_cases": [{"input": [1], "expected": "1"}, {"input": [4], "expected": "1211"}]},

    {"id": 48, "name": "有效的字母异位词", "category": "字符串", "difficulty": "简单",
     "prompt": "def is_anagram(s: str, t: str) -> bool:\n    '''判断t是否为s的字母异位词（字符重排）'''",
     "test_cases": [{"input": ["anagram", "nagaram"], "expected": True}, {"input": ["rat", "car"], "expected": False}]},

    {"id": 49, "name": "验证回文字符串", "category": "字符串", "difficulty": "简单",
     "prompt": "def is_palindrome_str(s: str) -> bool:\n    '''验证字符串是否为回文，只考虑字母数字，忽略大小写'''",
     "test_cases": [{"input": ["A man, a plan, a canal: Panama"], "expected": True}, {"input": ["race a car"], "expected": False}]},

    {"id": 50, "name": "字符串相加", "category": "字符串", "difficulty": "简单",
     "prompt": "def add_strings(num1: str, num2: str) -> str:\n    '''两个字符串形式的非负整数相加，返回字符串结果，不使用内置大整数'''",
     "test_cases": [{"input": ["11", "123"], "expected": "134"}, {"input": ["456", "77"], "expected": "533"}]},

    {"id": 51, "name": "Z字形变换", "category": "字符串", "difficulty": "中等",
     "prompt": "def convert(s: str, numRows: int) -> str:\n    '''将字符串按Z字形排列后按行读取'''",
     "test_cases": [{"input": ["PAYPALISHIRING", 3], "expected": "PAHNAPLSIIGYIR"}]},

    {"id": 52, "name": "正则表达式匹配", "category": "字符串", "difficulty": "困难",
     "prompt": "def is_match(s: str, p: str) -> bool:\n    '''实现正则表达式匹配，支持.和*'''\n    # . 匹配任意单个字符，* 匹配零个或多个前面的元素",
     "test_cases": [{"input": ["aa", "a"], "expected": False}, {"input": ["aa", "a*"], "expected": True}]},

    {"id": 53, "name": "通配符匹配", "category": "字符串", "difficulty": "困难",
     "prompt": "def is_match_wildcard(s: str, p: str) -> bool:\n    '''实现通配符匹配，支持?和*'''\n    # ? 匹配任意单个字符，* 匹配任意字符串（包括空）",
     "test_cases": [{"input": ["aa", "a"], "expected": False}, {"input": ["aa", "*"], "expected": True}]},

    {"id": 54, "name": "最小覆盖子串", "category": "字符串", "difficulty": "困难",
     "prompt": "def min_window(s: str, t: str) -> str:\n    '''找出s中涵盖t所有字符的最小子串'''",
     "test_cases": [{"input": ["ADOBECODEBANC", "ABC"], "expected": "BANC"}]},

    {"id": 55, "name": "找到字符串中所有字母异位词", "category": "字符串", "difficulty": "中等",
     "prompt": "def find_anagrams(s: str, p: str) -> list[int]:\n    '''找到s中所有p的字母异位词的起始索引'''",
     "test_cases": [{"input": ["cbaebabacd", "abc"], "expected": [0, 6]}]},

    {"id": 56, "name": "解码方法", "category": "字符串", "difficulty": "中等",
     "prompt": "def num_decodings(s: str) -> int:\n    '''数字字符串解码为字母（A=1...Z=26）的方法数'''",
     "test_cases": [{"input": ["12"], "expected": 2}, {"input": ["226"], "expected": 3}]},

    {"id": 57, "name": "简化路径", "category": "字符串", "difficulty": "中等",
     "prompt": "def simplify_path(path: str) -> str:\n    '''简化Unix风格的绝对路径'''",
     "test_cases": [{"input": ["/home/"], "expected": "/home"}, {"input": ["/../"], "expected": "/"}]},

    {"id": 58, "name": "编辑距离", "category": "字符串", "difficulty": "困难",
     "prompt": "def min_distance(word1: str, word2: str) -> int:\n    '''计算两个单词的最小编辑距离（插入、删除、替换）'''",
     "test_cases": [{"input": ["horse", "ros"], "expected": 3}, {"input": ["intention", "execution"], "expected": 5}]},

    {"id": 59, "name": "基本计算器", "category": "字符串", "difficulty": "困难",
     "prompt": "def calculate(s: str) -> int:\n    '''实现基本计算器，支持加减和括号'''\n    # 示例: \"1 + 1\" = 2, \" 2-1 + 2 \" = 3, \"(1+(4+5+2)-3)+(6+8)\" = 23",
     "test_cases": [{"input": ["1 + 1"], "expected": 2}, {"input": [" 2-1 + 2 "], "expected": 3}]},

    {"id": 60, "name": "文本左右对齐", "category": "字符串", "difficulty": "困难",
     "prompt": "def full_justify(words: list[str], maxWidth: int) -> list[str]:\n    '''将单词数组按每行最大宽度左对齐，最后一行左对齐其他均匀分布'''",
     "test_cases": [{"input": [["This", "is", "an", "example"], 16], "expected": []}]},

    # ===== 排序算法 (20题) =====
    {"id": 61, "name": "快速排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def quick_sort(nums: list[int]) -> list[int]:\n    '''实现快速排序算法，原地排序'''",
     "test_cases": [{"input": [[3,6,2,7,1]], "expected": [1,2,3,6,7]}]},

    {"id": 62, "name": "归并排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def merge_sort(nums: list[int]) -> list[int]:\n    '''实现归并排序算法'''",
     "test_cases": [{"input": [[3,6,2,7,1]], "expected": [1,2,3,6,7]}]},

    {"id": 63, "name": "堆排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def heap_sort(nums: list[int]) -> list[int]:\n    '''实现堆排序算法'''",
     "test_cases": [{"input": [[3,6,2,7,1]], "expected": [1,2,3,6,7]}]},

    {"id": 64, "name": "计数排序", "category": "排序算法", "difficulty": "简单",
     "prompt": "def counting_sort(nums: list[int]) -> list[int]:\n    '''实现计数排序，假设数值范围0-100'''",
     "test_cases": [{"input": [[3,6,2,7,1]], "expected": [1,2,3,6,7]}]},

    {"id": 65, "name": "桶排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def bucket_sort(nums: list[int], bucket_size: int = 5) -> list[int]:\n    '''实现桶排序'''",
     "test_cases": [{"input": [[3,6,2,7,1]], "expected": [1,2,3,6,7]}]},

    {"id": 66, "name": "基数排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def radix_sort(nums: list[int]) -> list[int]:\n    '''实现基数排序（LSD）'''",
     "test_cases": [{"input": [[170, 45, 75, 90, 2]], "expected": [2, 45, 75, 90, 170]}]},

    {"id": 67, "name": "第K大元素", "category": "排序算法", "difficulty": "中等",
     "prompt": "def find_kth_largest(nums: list[int], k: int) -> int:\n    '''在未排序数组中找出第k大的元素（使用快速选择）'''",
     "test_cases": [{"input": [[3,2,1,5,6,4], 2], "expected": 5}]},

    {"id": 68, "name": "前K个高频元素", "category": "排序算法", "difficulty": "中等",
     "prompt": "def top_k_frequent(nums: list[int], k: int) -> list[int]:\n    '''返回出现频率前k高的元素'''",
     "test_cases": [{"input": [[1,1,1,2,2,3], 2], "expected": [1,2]}]},

    {"id": 69, "name": "数组中的第K个最大元素II", "category": "排序算法", "difficulty": "中等",
     "prompt": "def find_kth_largest_heap(nums: list[int], k: int) -> int:\n    '''使用堆找出第k大元素'''",
     "test_cases": [{"input": [[3,2,3,1,2,4,5,5,6], 4], "expected": 4}]},

    {"id": 70, "name": "根据字符出现频率排序", "category": "排序算法", "difficulty": "中等",
     "prompt": "def frequency_sort(s: str) -> str:\n    '''按字符出现频率降序排列字符串'''",
     "test_cases": [{"input": ["tree"], "expected": "eert"}]},

    {"id": 71, "name": "摆动排序II", "category": "排序算法", "difficulty": "中等",
     "prompt": "def wiggle_sort(nums: list[int]) -> None:\n    '''将数组重新排列成nums[0]<nums[1]>nums[2]<nums[3]...的形式，原地修改'''",
     "test_cases": [{"input": [[1,5,1,1,6,4]], "expected": [1,6,1,5,1,4]}]},

    {"id": 72, "name": "最大间距", "category": "排序算法", "difficulty": "困难",
     "prompt": "def maximum_gap(nums: list[int]) -> int:\n    '''返回排序后相邻元素最大差值，要求线性时间'''",
     "test_cases": [{"input": [[3,6,9,1]], "expected": 3}]},

    {"id": 73, "name": "有序矩阵中第K小元素", "category": "排序算法", "difficulty": "中等",
     "prompt": "def kth_smallest(matrix: list[list[int]], k: int) -> int:\n    '''返回n×n有序矩阵中第k小的元素'''",
     "test_cases": [{"input": [[[1,5,9],[10,11,13],[12,13,15]], 8], "expected": 13}]},

    {"id": 74, "name": "寻找重复数", "category": "排序算法", "difficulty": "中等",
     "prompt": "def find_duplicate(nums: list[int]) -> int:\n    '''数组n+1个数都在1到n之间，找出唯一的重复数，不修改数组'''",
     "test_cases": [{"input": [[1,3,4,2,2]], "expected": 2}]},

    {"id": 75, "name": "区间合并", "category": "排序算法", "difficulty": "中等",
     "prompt": "def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:\n    '''合并所有重叠的区间'''",
     "test_cases": [{"input": [[[1,3],[2,6],[8,10],[15,18]]], "expected": [[1,6],[8,10],[15,18]]}]},

    {"id": 76, "name": "插入区间", "category": "排序算法", "difficulty": "中等",
     "prompt": "def insert(intervals: list[list[int]], newInterval: list[int]) -> list[list[int]]:\n    '''将新区间插入不重叠的区间列表'''",
     "test_cases": [{"input": [[[1,3],[6,9]], [2,5]], "expected": [[1,5],[6,9]]}]},

    {"id": 77, "name": "缺失的第一个正数", "category": "排序算法", "difficulty": "困难",
     "prompt": "def first_missing_positive(nums: list[int]) -> int:\n    '''找出未出现的最小正整数，要求O(n)时间和O(1)空间'''",
     "test_cases": [{"input": [[1,2,0]], "expected": 3}, {"input": [[3,4,-1,1]], "expected": 2}]},

    {"id": 78, "name": "寻找峰值", "category": "排序算法", "difficulty": "中等",
     "prompt": "def find_peak_element(nums: list[int]) -> int:\n    '''返回峰值元素索引，nums[i]≠nums[i+1]，使用二分查找O(log n)'''",
     "test_cases": [{"input": [[1,2,3,1]], "expected": 2}]},

    {"id": 79, "name": "数组中的逆序对", "category": "排序算法", "difficulty": "困难",
     "prompt": "def reverse_pairs(nums: list[int]) -> int:\n    '''返回数组中的逆序对总数，使用归并排序'''",
     "test_cases": [{"input": [[1,3,2,3,1]], "expected": 2}]},

    {"id": 80, "name": "计算右侧小于当前元素的个数", "category": "排序算法", "difficulty": "困难",
     "prompt": "def count_smaller(nums: list[int]) -> list[int]:\n    '''返回每个元素右侧小于它的元素个数'''",
     "test_cases": [{"input": [[5,2,6,1]], "expected": [2,1,1,0]}]},

    # ===== 动态规划 (20题) =====
    {"id": 81, "name": "不同路径", "category": "动态规划", "difficulty": "中等",
     "prompt": "def unique_paths(m: int, n: int) -> int:\n    '''m×n网格，从左上到右下，每次只能向下或向右，求不同路径数'''",
     "test_cases": [{"input": [3, 7], "expected": 28}, {"input": [3, 2], "expected": 3}]},

    {"id": 82, "name": "最小路径和", "category": "动态规划", "difficulty": "中等",
     "prompt": "def min_path_sum(grid: list[list[int]]) -> int:\n    '''找出从左上到右下的路径，使路径上数字总和最小'''",
     "test_cases": [{"input": [[[1,3,1],[1,5,1],[4,2,1]]], "expected": 7}]},

    {"id": 83, "name": "最长递增子序列", "category": "动态规划", "difficulty": "中等",
     "prompt": "def length_of_lis(nums: list[int]) -> int:\n    '''返回最长严格递增子序列的长度'''",
     "test_cases": [{"input": [[10,9,2,5,3,7,101,18]], "expected": 4}]},

    {"id": 84, "name": "零钱兑换", "category": "动态规划", "difficulty": "中等",
     "prompt": "def coin_change(coins: list[int], amount: int) -> int:\n    '''组成amount所需的最少硬币数，无解返回-1'''",
     "test_cases": [{"input": [[1,2,5], 11], "expected": 3}, {"input": [[2], 3], "expected": -1}]},

    {"id": 85, "name": "单词拆分", "category": "动态规划", "difficulty": "中等",
     "prompt": "def word_break(s: str, wordDict: list[str]) -> bool:\n    '''判断s是否能被空格拆分为字典中的单词'''",
     "test_cases": [{"input": ["leetcode", ["leet","code"]], "expected": True}]},

    {"id": 86, "name": "最长公共子序列", "category": "动态规划", "difficulty": "中等",
     "prompt": "def longest_common_subsequence(text1: str, text2: str) -> int:\n    '''返回两个字符串的最长公共子序列长度'''",
     "test_cases": [{"input": ["abcde", "ace"], "expected": 3}]},

    {"id": 87, "name": "编辑距离II", "category": "动态规划", "difficulty": "困难",
     "prompt": "def min_distance_dp(word1: str, word2: str) -> int:\n    '''使用动态规划计算最小编辑距离'''",
     "test_cases": [{"input": ["horse", "ros"], "expected": 3}]},

    {"id": 88, "name": "最大正方形", "category": "动态规划", "difficulty": "中等",
     "prompt": "def maximal_square(matrix: list[list[str]]) -> int:\n    '''二进制矩阵中只包含1的最大正方形面积'''",
     "test_cases": [{"input": [[["1","0","1","0","0"],["1","0","1","1","1"]]], "expected": 4}]},

    {"id": 89, "name": "分割等和子集", "category": "动态规划", "difficulty": "中等",
     "prompt": "def can_partition(nums: list[int]) -> bool:\n    '''判断能否将数组分割成两个和相等的子集（01背包）'''",
     "test_cases": [{"input": [[1,5,11,5]], "expected": True}, {"input": [[1,2,3,5]], "expected": False}]},

    {"id": 90, "name": "完全平方数", "category": "动态规划", "difficulty": "中等",
     "prompt": "def num_squares(n: int) -> int:\n    '''将n表示为若干个完全平方数之和，求最少个数'''",
     "test_cases": [{"input": [12], "expected": 3}, {"input": [13], "expected": 2}]},

    {"id": 91, "name": "矩阵链乘法", "category": "动态规划", "difficulty": "困难",
     "prompt": "def matrix_chain_order(dims: list[int]) -> int:\n    '''计算矩阵链相乘的最少乘法次数，dims为各矩阵维度'''",
     "test_cases": [{"input": [[10, 30, 5, 60]], "expected": 4500}]},

    {"id": 92, "name": "股票买卖III", "category": "动态规划", "difficulty": "困难",
     "prompt": "def max_profit_iii(prices: list[int]) -> int:\n    '''最多完成两笔交易的最大利润'''",
     "test_cases": [{"input": [[3,3,5,0,0,3,1,4]], "expected": 6}]},

    {"id": 93, "name": "打家劫舍II", "category": "动态规划", "difficulty": "中等",
     "prompt": "def rob_ii(nums: list[int]) -> int:\n    '''房屋围成一圈，相邻房屋不能同时偷，求最大金额'''",
     "test_cases": [{"input": [[2,3,2]], "expected": 3}, {"input": [[1,2,3,1]], "expected": 4}]},

    {"id": 94, "name": "最长回文子序列", "category": "动态规划", "difficulty": "中等",
     "prompt": "def longest_palindrome_subseq(s: str) -> int:\n    '''返回字符串的最长回文子序列长度'''",
     "test_cases": [{"input": ["bbbab"], "expected": 4}]},

    {"id": 95, "name": "交错字符串", "category": "动态规划", "difficulty": "中等",
     "prompt": "def is_interleave(s1: str, s2: str, s3: str) -> bool:\n    '''判断s3是否由s1和s2交错组成'''",
     "test_cases": [{"input": ["aabcc", "dbbca", "aadbbcbcac"], "expected": True}]},

    {"id": 96, "name": "不同的二叉搜索树", "category": "动态规划", "difficulty": "中等",
     "prompt": "def num_trees(n: int) -> int:\n    '''计算由1到n组成的不同二叉搜索树的个数（卡特兰数）'''",
     "test_cases": [{"input": [3], "expected": 5}]},

    {"id": 97, "name": "俄罗斯套娃信封", "category": "动态规划", "difficulty": "困难",
     "prompt": "def max_envelopes(envelopes: list[list[int]]) -> int:\n    '''信封套娃，宽和高都必须严格大于才能套，求最多套多少个'''",
     "test_cases": [{"input": [[[5,4],[6,4],[6,7],[2,3]]], "expected": 3}]},

    {"id": 98, "name": "摘樱桃", "category": "动态规划", "difficulty": "困难",
     "prompt": "def cherry_pickup(grid: list[list[int]]) -> int:\n    '''两人从左上到右下再返回，求能摘到的最大樱桃数'''",
     "test_cases": [{"input": [[[0,1,-1],[1,0,-1],[1,1,1]]], "expected": 5}]},

    {"id": 99, "name": "正则表达式匹配DP", "category": "动态规划", "difficulty": "困难",
     "prompt": "def is_match_dp(s: str, p: str) -> bool:\n    '''使用动态规划实现正则表达式匹配'''",
     "test_cases": [{"input": ["aa", "a*"], "expected": True}]},

    {"id": 100, "name": "戳气球", "category": "动态规划", "difficulty": "困难",
     "prompt": "def max_coins(nums: list[int]) -> int:\n    '''有n个气球，戳破第i个获得nums[i-1]*nums[i]*nums[i+1]硬币，求最大硬币数'''",
     "test_cases": [{"input": [[3,1,5,8]], "expected": 167}]},
]


class CodeEvaluator(BaseEvaluator):
    """代码生成能力评估器"""

    name = "code"
    description = "代码生成测试"

    @property
    def stage_name(self) -> str:
        return "深度能力测试-代码生成"

    @property
    def stage_number(self) -> int:
        return 3

    @property
    def threshold_percentage(self) -> float:
        return 0.5  # 50% 通过门槛

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        from utils.raw_data_logger import RawDataLogger
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行代码生成测试"""
        import requests

        test_results = []
        start_time = time.time()

        for test_case in CODE_TEST_CASES:
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
        """测试单个代码生成用例"""
        import requests

        url = f"{self.model_url}/v1/chat/completions"
        prompt = f"请编写Python代码解决以下问题。只输出代码，不要解释。\n\n{test_case['prompt']}\n\n代码："

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个专业的Python程序员。只输出代码，不要解释。确保代码语法正确。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 4096,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
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

            # 检查代码质量
            score = self._evaluate_code(content, test_case)
            passed = score >= 0.6

            # 记录原始数据
            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case['name'],
                "prompt": test_case['prompt'],
                "generated_code": content,
                "score": score,
                "passed": passed
            }, test_type="code_stage3")

            return TestResult(
                name=test_case['name'],
                category=test_case['category'],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "difficulty": test_case['difficulty'],
                    "response": content[:500]
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

    def _evaluate_code(self, content: str, test_case: dict) -> float:
        """评估代码质量"""
        score = 0.0
        content_lower = content.lower()

        # 检查是否有def或class定义
        if 'def ' in content or 'class ' in content:
            score += 0.4

        # 检查语法完整性
        if content.count('(') == content.count(')'):
            score += 0.2
        if content.count('[') == content.count(']'):
            score += 0.1
        if content.count('{') == content.count('}'):
            score += 0.1

        # 检查是否包含题目关键词
        keywords = test_case.get('keywords', [])
        if keywords:
            matched = sum(1 for kw in keywords if kw.lower() in content_lower)
            score += (matched / len(keywords)) * 0.2
        else:
            score += 0.2

        return min(score, 1.0)


def run_code_test(model_url: str, model_name: str) -> dict:
    """运行代码生成测试"""
    evaluator = CodeEvaluator(model_url, model_name)
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
    result = run_code_test("http://localhost:8400", "Qwen3VL-4B-Instruct-Q8_0")
    print(f"代码生成测试: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
