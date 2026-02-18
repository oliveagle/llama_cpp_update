#!/usr/bin/env python3
"""
模型配置包

自动发现和加载所有模型调优配置

使用方法:
    from model_configs import get_tuning_config

    config = get_tuning_config("JoyAI-LLM-Flash-Q4_K_M")
    tuned_prompt = config.apply_to_prompt("列出文件")
"""

import os
import sys
import importlib
from typing import Dict, List, Optional

from .base import ModelTuningConfig


# 缓存已加载的配置
_config_cache: Dict[str, ModelTuningConfig] = {}


def _discover_configs() -> List:
    """自动发现所有模型配置"""
    configs = []

    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 遍历目录中的.py文件
    for filename in os.listdir(current_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base.py']:
            module_name = filename[:-3]  # 去掉.py

            try:
                # 动态导入模块
                module = importlib.import_module(f'.{module_name}', package=__name__)

                # 检查是否有CONFIG和match_model
                if hasattr(module, 'CONFIG') and hasattr(module, 'match_model'):
                    configs.append({
                        'name': module_name,
                        'module': module,
                        'config': module.CONFIG,
                        'matcher': module.match_model,
                    })
            except Exception as e:
                print(f"[WARNING] 加载配置 {module_name} 失败: {e}", file=sys.stderr)

    return configs


# 全局配置列表
_DISCOVERED_CONFIGS = _discover_configs()


def get_tuning_config(model_name: str) -> ModelTuningConfig:
    """
    获取模型的调优配置

    Args:
        model_name: 模型名称

    Returns:
        ModelTuningConfig: 调优配置（如果没有则返回默认）
    """
    # 检查缓存
    if model_name in _config_cache:
        return _config_cache[model_name]

    # 查找匹配的配置
    for cfg_info in _DISCOVERED_CONFIGS:
        if cfg_info['matcher'](model_name):
            _config_cache[model_name] = cfg_info['config']
            return cfg_info['config']

    # 返回默认配置
    default_config = ModelTuningConfig(model_name=model_name)
    _config_cache[model_name] = default_config
    return default_config


def list_available_configs() -> List[str]:
    """列出所有可用的配置名称"""
    return [cfg['name'] for cfg in _DISCOVERED_CONFIGS]


def apply_model_tuning(tools: List[Dict], model_name: str) -> List[Dict]:
    """
    应用模型调优到工具定义

    Args:
        tools: 原始工具定义列表
        model_name: 模型名称

    Returns:
        调优后的工具定义列表
    """
    config = get_tuning_config(model_name)
    return config.apply_to_tools(tools)


# 导出主要接口
__all__ = [
    'ModelTuningConfig',
    'get_tuning_config',
    'apply_model_tuning',
    'list_available_configs',
]


# 模块加载时打印信息
if __name__ != '__main__':
    configs = list_available_configs()
    if configs:
        print(f"[INFO] 已加载模型配置: {', '.join(configs)}")
