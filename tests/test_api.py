"""FastAPI 接口测试。

默认 Mock 引擎离线可跑；外部可用 LLM_PROVIDER=ollama pytest 切换真模型。
"""
import os

os.environ.setdefault("LLM_PROVIDER", "mock")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    # provider 随环境切换：mock / openai-compat / ollama 均合法
    assert body["llm_provider"] in ("mock", "openai-compat", "ollama")


def test_generate_endpoint():
    payload = {
        "product": {
            "name": "无线蓝牙耳机",
            "category": "数码",
            "selling_points": ["降噪出色", "续航30小时"],
            "target_audience": "通勤白领",
        },
        "platform": "抖音",
        "content_type": "短视频脚本",
    }
    r = client.post("/api/generate", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["intent"]["platform"] == "抖音"
    assert data["storyboard"], "短视频脚本应输出分镜"
    assert data["review"]["passed"] is True
    assert len(data["agent_trace"]) >= 5


def test_deconstruct_endpoint():
    r = client.post(
        "/api/deconstruct",
        json={"text": "买前必看！这5个坑我替你踩过了，第一条就劝退很多人", "content_type": "种草图文"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["template"]["framework"]


def test_templates_endpoint():
    r = client.get("/api/templates")
    assert r.status_code == 200
    assert len(r.json()["templates"]) >= 4
