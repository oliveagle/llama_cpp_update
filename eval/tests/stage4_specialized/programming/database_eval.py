#!/usr/bin/env python3
"""
Stage 4 编程能力测试 - 数据库与 SQL (150 题生成器)
"""

import random
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import shuffle_options

DATABASE_TEMPLATES = {
    "SQL 基础": [
        {"q": "SELECT 语句用于？", "opts": ["查询数据", "插入数据", "更新数据", "删除数据"], "a": "A"},
        {"q": "WHERE 子句用于？", "opts": ["过滤记录", "排序", "分组", "连接"], "a": "A"},
        {"q": "ORDER BY 用于？", "opts": ["排序", "过滤", "分组", "连接"], "a": "A"},
        {"q": "GROUP BY 用于？", "opts": ["分组", "排序", "过滤", "连接"], "a": "A"},
        {"q": "COUNT(*) 用于？", "opts": ["统计行数", "求和", "平均值", "最大值"], "a": "A"},
        {"q": "DISTINCT 用于？", "opts": ["去重", "排序", "过滤", "分组"], "a": "A"},
        {"q": "LIKE 用于？", "opts": ["模糊匹配", "精确匹配", "排序", "分组"], "a": "A"},
        {"q": "IN 操作符用于？", "opts": ["匹配列表中的值", "范围查询", "模糊匹配", "连接"], "a": "A"},
        {"q": "BETWEEN 用于？", "opts": ["范围查询", "列表匹配", "模糊匹配", "连接"], "a": "A"},
        {"q": "NULL 表示？", "opts": ["空值", "0", "空字符串", "False"], "a": "A"},
        {"q": "IS NULL 用于？", "opts": ["判断空值", "赋值", "比较", "计算"], "a": "A"},
        {"q": "LIMIT 用于？", "opts": ["限制结果数", "排序", "分组", "过滤"], "a": "A"},
    ],
    "SQL 连接": [
        {"q": "INNER JOIN 返回？", "opts": ["匹配的行", "所有行", "左表所有行", "右表所有行"], "a": "A"},
        {"q": "LEFT JOIN 返回？", "opts": ["左表所有行和右表匹配行", "只匹配行", "右表所有行", "所有行"], "a": "A"},
        {"q": "RIGHT JOIN 返回？", "opts": ["右表所有行和左表匹配行", "只匹配行", "左表所有行", "所有行"], "a": "A"},
        {"q": "FULL OUTER JOIN 返回？", "opts": ["所有行", "只匹配行", "左表所有行", "右表所有行"], "a": "A"},
        {"q": "CROSS JOIN 返回？", "opts": ["笛卡尔积", "匹配行", "左表所有行", "右表所有行"], "a": "A"},
        {"q": "自连接是？", "opts": ["表和自己连接", "两个表连接", "多个表连接", "子查询"], "a": "A"},
        {"q": "UNION 用于？", "opts": ["合并结果集", "连接表", "过滤数据", "排序"], "a": "A"},
        {"q": "UNION ALL 和 UNION 的区别是？", "opts": ["UNION ALL 不去重", "UNION ALL 去重", "没有区别", "UNION 更快"], "a": "A"},
    ],
    "数据库设计": [
        {"q": "主键 (PRIMARY KEY) 的特点是？", "opts": ["唯一且非空", "可以为空", "不唯一", "自动递增"], "a": "A"},
        {"q": "外键 (FOREIGN KEY) 用于？", "opts": ["建立表间关系", "唯一标识", "加速查询", "数据备份"], "a": "A"},
        {"q": "UNIQUE 约束用于？", "opts": ["保证唯一性", "保证非空", "加速查询", "建立关系"], "a": "A"},
        {"q": "NOT NULL 约束用于？", "opts": ["保证非空", "保证唯一", "加速查询", "建立关系"], "a": "A"},
        {"q": "CHECK 约束用于？", "opts": ["验证数据", "保证唯一", "保证非空", "建立关系"], "a": "A"},
        {"q": "范式化的目的是？", "opts": ["减少冗余", "提高性能", "增加冗余", "简化查询"], "a": "A"},
        {"q": "第一范式 (1NF) 要求？", "opts": ["列不可再分", "消除部分依赖", "消除传递依赖", "所有属性依赖主键"], "a": "A"},
        {"q": "第二范式 (2NF) 要求？", "opts": ["消除非主属性对部分主键的依赖", "列不可再分", "消除传递依赖", "所有属性依赖主键"], "a": "A"},
        {"q": "第三范式 (3NF) 要求？", "opts": ["消除传递依赖", "列不可再分", "消除部分依赖", "所有属性依赖主键"], "a": "A"},
        {"q": "反范式化的目的是？", "opts": ["提高查询性能", "减少冗余", "简化更新", "保证一致性"], "a": "A"},
    ],
    "索引": [
        {"q": "索引的主要作用是？", "opts": ["加速查询", "加速写入", "减少存储", "数据备份"], "a": "A"},
        {"q": "聚簇索引的特点是？", "opts": ["数据按索引顺序存储", "一个表可以有多个", "不影响存储", "只用于主键"], "a": "A"},
        {"q": "非聚簇索引的特点是？", "opts": ["索引和数据分开存储", "数据按索引顺序存储", "一个表只能有一个", "只用于外键"], "a": "A"},
        {"q": "复合索引是？", "opts": ["多列组成的索引", "单个列索引", "主键索引", "唯一索引"], "a": "A"},
        {"q": "覆盖索引是指？", "opts": ["索引包含所有查询列", "索引覆盖全表", "索引包含主键", "索引包含外键"], "a": "A"},
        {"q": "索引失效的情况是？", "opts": ["对索引列使用函数", "精确匹配", "主键查询", " LIMIT 查询"], "a": "A"},
        {"q": "最左前缀原则用于？", "opts": ["复合索引查询", "单列索引", "主键查询", "外键查询"], "a": "A"},
    ],
    "事务": [
        {"q": "事务的 ACID 特性不包括？", "opts": ["Deadlock", "Atomicity", "Consistency", "Isolation"], "a": "A"},
        {"q": "原子性是指？", "opts": ["要么全做要么全不做", "数据一致", "并发隔离", "持久保存"], "a": "A"},
        {"q": "一致性是指？", "opts": ["事务前后数据一致", "要么全做要么全不做", "并发隔离", "持久保存"], "a": "A"},
        {"q": "隔离性是指？", "opts": ["并发事务互不干扰", "要么全做要么全不做", "数据一致", "持久保存"], "a": "A"},
        {"q": "持久性是指？", "opts": ["事务提交后永久保存", "要么全做要么全不做", "数据一致", "并发隔离"], "a": "A"},
        {"q": "脏读是指？", "opts": ["读到未提交数据", "读到已提交数据", "读不到数据", "读到错误数据"], "a": "A"},
        {"q": "不可重复读是指？", "opts": ["同一事务中两次读取不同", "读到未提交数据", "读不到数据", "读到错误数据"], "a": "A"},
        {"q": "幻读是指？", "opts": ["同一事务中两次查询行数不同", "读到未提交数据", "同一读取不同", "读不到数据"], "a": "A"},
        {"q": "COMMIT 用于？", "opts": ["提交事务", "回滚事务", "开始事务", "保存事务"], "a": "A"},
        {"q": "ROLLBACK 用于？", "opts": ["回滚事务", "提交事务", "开始事务", "保存事务"], "a": "A"},
    ],
    "NoSQL": [
        {"q": "Redis 是？", "opts": ["键值存储", "关系数据库", "文档数据库", "图数据库"], "a": "A"},
        {"q": "MongoDB 是？", "opts": ["文档数据库", "键值存储", "关系数据库", "图数据库"], "a": "A"},
        {"q": "Neo4j 是？", "opts": ["图数据库", "键值存储", "文档数据库", "关系数据库"], "a": "A"},
        {"q": "Redis 支持的数据结构不包括？", "opts": ["关系表", "字符串", "列表", "集合"], "a": "A"},
        {"q": "MongoDB 的查询语言是？", "opts": ["类 JSON", "SQL", "XQuery", "SPARQL"], "a": "A"},
        {"q": "CAP 理论中 Redis 通常是？", "opts": ["CP 或 AP", "CA", "只 C", "只 A"], "a": "A"},
    ],
}


def generate_database_questions(target_count=150):
    questions = []
    qid = 1
    easy_count = int(target_count * 0.35)
    medium_count = int(target_count * 0.45)
    hard_count = target_count - easy_count - medium_count

    easy_cats = ["SQL 基础", "SQL 连接"]
    medium_cats = ["数据库设计", "索引", "事务"]
    hard_cats = ["索引", "事务", "NoSQL"]

    for _ in range(easy_count):
        cat = random.choice(easy_cats)
        if cat in DATABASE_TEMPLATES and DATABASE_TEMPLATES[cat]:
            template = random.choice(DATABASE_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"数据库-{cat}-{qid}", "category": cat,
                "difficulty": "简单", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["database"]
            })
            qid += 1

    for _ in range(medium_count):
        cat = random.choice(medium_cats)
        if cat in DATABASE_TEMPLATES and DATABASE_TEMPLATES[cat]:
            template = random.choice(DATABASE_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"数据库-{cat}-{qid}", "category": cat,
                "difficulty": "中等", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["database"]
            })
            qid += 1

    for _ in range(hard_count):
        cat = random.choice(hard_cats)
        if cat in DATABASE_TEMPLATES and DATABASE_TEMPLATES[cat]:
            template = random.choice(DATABASE_TEMPLATES[cat])
            shuffled_opts, new_answer = shuffle_options(template)
            questions.append({
                "id": qid, "name": f"数据库-{cat}-{qid}", "category": cat,
                "difficulty": "困难", "question": template["q"], "options": shuffled_opts,
                "answer": new_answer, "keywords": ["database"]
            })
            qid += 1

    return questions


class DatabaseEvaluator:
    def __init__(self, model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from base import Stage4BaseEvaluator
        self.base_eval = Stage4BaseEvaluator(model_url, model_name, output_dir)
        self.test_cases = generate_database_questions(150)

    def run_tests(self):
        return self.base_eval.run_tests(self.test_cases, "database")

    def generate_report(self, result):
        return self.base_eval.generate_report(result)


def run_database_test(model_url: str, model_name: str, output_dir: str = "eval_results/stage4"):
    evaluator = DatabaseEvaluator(model_url, model_name, output_dir)
    result = evaluator.run_tests()
    report_file = evaluator.generate_report(result)
    return {"result": result, "report_file": report_file}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Stage 4 数据库测试")
    parser.add_argument("--model-url", default="http://localhost:8400")
    parser.add_argument("--model-name", default="JoyAI-LLM-Flash-Q4_K_M")
    parser.add_argument("--output-dir", default="eval_results/stage4")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    if args.generate_only:
        questions = generate_database_questions(150)
        print(f"生成了 {len(questions)} 道数据库题目")
        os.makedirs(args.output_dir, exist_ok=True)
        with open(os.path.join(args.output_dir, "database_questions.json"), "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    else:
        test_result = run_database_test(args.model_url, args.model_name, args.output_dir)
        print(f"通过率：{test_result['result'].pass_rate*100:.1f}%")
