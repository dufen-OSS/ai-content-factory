"""脚本生成 Agent：按模板骨架 + 商品卖点产出成稿，支持返修。"""
import logging

from ..llm.call import call_json
from .prompts import SYS_SCRIPT
from .state import ContentState

logger = logging.getLogger(__name__)


def _render_markdown(title: str, content_type: str, body, storyboard, stages) -> str:
    lines = [f"# {title}", ""]
    if content_type == "种草图文" and body:
        for i, p in enumerate(body, 1):
            lines.append(f"## 第{i}段")
            lines.append(p)
            lines.append("")
    elif content_type == "短视频脚本" and storyboard:
        lines.append("| 镜头 | 时长 | 画面 | 台词 |")
        lines.append("| --- | --- | --- | --- |")
        for s in storyboard:
            lines.append(
                f"| {s.get('scene')} | {s.get('duration')} | {s.get('visual')} | {s.get('narration')} |"
            )
        lines.append("")
    elif stages:
        for st in stages:
            lines.append(f"## {st.get('name')}")
            lines.append(f"{st.get('script')}")
            lines.append(f"> 要点：{st.get('note', '')}")
            lines.append("")
    return "\n".join(lines)


def make_script(llm):
    def run(state: ContentState) -> dict:
        content_type = state.intent.get("content_type", "短视频脚本")
        payload = {
            "task": "script",
            "product": state.product.model_dump(),
            "intent": state.intent,
            "template": state.template,
            "review_feedback": state.review_feedback,
            "retry_count": state.retry_count,
        }
        result = call_json(llm, SYS_SCRIPT, payload)
        title = result.get("title", "")
        body = result.get("body") or []
        storyboard = result.get("storyboard") or []
        stages = result.get("stages") or []
        image_prompts = result.get("image_prompts") or []
        hashtags = result.get("hashtags") or []
        script = _render_markdown(title, content_type, body, storyboard, stages)

        state.trace(
            "script",
            "脚本/文案生成",
            {
                "content_type": content_type,
                "title": title,
                "storyboard_len": len(storyboard),
                "stages_len": len(stages),
                "retry": state.retry_count > 0,
            },
        )
        return {
            "title": title,
            "body": body,
            "storyboard": storyboard,
            "stages": stages,
            "script": script,
            "image_prompts": image_prompts,
            "hashtags": hashtags,
            "agent_trace": state.agent_trace,
        }

    return run
