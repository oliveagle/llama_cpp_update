#!/usr/bin/env python3
"""
摘要总结能力测试

测试模型的文本摘要和信息提取能力
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from framework.base import BaseEvaluator, TestResult, StageResult
from utils.raw_data_logger import RawDataLogger


# 摘要测试用例
SUMMARIZATION_TEST_CASES = [
    {
        "name": "新闻摘要",
        "description": "新闻报道摘要",
        "text": "据新华社报道，中国科学家近日在量子计算领域取得重大突破。研究团队成功研制出具备255个光子的量子计算机原型机'九章三号'，在处理高斯玻色取样问题上，其计算速度比全球最快的超级计算机快一亿亿倍。这一成果标志着中国在量子计算领域继续保持国际领先地位。相关论文已发表于《物理评论快报》期刊。",
        "expected_keywords": ["量子计算", "九章三号", "255个光子", "突破"],
        "max_length": 50,
        "category": "新闻摘要"
    },
    {
        "name": "科技文章摘要",
        "description": "技术概念解释摘要",
        "text": "人工智能（AI）是指由计算机系统所表现出的智能行为。现代AI技术主要基于机器学习，特别是深度学习。深度学习使用多层神经网络来模拟人脑的工作方式，能够自动从大量数据中学习特征和模式。应用包括图像识别、自然语言处理、语音识别等。近年来，大语言模型如GPT系列引发了AI应用的新浪潮。",
        "expected_keywords": ["人工智能", "深度学习", "神经网络", "大语言模型"],
        "max_length": 40,
        "category": "科技摘要"
    },
    {
        "name": "会议记录摘要",
        "description": "工作会议要点提取",
        "text": "会议纪要：1. 产品发布日期确定为下月15日。2. 市场部负责制定推广方案，预算50万元。3. 技术部需要在10日前完成所有测试工作。4. 客服部准备FAQ文档和用户手册。5. 下次会议定于下周一上午10点。",
        "expected_keywords": ["发布", "15日", "测试", "FAQ"],
        "max_length": 30,
        "category": "会议摘要"
    },
    {
        "name": "故事梗概",
        "description": "文学作品情节摘要",
        "text": "《西游记》讲述了唐僧师徒四人西天取经的故事。唐僧受唐太宗之命前往西天求取真经，途中先后收服了孙悟空、猪八戒和沙僧三位徒弟。师徒四人历经九九八十一难，战胜各路妖魔鬼怪，最终到达西天取得真经，修成正果。",
        "expected_keywords": ["唐僧", "孙悟空", "西天取经", "八十一难"],
        "max_length": 40,
        "category": "文学摘要"
    },
    {
        "name": "产品描述摘要",
        "description": "产品功能要点",
        "text": "新款智能手机采用6.7英寸OLED显示屏，支持120Hz刷新率。搭载最新旗舰处理器，配备12GB内存和256GB存储。后置三摄系统包括5000万像素主摄、1200万超广角和800万长焦。电池容量5000mAh，支持65W快充和无线充电。起售价4999元。",
        "expected_keywords": ["6.7英寸", "OLED", "三摄", "5000mAh", "4999"],
        "max_length": 35,
        "category": "产品摘要"
    },
    {
        "name": "历史事件摘要",
        "description": "历史事件总结",
        "text": "1969年7月20日，美国阿波罗11号飞船成功登陆月球。宇航员尼尔·阿姆斯特朗成为第一个踏上月球表面的人类，他说出了那句著名的话：'这是个人的一小步，却是人类的一大步。' Buzz Aldrin紧随其后踏上月球表面，而Michael Collins则留在指令舱中绕月飞行。这次任务标志着人类太空探索的重大里程碑。",
        "expected_keywords": ["阿波罗11号", "月球", "阿姆斯特朗", "1969"],
        "max_length": 40,
        "category": "历史摘要"
    },
    {
        "name": "邮件摘要",
        "description": "工作邮件要点",
        "text": "张经理您好，关于Q3项目进度汇报：目前开发工作已完成80%，预计下周可以进行内部测试。遇到的主要问题是第三方接口响应较慢，正在与供应商协调解决。需要您协调资源支持测试环境部署。如有疑问请随时联系。谢谢！李华",
        "expected_keywords": ["Q3项目", "80%", "第三方接口", "测试环境"],
        "max_length": 30,
        "category": "邮件摘要"
    },
    {
        "name": "论文摘要",
        "description": "学术论文摘要",
        "text": "本研究提出了一种新型的深度学习架构Transformer-XL，通过引入片段级递归机制和相对位置编码，有效解决了标准Transformer在处理长序列时的上下文碎片化问题。实验表明，该模型在多个语言建模基准测试中取得了 state-of-the-art 的结果，同时显著提升了长文本理解能力。",
        "expected_keywords": ["Transformer-XL", "长序列", "递归机制", "语言建模"],
        "max_length": 40,
        "category": "学术摘要"
    },
    {
        "name": "对话摘要",
        "description": "对话内容总结",
        "text": "用户：我想订一张明天从北京到上海的机票。客服：好的，请问您需要什么舱位？用户：经济舱就行，最好是上午的航班。客服：明天上午有08:30和10:15两个航班，价格分别是980元和1200元。用户：选08:30的吧。客服：好的，已为您预订明天08:30北京到上海的航班，票价980元。",
        "expected_keywords": ["机票", "北京到上海", "08:30", "980元"],
        "max_length": 30,
        "category": "对话摘要"
    },
    {
        "name": "政策摘要",
        "description": "政策文件要点",
        "text": "关于推进新能源产业发展的指导意见：一、到2030年新能源汽车销量占比达到40%以上。二、完善充电基础设施建设，实现县城全覆盖。三、加大研发投入，突破电池核心技术。四、优化产业布局，培育具有国际竞争力的龙头企业。五、完善回收利用体系，促进产业绿色发展。",
        "expected_keywords": ["新能源汽车", "2030", "40%", "充电基础设施", "电池技术"],
        "max_length": 40,
        "category": "政策摘要"
    }
]


class SummarizationEvaluator(BaseEvaluator):
    """摘要总结能力评估器"""

    name = "summarization"
    description = "摘要总结能力测试"

    @property
    def stage_name(self) -> str:
        return "基础能力测试-摘要"

    @property
    def stage_number(self) -> int:
        return 2

    @property
    def threshold_percentage(self) -> float:
        return 0.5

    def __init__(self, model_url: str, model_name: str, **kwargs):
        super().__init__(model_url, model_name, **kwargs)
        backend = "v100" if "8401" in model_url else "vulkan"
        self.raw_logger = RawDataLogger(backend)

    def run_tests(self) -> StageResult:
        """运行摘要测试"""
        test_results = []
        start_time = time.time()

        for test_case in SUMMARIZATION_TEST_CASES:
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
        """测试单个摘要任务"""
        import requests

        prompt = f"请用不超过{test_case['max_length']}个字概括以下内容：\n\n{test_case['text']}"

        url = f"{self.model_url}/v1/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "你是一个文本摘要专家，请准确概括文本要点。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 128,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start

            if resp.status_code != 200:
                return TestResult(
                    name=test_case["name"],
                    category=test_case["category"],
                    passed=False,
                    duration_ms=elapsed * 1000,
                    error_message=f"HTTP {resp.status_code}"
                )

            data = resp.json()
            message = data["choices"][0]["message"]
            content = message.get("content", "")
            if not content:
                content = message.get("reasoning_content", "")

            # 检查关键词
            keywords = test_case["expected_keywords"]
            matched = sum(1 for kw in keywords if kw in content)
            passed = matched >= len(keywords) * 0.6  # 至少60%关键词

            self.raw_logger.log_test_result({
                "model": self.model_name,
                "test_name": test_case["name"],
                "text": test_case["text"][:200],
                "expected_keywords": keywords,
                "generated_summary": content,
                "keywords_matched": matched,
                "passed": passed,
                "raw_response": data
            }, test_type="summarization")

            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=passed,
                duration_ms=elapsed * 1000,
                details={
                    "summary": content[:200],
                    "keywords_matched": f"{matched}/{len(keywords)}"
                }
            )

        except Exception as e:
            return TestResult(
                name=test_case["name"],
                category=test_case["category"],
                passed=False,
                duration_ms=0,
                error_message=str(e)
            )


def run_summarization_test(model_url: str, model_name: str) -> dict:
    """运行摘要测试"""
    evaluator = SummarizationEvaluator(model_url, model_name)
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
    print("="*60)
    print("V100 (CUDA) 摘要总结能力测试")
    print("="*60)

    result = run_summarization_test(
        "http://localhost:8401",
        "test-model"
    )

    print(f"\n总测试: {result['total_tests']}")
    print(f"通过: {result['passed_tests']}")
    print(f"失败: {result['failed_tests']}")
    print(f"通过率: {result['pass_rate']*100:.1f}%")
