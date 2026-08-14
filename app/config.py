"""应用配置：从环境变量 / .env 读取，LLM 供应商可插拔切换。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ---- LLM 供应商：deepseek / openai / ollama / mock ----
    llm_provider: str = "deepseek"

    # DeepSeek（OpenAI 兼容）
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # 通用 OpenAI 兼容
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # 本地 Ollama（OpenAI 兼容端点 /v1，无需 Key）
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "qwen2.5:7b"

    # ---- 服务 ----
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    llm_timeout: float = 120.0
    max_review_retries: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
