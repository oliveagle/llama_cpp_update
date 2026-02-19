#!/usr/bin/env python3
"""
Generate individual HTML report pages for each model in Stage 2 testing.
"""

import json
import os
from datetime import datetime

# Configuration
RESULTS_DIR = "/mnt/volume3/llama_cpp/eval_results/stage2"
REPORT_WEB_DIR = "/mnt/volume3/llama_cpp/report_web"
MODEL_REPORTS_DIR = os.path.join(REPORT_WEB_DIR, "models")

# Ensure models directory exists
os.makedirs(MODEL_REPORTS_DIR, exist_ok=True)

# Category definitions
CATEGORIES = {
    'code': {'name': '代码能力', 'icon': '💻', 'description': 'Python代码生成'},
    'math': {'name': '数学推理', 'icon': '🔢', 'description': '数学问题求解'},
    'text': {'name': '文本理解', 'icon': '📚', 'description': '知识和理解'},
    'tool': {'name': '工具使用', 'icon': '🔧', 'description': '函数调用和API使用'},
    'reasoning': {'name': '逻辑推理', 'icon': '🧠', 'description': '逻辑和因果推理'},
    'knowledge': {'name': '知识问答', 'icon': '🌍', 'description': '世界知识和常识'},
    'translation': {'name': '翻译能力', 'icon': '🌐', 'description': '多语言翻译'},
    'summarization': {'name': '摘要总结', 'icon': '📝', 'description': '文本摘要和信息提取'},
    'safety': {'name': '安全合规', 'icon': '🛡️', 'description': '安全边界和合规性'},
    'multiturn': {'name': '多轮对话', 'icon': '💬', 'description': '上下文理解和多轮交互'},
}


def get_rating_class(pass_rate):
    """Get rating class based on pass rate"""
    if pass_rate >= 0.8:
        return 'excellent', '⭐⭐⭐⭐⭐ 优秀'
    elif pass_rate >= 0.6:
        return 'good', '⭐⭐⭐⭐ 良好'
    elif pass_rate >= 0.4:
        return 'average', '⭐⭐⭐ 及格'
    else:
        return 'poor', '⭐⭐ 需改进'


def generate_model_html(model_data, backend='cuda'):
    """Generate HTML report for a single model"""
    model_name = model_data['model']
    summary = model_data.get('summary', {})
    total_pass_rate = summary.get('total_pass_rate', 0)
    rating_class, rating_text = get_rating_class(total_pass_rate)

    # Generate category rows
    category_rows = []
    for cat_key, cat_info in CATEGORIES.items():
        if cat_key in model_data:
            cat = model_data[cat_key]
            passed = cat.get('passed', 0)
            total = cat.get('total', 0)
            pass_rate = cat.get('pass_rate', 0)
            duration = cat.get('duration', 0)

            cat_rating = 'excellent' if pass_rate >= 0.8 else 'good' if pass_rate >= 0.6 else 'average' if pass_rate >= 0.4 else 'poor'

            category_rows.append(f"""
                            <tr>
                                <td>{cat_info['icon']} {cat_info['name']}</td>
                                <td>{cat_info['description']}</td>
                                <td>{passed}/{total}</td>
                                <td><span class="score-badge {cat_rating}">{pass_rate*100:.1f}%</span></td>
                                <td>{duration:.1f}s</td>
                            </tr>""")

    # Generate test details sections
    test_details = []
    for cat_key, cat_info in CATEGORIES.items():
        if cat_key in model_data and 'details' in model_data[cat_key]:
            details = model_data[cat_key]['details']
            if not details:
                continue

            test_items = []
            for test in details:
                status_icon = '✅' if test.get('passed', False) else '❌'
                test_items.append(f'<li>{status_icon} {test.get("name", "Unknown")}</li>')

            test_details.append(f"""
                    <div class="test-category-detail">
                        <h4>{cat_info['icon']} {cat_info['name']}</h4>
                        <ul class="test-list">
                            {''.join(test_items)}
                        </ul>
                    </div>""")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{model_name} | Stage 2 测试报告</title>
    <link rel="stylesheet" href="../styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .model-header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        .model-title {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        .model-meta {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .meta-tag {{
            background: var(--bg-primary);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
        }}
        .score-overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .score-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }}
        .score-value {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--accent-primary);
        }}
        .score-label {{
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }}
        .category-table {{
            width: 100%;
            margin-top: 1rem;
        }}
        .test-category-detail {{
            background: var(--bg-secondary);
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }}
        .test-list {{
            list-style: none;
            padding: 0;
            margin: 0.5rem 0;
        }}
        .test-list li {{
            padding: 0.3rem 0;
            border-bottom: 1px solid var(--border-color);
        }}
        .test-list li:last-child {{
            border-bottom: none;
        }}
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--accent-primary);
            text-decoration: none;
            margin-bottom: 1rem;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo">
            <h2>🦙 llama.cpp</h2>
            <p>模型评测报告中心</p>
        </div>
        <ul class="nav-menu">
            <li><a href="../index.html">📊 概览</a></li>
            <li><a href="../stage1.html">⚡ Stage 1 - 性能测试</a></li>
            <li><a href="../stage2.html" class="active">🔧 Stage 2 - 基础能力</a></li>
            <li><a href="../stage3.html">🧠 Stage 3 - 综合能力</a></li>
            <li><a href="../methodology.html">📋 测试规范</a></li>
        </ul>
        <div class="nav-footer">
            <p>最后更新: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </nav>

    <main class="main-content">
        <a href="../stage2.html" class="back-link">← 返回 Stage 2 总览</a>

        <div class="model-header">
            <h1 class="model-title">🤖 {model_name}</h1>
            <div class="model-meta">
                <span class="meta-tag backend-tag {backend}">{backend.upper()}</span>
                <span class="meta-tag">📊 Stage 2 基础能力测试</span>
                <span class="meta-tag">⏱️ 测试耗时: {summary.get('total_duration', 0):.1f}s</span>
            </div>
        </div>

        <div class="content-section">
            <!-- Score Overview -->
            <div class="section-card">
                <h2>📈 测试得分概览</h2>
                <div class="score-overview">
                    <div class="score-card">
                        <div class="score-value">{summary.get('total_pass_rate', 0)*100:.1f}%</div>
                        <div class="score-label">总通过率</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{summary.get('total_passed', 0)}/{summary.get('total_tests', 0)}</div>
                        <div class="score-label">通过/总计</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{len([c for c in CATEGORIES.keys() if c in model_data])}</div>
                        <div class="score-label">测试类别</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">{rating_text}</div>
                        <div class="score-label">综合评级</div>
                    </div>
                </div>
            </div>

            <!-- Category Breakdown -->
            <div class="section-card">
                <h2>📊 分类详细得分</h2>
                <div class="ranking-table-container">
                    <table class="data-table category-table">
                        <thead>
                            <tr>
                                <th>测试类别</th>
                                <th>描述</th>
                                <th>通过/总计</th>
                                <th>通过率</th>
                                <th>耗时</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(category_rows)}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Test Details -->
            <div class="section-card">
                <h2>📝 测试详情</h2>
                {''.join(test_details) if test_details else '<p>暂无详细测试数据</p>'}
            </div>

            <!-- Summary -->
            <div class="section-card">
                <h2>💡 测试总结</h2>
                <div class="notice-box info">
                    <h4>测试信息</h4>
                    <ul>
                        <li><strong>模型名称:</strong> {model_name}</li>
                        <li><strong>测试后端:</strong> {backend.upper()}</li>
                        <li><strong>测试时间:</strong> {model_data.get('timestamp', 'N/A')}</li>
                        <li><strong>总测试数:</strong> {summary.get('total_tests', 0)}</li>
                        <li><strong>通过数:</strong> {summary.get('total_passed', 0)}</li>
                        <li><strong>失败数:</strong> {summary.get('total_tests', 0) - summary.get('total_passed', 0)}</li>
                        <li><strong>总耗时:</strong> {summary.get('total_duration', 0):.2f}秒</li>
                    </ul>
                </div>
            </div>
        </div>

        <footer class="page-footer">
            <p>llama.cpp 模型评测报告 | {model_name} | Stage 2 基础能力测试</p>
        </footer>
    </main>

    <script src="../scripts.js"></script>
</body>
</html>"""

    return html


def generate_model_index(models_data):
    """Generate index page for all model reports"""

    model_cards = []
    for model_data in models_data:
        model_name = model_data['model']
        summary = model_data.get('summary', {})
        total_pass_rate = summary.get('total_pass_rate', 0)
        rating_class, rating_text = get_rating_class(total_pass_rate)

        safe_name = model_name.replace('/', '_').replace(' ', '_')

        model_cards.append(f"""
                <div class="model-card">
                    <h3>{model_name}</h3>
                    <div class="model-score">
                        <span class="score-value">{total_pass_rate*100:.1f}%</span>
                        <span class="rating {rating_class}">{rating_text}</span>
                    </div>
                    <p>通过: {summary.get('total_passed', 0)}/{summary.get('total_tests', 0)}</p>
                    <a href="{safe_name}.html" class="btn-primary">查看详情 →</a>
                </div>""")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>模型详细报告 | Stage 2</title>
    <link rel="stylesheet" href="../styles.css">
    <style>
        .model-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }}
        .model-card {{
            background: var(--bg-secondary);
            padding: 1.5rem;
            border-radius: 12px;
            transition: transform 0.2s;
        }}
        .model-card:hover {{
            transform: translateY(-4px);
        }}
        .model-card h3 {{
            font-size: 1.1rem;
            margin-bottom: 1rem;
            word-break: break-all;
        }}
        .model-score {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 1rem 0;
        }}
        .score-value {{
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent-primary);
        }}
        .btn-primary {{
            display: inline-block;
            background: var(--accent-primary);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            text-decoration: none;
            margin-top: 1rem;
        }}
        .btn-primary:hover {{
            background: var(--accent-secondary);
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <div class="logo">
            <h2>🦙 llama.cpp</h2>
            <p>模型评测报告中心</p>
        </div>
        <ul class="nav-menu">
            <li><a href="../index.html">📊 概览</a></li>
            <li><a href="../stage1.html">⚡ Stage 1 - 性能测试</a></li>
            <li><a href="../stage2.html">🔧 Stage 2 - 基础能力</a></li>
            <li><a href="../stage3.html">🧠 Stage 3 - 综合能力</a></li>
            <li><a href="../methodology.html">📋 测试规范</a></li>
        </ul>
        <div class="nav-footer">
            <p>最后更新: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
    </nav>

    <main class="main-content">
        <header class="page-header">
            <div class="header-badge stage-2">Stage 2</div>
            <h1>🔧 模型详细报告</h1>
            <p>点击查看各模型的完整测试详情</p>
        </header>

        <div class="content-section">
            <div class="section-card">
                <h2>📊 所有模型</h2>
                <div class="model-grid">
                    {''.join(model_cards)}
                </div>
            </div>
        </div>

        <footer class="page-footer">
            <p>llama.cpp 模型评测报告 | Stage 2 基础能力测试</p>
        </footer>
    </main>

    <script src="../scripts.js"></script>
</body>
</html>"""

    return html


def main():
    """Generate all model report pages"""
    print("Generating individual model reports...")

    # Load aggregated results
    result_files = [
        os.path.join(RESULTS_DIR, "all_models_stage2_20260217_234021.json"),
        os.path.join(RESULTS_DIR, "all_models_stage2_20260217_232726.json"),
    ]

    models_data = []
    for result_file in result_files:
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        models_data = data
                        print(f"Loaded {len(data)} models from {result_file}")
                        break
            except Exception as e:
                print(f"Error loading {result_file}: {e}")

    if not models_data:
        print("No model data found!")
        return

    # Generate individual model pages
    generated = []
    for model_data in models_data:
        model_name = model_data['model']
        safe_name = model_name.replace('/', '_').replace(' ', '_')

        html = generate_model_html(model_data, backend='cuda')
        output_path = os.path.join(MODEL_REPORTS_DIR, f"{safe_name}.html")

        with open(output_path, 'w') as f:
            f.write(html)

        generated.append(f"  - {model_name} → models/{safe_name}.html")

    # Generate index page
    index_html = generate_model_index(models_data)
    index_path = os.path.join(MODEL_REPORTS_DIR, "index.html")
    with open(index_path, 'w') as f:
        f.write(index_html)

    print(f"\nGenerated {len(generated)} model reports:")
    print('\n'.join(generated))
    print(f"\nIndex page: models/index.html")
    print(f"\nAccess reports at: http://localhost:8080/models/")


if __name__ == "__main__":
    main()
