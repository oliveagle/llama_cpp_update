#!/usr/bin/env python3
"""
大规模工具使用测试案例集 (300个)
用于全面评估模型的工具调用能力
"""

from typing import List, Dict

# ========== 基础测试案例 (手动编写的高质量案例) ==========
BASE_TEST_CASES = [
    # 数学计算 - 基础 (10个)
    {"name": "基础乘法", "category": "数学计算", "prompt": "计算 123 乘以 456", "expected_tool": "calculator", "expected_args": {"expression": "123*456"}},
    {"name": "基础除法", "category": "数学计算", "prompt": "1000除以8等于多少", "expected_tool": "calculator", "expected_args": {"expression": "1000/8"}},
    {"name": "加法运算", "category": "数学计算", "prompt": "帮我算一下 999 + 111", "expected_tool": "calculator", "expected_args": {"expression": "999+111"}},
    {"name": "减法运算", "category": "数学计算", "prompt": "500减去123是多少", "expected_tool": "calculator", "expected_args": {"expression": "500-123"}},
    {"name": "混合运算", "category": "数学计算", "prompt": "计算 (100+200)*3-50", "expected_tool": "calculator", "expected_args": {"expression": "(100+200)*3-50"}},
    {"name": "平方计算", "category": "数学计算", "prompt": "25的平方是多少", "expected_tool": "calculator", "expected_args": {"expression": "25^2"}},
    {"name": "开方计算", "category": "数学计算", "prompt": "计算根号625", "expected_tool": "calculator", "expected_args": {"expression": "sqrt(625)"}},
    {"name": "百分比计算", "category": "数学计算", "prompt": "80的15%是多少", "expected_tool": "calculator", "expected_args": {"expression": "80*0.15"}},
    {"name": "阶乘计算", "category": "数学计算", "prompt": "5的阶乘等于多少", "expected_tool": "calculator", "expected_args": {"expression": "5!"}},
    {"name": "幂运算", "category": "数学计算", "prompt": "计算2的10次方", "expected_tool": "calculator", "expected_args": {"expression": "2^10"}},

    # 天气查询 - 基础 (10个)
    {"name": "北京天气", "category": "天气查询", "prompt": "今天北京天气怎么样", "expected_tool": "get_weather", "expected_args": {"location": "北京"}},
    {"name": "上海天气", "category": "天气查询", "prompt": "查询上海的当前天气", "expected_tool": "get_weather", "expected_args": {"location": "上海"}},
    {"name": "广州温度", "category": "天气查询", "prompt": "广州现在多少度", "expected_tool": "get_weather", "expected_args": {"location": "广州"}},
    {"name": "深圳天气", "category": "天气查询", "prompt": "深圳今天会下雨吗", "expected_tool": "get_weather", "expected_args": {"location": "深圳"}},
    {"name": "杭州天气", "category": "天气查询", "prompt": "杭州天气如何", "expected_tool": "get_weather", "expected_args": {"location": "杭州"}},
    {"name": "成都天气", "category": "天气查询", "prompt": "今天成都的天气预报", "expected_tool": "get_weather", "expected_args": {"location": "成都"}},
    {"name": "武汉天气", "category": "天气查询", "prompt": "武汉现在天气怎么样", "expected_tool": "get_weather", "expected_args": {"location": "武汉"}},
    {"name": "西安天气", "category": "天气查询", "prompt": "查询西安今日天气", "expected_tool": "get_weather", "expected_args": {"location": "西安"}},
    {"name": "南京天气", "category": "天气查询", "prompt": "南京今天气温多少", "expected_tool": "get_weather", "expected_args": {"location": "南京"}},
    {"name": "重庆天气", "category": "天气查询", "prompt": "重庆天气情况", "expected_tool": "get_weather", "expected_args": {"location": "重庆"}},

    # 时间日期 - 基础 (10个)
    {"name": "当前日期", "category": "时间日期", "prompt": "今天是什么日期", "expected_tool": "get_date", "expected_args": {}},
    {"name": "当前时间", "category": "时间日期", "prompt": "现在几点了", "expected_tool": "get_time", "expected_args": {}},
    {"name": "创建会议", "category": "时间日期", "prompt": "创建明天下午3点的会议", "expected_tool": "create_calendar_event", "expected_args": {"title": "会议", "time": "明天下午3点"}},
    {"name": "设置闹钟", "category": "时间日期", "prompt": "设置明天早上7点的闹钟", "expected_tool": "set_reminder", "expected_args": {"time": "明天早上7点", "content": "闹钟"}},
    {"name": "倒计时", "category": "时间日期", "prompt": "距离2025年春节还有多少天", "expected_tool": "countdown", "expected_args": {"target_date": "2025年春节"}},
    {"name": "日程提醒", "category": "时间日期", "prompt": "提醒我今晚8点打电话", "expected_tool": "set_reminder", "expected_args": {"time": "今晚8点", "content": "打电话"}},
    {"name": "查看日历", "category": "时间日期", "prompt": "查看今天的日程安排", "expected_tool": "get_calendar", "expected_args": {"date": "今天"}},
    {"name": "添加事件", "category": "时间日期", "prompt": "添加周末去公园的事件", "expected_tool": "create_calendar_event", "expected_args": {"title": "去公园", "time": "周末"}},
    {"name": "定时提醒", "category": "时间日期", "prompt": "30分钟后提醒我喝水", "expected_tool": "set_reminder", "expected_args": {"time": "30分钟后", "content": "喝水"}},
    {"name": "查询星期", "category": "时间日期", "prompt": "今天是星期几", "expected_tool": "get_date", "expected_args": {}},

    # 搜索查询 - 基础 (10个)
    {"name": "搜索AI", "category": "搜索查询", "prompt": "搜索人工智能最新进展", "expected_tool": "search", "expected_args": {"query": "人工智能"}},
    {"name": "搜索新闻", "category": "搜索查询", "prompt": "查找今天的科技新闻", "expected_tool": "search_news", "expected_args": {"category": "科技"}},
    {"name": "股票查询", "category": "搜索查询", "prompt": "查询阿里巴巴的股价", "expected_tool": "get_stock_price", "expected_args": {"symbol": "阿里巴巴"}},
    {"name": "汇率查询", "category": "搜索查询", "prompt": "美元兑人民币汇率", "expected_tool": "get_exchange_rate", "expected_args": {"from_currency": "USD", "to_currency": "CNY"}},
    {"name": "百科查询", "category": "搜索查询", "prompt": "搜索量子计算的定义", "expected_tool": "search", "expected_args": {"query": "量子计算"}},
    {"name": "视频搜索", "category": "搜索查询", "prompt": "搜索Python教程视频", "expected_tool": "search", "expected_args": {"query": "Python教程"}},
    {"name": "图片搜索", "category": "搜索查询", "prompt": "搜索猫咪图片", "expected_tool": "search", "expected_args": {"query": "猫咪"}},
    {"name": "地图搜索", "category": "搜索查询", "prompt": "搜索附近的咖啡店", "expected_tool": "search_location", "expected_args": {"query": "咖啡店"}},
    {"name": "商品搜索", "category": "搜索查询", "prompt": "搜索iPhone 16的价格", "expected_tool": "search", "expected_args": {"query": "iPhone 16"}},
    {"name": "学术搜索", "category": "搜索查询", "prompt": "搜索Transformer论文", "expected_tool": "search", "expected_args": {"query": "Transformer论文"}},

    # 翻译 - 基础 (10个)
    {"name": "英译中1", "category": "翻译", "prompt": "翻译Hello World为中文", "expected_tool": "translate", "expected_args": {"text": "Hello World", "target_lang": "中文"}},
    {"name": "中译英1", "category": "翻译", "prompt": "把你好翻译成英文", "expected_tool": "translate", "expected_args": {"text": "你好", "target_lang": "英文"}},
    {"name": "日译中", "category": "翻译", "prompt": "翻译こんにちは的意思", "expected_tool": "translate", "expected_args": {"text": "こんにちは", "target_lang": "中文"}},
    {"name": "法译中", "category": "翻译", "prompt": "Bonjour翻译成中文是什么", "expected_tool": "translate", "expected_args": {"text": "Bonjour", "target_lang": "中文"}},
    {"name": "德译中", "category": "翻译", "prompt": "翻译Guten Tag", "expected_tool": "translate", "expected_args": {"text": "Guten Tag", "target_lang": "中文"}},
    {"name": "西译中", "category": "翻译", "prompt": "Hola的中文意思", "expected_tool": "translate", "expected_args": {"text": "Hola", "target_lang": "中文"}},
    {"name": "韩译中", "category": "翻译", "prompt": "翻译안녕하세요", "expected_tool": "translate", "expected_args": {"text": "안녕하세요", "target_lang": "中文"}},
    {"name": "俄译中", "category": "翻译", "prompt": "Привет翻译成中文", "expected_tool": "translate", "expected_args": {"text": "Привет", "target_lang": "中文"}},
    {"name": "中译日", "category": "翻译", "prompt": "把谢谢翻译成日语", "expected_tool": "translate", "expected_args": {"text": "谢谢", "target_lang": "日语"}},
    {"name": "中译法", "category": "翻译", "prompt": "再见用法语怎么说", "expected_tool": "translate", "expected_args": {"text": "再见", "target_lang": "法语"}},

    # 文件操作 - 基础 (10个)
    {"name": "读取文件1", "category": "文件操作", "prompt": "读取report.txt文件", "expected_tool": "read_file", "expected_args": {"filename": "report.txt"}},
    {"name": "读取文件2", "category": "文件操作", "prompt": "打开document.docx", "expected_tool": "read_file", "expected_args": {"filename": "document.docx"}},
    {"name": "保存文件", "category": "文件操作", "prompt": "保存内容到notes.txt", "expected_tool": "write_file", "expected_args": {"filename": "notes.txt"}},
    {"name": "删除文件", "category": "文件操作", "prompt": "删除temp.tmp文件", "expected_tool": "delete_file", "expected_args": {"filename": "temp.tmp"}},
    {"name": "复制文件", "category": "文件操作", "prompt": "复制file1.txt到file2.txt", "expected_tool": "copy_file", "expected_args": {"source": "file1.txt", "destination": "file2.txt"}},
    {"name": "移动文件", "category": "文件操作", "prompt": "移动data.csv到backup文件夹", "expected_tool": "move_file", "expected_args": {"source": "data.csv", "destination": "backup/"}},
    {"name": "重命名文件", "category": "文件操作", "prompt": "把old.txt重命名为new.txt", "expected_tool": "rename_file", "expected_args": {"old_name": "old.txt", "new_name": "new.txt"}},
    {"name": "创建文件夹", "category": "文件操作", "prompt": "创建一个新的文件夹projects", "expected_tool": "create_directory", "expected_args": {"path": "projects"}},
    {"name": "列出文件", "category": "文件操作", "prompt": "列出当前目录的所有文件", "expected_tool": "list_directory", "expected_args": {"path": "."}},
    {"name": "文件信息", "category": "文件操作", "prompt": "查看file.pdf的文件大小", "expected_tool": "get_file_info", "expected_args": {"filename": "file.pdf"}},

    # 通信 - 基础 (10个)
    {"name": "发送邮件1", "category": "通信", "prompt": "发邮件给张三说会议改期", "expected_tool": "send_email", "expected_args": {"to": "张三", "subject": "会议改期"}},
    {"name": "发送邮件2", "category": "通信", "prompt": "给李四发送项目报告邮件", "expected_tool": "send_email", "expected_args": {"to": "李四", "subject": "项目报告"}},
    {"name": "发送短信", "category": "通信", "prompt": "发短信给妈妈说我晚点到", "expected_tool": "send_sms", "expected_args": {"to": "妈妈", "message": "我晚点到"}},
    {"name": "拨打电话", "category": "通信", "prompt": "给客服打电话", "expected_tool": "make_call", "expected_args": {"number": "客服"}},
    {"name": "视频会议", "category": "通信", "prompt": "发起团队视频会议", "expected_tool": "start_video_call", "expected_args": {"participants": "团队"}},
    {"name": "发送消息", "category": "通信", "prompt": "发微信给王五", "expected_tool": "send_message", "expected_args": {"to": "王五", "platform": "微信"}},
    {"name": "群发邮件", "category": "通信", "prompt": "群发邮件给全体成员", "expected_tool": "send_email", "expected_args": {"to": "全体成员", "subject": "群发"}},
    {"name": "发送传真", "category": "通信", "prompt": "发送传真到010-12345678", "expected_tool": "send_fax", "expected_args": {"number": "010-12345678"}},
    {"name": "语音留言", "category": "通信", "prompt": "给赵六留语音消息", "expected_tool": "send_voice_message", "expected_args": {"to": "赵六"}},
    {"name": "视频通话", "category": "通信", "prompt": "和孙七视频通话", "expected_tool": "make_video_call", "expected_args": {"to": "孙七"}},
]


def generate_weather_cases() -> List[Dict]:
    """生成天气查询测试案例 (20个)"""
    cities = [
        ("天津", "天津"), ("苏州", "苏州"), ("青岛", "青岛"), ("厦门", "厦门"),
        ("大连", "大连"), ("宁波", "宁波"), ("无锡", "无锡"), ("佛山", "佛山"),
        ("东莞", "东莞"), ("郑州", "郑州"), ("长沙", "长沙"), ("沈阳", "沈阳"),
        ("济南", "济南"), ("哈尔滨", "哈尔滨"), ("石家庄", "石家庄"), ("合肥", "合肥"),
        ("昆明", "昆明"), ("南昌", "南昌"), ("贵阳", "贵阳"), ("长春", "长春")
    ]
    cases = []
    templates = [
        "{city}今天天气如何",
        "查询{city}的天气",
        "{city}现在多少度",
        "{city}天气预报",
    ]
    for i, (city, name) in enumerate(cities):
        template = templates[i % len(templates)]
        cases.append({
            "name": f"天气_{name}",
            "category": "天气查询",
            "prompt": template.format(city=city),
            "expected_tool": "get_weather",
            "expected_args": {"location": city}
        })
    return cases


def generate_math_cases() -> List[Dict]:
    """生成数学计算测试案例 (30个)"""
    import random
    random.seed(42)  # 固定随机种子保证可重复

    cases = []
    # 基础运算
    for i in range(10):
        a, b = random.randint(10, 999), random.randint(10, 99)
        ops = [
            ("+", "加", "加上"),
            ("-", "减", "减去"),
            ("*", "乘", "乘以"),
            ("/", "除", "除以")
        ]
        op, op_name1, op_name2 = ops[i % 4]
        expr = f"{a}{op}{b}"
        prompts = [
            f"{a}{op_name1}{b}等于多少",
            f"计算{a}{op_name2}{b}",
            f"{a}{op_name1}{b}是多少",
        ]
        cases.append({
            "name": f"数学_基础_{i+1}",
            "category": "数学计算",
            "prompt": prompts[i % 3],
            "expected_tool": "calculator",
            "expected_args": {"expression": expr}
        })

    # 平方和开方
    squares = [16, 25, 36, 49, 64, 81, 100, 121, 144, 169]
    for i, n in enumerate(squares):
        cases.append({
            "name": f"数学_开方_{i+1}",
            "category": "数学计算",
            "prompt": f"根号{n}等于多少",
            "expected_tool": "calculator",
            "expected_args": {"expression": f"sqrt({n})"}
        })

    # 幂运算
    bases = [2, 3, 4, 5, 10]
    exps = [3, 4, 5, 6, 8]
    for i, (b, e) in enumerate(zip(bases, exps)):
        cases.append({
            "name": f"数学_幂_{i+1}",
            "category": "数学计算",
            "prompt": f"{b}的{e}次方是多少",
            "expected_tool": "calculator",
            "expected_args": {"expression": f"{b}^{e}"}
        })

    return cases


def generate_translation_cases() -> List[Dict]:
    """生成翻译测试案例 (10个)"""
    cases = [
        {"name": "翻译_IT", "category": "翻译", "prompt": "翻译Artificial Intelligence", "expected_tool": "translate", "expected_args": {"text": "Artificial Intelligence", "target_lang": "中文"}},
        {"name": "翻译_商务", "category": "翻译", "prompt": "把contract翻译成中文", "expected_tool": "translate", "expected_args": {"text": "contract", "target_lang": "中文"}},
        {"name": "翻译_日常", "category": "翻译", "prompt": "How are you的中文意思", "expected_tool": "translate", "expected_args": {"text": "How are you", "target_lang": "中文"}},
        {"name": "翻译_技术", "category": "翻译", "prompt": "翻译machine learning", "expected_tool": "translate", "expected_args": {"text": "machine learning", "target_lang": "中文"}},
        {"name": "翻译_长句", "category": "翻译", "prompt": "翻译The quick brown fox jumps over the lazy dog", "expected_tool": "translate", "expected_args": {"text": "The quick brown fox jumps over the lazy dog", "target_lang": "中文"}},
        {"name": "翻译_成语", "category": "翻译", "prompt": "把画蛇添足翻译成英文", "expected_tool": "translate", "expected_args": {"text": "画蛇添足", "target_lang": "英文"}},
        {"name": "翻译_诗歌", "category": "翻译", "prompt": "翻译床前明月光", "expected_tool": "translate", "expected_args": {"text": "床前明月光", "target_lang": "英文"}},
        {"name": "翻译_菜名", "category": "翻译", "prompt": "宫保鸡丁用英语怎么说", "expected_tool": "translate", "expected_args": {"text": "宫保鸡丁", "target_lang": "英语"}},
        {"name": "翻译_地名", "category": "翻译", "prompt": "翻译Mount Everest", "expected_tool": "translate", "expected_args": {"text": "Mount Everest", "target_lang": "中文"}},
        {"name": "翻译_问候", "category": "翻译", "prompt": "Good morning翻译成中文", "expected_tool": "translate", "expected_args": {"text": "Good morning", "target_lang": "中文"}},
    ]
    return cases


def generate_file_cases() -> List[Dict]:
    """生成文件操作测试案例 (10个)"""
    files = [
        ("data.csv", "CSV"), ("image.png", "PNG图片"), ("presentation.pptx", "PPT"),
        ("spreadsheet.xlsx", "Excel"), ("notes.md", "Markdown"), ("script.py", "Python脚本"),
        ("config.json", "JSON配置"), ("archive.zip", "压缩包"), ("music.mp3", "音频"), ("video.mp4", "视频")
    ]
    cases = []
    for i, (filename, ftype) in enumerate(files):
        cases.append({
            "name": f"文件_读取_{ftype}",
            "category": "文件操作",
            "prompt": f"读取{filename}文件",
            "expected_tool": "read_file",
            "expected_args": {"filename": filename}
        })
    return cases


def generate_search_cases() -> List[Dict]:
    """生成搜索查询测试案例 (20个)"""
    queries = [
        ("最新电影", "电影"), ("热门音乐", "音乐"), ("美食推荐", "美食"), ("旅游攻略", "旅游"),
        ("健身方法", "健身"), ("编程教程", "编程"), ("理财知识", "理财"), ("健康常识", "健康"),
        ("历史事件", "历史"), ("科学发现", "科学"), ("文学作品", "文学"), ("艺术展览", "艺术"),
        ("汽车评测", "汽车"), ("房产信息", "房产"), ("招聘信息", "招聘"), ("购物优惠", "购物"),
        ("游戏攻略", "游戏"), ("摄影技巧", "摄影"), ("穿搭指南", "穿搭"), ("育儿知识", "育儿")
    ]
    cases = []
    for i, (query, category) in enumerate(queries):
        cases.append({
            "name": f"搜索_{category}",
            "category": "搜索查询",
            "prompt": f"搜索{query}",
            "expected_tool": "search",
            "expected_args": {"query": query}
        })
    return cases


def generate_reminder_cases() -> List[Dict]:
    """生成提醒设置测试案例 (10个)"""
    reminders = [
        ("1小时后", "休息"), ("明天早上", "起床"), ("今天下午", "开会"),
        ("今晚", "睡觉"), ("周末", "购物"), ("下周一", "交报告"),
        ("15分钟后", "关煤气"), ("半小时后", "取快递"), ("明天中午", "吃饭"), ("下周五", "约会")
    ]
    cases = []
    for i, (time, content) in enumerate(reminders):
        cases.append({
            "name": f"提醒_{content}",
            "category": "时间日期",
            "prompt": f"{time}提醒我{content}",
            "expected_tool": "set_reminder",
            "expected_args": {"time": time, "content": content}
        })
    return cases


def generate_conversion_cases() -> List[Dict]:
    """生成单位换算测试案例 (20个)"""
    conversions = [
        ("1", "米", "厘米"), ("5", "千克", "克"), ("10", "公里", "米"), ("100", "厘米", "米"),
        ("1", "小时", "分钟"), ("30", "分钟", "秒"), ("2", "天", "小时"), ("1", "周", "天"),
        ("25", "摄氏度", "华氏度"), ("98.6", "华氏度", "摄氏度"), ("1", "升", "毫升"), ("500", "毫升", "升"),
        ("1", "平方米", "平方厘米"), ("1", "立方米", "升"), ("100", "兆字节", "千兆字节"), ("1024", "字节", "千字节"),
        ("1", "吨", "千克"), ("500", "克", "千克"), ("100", "人民币", "美元"), ("50", "欧元", "人民币")
    ]
    cases = []
    for i, (val, from_unit, to_unit) in enumerate(conversions):
        cases.append({
            "name": f"换算_{i+1}",
            "category": "单位换算",
            "prompt": f"{val}{from_unit}等于多少{to_unit}",
            "expected_tool": "unit_converter",
            "expected_args": {"value": val, "from_unit": from_unit, "to_unit": to_unit}
        })
    return cases


def generate_edge_cases() -> List[Dict]:
    """生成边界情况测试案例 (30个)"""
    cases = [
        # 模糊意图
        {"name": "模糊_数学1", "category": "边界情况", "prompt": "帮我算算100加200", "expected_tool": "calculator", "expected_args": {"expression": "100+200"}},
        {"name": "模糊_数学2", "category": "边界情况", "prompt": "300减50是多少", "expected_tool": "calculator", "expected_args": {"expression": "300-50"}},
        {"name": "模糊_天气1", "category": "边界情况", "prompt": "那边天气怎么样", "expected_tool": "get_weather", "expected_args": {}},
        {"name": "模糊_时间1", "category": "边界情况", "prompt": "现在是什么时候", "expected_tool": "get_time", "expected_args": {}},
        {"name": "模糊_日期1", "category": "边界情况", "prompt": "今天几号", "expected_tool": "get_date", "expected_args": {}},

        # 多意图
        {"name": "多意图_1", "category": "边界情况", "prompt": "查一下天气然后设置提醒", "expected_tool": "get_weather", "expected_args": {}},
        {"name": "多意图_2", "category": "边界情况", "prompt": "搜索新闻并发送邮件", "expected_tool": "search_news", "expected_args": {}},

        # 长查询
        {"name": "长查询_1", "category": "边界情况", "prompt": "帮我搜索一下关于人工智能在医疗领域应用的最新研究论文和新闻报道", "expected_tool": "search", "expected_args": {"query": "人工智能医疗"}},
        {"name": "长查询_2", "category": "边界情况", "prompt": "我想了解一下最近有哪些好看的电影，特别是科幻类型的，能帮我搜索一下吗", "expected_tool": "search", "expected_args": {"query": "科幻电影"}},

        # 口语化
        {"name": "口语_1", "category": "边界情况", "prompt": "今儿个北京天气咋样", "expected_tool": "get_weather", "expected_args": {"location": "北京"}},
        {"name": "口语_2", "category": "边界情况", "prompt": "帮我瞅瞅现在几点了", "expected_tool": "get_time", "expected_args": {}},
        {"name": "口语_3", "category": "边界情况", "prompt": "整一份明天会议的提醒", "expected_tool": "set_reminder", "expected_args": {"time": "明天", "content": "会议"}},

        # 中英文混合
        {"name": "混合_1", "category": "边界情况", "prompt": "翻译machine learning是什么意思", "expected_tool": "translate", "expected_args": {"text": "machine learning"}},
        {"name": "混合_2", "category": "边界情况", "prompt": "把AI翻译成中文", "expected_tool": "translate", "expected_args": {"text": "AI"}},

        # 反问句
        {"name": "反问_1", "category": "边界情况", "prompt": "你能告诉我现在几点了吗", "expected_tool": "get_time", "expected_args": {}},
        {"name": "反问_2", "category": "边界情况", "prompt": "能不能查一下天气", "expected_tool": "get_weather", "expected_args": {}},

        # 否定句
        {"name": "否定_1", "category": "边界情况", "prompt": "不要翻译这个词", "expected_tool": None, "expected_args": {}},
        {"name": "否定_2", "category": "边界情况", "prompt": "不用搜索了", "expected_tool": None, "expected_args": {}},

        # 条件句
        {"name": "条件_1", "category": "边界情况", "prompt": "如果明天下雨就提醒我带伞", "expected_tool": "set_reminder", "expected_args": {"condition": "明天下雨", "content": "带伞"}},
        {"name": "条件_2", "category": "边界情况", "prompt": "要是股价涨了通知我", "expected_tool": "set_stock_alert", "expected_args": {"condition": "涨"}},

        # 省略主语
        {"name": "省略_1", "category": "边界情况", "prompt": "查询天气", "expected_tool": "get_weather", "expected_args": {}},
        {"name": "省略_2", "category": "边界情况", "prompt": "设置闹钟", "expected_tool": "set_reminder", "expected_args": {}},

        # 复杂参数
        {"name": "复杂_1", "category": "边界情况", "prompt": "搜索2024年 published 的关于 climate change 的论文", "expected_tool": "search", "expected_args": {"query": "climate change", "year": "2024"}},
        {"name": "复杂_2", "category": "边界情况", "prompt": "发送邮件给张三和李四，主题是项目进度汇报", "expected_tool": "send_email", "expected_args": {"to": "张三和李四", "subject": "项目进度汇报"}},

        # 嵌套意图
        {"name": "嵌套_1", "category": "边界情况", "prompt": "搜索如何计算圆的面积然后帮我算一个半径为5的", "expected_tool": "calculator", "expected_args": {"expression": "pi*5^2"}},
        {"name": "嵌套_2", "category": "边界情况", "prompt": "查一下汇率然后换算100美元", "expected_tool": "get_exchange_rate", "expected_args": {"from_currency": "USD", "amount": "100"}},

        # 干扰信息
        {"name": "干扰_1", "category": "边界情况", "prompt": "顺便问一下，今天天气怎么样，我想知道要不要带伞", "expected_tool": "get_weather", "expected_args": {}},
        {"name": "干扰_2", "category": "边界情况", "prompt": "对了，帮我查一下，就是那个，现在几点了", "expected_tool": "get_time", "expected_args": {}},

        # 专业术语
        {"name": "专业_1", "category": "边界情况", "prompt": "计算covariance matrix", "expected_tool": "calculator", "expected_args": {"expression": "covariance matrix"}},
        {"name": "专业_2", "category": "边界情况", "prompt": "查询NVDA的P/E ratio", "expected_tool": "get_stock_price", "expected_args": {"symbol": "NVDA"}},

        # 俚语/网络用语
        {"name": "网络_1", "category": "边界情况", "prompt": "yyds是什么意思", "expected_tool": "search", "expected_args": {"query": "yyds"}},
        {"name": "网络_2", "category": "边界情况", "prompt": "翻译emo", "expected_tool": "translate", "expected_args": {"text": "emo"}},
    ]
    return cases


def get_all_test_cases() -> List[Dict]:
    """获取所有300个测试案例"""
    all_cases = []

    # 1. 基础案例 (60个)
    all_cases.extend(BASE_TEST_CASES)

    # 2. 天气案例 (20个)
    all_cases.extend(generate_weather_cases())

    # 3. 数学计算案例 (30个)
    all_cases.extend(generate_math_cases())

    # 4. 翻译案例 (10个)
    all_cases.extend(generate_translation_cases())

    # 5. 文件操作案例 (10个)
    all_cases.extend(generate_file_cases())

    # 6. 搜索案例 (20个)
    all_cases.extend(generate_search_cases())

    # 7. 提醒案例 (10个)
    all_cases.extend(generate_reminder_cases())

    # 8. 单位换算案例 (20个)
    all_cases.extend(generate_conversion_cases())

    # 9. 边界案例 (30个)
    all_cases.extend(generate_edge_cases())

    # 10. 补充更多案例以达到300个
    # 更多城市天气 (20个)
    more_cities = [
        "拉萨", "乌鲁木齐", "银川", "西宁", "兰州", "太原", "呼和浩特",
        "海口", "南宁", "福州", "台北", "香港", "澳门", "昆明", "贵阳",
        "哈尔滨", "长春", "沈阳", "石家庄", "济南"
    ]
    for city in more_cities:
        all_cases.append({
            "name": f"天气_{city}",
            "category": "天气查询",
            "prompt": f"{city}天气",
            "expected_tool": "get_weather",
            "expected_args": {"location": city}
        })

    # 更多数学计算 (20个)
    import random
    random.seed(123)
    for i in range(20):
        a, b = random.randint(100, 9999), random.randint(10, 999)
        all_cases.append({
            "name": f"数学随机_{i+1}",
            "category": "数学计算",
            "prompt": f"计算{a}加{b}",
            "expected_tool": "calculator",
            "expected_args": {"expression": f"{a}+{b}"}
        })

    # 更多搜索 (40个)
    more_queries = [
        "Python入门", "Java教程", "Go语言", "Rust编程", "JavaScript基础",
        "React框架", "Vue开发", "Angular学习", "Node.js后端", "Django框架",
        "Flask入门", "Spring Boot", "MySQL教程", "PostgreSQL", "MongoDB",
        "Redis缓存", "Docker容器", "Kubernetes", "AWS服务", "阿里云教程",
        "机器学习入门", "深度学习框架", "神经网络", "CNN卷积神经网络", "RNN循环神经网络",
        "Transformer模型", "BERT模型", "GPT模型", "LLM大语言模型", "Prompt工程",
        "数据结构与算法", "操作系统原理", "计算机网络", "数据库设计", "软件工程",
        "敏捷开发", "DevOps实践", "CI/CD流水线", "微服务架构", "分布式系统"
    ]
    for i, query in enumerate(more_queries):
        all_cases.append({
            "name": f"搜索技术_{i+1}",
            "category": "搜索查询",
            "prompt": f"搜索{query}",
            "expected_tool": "search",
            "expected_args": {"query": query}
        })

    # 补充10个额外的边界测试案例以达到300个
    extra_edge_cases = [
        {"name": "额外_代码生成", "category": "边界情况", "prompt": "写一个Python函数计算斐波那契数列", "expected_tool": "search", "expected_args": {"query": "Python斐波那契数列"}},
        {"name": "额外_健康咨询", "category": "边界情况", "prompt": "查询感冒的症状和治疗方法", "expected_tool": "search", "expected_args": {"query": "感冒症状治疗"}},
        {"name": "额外_菜谱搜索", "category": "边界情况", "prompt": "搜索红烧肉的做法", "expected_tool": "search", "expected_args": {"query": "红烧肉做法"}},
        {"name": "额外_快递查询", "category": "边界情况", "prompt": "查询顺丰快递单号", "expected_tool": "search", "expected_args": {"query": "顺丰快递"}},
        {"name": "额外_诗词查询", "category": "边界情况", "prompt": "搜索李白的静夜思", "expected_tool": "search", "expected_args": {"query": "李白静夜思"}},
        {"name": "额外_笑话请求", "category": "边界情况", "prompt": "给我讲个笑话", "expected_tool": "search", "expected_args": {"query": "笑话"}},
        {"name": "额外_名言搜索", "category": "边界情况", "prompt": "搜索爱因斯坦的名言", "expected_tool": "search", "expected_args": {"query": "爱因斯坦名言"}},
        {"name": "额外_节日查询", "category": "边界情况", "prompt": "今年中秋节是几月几号", "expected_tool": "search", "expected_args": {"query": "中秋节日期"}},
        {"name": "额外_彩票查询", "category": "边界情况", "prompt": "查询双色球开奖结果", "expected_tool": "search", "expected_args": {"query": "双色球开奖结果"}},
        {"name": "额外_油价查询", "category": "边界情况", "prompt": "今天油价多少钱一升", "expected_tool": "search", "expected_args": {"query": "今日油价"}},
    ]
    all_cases.extend(extra_edge_cases)

    # 确保每个案例都有description字段
    for case in all_cases:
        if "description" not in case:
            case["description"] = f"测试{case['category']}能力"

    # 如果超过300个，截取前300个；如果不足，保持不变
    if len(all_cases) > 300:
        return all_cases[:300]
    return all_cases


# 导出测试案例
TOOLS_TEST_CASES_LARGE = get_all_test_cases()

if __name__ == "__main__":
    print(f"生成了 {len(TOOLS_TEST_CASES_LARGE)} 个测试案例")

    # 统计各类别数量
    from collections import Counter
    categories = Counter(case["category"] for case in TOOLS_TEST_CASES_LARGE)
    print("\n类别分布:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}个")
