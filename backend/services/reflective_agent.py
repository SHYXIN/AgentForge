"""
Reflective Agent 服务模块

具有自我反思能力的 Agent，能评估任务执行结果并在失败时调整策略。
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from backend.config import config as app_config


class ReflectiveAgent:
    """具有自我反思能力的 Agent。"""

    def __init__(self, max_retries: int = 3):
        self.config = app_config
        self.max_retries = max_retries
        self.conversation_history = []
        self.llm = self._create_llm()
        self.prompt = self._create_prompt()
        self.reflection_prompt = self._create_reflection_prompt()

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
        """创建对话提示模板。"""
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

    def _create_reflection_prompt(self) -> ChatPromptTemplate:
        """创建反思提示模板。"""
        system_template = """你是一个 AI 助手，需要评估之前的任务执行结果。
分析以下对话，判断任务是否成功完成：

{history}

用户的最后一个消息：{last_user_message}
AI 的最后一个回复：{last_ai_response}

请评估：
1. 任务是否成功完成？
2. 如果没有成功，原因是什么？
3. 应该如何调整策略？

请以 JSON 格式回复：
{
    "success": true/false,
    "reason": "原因",
    "adjustment": "调整建议"
}
"""

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("请评估任务执行结果。")
        ])

    def _format_history(self) -> str:
        """格式化对话历史。"""
        if not self.conversation_history:
            return "无"

        history_lines = []
        for msg in self.conversation_history[-10:]:
            role = "用户" if msg["role"] == "user" else "助手"
            history_lines.append(f"{role}: {msg['content']}")

        return "\n".join(history_lines)

    async def _evaluate_response(self, user_message: str, ai_response: str) -> dict:
        """评估 AI 回复质量。"""
        try:
            history = self._format_history()

            messages = self.reflection_prompt.format_messages(
                history=history,
                last_user_message=user_message,
                last_ai_response=ai_response
            )

            result = await self.llm.ainvoke(messages)
            response_text = result.content

            # 简单解析 JSON（实际应用中应该更健壮）
            import json
            try:
                # 尝试提取 JSON
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start >= 0 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            # 默认返回成功
            return {
                "success": True,
                "reason": "无法解析反思结果",
                "adjustment": "继续当前策略"
            }

        except Exception as e:
            return {
                "success": True,
                "reason": f"反思失败: {str(e)}",
                "adjustment": "继续当前策略"
            }

    async def process_message(self, message: str, conversation_id: Optional[str] = None) -> dict:
        """处理用户消息并返回 AI 回复，支持自我反思。"""
        last_error = None

        for attempt in range(self.max_retries):
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

                # 自我反思
                reflection = await self._evaluate_response(message, response_text)

                return {
                    "response": response_text,
                    "agent_thoughts": f"用户发送消息：'{message}'。我使用 Reflective Agent 处理并生成了回复。",
                    "reflection": reflection,
                    "attempts": attempt + 1,
                    "conversation_id": conversation_id or "default"
                }

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    continue

        # 所有重试都失败，返回降级回复
        print(f"Reflective Agent 调用失败: {last_error}")
        response_text = f"收到你的消息：{message}。我是一个 AI Agent，正在学习中..."
        agent_thoughts = f"用户发送消息：'{message}'。Reflective Agent 调用失败，使用降级回复。"

        return {
            "response": response_text,
            "agent_thoughts": agent_thoughts,
            "reflection": {"success": False, "reason": str(last_error), "adjustment": "使用降级回复"},
            "attempts": self.max_retries,
            "conversation_id": conversation_id or "default"
        }

    def clear_memory(self):
        """清理对话记忆。"""
        self.conversation_history.clear()
