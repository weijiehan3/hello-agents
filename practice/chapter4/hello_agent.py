# %%
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()


# %%

class HelloAgent:
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = None) -> None:
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout= timeout or 30

        if not all ([self.model, self.api_key, self.base_url]):
            raise ValueError("模型ID，API密钥和服务器地址必须被提供或在 .env 文件中定义")

        self.client = OpenAI(api_key = self.api_key, base_url = self.base_url, timeout = self.timeout)

    def think(self, messages: list[dict[str, str]], temperature: float = 0.5 ) -> str:
        logger.info(f"正在调用 {self.model} 模型进行推理...")

        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )

            logger.info("大模型响应成功：")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""

                collected_content.append(content)
            print("大模型响应完成。")
            return "".join(collected_content)
        
        except Exception as e:
            logger.error(f"调用大模型时发生错误： {e}")
            return None


if __name__ == "__main__":
    try:
        agent = HelloAgent()

        messages = [
            {"role": "system", "content": "你是一个非常擅长写python的程序员"},
            {"role": "user", "content": "请帮我写一个快速排序算法，并进行讲解"}
        ]

        logger.info("-------开始调用大模型进行推理-------")
        response = agent.think(messages=messages, temperature=0.5)
        if response:
            logger.info(f"大模型的最终响应: {response}")
        
    except Exception as e:
        logger.error(f"程序执行过程中发生错误： {e}")



