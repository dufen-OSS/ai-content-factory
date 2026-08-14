"""Agent 调用 LLM 的安全包装：真实供应商失败时自动回退 Mock，保证流程不中断。"""
import json
import logging

from .client import LLMClient
from .mock import MockClient

logger = logging.getLogger(__name__)


def call_json(llm: LLMClient, system: str, payload: dict, temperature: float = 0.3) -> dict:
    """发送 task 约定格式的 JSON 请求；真实 LLM 失败则用 Mock 兜底。"""
    message = json.dumps(payload, ensure_ascii=False)
    try:
        return llm.chat_json(system, message, temperature=temperature)
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM(%s) 调用失败，回退 Mock：%s", llm.name, e)
        return MockClient().chat_json(system, message, temperature=temperature)
