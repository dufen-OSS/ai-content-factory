"""AI 电商内容工厂 - Streamlit 演示界面。

运行: streamlit run frontend/app.py
依赖后端: uvicorn app.main:app (默认 http://localhost:8000，可在侧边栏改)
"""
import os

import requests
import streamlit as st

st.set_page_config(page_title="AI 电商内容工厂", page_icon="🏭", layout="wide")

API_BASE = os.environ.get("STREAMLIT_API_URL", "http://localhost:8000").rstrip("/")

PLATFORMS = ["auto", "抖音", "小红书", "快手", "视频号", "B站"]
CONTENT_TYPES = ["auto", "种草图文", "短视频脚本", "直播话术"]

st.sidebar.title("🏭 AI 电商内容工厂")
st.sidebar.caption("LangGraph 多 Agent 电商内容生成 Demo")


def api_url(path: str) -> str:
    return f"{API_BASE}{path}"


def post_json(path: str, payload: dict) -> dict:
    resp = requests.post(api_url(path), json=payload, timeout=180)
    resp.raise_for_status()
    return resp.json()


@st.cache_data(ttl=60)
def fetch_templates():
    return requests.get(api_url("/api/templates"), timeout=30).json().get("templates", [])


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
            price = st.text_input("参考价格", placeholder="如：¥129/30ml")
        c4, c5 = st.columns(2)
        with c4:
            audience = st.text_input("目标人群", placeholder="如：25-35岁干皮女性")
        with c5:
            platform = st.selectbox("目标平台", PLATFORMS)
        content_type = st.selectbox("内容类型", CONTENT_TYPES)
        points = st.text_area("核心卖点（每行一个）", placeholder="补水保湿\n成分温和\n性价比高", height=90)
        link = st.text_input("商品链接（可选）", placeholder="https://...")
        st.markdown("---")
        st.markdown("**可选：模板拆解驱动** — 粘贴一段竞品爆款文案，生成会先按它拆解出模板再写稿")
        deconstruct_text = st.text_area("竞品爆款文案（可选）", height=80)
        submitted = st.form_submit_button("🚀 开始生成", type="primary")

    if submitted:
        if not name.strip():
            st.error("请至少填写商品名称")
        else:
            payload = {
                "product": {
                    "name": name.strip(),
                    "category": category.strip(),
                    "price": price.strip(),
                    "target_audience": audience.strip(),
                    "link": link.strip(),
                    "selling_points": [x.strip() for x in points.splitlines() if x.strip()],
                },
                "platform": platform,
                "content_type": content_type,
                "deconstruct_text": deconstruct_text.strip(),
            }
            try:
                with st.spinner("多 Agent 正在协作生成…"):
                    out = post_json("/api/generate", payload)
                meta = out.get("meta", {})
                st.success(f"生成完成：{meta.get('agent_count', '-')} 个 Agent 参与，审核 {meta.get('review_rounds', 0)} 轮，耗时 {meta.get('elapsed_ms', '-')}ms（{meta.get('llm_provider')}）")

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
                st.error(f"调用后端失败：{e}")

# ===================== 模板拆解 =====================
with tab_dec:
    st.subheader("粘贴竞品爆款文案 → 拆解为可复用模板（七维表）")
    dec_text = st.text_area(
        "竞品爆款文案",
        height=160,
        placeholder="把小红书/抖音上爆款文案整段粘贴过来…",
        key="dec_text",
    )
    dec_type = st.selectbox("目标内容类型", ["种草图文", "短视频脚本", "直播话术"], key="dec_type")
    if st.button("🧩 开始拆解", type="primary"):
        if not dec_text.strip():
            st.warning("请先粘贴爆款文案")
        else:
            try:
                with st.spinner("模板拆解 Agent 分析中…"):
                    out = post_json("/api/deconstruct", {"text": dec_text.strip(), "content_type": dec_type})
                t = out.get("template", {})
                st.markdown(f"**可抄骨架（framework）**：{t.get('framework', '-')}")
                st.markdown(f"**标题公式**：{t.get('title_formula', '-')}")
                st.markdown(f"**开头钩子**：{t.get('hook', '-')}")
                st.markdown("**内容骨架**：")
                for i, s in enumerate(t.get("skeleton", []), 1):
                    st.markdown(f"{i}. {s}")
                st.markdown(f"**收尾CTA**：{t.get('cta', '-')}")
                st.markdown(f"**数据预估**：{t.get('data_estimate', '-')}")
                st.caption(f"拆解耗时 {out.get('meta', {}).get('elapsed_ms', '-')}ms · {out.get('meta', {}).get('llm_provider')}")
            except Exception as e:  # noqa: BLE001
                st.error(f"调用后端失败：{e}")

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
        "**条件路由**：审核 Agent 返回 `review_passed`，不通过且未超返修上限时，LangGraph 条件边回跳脚本生成节点重新创作（携带 `review_feedback` 修正违禁词）。"
    )
    st.markdown(
        "**可观测性**：每个节点在共享状态 `agent_trace` 记录执行日志，界面可逐条展开查看中间产物——这是面试中展示 Agent 架构能力的核心证据。"
    )

# ===================== 模板库 =====================
with tab_lib:
    st.subheader("内置爆款模板库")
    try:
        for t in fetch_templates():
            with st.expander(f"[{t.get('platform')}] {t.get('content_type')} · {t.get('name')}"):
                st.markdown(f"**标题公式**：{t.get('title_formula')}")
                st.markdown(f"**开头钩子**：{t.get('hook')}")
                st.markdown("**内容骨架**：" + " → ".join(t.get("skeleton", [])))
                st.markdown(f"**收尾CTA**：{t.get('cta')}")
                st.markdown(f"**数据预估**：{t.get('data_estimate')}")
    except Exception as e:  # noqa: BLE001
        st.error(f"获取模板库失败：{e}")
