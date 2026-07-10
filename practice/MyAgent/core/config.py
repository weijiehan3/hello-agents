"""配置管理"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Config(BaseModel):
    """HelloAgents配置类，用于管理全局配置参数"""

    # LLM配置
    default_model: str = "deepseek-v4-flash"
    default_base_url: str = "https://api.deepseek.com"
    temperature: float = 0.7
    max_tokens: Optional[int] = 2048

    # 系统配置
    debug: bool = False
    log_level: str = "INFO"

    # 其他配置
    max_history_length: int = 100

    @classmethod
    def form_env(cls) -> "Config":
        """从环境变量中创建配置"""
        return cls(
            debug = os.getenv("DEBUG", "false").lower() == "true",
            log_level = os.getenv("LOG_LEVEL", "INFO"),
            temperature = float(os.getenv("TEMPERATURE", 0.7)),
            max_tokens = int(os.getenv("MAX_TOKENS", 2048)),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return self.dict()