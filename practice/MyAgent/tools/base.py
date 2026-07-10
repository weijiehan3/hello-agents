# tool.py 工具基类
from abc import ABC, abstractmethod
from typing import Any, Dict, Callable
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class Toolparameter(BaseModel):
    """
    工具参数类，用于描述工具所需的参数信息
    """
    name: str = Field(description="参数名称")
    type: str = Field(description="参数类型")
    description: str = Field(description="参数描述")
    required: bool = Field(default=True, description="参数是否必需")
    default: Any = Field(default=None, description="参数默认值")


class Tool(ABC):
    """
    工具基类
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description


    @abstractmethod
    def run(self, parameters: dict[str, Any]) -> str:
        """
        执行工具的主要逻辑
        :param parameters: 工具所需的参数字典
        :return: 工具执行结果的字符串表示
        """
        pass

    @abstractmethod
    def get_parameters(self) -> list[Toolparameter]:
        """
        获取工具所需的参数信息
        :return: 工具参数列表
        """
        pass


 





 