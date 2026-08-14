"""Ollama 真模型端到端验证脚本（临时）。"""
import json
import os
import time

os.environ["LLM_PROVIDER"] = "ollama"

from app.agents.state import ContentState, ProductInfo  # noqa: E402
from app.graph import run_deconstruct, run_generate  # noqa: E402
from app.llm import get_llm_client  # noqa: E402


def main():
    llm = get_llm_client()
    print(f"[provider] {llm.name}")

    # ---------- 生成链路 ----------
    product = ProductInfo(
        name="XX玻尿酸保湿面霜",
        category="护肤",
        selling_points=["深层补水", "成分温和", "性价比高"],
        target_audience="25-35岁干皮女性",
        price="129元/30ml",
    )
    state = ContentState(product=product, platform="auto", content_type="auto")
    t0 = time.perf_counter()
    out = run_generate(state)
    print(f"[generate] elapsed={time.perf_counter()-t0:.1f}s")
    print(f"[intent] {out.intent}")
    print(f"[topics] {json.dumps(out.topics, ensure_ascii=False)}")
    print(f"[template_source] {out.template_source} | framework={out.template.get('framework','')}")
    print(f"[title] {out.title}")
    print(f"[review] passed={out.review_passed} retry={out.retry_count}")
    print(f"[feedback] {json.dumps(out.review_feedback, ensure_ascii=False)}")
    print(f"[agents] {[t['agent'] for t in out.agent_trace]}")
    print(f"[image_prompts] {len(out.image_prompts)} | [hashtags] {json.dumps(out.hashtags, ensure_ascii=False)}")
    print("===== script =====")
    print(out.script[:1500])

    # ---------- 模板拆解 ----------
    text = "干皮救星！这个面霜我用了7天真的会谢，睡前涂一层第二天脸嫩到发光。质地像冰淇淋一抹就化开，不闷痘不搓泥，敏感肌也友好，链接放这了先收藏再买！"
    t0 = time.perf_counter()
    dec = run_deconstruct(text, "种草图文")
    print(f"\n[deconstruct] elapsed={time.perf_counter()-t0:.1f}s source={dec['template_source']}")
    for k, v in dec["template"].items():
        if k == "skeleton":
            print(f"  skeleton({len(v)}):")
            for s in v:
                print(f"    - {s}")
        else:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
