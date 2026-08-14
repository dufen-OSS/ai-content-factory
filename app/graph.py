"""LangGraph 多 Agent 工作流。

Supervisor -> 选题 -> 模板拆解 -> 脚本生成 -> 审核（不通过则返修，最多 N 次）。

条件路由示例：review 节点输出 review_passed / retry_count，
decide_review 决定回跳 script（返修）还是结束。
"""
import logging

from langgraph.graph import END, START, StateGraph

from .agents.deconstruct import make_deconstruct
from .agents.review import make_review
from .agents.script import make_script
from .agents.state import ContentState
from .agents.supervisor import make_supervisor
from .agents.topic import make_topic
from .config import get_settings
from .llm import get_llm_client

logger = logging.getLogger(__name__)


def _decide_review(state: ContentState) -> str:
    max_retries = get_settings().max_review_retries
    if not state.review_passed and state.retry_count <= max_retries:
        return "revise"
    return "pass"


def build_graph():
    """构造并编译 5-Agent 工作流。"""
    llm = get_llm_client()

    g = StateGraph(ContentState)
    g.add_node("supervisor", make_supervisor(llm))
    g.add_node("topic", make_topic(llm))
    g.add_node("deconstruct", make_deconstruct(llm))
    g.add_node("script", make_script(llm))
    g.add_node("review", make_review(llm))

    g.add_edge(START, "supervisor")
    g.add_edge("supervisor", "topic")
    g.add_edge("topic", "deconstruct")
    g.add_edge("deconstruct", "script")
    g.add_edge("script", "review")
    g.add_conditional_edges(
        "review",
        _decide_review,
        {"revise": "script", "pass": END},
    )
    return g.compile()


def run_generate(state: ContentState) -> ContentState:
    """执行完整生成链路（langgraph 1.x invoke 返回 dict，需还原为状态模型）。"""
    graph = build_graph()
    result = graph.invoke(state)
    return ContentState(**result)


def run_deconstruct(text: str, content_type: str = "种草图文") -> dict:
    """只执行模板拆解 Agent：粘贴竞品爆款文案 -> 七维表结构。"""
    llm = get_llm_client()
    state = ContentState(
        deconstruct_text=text,
        intent={"platform": "", "content_type": content_type},
    )
    result = make_deconstruct(llm)(state)
    return {
        "template": result["template"],
        "template_source": result["template_source"],
        "agent_trace": result["agent_trace"],
    }
