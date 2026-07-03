# %%
from pathlib import Path

from serpapi import SerpApiClient
from dotenv import load_dotenv
import logging
import os
import sys
import serpapi

print(sys.executable)
print(serpapi.__file__)


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# %%
def search(query: str) -> str:
    """
    一个基于 SerpApi 的搜索函数，返回搜索结果的摘要。
    """
    logger.info(f"正在调用 serapi 进行搜索： {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "SERPAPI_API_KEY 未设置，请检查 .env 文件。"
        
        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",
            "hl": "zh-cn"
            }
        
        client = SerpApiClient(params)
        results = client.get_dict()

        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            snippets = [f"[{i+1}] {res.get('title', "")}\n{res.get("snippet", "")}" for i, res in enumerate(results["organic_results"][:3])]
            return "\n\n".join(snippets)

        return f"未找到关于{query}的相关信息。"

    except Exception as e:
        logger.error(f"搜索过程中发生错误: {e}")
        return f"搜索过程中发生错误: {e}"    


# %%
def calculator(expression: str) -> str:
    """
    一个简单的计算器函数，计算数学表达式的结果。
    """
    logger.info(f"正在计算表达式： {expression}")
    try:
        # 使用 eval 进行计算，注意安全性问题，这里仅用于演示
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        logger.error(f"计算过程中发生错误: {e}")
        return f"计算过程中发生错误: {e}"

# %%
class ToolExecutor:
    """
    工具执行器类，用于调用不同的工具函数。
    """
    def __init__(self):
        self.tools: dict[str, dict[str, any]] = {}

    def register_tool(self, name: str, description: str, func: callable):
        """
        注册一个工具函数。
        
        """
        if name in self.tools:
            logger.warning(f"警告：工具 {name} 已经注册，将覆盖原有工具。")

        self.tools[name] = {
            "description": description,
            "function": func
        }
        logger.info(f"工具 {name} 已注册。")

    def get_tool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数
        """
        return self.tools.get(name, {}).get("function")
    
    def get_available_tools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串
        """
        return "\n".join(f"- {name}: {info['description']}" for name, info in self.tools.items())


def create_default_tool_executor() -> ToolExecutor:
    """
    创建一个默认的工具执行器，并预先注册常用工具。
    """
    tool_executor = ToolExecutor()
    tool_executor.register_tool(
        name="search",
        description="使用 SerpApi 进行搜索，返回搜索结果的摘要。",
        func=search,
    )
    return tool_executor

# %%
if __name__ == "__main__":
    tool_executor = ToolExecutor()

    tool_executor.register_tool(
        name="search",
        description="使用 SerpApi 进行搜索，返回搜索结果的摘要。",
        func=search
        )
    tool_executor.register_tool(
        name="calculator",
        description="一个简单的计算器函数，计算数学表达式的结果。",
        func=calculator
    )

    logger.info(f"可用工具：{tool_executor.get_available_tools()}")

    # tool_name = "search"
    # tool_input = "nvidia 最新的 GPU 产品是什么？"

    # tool_func = tool_executor.get_tool(tool_name)
    # if tool_func:
    #     result = tool_func(tool_input)
    #     logger.info(f"工具 {tool_name} 的执行结果：\n{result}")
    # else:
    #     logger.error(f"工具 {tool_name} 未找到。")


    tool_name = "calculator"
    tool_input = "3 * (4 + 5) - 10 / 2"

    tool_func = tool_executor.get_tool(tool_name)
    if tool_func:
        result = tool_func(tool_input)
        logger.info(f"工具 {tool_name} 的执行结果：\n{result}")
    else:
        logger.error(f"工具 {tool_name} 未找到。")

