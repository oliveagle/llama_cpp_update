#!/usr/bin/env python3
"""
ONNX Runtime Inference Server
支持多种 Execution Provider (CPU/CUDA/XDNA/ROCm/OpenVINO)
"""

import os
import sys
import time
import json
import signal
from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np

try:
    import onnxruntime as ort
except ImportError:
    print("Error: onnxruntime not installed")
    print("Install with: pip install onnxruntime")
    sys.exit(1)

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    print("Warning: Flask not installed, API server disabled")
    FLASK_AVAILABLE = False


class ExecutionProvider:
    """Execution Provider 类型"""
    CPU = 'CPUExecutionProvider'
    CUDA = 'CUDAExecutionProvider'
    ROCM = 'ROCMExecutionProvider'
    XDNA = 'XDNAExecutionProvider'
    OPENVINO = 'OpenVINOExecutionProvider'
    TENSORRT = 'TensorrtExecutionProvider'

    @staticmethod
    def from_string(name: str) -> str:
        ep_map = {
            'cpu': ExecutionProvider.CPU,
            'cuda': ExecutionProvider.CUDA,
            'rocm': ExecutionProvider.ROCM,
            'xdna': ExecutionProvider.XDNA,
            'openvino': ExecutionProvider.OPENVINO,
            'tensorrt': ExecutionProvider.TENSORRT,
        }
        return ep_map.get(name.lower(), ExecutionProvider.CPU)


class ONNXSession:
    """ONNX Runtime 会话封装"""

    def __init__(self, model_path: str, ep: str = None,
                 num_threads: int = 1, enable_profiling: bool = False):
        """
        初始化 ONNX 会话

        Args:
            model_path: ONNX 模型路径
            ep: Execution Provider (默认自动选择)
            num_threads: CPU 线程数
            enable_profiling: 启用性能分析
        """
        self.model_path = model_path
        self.ep = ep
        self.num_threads = num_threads
        self.enable_profiling = enable_profiling

        self.session: Optional[ort.InferenceSession] = None
        self.input_info: List[Dict] = []
        self.output_info: List[Dict] = []

        self.inference_count = 0
        self.total_inference_time = 0.0

        self._initialize()

    def _initialize(self):
        """初始化 ONNX Runtime 会话"""
        # 获取可用的 EP
        available_eps = ort.get_available_providers()
        print(f"Available Execution Providers: {available_eps}")

        # 选择 EP
        if self.ep is None:
            # 优先选择可用的 EP
            for ep in [ExecutionProvider.CUDA, ExecutionProvider.ROCM,
                       ExecutionProvider.XDNA, ExecutionProvider.OPENVINO,
                       ExecutionProvider.TENSORRT, ExecutionProvider.CPU]:
                if ep in available_eps:
                    self.ep = ep
                    break
        elif self.ep not in available_eps:
            print(f"Warning: {self.ep} not available, falling back to CPU")
            self.ep = ExecutionProvider.CPU

        print(f"Using Execution Provider: {self.ep}")

        # 创建会话选项
        session_options = ort.SessionOptions()
        session_options.intra_op_num_threads = self.num_threads
        session_options.inter_op_num_threads = self.num_threads
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        if self.enable_profiling:
            session_options.enable_profiling = True

        # 加载模型
        try:
            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=session_options,
                providers=[self.ep]
            )
            print(f"Model loaded: {self.model_path}")

            # 解析输入/输出信息
            self._parse_model_info()

        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def _parse_model_info(self):
        """解析模型输入/输出信息"""
        self.input_info = []
        for input_def in self.session.get_inputs():
            self.input_info.append({
                'name': input_def.name,
                'type': input_def.type,
                'shape': input_def.shape,
            })

        self.output_info = []
        for output_def in self.session.get_outputs():
            self.output_info.append({
                'name': output_def.name,
                'type': output_def.type,
                'shape': output_def.shape,
            })

        print(f"Inputs: {len(self.input_info)}, Outputs: {len(self.output_info)}")

    def run(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        运行推理

        Args:
            inputs: 输入张量字典 {name: array}

        Returns:
            输出张量字典 {name: array}
        """
        start_time = time.perf_counter()

        # 准备输入
        input_names = [info['name'] for info in self.input_info]
        input_arrays = [inputs.get(name) for name in input_names]

        if None in input_arrays:
            missing = [input_names[i] for i, x in enumerate(input_arrays) if x is None]
            raise ValueError(f"Missing inputs: {missing}")

        # 运行推理
        try:
            outputs = self.session.run(
                None,  # 输出名称 (None 表示全部)
                input_arrays
            )
        except Exception as e:
            print(f"Inference error: {e}")
            raise

        # 收集输出
        result = {}
        for info, output in zip(self.output_info, outputs):
            result[info['name']] = output

        # 统计
        inference_time = (time.perf_counter() - start_time) * 1000  # ms
        self.inference_count += 1
        self.total_inference_time += inference_time

        return result

    def get_stats(self) -> Dict:
        """获取性能统计"""
        avg_time = self.total_inference_time / self.inference_count if self.inference_count > 0 else 0
        return {
            'inference_count': self.inference_count,
            'total_time_ms': self.total_inference_time,
            'average_time_ms': avg_time,
            'ep': self.ep,
            'model_path': self.model_path,
        }


class ONNXRuntimeServer:
    """ONNX Runtime HTTP 服务器"""

    def __init__(self, host: str = '0.0.0.0', port: int = 8406):
        self.host = host
        self.port = port
        self.sessions: Dict[str, ONNXSession] = {}

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            self._setup_routes()

    def _setup_routes(self):
        """设置 API 路由"""

        @self.app.route('/health', methods=['GET'])
        def health():
            """健康检查"""
            return jsonify({'status': 'ok', 'sessions': len(self.sessions)})

        @self.app.route('/sessions', methods=['GET'])
        def list_sessions():
            """列出所有会话"""
            return jsonify({
                'sessions': list(self.sessions.keys()),
                'stats': {sid: session.get_stats()
                          for sid, session in self.sessions.items()}
            })

        @self.app.route('/sessions', methods=['POST'])
        def create_session():
            """创建新会话"""
            data = request.json
            session_id = data.get('session_id', 'default')
            model_path = data.get('model_path')
            ep = data.get('ep')
            num_threads = data.get('num_threads', 1)

            if not model_path or not os.path.exists(model_path):
                return jsonify({'error': 'Model not found'}), 404

            try:
                session = ONNXSession(model_path, ep, num_threads)
                self.sessions[session_id] = session
                return jsonify({
                    'session_id': session_id,
                    'model_path': model_path,
                    'ep': session.ep,
                    'inputs': session.input_info,
                    'outputs': session.output_info
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/sessions/<session_id>', methods=['DELETE'])
        def delete_session(session_id):
            """删除会话"""
            if session_id in self.sessions:
                del self.sessions[session_id]
                return jsonify({'status': 'deleted'})
            return jsonify({'error': 'Session not found'}), 404

        @self.app.route('/sessions/<session_id>/info', methods=['GET'])
        def session_info(session_id):
            """获取会话信息"""
            if session_id not in self.sessions:
                return jsonify({'error': 'Session not found'}), 404
            session = self.sessions[session_id]
            return jsonify({
                'inputs': session.input_info,
                'outputs': session.output_info,
                'stats': session.get_stats()
            })

        @self.app.route('/sessions/<session_id>/run', methods=['POST'])
        def run_inference(session_id):
            """运行推理"""
            if session_id not in self.sessions:
                return jsonify({'error': 'Session not found'}), 404

            session = self.sessions[session_id]
            data = request.json

            # 转换输入为 numpy 数组
            inputs_data = data.get('inputs', [])
            inputs = {}
            for item in inputs_data:
                if isinstance(item, dict):
                    inputs[item['name']] = np.array(item['value'], dtype=np.float32)
                else:
                    inputs[item] = np.array([item['value']], dtype=np.float32)

            try:
                outputs = session.run(inputs)
                # 转换输出为列表
                output_data = {name: arr.tolist() for name, arr in outputs.items()}
                return jsonify({
                    'outputs': output_data,
                    'stats': {
                        'inference_time_ms': session.total_inference_time - session.total_inference_time + 0,
                        'inference_count': session.inference_count,
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/v1/chat/completions', methods=['POST'])
        def chat_completions():
            """OpenAI 兼容的聊天完成 API"""
            # 这需要一个文本生成模型 (如 GPT-2/Llama)
            # 简化版 - 仅演示
            data = request.json
            session_id = data.get('model', 'default')

            if session_id not in self.sessions:
                return jsonify({'error': 'Model not loaded'}), 404

            # TODO: 实现 tokenization 和生成逻辑
            return jsonify({
                'error': 'Chat completion not yet implemented for ONNX models'
            }), 501

    def run(self):
        """启动服务器"""
        if not FLASK_AVAILABLE:
            print("Error: Flask not available. Install with: pip install flask")
            return

        print(f"Starting ONNX Runtime server on {self.host}:{self.port}")
        print(f"API Documentation:")
        print(f"  - GET  /health")
        print(f"  - GET  /sessions")
        print(f"  - POST /sessions")
        print(f"  - POST /sessions/<id>/run")

        try:
            self.app.run(host=self.host, port=self.port, threaded=True)
        except KeyboardInterrupt:
            print("\nServer stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='ONNX Runtime Inference Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=8406, help='Server port')
    parser.add_argument('--model', help='Load model at startup')
    parser.add_argument('--ep', help='Execution Provider (cpu/cuda/rocm/xdna/openvino/tensorrt)')
    parser.add_argument('--threads', type=int, default=1, help='CPU threads')
    parser.add_argument('--test', action='store_true', help='Run test only')

    args = parser.parse_args()

    # 测试模式
    if args.test:
        print("Testing ONNX Runtime...")
        print(f"Available EPs: {ort.get_available_providers()}")

        if args.model and os.path.exists(args.model):
            try:
                session = ONNXSession(args.model, args.ep, args.threads)
                print(f"Model loaded successfully!")
                print(f"Inputs: {session.input_info}")
                print(f"Outputs: {session.output_info}")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            print("No model specified or not found")
            print("Usage: python onnx_runtime_server.py --test --model <path>")
            sys.exit(1)
        return

    # 服务器模式
    server = ONNXRuntimeServer(args.host, args.port)

    # 加载初始模型
    if args.model and os.path.exists(args.model):
        print(f"Loading model: {args.model}")
        try:
            ep = args.ep or None
            if args.ep:
                ep = ExecutionProvider.from_string(args.ep)
            session = ONNXSession(args.model, ep, args.threads)
            server.sessions['default'] = session
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")

    server.run()


if __name__ == '__main__':
    main()
