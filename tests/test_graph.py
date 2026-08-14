"""5-Agent 工作流端到端测试。

默认 Mock 引擎离线可跑；外部可用 LLM_PROVIDER=ollama pytest 切换真模型。
"""
import os

os.environ.setdefault("LLM_PROVIDER", "mock")

from app.agents.state import ContentState, ProductInfo  # noqa: E402
from app.graph import build_graph, run_deconstruct, run_generate  # noqa: E402
from app.templates import select_template  # noqa: E402

PRODUCT = ProductInfo(
    name="XX玻尿酸保湿面霜",
    category="护肤",
    selling_points=["深层补水", "成分温和", "性价比高"],
    target_audience="25-35岁干皮女性",
    price="¥129/30ml",
)


def test_template_library_selection():
    t = select_template("小红书", "种草图文", "护肤")
    assert t is not None
    assert t["platform"] == "小红书"
    assert "skeleton" in t and len(t["skeleton"]) > 0


def test_generate_full_flow_mock():
    state = ContentState(product=PRODUCT, platform="auto", content_type="auto")
    out = run_generate(state)
    agents = [s["agent"] for s in out.agent_trace]
    # 5 个 Agent 都必须执行
    assert "supervisor" in agents
    assert "topic" in agents
    assert "deconstruct" in agents
    assert "script" in agents
    assert "review" in agents
    # 有产出
    assert out.intent.get("platform") in ("小红书", "抖音", "快手", "视频号", "B站")
    assert out.topics, "选题不能为空"
    assert out.script and out.title, "成稿不能为空"
    assert out.image_prompts and out.hashtags
    # 正常路径审核通过
    assert out.review_passed is True


def test_review_retry_loop_triggers():
    """卖点含违禁词时，审核失败 -> 返修 -> 最终通过或收敛。"""
    product = ProductInfo(
        name="全网最低价面霜",
        category="护肤",
        selling_points=["全网最低价", "绝对好用"],
        target_audience="学生党",
    )
    state = ContentState(product=product, content_type="种草图文")
    out = run_generate(state)
    # 返修逻辑：要么最终通过，要么在达上限后停止（retry_count 有界）
    assert out.retry_count <= 3
    # 若返修生效，最终文案不再含原违禁词
    assert "全网最低价" not in out.script


def test_deconstruct_only():
    out = run_deconstruct("干皮救星！这个面霜我用了7天真的会谢，睡前涂一层第二天脸嫩到发光", "种草图文")
    t = out["template"]
    assert t.get("framework")
    assert t.get("title_formula")
    assert t.get("hook")
    assert len(t.get("skeleton", [])) >= 3
    assert out["template_source"] == "llm"
