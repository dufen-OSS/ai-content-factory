"""LLM 供应商公共接口。

约定：所有 Agent 调用 LLM 时，user 消息一律是 JSON 对象，格式为
    {"task": "<任务名>", ...业务字段}
system 消息为角色设定与输出要求（含 "json" 字样以触发 JSON 模式）。
MockClient 依据 task 分发到规则引擎；真实供应商遵循提示词生成。
"""
from abc import ABC, abstractmethod


class LLMClient(ABC):
    name: str = "base"

    @abstractmethod
    def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        """普通对话，返回文本。"""

    @abstractmethod
    def chat_json(self, system: str, user: str, temperature: float = 0.3) -> dict:
        """返回合法 JSON 对象；失败时由实现方负责兜底（重试/回退）。"""
