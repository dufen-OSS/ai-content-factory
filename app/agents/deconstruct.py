"""模板拆解 Agent（核心卖点）。

两种路径：
1. 库内检索：按 平台+内容类型+品类 从爆款模板库选择最匹配模板；
2. LLM 拆解：用户粘贴竞品爆款文案，现场拆出七维表结构。
"""
from ..llm.call import call_json
from ..templates import select_template
from .prompts import SYS_DECONSTRUCT
from .state import ContentState


def make_deconstruct(llm):
    def run(state: ContentState) -> dict:
        platform = state.intent.get("platform", "")
        content_type = state.intent.get("content_type", "")
        category = state.product.category

        if state.deconstruct_text.strip():
            # 路径 2：现场拆解爆款文案
            payload = {
                "task": "deconstruct",
                "text": state.deconstruct_text[:3000],
                "content_type": content_type,
            }
            result = call_json(llm, SYS_DECONSTRUCT, payload)
            template = result.get("template") or {}
            template["framework"] = template.get("framework", "LLM 现场拆解的可抄骨架")
            source = "llm"
            note = "基于用户提供的竞品文案拆解"
        else:
            # 路径 1：库内检索
            template = select_template(platform, content_type, category) or {}
            source = "library"
            note = f"从模板库匹配：{template.get('name', '通用')}"

        state.trace(
            "deconstruct",
            "模板拆解/检索",
            {
                "source": source,
                "framework": template.get("framework", ""),
                "skeleton_len": len(template.get("skeleton", [])),
                "note": note,
            },
        )
        return {
            "template": template,
            "template_source": source,
            "agent_trace": state.agent_trace,
        }

    return run
