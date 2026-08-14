"""Supervisor Agent：意图识别 + 任务路由（平台/内容类型决策）。"""
import logging

from ..llm.call import call_json
from .prompts import SYS_SUPERVISOR
from .state import ContentState

logger = logging.getLogger(__name__)


def make_supervisor(llm):
    def run(state: ContentState) -> dict:
        payload = {
            "task": "supervise",
            "product": state.product.model_dump(),
            "requested_platform": state.platform,
            "requested_content_type": state.content_type,
        }
        result = call_json(llm, SYS_SUPERVISOR, payload)
        intent = result.get("intent") or {}
        # 防御：小模型可能把 "auto" 当字面值回显，需归一化为真实平台/类型
        platform = intent.get("platform") or state.platform or "抖音"
        content_type = intent.get("content_type") or state.content_type
        if platform in ("", "auto"):
            platform = "抖音"
        if content_type in ("", "auto"):
            # 按平台给出内容类型默认值
            content_type = {
                "小红书": "种草图文",
                "抖音": "短视频脚本",
                "快手": "短视频脚本",
                "视频号": "短视频脚本",
                "B站": "短视频脚本",
            }.get(platform, "种草图文")
        intent = {"platform": platform, "content_type": content_type}

        state.trace(
            "supervisor",
            "意图识别与任务路由",
            {"intent": intent, "reason": result.get("reason", "")},
        )
        return {"intent": intent, "agent_trace": state.agent_trace}

    return run
