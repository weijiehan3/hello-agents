from typing import Optional, Iterator
from hello_agents import SimpleAgent, HelloAgentsLLM, Config, Message, ToolRegistry
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class MySimpleAgent(SimpleAgent):
    """
    重写的简单对话Agent
    """

    def __init__(
            self,
            name: str,
            llm: HelloAgentsLLM,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            tool_registry: Optional["ToolRegistry"] = None,
            enable_tool_calling: bool = True
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.enable_tool_calling = enable_tool_calling and tool_registry is not None
        logger.info(f"{name} 初始化完成， 工具调用：{'启用' if self.enable_tool_calling else '禁用'}")

    def run(self, input_text: str, max_tool_iteratios: int =3, **kwargs) -> str:
        """
        重写的run方法 - 实现简单对话逻辑，支持可选工具调用
        """
        logger.info(f"Agent {self.name} 收到输入： {input_text}")

        # 构造消息队列
        messages = []

        # 添加系统消息
        enhanced_system_prompt = self._get_enhanced_system_prompt()
        messages.append({"role": "system", "content": enhanced_system_prompt})

        # 添加历史消息
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})

        # 添加当前用户信息
        messages.append({"role": "user", "content": input_text})

        # 如果没有启用工具调用，使用简单对话逻辑
        if not self.enable_tool_calling:
            response = self.llm.invoke(messages, **kwargs)
            self.add_message(Message(response, role="assistant"))
            self.add_message(Message(input_text, role="user"))
            # logger.info(f"Agent {self.name} 回复： {response}")
            return response
        
        # 如果启用工具调用， 使用工具调用逻辑
        return self._run_with_tools(messages, input_text, max_tool_iteratios, **kwargs)
    
    def _get_enhanced_system_prompt(self) -> str:
        """
        构建增强的系统提示词，包含工具信息
        """
        base_prompt = self.system_prompt or "You are a helpful assistant."

        if not self.enable_tool_calling or not self.tool_registry:
            return base_prompt
        
        # 获取工具描述
        tools_description = self.tool_registry.get_tools_description()
        if not tools_description or tools_description == "暂无可用工具":
            return base_prompt
        
        tools_section = "\n\n## 可用工具\n"
        tools_section += "你可以使用以下工具来帮助回答问题:\n"
        tools_section += tools_description + "\n"

        tools_section += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"
        tools_section += "例如:`[TOOL_CALL:search:Python编程]` 或 `[TOOL_CALL:memory:recall=用户信息]`\n\n"
        tools_section += "工具调用结果会自动插入到对话中，然后你可以基于结果继续回答。\n"

        return base_prompt + tools_section
    
    def _run_with_tools(self, messages: list, input_text: str, max_tool_iterations: int, **kwargs) -> str:
        """
        支持工具调用的运行逻辑
        """
        current_iteration = 0
        final_response = ""

        while current_iteration < max_tool_iterations:
            # 调用 llm
            response = self.llm.invoke(messages, **kwargs)

            # 检查是否有工具调用
            tool_calls = self._parse_tool_calls(response)

            if tool_calls:
                logger.info(f"Agent {self.name} 检测到工具调用: {tool_calls}")
                # 执行工具调用
                tool_results = []
                clean_response = response

                for call in tool_calls:
                    result = self._execute_tool_call(call["tool_name"], call["parameters"])
                    tool_results.append(result)

                    clean_response = clean_response.replace(call["original"], "")

                # 构建包含工具结果的消息
                messages.append({"role": "assistant", "content": clean_response})

                # 添加工具结果
                tool_results_text = "\n\n".join(tool_results)
                messages.append({"role": "user", "content": f"工具执行结果：\n{tool_results_text}"})

                current_iteration += 1
                continue

            # 如果没有工具调用，直接返回最终响应    
            final_response = response
            break

        # 如果超过最大迭代次数，获取最后一次回答
        if current_iteration >= max_tool_iterations and not final_response:
            final_response = self.llm.invoke(messages, **kwargs)

        # 保存到历史记录
        self.add_message(Message(input_text, role="user"))
        self.add_message(Message(final_response, role="assistant"))
        logger.info(f"Agent {self.name} 响应完成")
        
        return final_response
    

    def _parse_tool_calls(self, text: str) -> list:
        """
        解析文本中的工具调用功能
        """
        pattern = r'\[TOOL_CALL:([^:]+):([^\]]+)\]'
        matches = re.findall(pattern, text)


        tool_calls = []
        for tool_name, parameters in matches:
            tool_calls.append(
                {
                    "tool_name": tool_name.strip(),
                    "parameters": parameters.strip(),
                    "original": f"[TOOL_CALL:{tool_name}:{parameters}]"
                }
            )
        return tool_calls
    
    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """执行工具调用"""
        if not self.tool_registry:
            return f"错误：未配置工具注册表"
        
        try:
            # 智能参数解析
            if tool_name == 'calculator':
                # 计算器工具直接传入表达式
                result = self.tool_registry.execute_tool(tool_name, parameters)
            else:
                # 其他工具使用智能参数解析
                param_dict = self._parse_tool_parameters(tool_name, parameters)
                tool = self.tool_registry.get_tool(tool_name)
                if not tool:
                    return f"错误：未找到名为 '{tool_name}' 的工具。"
                result = tool.run(param_dict)
            return f"[工具调用结果: {tool_name}] {result}"
        
        except Exception as e:
            return f"错误：执行工具 '{tool_name}' 时发生异常: {str(e)}"
        
    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """智能解析工具"""
        param_dict = {}
        if '=' in parameters:
            # 格式： key = value 或 action = search, query = Python
            if ',' in parameters:
                # 多个参数：action=search, query=Python，limit=3
                pairs = parameters.split(',')
                for pair in pairs:
                    key, value = pair.split('=', 1)
                    param_dict[key.strip()] = value.strip()
            
            else:
                # 单个参数: key=value
                key, value = parameters.split('=', 1)
                param_dict[key.strip()] = value.strip()

        else:
            # 直接传入参数，根据工具类型智能推断
            if tool_name == 'search':
                param_dict = {'query': parameters}
            elif tool_name == 'memory':
                param_dict = {'action': 'search', 'query': parameters}
            else:
                param_dict = {'input': parameters}
        
        return param_dict
    
    def stream_run(self, input_text, **kwargs) -> Iterator[str]:
        """
        自定义的流式运行方法，支持工具调用
        """

        logger.info(f"Agent {self.name} 开始流式运行，输入：{input_text}")

        messages = []

        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": input_text})

        # 调用 llm 流式输出
        full_response = ""
        print("实时响应：", end="")
        for chunk in self.llm.stream_invoke(messages, **kwargs):
            full_response += chunk
            # think() 内部已打印每个 chunk，这里不再重复打印
            yield chunk
        
        print()  # 换行

        # 保存完整对话到历史记录
        self.add_message(Message(input_text, role="user"))
        self.add_message(Message(full_response, role="assistant"))
        logger.info(f"Agent {self.name} 流式响应完成，完整响应：{full_response}")


    def add_tool(self, tool) -> None:
        """添加工具到Agent"""
        if not self.tool_registry:
            from hello_agents import ToolRegistry
            self.tool_registry = ToolRegistry()
            self.enable_tool_calling = True

        self.tool_registry.register_tool(tool)
        logger.info(f"Agent {self.name} 添加工具: {tool.name}")

    def has_tools(self) -> bool:
        """检查是否有可用工具"""
        return self.enable_tool_calling and self.tool_registry is not None
    
    def remove_tool(self, tool_name: str) -> bool:
        """移除工具"""
        if self.tool_registry:
            self.tool_registry.unregister(tool_name)
            logger.info(f"Agent {self.name} 移除工具: {tool_name}")
            return True
        return False
    
    def list_tools(self) -> list:
        """列出所有可用工具"""
        if self.tool_registry:
            return self.tool_registry.list_tools()
        return []

