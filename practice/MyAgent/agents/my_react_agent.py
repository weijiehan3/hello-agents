import re
from typing import Optional, List, Tuple
from hello_agents import ReActAgent, Config, Message, ToolRegistry, HelloAgentsLLM
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MY_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动。
Action: 选择一个行动，格式必须是以下之一:
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循:工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""

class MyReactAgent(ReActAgent):
    """
    重写的ReActAgent
    """

    def __init__(
            self,
            name: str,
            llm: HelloAgentsLLM,
            tool_registry: ToolRegistry,
            system_prompt: Optional[str] = None,
            config: Optional[Config] = None,
            max_steps: int = 5,
            custom_prompt: Optional[str] = None):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry 
        self.prompt_template = custom_prompt if custom_prompt else MY_REACT_PROMPT   
        logger.info(f"{name} 初始化完成，最大步骤数：{max_steps}")

    def run(self, input_text: str, **kwargs) -> str:
        """运行ReAct Agent"""
        self.current_history = []
        current_step = 0

        logger.info(f"🤖 {self.name} 开始处理问题: {input_text}")

        while current_step < self.max_steps:
            current_step += 1
            logger.info(f"\n--- 第 {current_step} 步 ---")

            # 1. 构建提示词
            tools_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tools_desc,
                question=input_text,
                history=history_str
            )  # 用 format 方法填充提示词模板
            # logger.info(f"构建的提示词:\n{prompt}")

            # 2. 调用LLM
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm.invoke(messages, **kwargs)
            logger.info(f"LLM的原始输出:\n{response_text}")
            logger.info(f"整体信息：{messages}")

            # 3. 解析输出
            thought, action = self._parse_output(response_text)

            # 4. 检查完成条件
            if action and action.startswith("Finish"):
                final_answer = self._parse_action_input(action)
                self.add_message(Message(input_text, role="user"))
                self.add_message(Message(final_answer, "assistant"))
                return final_answer
       
            
            # 5. 执行工具调用
            if action:
                tool_name, tool_input = self._parse_action(action)
                logger.info(f"执行工具调用: {tool_name}({tool_input})")
                observation = self.tool_registry.execute_tool(tool_name, tool_input)
                self.current_history.append(f"Observation: {observation}")

        # 超过最大步骤数仍未完成
        final_answer = "抱歉，我无法在规定的步骤内给出答案。"
        self.add_message(Message(input_text, role="user"))
        self.add_message(Message(final_answer, "assistant"))
        return final_answer


        

