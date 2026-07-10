# %%
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# %%
MessageRole = Literal["user", "assistant", "system", "tool"]


# %%
class Message(BaseModel):
    """消息类"""

    content: str
    role: MessageRole
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """将消息对象转换为字典"""
        return {
            "role": self.role,
            "content": self.content,
        }

    def __str__(self) -> str:
        """返回消息的字符串表示"""
        return f"[{self.role}] {self.content}"






