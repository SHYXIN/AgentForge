"""
LangChain Agent 服务模块

使用 LangChain 接入 MiMo API，提供真实 AI 回复和对话记忆。
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from backend.config import config as app_config


class LangChainAgent:
    """LangChain Agent，接入 MiMo API 提供真实 AI 回复。"""

    def __init__(self):
        self.config = app_config
        self.conversation_history = []
        self.llm = self._create_llm()
        self.prompt = self._create_prompt()

    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM。"""
        return ChatOpenAI(
            model_name=self.config.openai_model,
            openai_api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            temperature=0.7,
            max_tokens=2000,
        )

    def _create_prompt(self) -> ChatPromptTemplate:
        """创建提示模板。"""
        system_template = """你是一个友好的 AI 助手，名叫 AgentForge。
你应该：
1. 用中文回复
2. 提供有帮助的回答
3. 记住对话上下文
4. 如果不确定，诚实地说不知道

对话历史：
{history}
"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{input}")
        ])

    def _format_history(self) -> str:
        """格式化对话历史。"""
        if not self.conversation_history:
            return "无"

        history_lines = []
        for msg in self.conversation_history[-10:]:  # 只保留最近10条
            role = "用户" if msg["role"] == "user" else "助手"
            history_lines.append(f"{role}: {msg['content']}")

        return "\n".join(history_lines)

    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> dict:
        """处理用户消息并返回 AI 回复。

        Args:
            message: 用户消息
            conversation_id: 对话 ID（可选）

        Returns:
            包含 response, agent_thoughts, conversation_id 的字典
        """
        try:
            # 格式化对话历史
            history = self._format_history()

            # 创建提示
            messages = self.prompt.format_messages(history=history, input=message)

            # 调用 LLM
            response = await self.llm.ainvoke(messages)
            response_text = response.content

            # 添加到对话历史
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response_text})

            # 生成思考过程
            agent_thoughts = f"用户发送消息：'{message}'。我使用 LangChain 处理并生成了回复。"

            return {
                "response": response_text,
                "agent_thoughts": agent_thoughts,
                "conversation_id": conversation_id or "default"
            }

        except Exception as e:
            # 降级到模拟回复
            print(f"LangChain 调用失败: {e}")
            response_text = f"收到你的消息：{message}。我是一个 AI Agent，正在学习中..."
            agent_thoughts = f"用户发送消息：'{message}'。LangChain 调用失败，使用降级回复。"

            return {
                "response": response_text,
                "agent_thoughts": agent_thoughts,
                "conversation_id": conversation_id or "default"
            }

    def clear_memory(self):
        """清理对话记忆。"""
        self.conversation_history.clear()
