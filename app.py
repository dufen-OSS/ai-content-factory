"""AI 电商内容工厂 - 独立 Streamlit 应用（Streamlit Cloud 部署版）。

无需 FastAPI 后端：LangGraph 工作流在应用内直接运行。
LLM 配置：Streamlit Cloud 用 Secrets；本地用 .env / 环境变量。
"""
import os
import time

# ---- Streamlit Cloud Secrets -> 环境变量（供 app.config 读取）----
try:
    import streamlit as st  # noqa: E402

    _SECRET_TO_ENV = {
        "LLM_PROVIDER": "LLM_PROVIDER",
        "OPENAI_API_KEY": "OPENAI_API_KEY",
        "OPENAI_BASE_URL": "OPENAI_BASE_URL",
        "OPENAI_MODEL": "OPENAI_MODEL",
        "DEEPSEEK_API_KEY": "DEEPSEEK_API_KEY",
        "DEEPSEEK_BASE_URL": "DEEPSEEK_BASE_URL",
        "DEEPSEEK_MODEL": "DEEPSEEK_MODEL",
        "OLLAMA_BASE_URL": "OLLAMA_BASE_URL",
        "OLLAMA_MODEL": "OLLAMA_MODEL",
    }
    for sec_key, env_key in _SECRET_TO_ENV.items():
        if sec_key in st.secrets and env_key not in os.environ:
            os.environ[env_key] = str(st.secrets[sec_key])
except Exception:  # noqa: BLE001 - 本地无 streamlit/secrets 时忽略
    pass

from app.agents.state import ContentState, ProductInfo  # noqa: E402
from app.graph import run_deconstruct, run_generate  # noqa: E402
from app.llm import get_llm_client  # noqa: E402
from app.templates import list_templates  # noqa: E402

st.set_page_config(page_title="AI 电商内容工厂", page_icon="🏭", layout="wide")

PLATFORMS = ["auto", "抖音", "小红书", "快手", "视频号", "B站"]
CONTENT_TYPES = ["auto", "种草图文", "短视频脚本", "直播话术"]

st.sidebar.title("🏭 AI 电商内容工厂")
st.sidebar.caption("LangGraph 多 Agent 电商内容生成")


def build_state(product: dict, platform: str, content_type: str, deconstruct_text: str) -> ContentState:
    return ContentState(
        product=ProductInfo(
            name=product.get("name", ""),
            category=product.get("category", ""),
            selling_points=[str(x) for x in (product.get("selling_points") or [])],
            target_audience=product.get("target_audience", ""),
            price=product.get("price", ""),
            link=product.get("link", ""),
        ),
        platform=platform,
        content_type=content_type,
        deconstruct_text=deconstruct_text,
    )


tab_gen, tab_dec, tab_arch, tab_lib = st.tabs(["🎬 内容生成", "🧩 模板拆解", "🤖 Agent 架构", "📚 模板库"])

# ===================== 内容生成 =====================
with tab_gen:
    st.subheader("输入商品 → 多 Agent 协作 → 可发布内容")
    with st.form("gen_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("商品名称 *", placeholder="如：XX玻尿酸保湿面霜")
        with c2:
            category = st.text_input("商品品类", placeholder="如：护肤 / 数码 / 食品")
        with c3:
            price = st.text_input("参考价格", placeholder="如：129元/30ml")
        c4, c5 = st.columns(2)
        with c4:
            audience = st.text_input("目标人群", placeholder="如：25-35岁干皮女性")
        with c5:
            platform = st.selectbox("目标平台", PLATFORMS)
        content_type = st.selectbox("内容类型", CONTENT_TYPES)
        points = st.text_area("核心卖点（每行一个）", placeholder="深层补水\n成分温和\n性价比高", height=90)
        link = st.text_input("商品链接（可选）", placeholder="https://...")
        st.markdown("---")
        st.markdown("**可选：模板拆解驱动** — 粘贴竞品爆款文案，先生成会先拆模板再写稿")
        deconstruct_text = st.text_area("竞品爆款文案（可选）", height=80)
        submitted = st.form_submit_button("🚀 开始生成", type="primary")

    if submitted:
        if not name.strip():
            st.error("请至少填写商品名称")
        else:
            state = build_state(
                {"name": name, "category": category, "price": price,
                 "target_audience": audience, "link": link,
                 "selling_points": [x.strip() for x in points.splitlines() if x.strip()]},
                platform, content_type, deconstruct_text.strip(),
            )
            t0 = time.time()
            try:
                with st.spinner("多 Agent 正在协作生成（推理模型约需 60-120 秒）…"):
                    out = run_generate(state).to_output()
                elapsed = int((time.time() - t0) * 1000)
                provider = get_llm_client().name
                st.success(f"生成完成：5 个 Agent 参与，审核 {out['review']['retry_count']} 轮返修，耗时 {elapsed}ms（{provider}）")

                intent = out.get("intent", {})
                col_a, col_b = st.columns(2)
                col_a.metric("目标平台", intent.get("platform", "-"))
                col_b.metric("内容类型", intent.get("content_type", "-"))

                st.markdown("**📌 选题方向**")
                st.write(" / ".join(out.get("topics", [])))

                tpl = out.get("template", {})
                with st.expander("📐 使用的模板骨架", expanded=False):
                    st.markdown(f"**来源**: `{out.get('template_source')}` · **可抄骨架**: {tpl.get('framework', '-')}")
                    st.markdown(f"**标题公式**: {tpl.get('title_formula', '-')}")
                    st.markdown(f"**开头钩子**: {tpl.get('hook', '-')}")
                    st.markdown("**内容骨架**:")
                    for s in tpl.get("skeleton", []):
                        st.markdown(f"- {s}")
                    st.markdown(f"**收尾CTA**: {tpl.get('cta', '-')}")

                st.markdown("---")
                st.markdown("### 📝 成稿")
                st.markdown(out.get("script") or "_（无正文输出）_")

                st.markdown("### 🖼️ 配图提示词")
                for img in out.get("image_prompts", []):
                    st.markdown(f"- {img}")

                st.markdown("### #️⃣ 推荐标签")
                st.write(" ".join(out.get("hashtags", [])))

                st.markdown("---")
                review = out.get("review", {})
                if review.get("passed"):
                    st.success(f"✅ 审核通过：{'；'.join(review.get('feedback', []))}")
                else:
                    st.error(f"❌ 审核未通过（已返修 {review.get('retry_count', 0)} 轮）：{'；'.join(review.get('feedback', []))}")

                with st.expander("👁️ Agent 执行日志（可观测性）"):
                    for step in out.get("agent_trace", []):
                        st.markdown(f"**`{step.get('agent')}`** — {step.get('action')}")
                        st.code(step.get("result"), language="json")
            except Exception as e:  # noqa: BLE001
                st.error(f"生成失败：{e}")

# ===================== 模板拆解 =====================
with tab_dec:
    st.subheader("粘贴竞品爆款文案 → 拆解为可复用模板（七维表）")
    dec_text = st.text_area("竞品爆款文案", height=160, key="dec_text",
                            placeholder="把小红书/抖音上爆款文案整段粘贴过来…")
    dec_type = st.selectbox("目标内容类型", ["种草图文", "短视频脚本", "直播话术"], key="dec_type")
    if st.button("🧩 开始拆解", type="primary"):
        if not dec_text.strip():
            st.warning("请先粘贴爆款文案")
        else:
            t0 = time.time()
            try:
                with st.spinner("模板拆解 Agent 分析中（推理模型约需 20-60 秒）…"):
                    out = run_deconstruct(dec_text.strip(), dec_type)
                elapsed = int((time.time() - t0) * 1000)
                t = out.get("template", {})
                st.markdown(f"**可抄骨架（framework）**：{t.get('framework', '-')}")
                st.markdown(f"**标题公式**：{t.get('title_formula', '-')}")
                st.markdown(f"**开头钩子**：{t.get('hook', '-')}")
                st.markdown("**内容骨架**：")
                for i, s in enumerate(t.get("skeleton", []), 1):
                    st.markdown(f"{i}. {s}")
                st.markdown(f"**收尾CTA**：{t.get('cta', '-')}")
                st.markdown(f"**数据预估**：{t.get('data_estimate', '-')}")
                st.caption(f"拆解耗时 {elapsed}ms · {get_llm_client().name}")
            except Exception as e:  # noqa: BLE001
                st.error(f"拆解失败：{e}")

# ===================== Agent 架构 =====================
with tab_arch:
    st.subheader("5-Agent 协作架构（LangGraph 状态机）")
    st.markdown(
        """
```
        用户输入（商品信息 / 平台 / 类型 / 可选爆款文案）
                          │
                          ▼
             ┌──────────────────────────┐
             │ ① Supervisor 意图识别/路由 │
             └────────────┬─────────────┘
                          │
             ┌────────────▼─────────────┐
             │ ② 选题 Agent             │  生成 4 个差异化选题
             └────────────┬─────────────┘
                          │
             ┌────────────▼─────────────┐
             │ ③ 模板拆解 Agent         │  库内检索 / LLM 拆爆款→七维表
             └────────────┬─────────────┘
                          │
             ┌────────────▼─────────────┐
             │ ④ 脚本生成 Agent         │  模板骨架×商品卖点→成稿
             └────────────┬─────────────┘
                          │
             ┌────────────▼─────────────┐
             │ ⑤ 审核 Agent            │  广告法合规 + 完整性
             └──────┬────────────┬──────┘
                    │ 通过       │ 不通过（≤N 次）
                    ▼            ▼
                 交付成稿     返修→④脚本生成
```
"""
    )
    st.markdown(
        "**条件路由**：审核 Agent 返回 `review_passed`，不通过且未超返修上限时，"
        "LangGraph 条件边回跳脚本生成节点重新创作（携带 `review_feedback` 修正违禁词）。"
    )
    st.markdown(
        "**可观测性**：每个节点在共享状态 `agent_trace` 记录执行日志，界面可逐条展开查看中间产物。"
    )

# ===================== 模板库 =====================
with tab_lib:
    st.subheader("内置爆款模板库")
    for t in list_templates():
        with st.expander(f"[{t.get('platform')}] {t.get('content_type')} · {t.get('name')}"):
            st.markdown(f"**标题公式**：{t.get('title_formula')}")
            st.markdown(f"**开头钩子**：{t.get('hook')}")
            st.markdown("**内容骨架**：" + " → ".join(t.get("skeleton", [])))
            st.markdown(f"**收尾CTA**：{t.get('cta')}")
            st.markdown(f"**数据预估**：{t.get('data_estimate')}")
