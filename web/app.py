#!/usr/bin/env python3
"""
llama.cpp Test Report Web Server
Serves test reports at 0.0.0.0:9820
"""

import json
import os
from flask import Flask, render_template, jsonify
from pathlib import Path
import glob

app = Flask(__name__)

# Base paths
BASE_DIR = Path("/mnt/volume3/llama_cpp")
EVAL_RESULTS = BASE_DIR / "eval_results"


def load_json_files(pattern):
    """Load all JSON files matching pattern and return list of data."""
    files = glob.glob(str(pattern))
    results = []
    for f in sorted(files):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                data['_source_file'] = os.path.basename(f)
                results.append(data)
        except Exception as e:
            print(f"Error loading {f}: {e}")
    return results


def parse_stage1_data():
    """Parse Stage 1 test results."""
    files = glob.glob(str(EVAL_RESULTS / "stage1" / "*_stage1.json"))
    models = []

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                model_name = data.get('model', 'Unknown')
                categories = data.get('categories', {})

                func = categories.get('functionality', {})
                ctx = categories.get('context', {})
                perf = categories.get('performance', {})

                models.append({
                    'name': model_name,
                    'functionality_passed': func.get('passed', 0),
                    'functionality_total': func.get('total', 0),
                    'functionality_rate': func.get('pass_rate', 0) * 100,
                    'context_passed': ctx.get('passed', 0),
                    'context_total': ctx.get('total', 0),
                    'context_rate': ctx.get('pass_rate', 0) * 100,
                    'max_context': ctx.get('max_successful_tokens', 0),
                    'throughput': perf.get('throughput_tps', 0),
                    'latency': perf.get('prompt_latency_ms', 0),
                    'total_passed': data.get('summary', {}).get('total_passed', 0),
                    'total_tests': data.get('summary', {}).get('total_tests', 0),
                    'total_rate': data.get('summary', {}).get('total_pass_rate', 0) * 100,
                    'raw_data': data
                })
        except Exception as e:
            print(f"Error parsing {f}: {e}")

    # Sort by total rate descending
    models.sort(key=lambda x: x['total_rate'], reverse=True)
    return models


def parse_stage2_data():
    """Parse Stage 2 test results - get latest result for each model."""
    # Get tool test results (most complete)
    files = glob.glob(str(EVAL_RESULTS / "stage2" / "*_tool_result.json"))

    model_data = {}

    for f in files:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                model_name = data.get('model', 'Unknown')

                # Extract scores from different test types
                tool = data.get('tool', {})

                model_data[model_name] = {
                    'name': model_name,
                    'tool_passed': tool.get('passed', 0),
                    'tool_total': tool.get('total', 0),
                    'tool_rate': tool.get('pass_rate', 0) * 100,
                    'raw_data': data
                }
        except Exception as e:
            print(f"Error parsing {f}: {e}")

    # Also load consolidated results if available
    consolidated_files = glob.glob(str(EVAL_RESULTS / "stage2" / "all_models_stage2_*.json"))
    if consolidated_files:
        try:
            with open(consolidated_files[-1], 'r', encoding='utf-8') as fp:
                consolidated = json.load(fp)
                for item in consolidated:
                    model_name = item.get('model', '')
                    if model_name in model_data:
                        model_data[model_name]['code_passed'] = item.get('code', {}).get('passed', 0)
                        model_data[model_name]['code_total'] = item.get('code', {}).get('total', 0)
                        model_data[model_name]['code_rate'] = item.get('code', {}).get('pass_rate', 0) * 100
                        model_data[model_name]['math_passed'] = item.get('math', {}).get('passed', 0)
                        model_data[model_name]['math_total'] = item.get('math', {}).get('total', 0)
                        model_data[model_name]['math_rate'] = item.get('math', {}).get('pass_rate', 0) * 100
                        model_data[model_name]['text_passed'] = item.get('text', {}).get('passed', 0)
                        model_data[model_name]['text_total'] = item.get('text', {}).get('total', 0)
                        model_data[model_name]['text_rate'] = item.get('text', {}).get('pass_rate', 0) * 100
                        model_data[model_name]['total_passed'] = item.get('total', {}).get('passed', 0)
                        model_data[model_name]['total_total'] = item.get('total', {}).get('total', 0)
                        model_data[model_name]['total_rate'] = item.get('total', {}).get('pass_rate', 0) * 100
        except Exception as e:
            print(f"Error parsing consolidated: {e}")

    # Fill in defaults for missing data
    for model in model_data.values():
        model.setdefault('code_passed', 0)
        model.setdefault('code_total', 9)
        model.setdefault('code_rate', 0)
        model.setdefault('math_passed', 0)
        model.setdefault('math_total', 11)
        model.setdefault('math_rate', 0)
        model.setdefault('text_passed', 0)
        model.setdefault('text_total', 10)
        model.setdefault('text_rate', 0)
        model.setdefault('total_passed', model['tool_passed'])
        model.setdefault('total_total', model['tool_total'])
        model.setdefault('total_rate', model['tool_rate'])

    models = list(model_data.values())
    models.sort(key=lambda x: x.get('total_rate', 0), reverse=True)
    return models


def parse_stage3_data():
    """Parse Stage 3 test results."""
    files = glob.glob(str(EVAL_RESULTS / "stage3" / "*_stage3.json"))

    # Track latest result per model
    model_files = {}
    for f in files:
        basename = os.path.basename(f)
        # Extract model name (remove timestamp and _stage3.json)
        parts = basename.replace('_stage3.json', '').split('_')
        # Find where timestamp starts (2026...)
        model_name_parts = []
        for part in parts:
            if part.startswith('2026'):
                break
            model_name_parts.append(part)
        model_name = '_'.join(model_name_parts)

        if model_name not in model_files or f > model_files[model_name]:
            model_files[model_name] = f

    models = []
    for model_name, f in model_files.items():
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                categories = data.get('categories', {})

                math_cat = categories.get('数学推理', {})
                code_cat = categories.get('代码生成', {})
                logic_cat = categories.get('逻辑推理', {})
                commonsense_cat = categories.get('常识问答', {})
                text_cat = categories.get('文本理解', {})
                shell_cat = categories.get('Linux Shell', {})

                total_passed = (math_cat.get('passed_weight', 0) +
                               code_cat.get('passed_weight', 0) +
                               logic_cat.get('passed_weight', 0) +
                               commonsense_cat.get('passed_weight', 0) +
                               text_cat.get('passed_weight', 0) +
                               shell_cat.get('passed_weight', 0))
                total_weight = (math_cat.get('total_weight', 0) +
                               code_cat.get('total_weight', 0) +
                               logic_cat.get('total_weight', 0) +
                               commonsense_cat.get('total_weight', 0) +
                               text_cat.get('total_weight', 0) +
                               shell_cat.get('total_weight', 0))

                models.append({
                    'name': model_name,
                    'math_score': math_cat.get('score', 0),
                    'math_passed': math_cat.get('passed_weight', 0),
                    'math_total': math_cat.get('total_weight', 0),
                    'code_score': code_cat.get('score', 0),
                    'code_passed': code_cat.get('passed_weight', 0),
                    'code_total': code_cat.get('total_weight', 0),
                    'logic_score': logic_cat.get('score', 0),
                    'logic_passed': logic_cat.get('passed_weight', 0),
                    'logic_total': logic_cat.get('total_weight', 0),
                    'commonsense_score': commonsense_cat.get('score', 0),
                    'commonsense_passed': commonsense_cat.get('passed_weight', 0),
                    'commonsense_total': commonsense_cat.get('total_weight', 0),
                    'text_score': text_cat.get('score', 0),
                    'text_passed': text_cat.get('passed_weight', 0),
                    'text_total': text_cat.get('total_weight', 0),
                    'shell_score': shell_cat.get('score', 0),
                    'shell_passed': shell_cat.get('passed_weight', 0),
                    'shell_total': shell_cat.get('total_weight', 0),
                    'total_passed': total_passed,
                    'total_total': total_weight,
                    'total_rate': (total_passed / total_weight * 100) if total_weight > 0 else 0,
                    'raw_data': data
                })
        except Exception as e:
            print(f"Error parsing {f}: {e}")

    models.sort(key=lambda x: x['total_rate'], reverse=True)
    return models


@app.route('/')
def index():
    """Main dashboard page."""
    stage1_models = parse_stage1_data()
    stage2_models = parse_stage2_data()
    stage3_models = parse_stage3_data()

    # Calculate statistics
    stats = {
        'stage1_count': len(stage1_models),
        'stage2_count': len(stage2_models),
        'stage3_count': len(stage3_models),
        'stage1_top': stage1_models[0]['name'] if stage1_models else 'N/A',
        'stage2_top': stage2_models[0]['name'] if stage2_models else 'N/A',
        'stage3_top': stage3_models[0]['name'] if stage3_models else 'N/A',
    }

    return render_template('index.html',
                         stage1_models=stage1_models,
                         stage2_models=stage2_models,
                         stage3_models=stage3_models,
                         stats=stats)


@app.route('/stage1')
def stage1():
    """Stage 1 test reports page."""
    models = parse_stage1_data()
    return render_template('stage1.html', models=models)


@app.route('/stage2')
def stage2():
    """Stage 2 test reports page."""
    models = parse_stage2_data()
    return render_template('stage2.html', models=models)


@app.route('/stage3')
def stage3():
    """Stage 3 test reports page."""
    models = parse_stage3_data()
    return render_template('stage3.html', models=models)


@app.route('/methodology')
def methodology():
    """Testing methodology and specification page."""
    return render_template('methodology.html')


@app.route('/api/stage1')
def api_stage1():
    """API endpoint for Stage 1 data."""
    return jsonify(parse_stage1_data())


@app.route('/api/stage2')
def api_stage2():
    """API endpoint for Stage 2 data."""
    return jsonify(parse_stage2_data())


@app.route('/api/stage3')
def api_stage3():
    """API endpoint for Stage 3 data."""
    return jsonify(parse_stage3_data())


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9821
    app.run(host='0.0.0.0', port=port, debug=False)
