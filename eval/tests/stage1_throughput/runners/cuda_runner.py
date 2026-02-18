#!/usr/bin/env python3
"""
CUDA 后端运行器 - 实现 Stage1Evaluator 接口

用于 NVIDIA GPU (V100) 的 CUDA 后端测试。
"""

import os
import sys
import subprocess
import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.base_evaluator import Stage1Evaluator
from core.data_logger import DataLogger


class CudaRunner(Stage1Evaluator):
    """
    CUDA 后端运行器

    专为 NVIDIA V100 设计的测试运行器。
    支持 CUDA_VISIBLE_DEVICES 环境设置和大型 context。
    """

    def __init__(self, backend_config: Dict, model_config: Dict, base_url: str = "http://localhost:8401"):
        """
        初始化 CUDA 运行器

        Args:
            backend_config: 后端配置（从 YAML 加载）
            model_config: 模型配置
            base_url: llama-server API 端点
        """
        super().__init__(backend_config, model_config, base_url)

        # 加载详细配置
        self.server_config = backend_config.get('server', {})
        self.env_vars = self.server_config.get('env', {})
        self.binary_path = self.server_config.get('binary_path', '/home/oliveagle/opt/llama.cpp/build/bin/llama-server')

        # 设置日志
        self.server_process = None
        self.logger = None

    def setup_server(self, model_file: str, **kwargs) -> bool:
        """
        启动 CUDA llama-server

        Args:
            model_file: GGUF 模型文件路径
            **kwargs: 覆盖默认参数的额外参数

        Returns:
            bool: 是否成功启动
        """
        # 设置环境变量
        env = os.environ.copy()
        env.update(self.env_vars)

        # 构建启动参数
        default_params = self.server_config.get('default_params', {})
        model_params = self.server_config.get('model_params', {})

        # 应用后端特定的模型覆盖
        backend_overrides = self.model_config.get('backend_overrides', {}).get('cuda', {})

        # 合并参数
        params = {**default_params, **model_params, **backend_overrides, **kwargs}

        # 构建命令行
        cmd = [self.binary_path, "-m", model_file]

        # 添加参数
        for key, value in params.items():
            if key == 'ngl':
                cmd.extend(["--ngl", str(value)])
            elif key == 'n_ctx':
                cmd.extend(["--ctx-size", str(value)])
            elif key == 'n_batch':
                cmd.extend(["--batch-size", str(value)])
            elif key == 'n_ubatch':
                cmd.extend(["--ubatch-size", str(value)])
            elif key == 'n_threads':
                cmd.extend(["--threads", str(value)])
            elif key == 'n_threads_batch':
                cmd.extend(["--threads-batch", str(value)])
            elif key == 'chat_template':
                cmd.extend(["--chat-template", str(value)])
            elif key == 'embeddings' and value:
                cmd.append("--embeddings")

        # 端口
        port = self.server_config.get('port', 8401)
        cmd.extend(["--port", str(port)])

        try:
            # 启动服务器
            print(f"Starting CUDA server: {' '.join(cmd)}")
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 等待服务器就绪
            if self._wait_for_server(timeout=60):
                print(f"CUDA server ready on port {port}")
                return True
            else:
                print("CUDA server failed to start")
                self.teardown_server()
                return False

        except Exception as e:
            print(f"Error starting CUDA server: {e}")
            return False

    def teardown_server(self) -> bool:
        """
        停止 CUDA llama-server

        Returns:
            bool: 是否成功停止
        """
        try:
            if self.server_process:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()
                self.server_process = None
                print("CUDA server stopped")
            return True
        except Exception as e:
            print(f"Error stopping CUDA server: {e}")
            return False

    def get_server_params(self) -> Dict[str, Any]:
        """
        获取 CUDA 特定的服务器参数

        Returns:
            参数字典
        """
        default_params = self.server_config.get('default_params', {})
        model_params = self.server_config.get('model_params', {})
        backend_overrides = self.model_config.get('backend_overrides', {}).get('cuda', {})

        return {**default_params, **model_params, **backend_overrides}

    def _wait_for_server(self, timeout: int = 60) -> bool:
        """等待服务器就绪"""
        import urllib.request
        import time

        port = self.server_config.get('port', 8401)
        url = f"http://localhost:{port}/health"

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                urllib.request.urlopen(url, timeout=1)
                return True
            except:
                time.sleep(0.5)

        return False

    def set_logger(self, logger: DataLogger):
        """设置数据记录器"""
        self.logger = logger


def load_cuda_backend_config(config_dir: str = None) -> Dict:
    """
    加载 CUDA 后端配置

    Args:
        config_dir: 配置目录路径，默认为相对路径

    Returns:
        后端配置字典
    """
    if config_dir is None:
        config_dir = Path(__file__).parent.parent / "config" / "backends"

    config_file = Path(config_dir) / "v100_cuda.yaml"

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    # 测试运行器
    config = load_cuda_backend_config()
    print(f"Loaded CUDA config: {config['backend']['name']}")

    model_config = {
        'id': 'test-model',
        'gguf_file': 'test.gguf',
        'backend_overrides': {}
    }

    runner = CudaRunner(config, model_config)
    print(f"Server params: {runner.get_server_params()}")
