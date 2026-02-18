#!/usr/bin/env python3
"""
Vulkan 后端运行器 - 实现 Stage1Evaluator 接口

用于 AMD GPU (gfx1151) 的 Vulkan 后端测试。
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


class VulkanRunner(Stage1Evaluator):
    """
    Vulkan 后端运行器

    专为 AMD gfx1151 (Strix Halo) 设计的测试运行器。
    自动处理 Vulkan ICD 环境设置和服务器管理。
    """

    def __init__(self, backend_config: Dict, model_config: Dict, base_url: str = "http://localhost:8400"):
        """
        初始化 Vulkan 运行器

        Args:
            backend_config: 后端配置（从 YAML 加载）
            model_config: 模型配置
            base_url: llama-server API 端点
        """
        super().__init__(backend_config, model_config, base_url)

        # 加载详细配置
        self.server_config = backend_config.get('server', {})
        self.env_vars = self.server_config.get('env', {})
        self.binary_path = self.server_config.get('binary_path', '/mnt/volume3/llama_cpp/current/llama-server')

        # 设置日志
        self.server_process = None
        self.logger = None

    def setup_server(self, model_file: str, **kwargs) -> bool:
        """
        启动 Vulkan llama-server

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
        backend_overrides = self.model_config.get('backend_overrides', {}).get('vulkan', {})

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
        port = self.server_config.get('port', 8400)
        cmd.extend(["--port", str(port)])

        try:
            # 启动服务器
            print(f"Starting Vulkan server: {' '.join(cmd)}")
            self.server_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # 等待服务器就绪
            if self._wait_for_server(timeout=60):
                print(f"Vulkan server ready on port {port}")
                return True
            else:
                print("Vulkan server failed to start")
                self.teardown_server()
                return False

        except Exception as e:
            print(f"Error starting Vulkan server: {e}")
            return False

    def teardown_server(self) -> bool:
        """
        停止 Vulkan llama-server

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
                print("Vulkan server stopped")
            return True
        except Exception as e:
            print(f"Error stopping Vulkan server: {e}")
            return False

    def get_server_params(self) -> Dict[str, Any]:
        """
        获取 Vulkan 特定的服务器参数

        Returns:
            参数字典
        """
        default_params = self.server_config.get('default_params', {})
        model_params = self.server_config.get('model_params', {})
        backend_overrides = self.model_config.get('backend_overrides', {}).get('vulkan', {})

        return {**default_params, **model_params, **backend_overrides}

    def _wait_for_server(self, timeout: int = 60) -> bool:
        """等待服务器就绪"""
        import urllib.request
        import time

        port = self.server_config.get('port', 8400)
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


def load_vulkan_backend_config(config_dir: str = None) -> Dict:
    """
    加载 Vulkan 后端配置

    Args:
        config_dir: 配置目录路径，默认为相对路径

    Returns:
        后端配置字典
    """
    if config_dir is None:
        config_dir = Path(__file__).parent.parent / "config" / "backends"

    config_file = Path(config_dir) / "vulkan_gfx1151.yaml"

    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    # 测试运行器
    config = load_vulkan_backend_config()
    print(f"Loaded Vulkan config: {config['backend']['name']}")

    model_config = {
        'id': 'test-model',
        'gguf_file': 'test.gguf',
        'backend_overrides': {}
    }

    runner = VulkanRunner(config, model_config)
    print(f"Server params: {runner.get_server_params()}")
