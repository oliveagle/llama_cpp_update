#!/usr/bin/env python3
"""
模型调优配置基类

所有模型配置必须继承此类
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ModelTuningConfig:
    """模型调优配置基类"""

    model_name: str
    """模型标识名"""

    # 工具描述覆盖（可选）
    tool_description_overrides: Dict[str, str] = field(default_factory=dict)
    """覆盖默认工具描述，key为工具名"""

    # Prompt前缀/后缀
    prompt_prefix: str = ""
    """添加到所有prompt前的内容"""

    prompt_suffix: str = ""
    """添加到所有prompt后的内容"""

    # 参数调优
    temperature: float = 0.1
    """采样温度"""

    top_p: float = 0.9
    """核采样阈值"""

    max_tokens: int = 2048
    """最大生成token数"""

    # 允许的替代工具
    alternative_tools: Dict[str, List[str]] = field(default_factory=dict)
    """当期望工具不可得时的备选工具映射"""

    def apply_to_prompt(self, prompt: str) -> str:
        """应用调优配置到prompt"""
        result = prompt
        if self.prompt_prefix:
            result = f"{self.prompt_prefix}{result}"
        if self.prompt_suffix:
            result = f"{result}{self.prompt_suffix}"
        return result

    def apply_to_tools(self, tools: List[Dict]) -> List[Dict]:
        """应用调优配置到工具定义"""
        if not self.tool_description_overrides:
            return tools

        import copy
        tuned_tools = copy.deepcopy(tools)

        for tool in tuned_tools:
            tool_name = tool.get("function", {}).get("name", "")
            if tool_name in self.tool_description_overrides:
                tool["function"]["description"] = self.tool_description_overrides[tool_name]

        return tuned_tools

    def get_api_params(self) -> Dict[str, Any]:
        """获取API调用参数"""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
