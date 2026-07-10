from .base import Tool
from typing import Callable, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    工具注册表
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}


    def register_tool(self, tool: Tool) -> None:
        """注册Tool对象"""
        if tool.name in self._tools:
            logger.info(f"工具 {tool.name} 已经存在，将被覆盖")
        self._tools[tool.name] = tool
        logger.info(f"工具 {tool.name} 已注册")

    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """
        直接注册函数作为工具

        Args: 
            name: 工具名
            description: 工具描述
            func: 工具函数，接受字符串参数，返回字符串结果
        """

        if name in self._funciton:
            logger.info(f"工具 {name} 已经存在，将被覆盖")

        self._functions[name] = {
            "description": description,
            "func": func
        }
        logger.info(f"工具 {name} 已注册")

        def get_tools_description(self) -> str:
            """
            获取所有可用工具的格式化描述字符串
            """
            descriptions = []

            # Tool 对象描述
            for tool in self._tools.values():
                descriptions.append(f"-{tool.name}: {tool.description}")

            # 函数工具描述
            for name, info in self._functions.items():
                descriptions.append(f"-{name}: {info['description']}")

            return "\n".join(descriptions) if descriptions else "无可用工具"
        
        def to_openai_schema(self) -> Dict[str, Any]:
            """
            转换为 OpenAI function calling schema 格式

            用于 FunctionCall Agent，使工具能够被 OpenAI 原生 function calling 使用

            Returns:
                符合 OpenAI funciton calling schema 的schema
            """

            parameters = self.get_parameters()

            # 构造 properties
            properties = {}
            required = []

            for param in parameters:
                # 基础属性定义
                prop = {
                    "type": param.type,
                    "description": param.description
                }

                # 如果有默认值，添加到描述中（OpenAI schema 不支持直接设置默认值）
                if param.default is not None:
                    prop["description"] = f"{param.description}(默认值: {param.default})"

                # 如果是数组类型，添加 items 定义
                if param.type == "array":
                    prop["items"] = {"type": "string"}  # 默认字符串数组

                    properties[param.name] = prop

                # 收集必须参数
                if param.required:
                    required.append(param.name)

            return{
                "type": "function",
                "function":{
                    "name": self.name,
                    
                }
            }
