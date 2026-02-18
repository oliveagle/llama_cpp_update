#!/usr/bin/env python3
"""Generate individual model report pages from Stage 2 test results."""

import json
import os
from pathlib import Path
from datetime import datetime

# Template for model report page
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{model_name} | 模型评测报告</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .model-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}
        .model-header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        .model-meta {{
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .meta-label {{
            opacity: 0.8;
            font-size: 0.9rem;
        }}
        .meta-value {{
            font-weight: 600;
            font-size: 1.1rem;
        }}
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .score-card {{
            background: var(--card-bg, #ffffff);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            border-left: 4px solid {border_color};
        }}
        .score-card h3 {{
            color: var(--text-secondary, #64748b);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        .score-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {border_color};
        }}
        .score-detail {{
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-secondary, #64748b);
        }}
        .test-details {{
            background: var(--card-bg, #ffffff);
            border-radius: 1rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .test-details h2 {{
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color, #e2e8f0);
        }}
        .test-item {{
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            background: #f8fafc;
        }}
        .test-item.passed {{
            border-left: 4px solid #10b981;
        }}
        .test-item.failed {{
            border-left: 4px solid #ef4444;
        }}
        .test-name {{
            font-weight: 600;
            margin-bottom: 0.25rem;
        }}
        .test-status {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .test-status.pass {{
            background: #d1fae5;
            color: #065f46;
        }}
        .test-status.fail {{
            background: #fee2e2;
            color: #991b1b;
        }}
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
            color: var(--primary-color, #2563eb);
            text-decoration: none;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../stage2.html" class="back-link">← 返回 Stage 2 报告</a>

        <div class="model-header">
            <h1>{model_name}</h1>
            <div class="model-meta">
                <div class="meta-item">
                    <span class="meta-label">模型大小:</span>
                    <span class="meta-value">{model_size}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">测试时间:</span>
                    <span class="meta-value">{test_date}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">总体评分:</span>
                    <span class="meta-value">{overall_score:.1f}%</span>
                </div>
            </div>
        </div>

        <div class="score-grid">
            <div class="score-card">
                <h3>代码能力</h3>
                <div class="score-value">{code_rate:.0f}%</div>
                <div class="score-detail">{code_passed}/{code_total} 通过</div>
            </div>
            <div class="score-card">
                <h3>数学推理</h3>
                <div class="score-value">{math_rate:.0f}%</div>
                <div class="score-detail">{math_passed}/{math_total} 通过</div>
            </div>
            <div class="score-card">
                <h3>文本理解</h3>
                <div class="score-value">{text_rate:.0f}%</div>
                <div class="score-detail">{text_passed}/{text_total} 通过</div>
            </div>
        </div>

        {test_details_html}

        <footer class="footer" style="text-align: center; padding: 2rem; color: #64748b;">
            <p>llama.cpp 模型评测报告 | 生成时间: {generated_date}</p>
        </footer>
    </div>
</body>
</html>
'''

TEST_SECTION_TEMPLATE = '''
        <div class="test-details">
            <h2>{category_name}</h2>
            {test_items}
        </div>
'''

TEST_ITEM_TEMPLATE = '''
            <div class="test-item {status_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="test-name">{test_name}</span>
                    <span class="test-status {status_class2}">{status_text}</span>
                </div>
                {test_desc}
            </div>
'''


def get_score_color(rate):
    """Get color based on pass rate."""
    if rate >= 0.8:
        return "#10b981"  # Green
    elif rate >= 0.6:
        return "#f59e0b"  # Yellow
    else:
        return "#ef4444"  # Red


def generate_test_details(data, category):
    """Generate HTML for test details section."""
    if category not in data or not data[category].get("details"):
        return ""

    details = data[category]["details"]
    test_items = []

    for item in details:
        name = item.get("name", "Unknown")
        passed = item.get("passed", False)
        desc = item.get("details", {}).get("description", "")
        error = item.get("error", "")

        status_class = "passed" if passed else "failed"
        status_class2 = "pass" if passed else "fail"
        status_text = "通过" if passed else "失败"

        desc_html = f"<p style='margin-top: 0.5rem; font-size: 0.9rem; color: #64748b;'>{desc}</p>" if desc else ""
        if error and not passed:
            desc_html += f"<p style='margin-top: 0.5rem; font-size: 0.85rem; color: #ef4444;'>错误: {error[:100]}...</p>"

        test_items.append(TEST_ITEM_TEMPLATE.format(
            test_name=name,
            status_class=status_class,
            status_class2=status_class2,
            status_text=status_text,
            test_desc=desc_html
        ))

    category_names = {
        "code": "代码能力测试详情",
        "math": "数学推理测试详情",
        "text": "文本理解测试详情"
    }

    return TEST_SECTION_TEMPLATE.format(
        category_name=category_names.get(category, category),
        test_items="".join(test_items)
    )


def generate_model_report(json_path, output_dir):
    """Generate HTML report for a single model."""
    with open(json_path, "r") as f:
        data = json.load(f)

    model_name = data.get("model", "Unknown")
    model_size = data.get("size", "Unknown")
    timestamp = data.get("timestamp", "")

    # Parse date
    try:
        test_date = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
    except:
        test_date = timestamp

    # Calculate scores
    code = data.get("code", {})
    math = data.get("math", {})
    text = data.get("text", {})

    code_passed = code.get("passed", 0)
    code_total = code.get("total", 0)
    code_rate = code.get("pass_rate", 0) * 100

    math_passed = math.get("passed", 0)
    math_total = math.get("total", 0)
    math_rate = math.get("pass_rate", 0) * 100

    text_passed = text.get("passed", 0)
    text_total = text.get("total", 0)
    text_rate = text.get("pass_rate", 0) * 100

    # Calculate overall score
    total_passed = code_passed + math_passed + text_passed
    total_tests = code_total + math_total + text_total
    overall_score = (total_passed / total_tests * 100) if total_tests > 0 else 0

    # Get border color based on overall score
    border_color = get_score_color(overall_score / 100)

    # Generate test details sections
    test_details_html = ""
    for category in ["code", "math", "text"]:
        test_details_html += generate_test_details(data, category)

    # Generate HTML
    html = HTML_TEMPLATE.format(
        model_name=model_name,
        model_size=model_size,
        test_date=test_date,
        overall_score=overall_score,
        code_rate=code_rate,
        code_passed=code_passed,
        code_total=code_total,
        math_rate=math_rate,
        math_passed=math_passed,
        math_total=math_total,
        text_rate=text_rate,
        text_passed=text_passed,
        text_total=text_total,
        border_color=border_color,
        test_details_html=test_details_html,
        generated_date=datetime.now().strftime("%Y-%m-%d")
    )

    # Save to file
    safe_name = model_name.replace(" ", "_").replace("/", "_")
    output_path = Path(output_dir) / f"{safe_name}.html"
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Generated: {output_path}")
    return output_path.name


def main():
    """Generate reports for all models."""
    base_dir = Path("/mnt/volume3/llama_cpp")
    results_dir = base_dir / "eval_results/stage2/vulkan"
    output_dir = base_dir / "web/models"

    output_dir.mkdir(exist_ok=True)

    # Find all stage2 result files
    json_files = sorted(results_dir.glob("*_stage2.json"))

    print(f"Found {len(json_files)} model result files")
    generated_files = []

    for json_file in json_files:
        try:
            filename = generate_model_report(json_file, output_dir)
            generated_files.append(filename)
        except Exception as e:
            print(f"Error processing {json_file}: {e}")

    print(f"\nGenerated {len(generated_files)} model reports")
    return generated_files


if __name__ == "__main__":
    main()
