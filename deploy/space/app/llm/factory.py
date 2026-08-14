"""LLM 客户端工厂：按配置选择供应商，无 Key 自动回退 Mock。

客户端按进程缓存：本地 Ollama 的 warmup（模型预热）只执行一次，
避免每个请求/Agent 调用重复加载模型。
"""
import logging
from functools import lru_cache

from ..config import get_settings
from .client import LLMClient
from .mock import MockClient
from .openai_compat import OpenAICompatClient

logger = logging.getLogger(__name__)


@lru_cache
def get_llm_client() -> LLMClient:
    s = get_settings()
    provider = (s.llm_provider or "deepseek").strip().lower()

    if provider == "mock":
        return MockClient()

    if provider in ("deepseek", "openai"):
        key = s.deepseek_api_key if provider == "deepseek" else s.openai_api_key
        base = s.deepseek_base_url if provider == "deepseek" else s.openai_base_url
        model = s.deepseek_model if provider == "deepseek" else s.openai_model
        if key:
            logger.info("使用 %s 供应商, model=%s", provider, model)
            return OpenAICompatClient(api_key=key, base_url=base, model=model, timeout=s.llm_timeout)
        logger.warning("未配置 %s API Key，自动回退到 Mock 引擎。", provider.upper())
        return MockClient()

    if provider == "ollama":
        logger.info("使用本地 Ollama, model=%s", s.ollama_model)
        # Ollama OpenAI 兼容端点；用占位 Key（Ollama 不校验）；warmup 防冷启动超时
        client = OpenAICompatClient(
            api_key="ollama",
            base_url=s.ollama_base_url,
            model=s.ollama_model,
            timeout=s.llm_timeout,
            warmup=True,
        )
        client.name = "ollama"
        return client

    logger.warning("未知 LLM_PROVIDER=%s，回退 Mock。", provider)
    return MockClient()
