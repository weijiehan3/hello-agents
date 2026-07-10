# %%


# %%
import os 
from typing import Optional
from openai import OpenAI
from hello_agents import HelloAgentsLLM, SimpleAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# %%
class MyLLM(HelloAgentsLLM):
    """
    自定义LLM类，继承自HelloAgentsLLM，增加对其他模型供应商的支持。
    """
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            base_url: Optional[str] = None,
            provider: Optional[str] = "auto",
            **kwargs
            ):
        
        if provider == "modelscope":
            logger.info("Using ModelScope LLM")
            self.provider = "modelscope"

            # 解析 ModelScope 的凭证
            self.api_key = api_key or os.getenv("MODELSCOPE_API_KEY")
            self.base_url = base_url or os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1/")

            if not self.api_key:
                raise ValueError("ModelScope API key is required. Please set it via the 'api_key' parameter")
            
            # 设置默认模型和其他参数
            self.model = model or os.getenv("LLM_MODEL_ID") or "Qwen/Qwen2.5-VL-72B-Instruct"
            self.api_key = api_key or os.getenv("LLM_API_KEY")
            self.temperature = kwargs.get("temperature", 0.7)
            self.max_tokens = kwargs.get("max_tokens", 2048)
            self.timeout = kwargs.get("timeout", 30)

            # 使用 OpenAI 的客户端来调用 ModelScope API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
        else:
            logger.info("使用默认模型")
            self.super().__init__(model=model, api_key=api_key, **kwargs)

        

            
        

# %%
class MyLLM2(HelloAgentsLLM):
    def __init__(self, provider: Optional[str] = "auto", **kwargs):
        if provider == "silliconflow":
            # 让父类做剩下的所有事
            super().__init__(  
                provider="siliconflow",
                base_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1/"),
                api_key=os.getenv("SILICONFLOW_API_KEY"),
                model=os.getenv("SILICONFLOW_MODEL_ID"), **kwargs)
        elif provider == "modelscope":
            super().__init__(
                provider="modelscope",
                base_url=os.getenv("MODELSCOPE_BASE_URL", "https://api-inference.modelscope.cn/v1/"),
                api_key=os.getenv("MODELSCOPE_API_KEY"),
                model=os.getenv("MODELSCOPE_MODEL_ID"), **kwargs)
        else:
            super().__init__(provider=provider, **kwargs)


