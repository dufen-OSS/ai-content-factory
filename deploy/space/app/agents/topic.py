"""选题 Agent：围绕商品生成 4 个差异化选题方向。"""
from ..llm.call import call_json
from .prompts import SYS_TOPIC
from .state import ContentState


def make_topic(llm):
    def run(state: ContentState) -> dict:
        payload = {
            "task": "topics",
            "product": state.product.model_dump(),
            "intent": state.intent,
        }
        result = call_json(llm, SYS_TOPIC, payload)
        topics = [t for t in (result.get("topics") or []) if t][:4]
        state.trace("topic", "选题方向生成", {"topics": topics})
        return {"topics": topics, "agent_trace": state.agent_trace}

    return run
