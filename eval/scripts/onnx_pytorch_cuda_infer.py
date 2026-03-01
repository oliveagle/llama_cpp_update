#!/usr/bin/env python3
"""
AMD GPU/CUDA 加速的 ONNX 模型推理服务器

使用 PyTorch + CUDA 运行 ONNX 模型进行推理
虽然不是原生 XDNA NPU，但使用 GPU 加速提供高性能推理
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path

try:
    from flask import Flask, request, jsonify
    import numpy as np
    import torch
    import onnx
    import onnxruntime as ort
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install: pip install flask numpy torch onnx onnxruntime")
    sys.exit(1)

app = Flask(__name__)

# 全局变量
session = None
ort_session = None
model_path = None
model_info = {}

def load_onnx_model(model_file):
    """加载 ONNX 模型"""
    global session, model_info

    print(f"Loading ONNX model: {model_file}")

    # 验证模型文件
    if not os.path.exists(model_file):
        raise FileNotFoundError(f"Model file not found: {model_file}")

    # 使用 ONNX Runtime 加载模型
    session = ort.InferenceSession(
        model_file,
        providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
    )

    # 获取模型信息
    model_info = {
        'inputs': [{'name': i.name, 'shape': i.shape, 'type': i.type}
                   for i in session.get_inputs()],
        'outputs': [{'name': o.name, 'shape': o.shape, 'type': o.type}
                    for o in session.get_outputs()],
        'providers': session.get_providers()
    }

    print(f"Model loaded successfully")
    print(f"Inputs: {len(model_info['inputs'])}")
    print(f"Outputs: {len(model_info['outputs'])}")
    print(f"Providers: {model_info['providers']}")

    return session, model_info

def run_onnx_inference(session, inputs_dict):
    """运行 ONNX 推理"""
    # 准备输入
    ort_inputs = {}
    for name, value in inputs_dict.items():
        if isinstance(value, np.ndarray):
            ort_inputs[name] = value
        else:
            # 转换为 numpy 数组
            ort_inputs[name] = np.array(value, dtype=np.float32)

    # 运行推理
    start_time = time.time()
    outputs = session.run(None, ort_inputs)
    inference_time = (time.time() - start_time) * 1000

    return {
        'outputs': outputs,
        'inference_time_ms': inference_time
    }

@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok' if session is not None else 'error',
        'sessions': 1 if session is not None else 0,
        'model_path': model_path
    })

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """列出会话"""
    sessions_list = []
    if session is not None:
        sessions_list.append({
            'id': 'default',
            'model_path': model_path,
            'inputs_count': len(model_info.get('inputs', [])),
            'outputs_count': len(model_info.get('outputs', [])),
            'status': 'active'
        })
    return jsonify({'sessions': sessions_list})

@app.route('/sessions', methods=['POST'])
def create_session():
    """创建推理会话"""
    global model_path

    data = request.get_json()

    if not data or 'model_path' not in data:
        return jsonify({'error': 'model_path is required'}), 400

    try:
        model_path = data['model_path']
        load_onnx_model(model_path)

        return jsonify({
            'id': 'default',
            'status': 'created',
            'model_path': model_path,
            'inputs': model_info['inputs'],
            'outputs': model_info['outputs'],
            'providers': model_info['providers']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sessions/<session_id>/run', methods=['POST'])
def run_inference(session_id):
    """运行推理"""
    global session

    if session is None:
        return jsonify({'error': 'No active session'}), 400

    try:
        data = request.get_json()

        # 解析输入
        inputs = {}
        if 'inputs' in data:
            input_data = data['inputs']
            if isinstance(input_data, list):
                for item in input_data:
                    if isinstance(item, dict) and 'name' in item and 'value' in item:
                        inputs[item['name']] = item['value']
            elif isinstance(input_data, dict):
                inputs = input_data

        if not inputs:
            return jsonify({'error': 'No inputs provided'}), 400

        # 运行推理
        result = run_onnx_inference(session, inputs)

        # 格式化输出
        outputs_list = []
        for i, output in enumerate(result['outputs']):
            outputs_list.append({
                'name': model_info['outputs'][i]['name'] if i < len(model_info['outputs']) else f'output_{i}',
                'value': output.tolist() if isinstance(output, np.ndarray) else output,
                'shape': list(output.shape) if isinstance(output, np.ndarray) else []
            })

        response = {
            'session_id': session_id,
            'outputs': outputs_list,
            'inference_time_ms': result['inference_time_ms']
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI 兼容的聊天完成 API"""
    global session

    if session is None:
        return jsonify({'error': 'Model not loaded'}), 400

    try:
        data = request.get_json()

        messages = data.get('messages', [])
        if not messages:
            return jsonify({'error': 'messages is required'}), 400

        # 获取最后一个用户消息
        last_message = messages[-1].get('content', '')

        # 简化处理：将文本转换为输入张量
        # 注意：这是一个简化的实现，实际需要完整的 tokenizer
        input_tokens = [ord(c) % 128 for c in last_message[:512]]
        input_array = np.array(input_tokens, dtype=np.float32).reshape(1, -1)

        # 创建输入字典
        input_name = model_info['inputs'][0]['name'] if model_info['inputs'] else 'input'
        inputs = {input_name: input_array}

        # 运行推理
        result = run_onnx_inference(session, inputs)

        # 简化输出处理
        output_array = result['outputs'][0]
        output_tokens = output_array.flatten()

        # 将 tokens 转换为文本
        response_text = ''.join([chr(int(t) % 128) for t in output_tokens if int(t) < 128])

        return jsonify({
            'id': 'chatcmpl-' + str(int(time.time() * 1000)),
            'object': 'chat.completion',
            'created': int(time.time()),
            'model': data.get('model', 'onnx-model'),
            'choices': [{
                'index': 0,
                'message': {
                    'role': 'assistant',
                    'content': response_text
                },
                'finish_reason': 'stop'
            }],
            'usage': {
                'prompt_tokens': len(input_tokens),
                'completion_tokens': len(output_tokens),
                'total_tokens': len(input_tokens) + len(output_tokens)
            }
        })

    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

def main():
    parser = argparse.ArgumentParser(description='ONNX PyTorch/CUDA Inference Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8407, help='Port to listen on')
    parser.add_argument('--model', type=str, required=True, help='Path to ONNX model file')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')

    args = parser.parse_args()

    print("=" * 60)
    print("ONNX PyTorch/CUDA Inference Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Model: {args.model}")
    print(f"Workers: {args.workers}")
    print("=" * 60)

    # 加载模型
    global model_path
    model_path = args.model
    load_onnx_model(model_path)

    print("\nStarting server...")
    app.run(host=args.host, port=args.port, workers=args.workers, threaded=False)

if __name__ == '__main__':
    main()
