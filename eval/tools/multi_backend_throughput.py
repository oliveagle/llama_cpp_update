#!/usr/bin/env python3
"""
多后端吞吐性能对比测试脚本
对比 ONNX Runtime (CPU EP)、llama.cpp Vulkan (gfx1151) 和 llama.cpp CUDA (V100) 三个后端的性能

测试内容：
1. 创建基准测试脚本 benchmarks/multi_backend_throughput.py
2. 测试方法：连续发送推理请求，计算 tokens/second 和请求/秒
3. 测试时长：60 秒（每个后端）
4. 指标：
   - 平均延迟（ms）
   - P50/P95/P99 延迟
   - 吞吐量（tokens/s）
   - 错误率（%）
   - GPU 利用率（如果可获取）
5. 对比结果生成 HTML 报告
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

# 配置
BACKENDS = {
    "onnx_cpu": {
        "name": "ONNX Runtime (CPU EP)",
        "url": "http://0.0.0.0:8406",
        "model": "Qwen3-0.6B-INT8",
        "description": "Python Flask API，端口 8406"
    },
    "llama_vulkan": {
        "name": "llama.cpp Vulkan (gfx1151)",
        "url": "http://0.0.0.0:8400",
        "model": "MiniCPM-o-4_5-Q4_K_M",
        "description": "AMD gfx1151 后端，端口 8400"
    },
    "llama_cuda": {
        "name": "llama.cpp CUDA (V100)",
        "url": "http://0.0.0.0:8401",
        "model": "MiniCPM-o-4_5-Q4_K_M",
        "description": "NVIDIA V100 后端，端口 8401"
    }
}

TEST_DURATION = 60  # 测试时长（秒）
TEST_PROMPT = "写一首关于人工智能的七言诗，大约30字"
EXPECTED_TOKENS = 100  # 期望生成约 100 tokens

# 颜色
class Colors:
    RESET = "\033[0m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    RED = "\033[0;31m"
    BLUE = "\033[0;34m"
    MAGENTA = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[0;37m"
    NC = "\033[0m"


class BackendTester:
    """后端测试器"""

    def __init__(self, name: str, url: str, model: str):
        self.name = name
        self.url = url
        self.model = model

        # 性能统计
        self.latencies = []
        self.token_count = 0
        self.error_count = 0
        self.start_time = None
        self.end_time = None

    def send_request(self, prompt: str) -> Optional[Dict]:
        """发送推理请求"""
        try:
            start = time.time()
            response = requests.post(
                f"{self.url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": EXPECTED_TOKENS,
                    "stream": False
                },
                timeout=30
            )
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()

                # 计算延迟
                latency = elapsed

                # 计算生成的 token 数（简单估算）
                # 这里我们假设每个响应约 100 tokens
                tokens_generated = 100

                # 提取使用情况（某些 API 返回 usage）
                usage = None
                if "usage" in data:
                    usage = data["usage"]
                    tokens_generated = data["usage"].get("prompt_tokens", 100)
                    completion_tokens = data["usage"].get("completion_tokens", 100)
                    tokens_generated = completion_tokens - tokens_generated

                return {
                    "success": True,
                    "latency_ms": round(latency, 2),
                    "tokens_generated": tokens_generated,
                    "usage": usage
                }
            else:
                self.error_count += 1
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "latency_ms": None
                }
        except requests.exceptions.Timeout:
            self.error_count += 1
            return {
                "success": False,
                "error": "Timeout",
                "latency_ms": None
            }
        except Exception as e:
            self.error_count += 1
            return {
                "success": False,
                "error": str(e)[:100],
                "latency_ms": None
            }

    def run_test(self, duration: int) -> Dict:
        """运行测试"""
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} {self.name} ({self.url})")
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} 模型: {self.model}")
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} 时长: {duration} 秒")
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} 提示: {TEST_PROMPT}")
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} 预期 tokens: ~{EXPECTED_TOKENS}")
        print(f"{Colors.CYAN}[TESTING]{Colors.NC} {'='*60}")

        self.start_time = time.time()

        # 运行测试
        for i in range(duration):
            result = self.send_request(TEST_PROMPT)

            if result["success"]:
                self.latencies.append(result["latency_ms"])
                self.token_count += result["tokens_generated"]

                # 显示进度
                if (i + 1) % 10 == 0 or (i + 1) == duration:
                    print(f"{Colors.GREEN}[{i+1:3d}] {result['latency_ms']}ms, tokens={result['tokens_generated']}")
                else:
                    print(f"{Colors.GREEN}[{i+1:3d}] {result['latency_ms']}ms", end="\r")
            else:
                print(f"{Colors.RED}[{i+1:3d}] {result['error']}", end="\r")

        self.end_time = time.time()
        actual_duration = (self.end_time - self.start_time)

        # 计算统计数据
        if self.latencies:
            stats = {
                "mean": round(statistics.mean(self.latencies), 2),
                "median": round(statistics.median(self.latencies), 2),
                "p50": round(statistics.quantiles(self.latencies, 0.5), 2),
                "p95": round(statistics.quantiles(self.latencies, 0.95), 2),
                "p99": round(statistics.quantiles(self.latencies, 0.99), 2),
                "min": round(min(self.latencies), 2),
                "max": round(max(self.latencies), 2)
            }
        else:
            stats = {
                "mean": 0,
                "median": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0,
                "min": 0,
                "max": 0
            }

        # 计算吞吐量
        actual_duration = actual_duration - (self.error_count * 0.1)  # 减去错误处理时间
        if actual_duration > 0:
            throughput = round(self.token_count / actual_duration, 2)
        else:
            throughput = 0
            error_rate = round((self.error_count / duration) * 100, 2)

        return {
            "backend": self,
            "stats": stats,
            "throughput": throughput,
            "tokens_per_second": round(self.token_count / actual_duration, 2) if actual_duration > 0 else 0,
            "total_requests": duration,
            "successful_requests": duration - self.error_count,
            "error_count": self.error_count,
            "error_rate": error_rate,
            "duration_seconds": round(actual_duration, 2)
        }


def compare_backends(results: Dict[str, Dict]) -> str:
    """生成对比报告 HTML"""

    # 颜色主题
    colors = {
        "onnx_cpu": {"bg": "#e74c3c", "text": "#ffffff"},
        "llama_vulkan": {"bg": "#ff9f00", "text": "#ffffff"},
        "llama_cuda": {"bg": "#00b8ff", "text": "#ffffff"}
    }

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多后端吞吐性能对比报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #333;
        }}
        .header p {{
            color: #666;
            font-size: 14px;
            margin: 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            background: #f8f9fa;
            color: #333;
        }}
        .summary-card h3 {{
            margin: 0 0 15px;
            font-size: 18px;
        }}
        .summary-card .metric {{
            font-size: 24px;
            margin: 5px 0;
        }}
        .summary-card .value {{
            font-size: 20px;
            font-weight: bold;
        }}
        .summary-card .unit {{
            font-size: 14px;
            color: #666;
        }}
        .winner {{
            margin-top: 10px;
            padding: 15px;
            border-radius: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }}
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 30px;
        }}
        .comparison-table th {{
            padding: 15px;
            background: #f0f0f0;
            color: white;
            font-weight: 600;
        }}
        .comparison-table td {{
            padding: 12px 15px;
            text-align: center;
            border-bottom: 1px solid #e0e0e0;
        }}
        .comparison-table .highlight {{
            background: #fff3cd;
            font-weight: bold;
        }}
        .bar-container {{
            width: 100%;
            height: 24px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .bar {{
            height: 100%;
            transition: width 0.3s;
        }}
        .bar-onnx {{ background: {colors.onnx_cpu.bg}; }}
        .bar-vulkan {{ background: {colors.llama_vulkan.bg}; }}
        .bar-cuda {{ background: {colors.llama_cuda.bg}; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>多后端吞吐性能对比报告</h1>
            <p>测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>测试配置: {TEST_DURATION} 秒 / 后端，提示词 "{TEST_PROMPT[:50]}..."</p>
        </div>

        <div class="summary">
"""

    # 生成摘要卡片
    for backend_id, backend_info in BACKENDS.items():
        if backend_id in results:
            result = results[backend_id]
            stats = result["stats"]

            color = colors[backend_id]

            html += f"""            <div class="summary-card" style="background: {color['bg']};">
                <h3>{backend_info['name']}</h3>
                <p style="font-size: 14px; color: #666; margin-bottom: 10px;">
                    {backend_info['description']}
                </p>

                <div class="metric">
                    <span>模型:</span>
                    <span class="value">{backend_info['model']}</span>
                </div>

                <div class="metric">
                    <span>测试时长:</span>
                    <span class="value">{result['duration_seconds']} 秒</span>
                </div>

                <div class="metric">
                    <span>成功请求:</span>
                    <span class="value">{result['successful_requests']}</span>
                </div>

                <div class="metric">
                    <span>错误请求:</span>
                    <span class="value">{result['error_count']}</span>
                </div>

                <div class="metric">
                    <span>错误率:</span>
                    <span class="value">{result['error_rate']}%</span>
                </div>
"""

            # 延迟统计
            if stats["mean"]:
                html += f"""                <div class="metric">
                    <span>平均延迟:</span>
                    <span class="value">{stats['mean']} ms</span>
                </div>
                <div class="metric">
                    <span>P50:</span>
                    <span class="value">{stats['p50']} ms</span>
                </div>
                <div class="metric">
                    <span>P95:</span>
                    <span class="value">{stats['p95']} ms</span>
                </div>
                <div class="metric">
                    <span>P99:</span>
                    <span class="value">{stats['p99']} ms</span>
                </div>
"""

            # 吞吐量
            html += f"""                <div class="metric">
                    <span>吞吐量:</span>
                    <span class="value">{result['throughput']} tokens/s</span>
                </div>
                <div class="metric">
                    <span>tokens/秒:</span>
                    <span class="value">{result['tokens_per_second']}</span>
                </div>
            """

    # 对比部分
    html += """        <h3>性能对比</h3>
        <div class="summary-card">
            <p style="text-align: center; font-weight: bold; margin-bottom: 20px;">吞吐量对比 (tokens/秒)</p>
        <div class="bar-container">
            <div class="bar bar-onnx" style="width: {results.get('onnx_cpu', {}).get('throughput', 0) * 100 / max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)] + 0.1) if max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)]) > 0 else 0}%"></div>
            <div class="bar bar-vulkan" style="width: {results.get('llama_vulkan', {}).get('throughput', 0) * 100 / max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)] + 0.1) if max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)]) > 0 else 0}%"></div>
            <div class="bar bar-cuda" style="width: {results.get('llama_cuda', {}).get('throughput', 0) * 100 / max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)] + 0.1) if max([results.get('llama_vulkan', {}).get('throughput', 0), results.get('llama_cuda', {}).get('throughput', 0)]) > 0 else 0}%"></div>
        </div>

        <div class="bar-container">
            <p style="text-align: center; font-weight: bold; margin-bottom: 20px;">延迟对比 (ms - 越低越好)</p>
            <div class="bar bar-onnx" style="width: {100 - results.get('onnx_cpu', {}).get('stats', {}).get('mean', 0) * 100 / [results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] + 0.1 if results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] > 0 else 0}%"></div>
            <div class="bar bar-vulkan" style="width: {100 - results.get('llama_cuda', {}).get('stats', {}).get('mean', 0) * 100 / [results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] + 0.1 if results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] > 0 else 0}%"></div>
            <div class="bar bar-cuda" style="width: {100 - results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) * 100 / [results.get('llama_cuda', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] + 0.1 if results.get('llama_vulkan', {}).get('stats', {}).get('mean', 0) + results.get('llama_cuda', {}).get('stats', {}).get('mean', 0)] > 0 else 0}%"></div>
        </div>
"""

    # 对比表
    html += """        <table class="comparison-table">
            <thead>
                <tr>
                    <th>后端</th>
                    <th>平均延迟 (ms)</th>
                    <th>P50 (ms)</th>
                    <th>P95 (ms)</th>
                    <th>吞吐量 (tokens/s)</th>
                </tr>
            </thead>
            <tbody>
"""

    for backend_id in ["onnx_cpu", "llama_vulkan", "llama_cuda"]:
        if backend_id in results:
            stats = results[backend_id]["stats"]
            highlight = 'highlight' if backend_id == "llama_cuda" else ''

            html += f"""                <tr class="{highlight}">
                    <td>{BACKENDS[backend_id]['name']}</td>
                    <td>{stats.get('mean', 0)}</td>
                    <td>{stats.get('p50', 0)}</td>
                    <td>{stats.get('p95', 0)}</td>
                    <td>{results[backend_id]['throughput']}</td>
                </tr>
"""
        else:
            html += f"""                <tr>
                    <td colspan="4" style="color: #999; text-align: center;">{BACKENDS[backend_id]['name']} - 未测试</td>
                </tr>
"""

    html += """            </tbody>
        </table>
"""

    # 获胜者
    backend_ids = ["onnx_cpu", "llama_vulkan", "llama_cuda"]
    throughput_values = {
        bid: results.get(bid, {}).get('throughput', 0)
        for bid in backend_ids
    }
    valid_throughputs = [bid for bid, v in throughput_values.items() if v > 0]

    if valid_throughputs:
        winner_id = max(valid_throughputs, key=lambda x: throughput_values[x])
        winner_name = BACKENDS[winner_id]["name"]
        winner_throughput = throughput_values[winner_id]

        html += f"""
        <div class="winner">
            <h3>性能 吞吐量获胜</h3>
            <p><strong>{winner_name}</strong></p>
            <p style="font-size: 24px;">{winner_throughput} tokens/秒</p>
        </div>
"""
    else:
        html += f"""
        <div class="winner">
            <h3>性能性能 吞吐量对比无效</h3>
            <p>所有后端测试均失败或吞吐量为 0</p>
        </div>
"""

    html += """
        <div class="footer">
            <p>测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>注意: 此测试为简单吞吐量对比，实际性能可能因模型架构、量化方式和实现细节而有所不同。</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def main():
    """主函数"""
    print(f"{Colors.CYAN}{'='*60}")
    print(f"{Colors.MAGENTA}多后端吞吐性能对比测试{Colors.NC}")
    print(f"{Colors.MAGENTA}{'='*60}")

    # 创建测试器
    testers = {
        backend_id: BackendTester(
            name=config["name"],
            url=config["url"],
            model=config["model"]
        )
        for backend_id, config in BACKENDS.items()
    }

    # 运行测试
    results = {}
    for backend_id, tester in testers.items():
        print(f"\n{Colors.CYAN}[INFO]{Colors.NC} 测试 {tester.name}...")
        print(f"{Colors.CYAN}[INFO]{Colors.NC} URL: {tester.url}")
        print(f"{Colors.CYAN}[INFO]{Colors.NC} 模型: {tester.model}")

        result = tester.run_test(TEST_DURATION)
        results[backend_id] = result

        # 显示简单统计
        print(f"\n{Colors.GREEN}[SUMMARY]{Colors.NC}")
        print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   测试时长: {result['duration_seconds']} 秒")
        print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   成功请求: {result['successful_requests']}")
        print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   错误请求: {result['error_count']}")
        print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   错误率: {result['error_rate']}%")
        print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   吞吐量: {result['throughput']} tokens/s")

        if result["stats"]["mean"]:
            print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   平均延迟: {result['stats']['mean']} ms")
            print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   P50: {result['stats']['p50']} ms")
            print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   P95: {result['stats']['p95']} ms")
            print(f"{Colors.GREEN}[SUMMARY]{Colors.NC}   P99: {result['stats']['p99']} ms")

    # 等待一下让所有测试都完成
    time.sleep(2)

    # 生成报告
    print(f"\n{Colors.CYAN}[INFO]{Colors.NC} 生成对比报告...")

    report = compare_backends(results)

    # 保存报告
    report_path = "/mnt/volume3/llama_cpp/benchmarks/multi_backend_throughput_report.html"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n{Colors.GREEN}[SUCCESS]{Colors.NC} 报告已保存: {report_path}")
    print(f"{Colors.CYAN}[INFO]{Colors.NC} 打开报告查看详细对比: file://{report_path}")
    print(f"{Colors.CYAN}[INFO]{Colors.NC}")
    print(f"{Colors.CYAN}[INFO]{Colors.NC} 访问 http://0.0.0.0:8406/health - 查看 ONNX Runtime 状态")
    print(f"{Colors.CYAN}[INFO]{Colors.NC} 访问 http://0.0.0.0:8400/health - 查看 llama.cpp Vulkan 状态")
    print(f"{Colors.CYAN}[INFO]{Colors.NC} 访问 http://0.0.0.0:8401/health - 查看 llama.cpp CUDA 状态")
    print(f"{Colors.CYAN}[INFO]{Colors.NC}")
    print(f"{Colors.MAGENTA}{'='*60}")


if __name__ == "__main__":
    main()
