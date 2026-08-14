"""FastAPI 后端：生成 / 拆解 / 模板列表 / 健康检查。"""
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agents.state import ContentState, ProductInfo
from .graph import run_deconstruct, run_generate
from .llm import get_llm_client
from .templates import list_templates


class GenerateRequest(BaseModel):
    product: dict = Field(default_factory=dict)
    platform: str = "auto"
    content_type: str = "auto"
    deconstruct_text: str = ""


class DeconstructRequest(BaseModel):
    text: str
    content_type: str = "种草图文"


def _build_state(req: GenerateRequest) -> ContentState:
    p = req.product or {}
    product = ProductInfo(
        name=str(p.get("name", "")),
        category=str(p.get("category", "")),
        selling_points=[str(x) for x in (p.get("selling_points") or []) if x],
        target_audience=str(p.get("target_audience", "")),
        price=str(p.get("price", "")),
        link=str(p.get("link", "")),
    )
    return ContentState(
        product=product,
        platform=req.platform,
        content_type=req.content_type,
        deconstruct_text=req.deconstruct_text,
    )


def create_app() -> FastAPI:
    app = FastAPI(title="AI 电商内容工厂", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        return {"status": "ok", "llm_provider": get_llm_client().name}

    @app.post("/api/generate")
    def generate(req: GenerateRequest):
        t0 = time.perf_counter()
        state = run_generate(_build_state(req))
        out = state.to_output()
        out["meta"] = {
            "elapsed_ms": round((time.perf_counter() - t0) * 1000),
            "llm_provider": get_llm_client().name,
            "agent_count": len(out["agent_trace"]),
            "review_rounds": state.retry_count,
        }
        return out

    @app.post("/api/deconstruct")
    def deconstruct(req: DeconstructRequest):
        t0 = time.perf_counter()
        result = run_deconstruct(req.text, req.content_type)
        result["meta"] = {
            "elapsed_ms": round((time.perf_counter() - t0) * 1000),
            "llm_provider": get_llm_client().name,
        }
        return result

    @app.get("/api/templates")
    def templates():
        return {"templates": list_templates()}

    return app
