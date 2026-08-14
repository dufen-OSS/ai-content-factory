"""审核 Agent：广告法合规 + 内容完整性检查，失败自动返修。"""
import logging

from ..llm.call import call_json
from .prompts import SYS_REVIEW
from .state import ContentState

logger = logging.getLogger(__name__)


def make_review(llm):
    def run(state: ContentState) -> dict:
        payload = {
            "task": "review",
            "title": state.title,
            "content": state.script,
            "product": state.product.model_dump(),
        }
        result = call_json(llm, SYS_REVIEW, payload)
        passed = bool(result.get("passed", False))
        feedback = result.get("feedback") or []
        # 本节点对「已失败」计数，供条件路由判断是否再返修一次
        new_retry = state.retry_count + 1 if not passed else state.retry_count

        state.trace(
            "review",
            "合规审核",
            {"passed": passed, "feedback": feedback, "retry_count": new_retry},
        )
        return {
            "review_passed": passed,
            "review_feedback": feedback,
            "retry_count": new_retry,
            "agent_trace": state.agent_trace,
        }

    return run
