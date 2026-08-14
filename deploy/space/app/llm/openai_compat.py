"""OpenAI 兼容客户端：DeepSeek / 智谱 / 通义 / 硅基流动 等共用。"""
import json
import logging

from openai import OpenAI

from .client import LLMClient

logger = logging.getLogger(__name__)


class OpenAICompatClient(LLMClient):
    name = "openai-compat"

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        timeout: float = 120.0,
        warmup: bool = False,
    ):
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self._model = model
        if warmup:
            self._warmup()

    def _warmup(self) -> None:
        """预热：本地 Ollama 冷启动时先加载模型，避免首个 Agent 调用超时。"""
        try:
            self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
                timeout=300,
            )
            logger.info("LLM 预热完成（%s）", self._model)
        except Exception as e:  # noqa: BLE001
            logger.warning("LLM 预热失败（忽略）：%s", e)

    def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()

    def chat_json(self, system: str, user: str, temperature: float = 0.3) -> dict:
        last_err: Exception | None = None
        for attempt in range(2):
            try:
                resp = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                content = (resp.choices[0].message.content or "").strip()
                # 去除可能的 markdown 代码围栏
                if content.startswith("```"):
                    content = content.strip("`")
                    if content.startswith("json"):
                        content = content[4:]
                return json.loads(content)
            except Exception as e:  # noqa: BLE001 - 解析/网络失败重试一次
                last_err = e
                logger.warning("chat_json 第 %s 次失败: %s", attempt + 1, e)
        # 完全失败时抛错，由调用方（agent）回退 Mock
        raise RuntimeError(f"LLM JSON 输出失败: {last_err}") from last_err
