"""批量任务调度：SQLite 持久化的任务队列 + 线程池并发执行。

- create_batch: 批量建任务（status=pending 落库）
- run_batch: 线程池并发处理，进度回调，结果写入 contents 表
- 查询: list_batches / get_tasks_by_batch / get_content_by_task
"""
import json
import uuid
from concurrent.futures import ThreadPoolExecutor

from . import db
from .agents.state import ContentState, ProductInfo
from .graph import run_generate


def build_state(product: dict, platform: str, content_type: str) -> ContentState:
    return ContentState(
        product=ProductInfo(
            name=str(product.get("name", "")),
            category=str(product.get("category", "")),
            selling_points=[str(x) for x in (product.get("selling_points") or [])],
            target_audience=str(product.get("target_audience", "")),
            price=str(product.get("price", "")),
            link=str(product.get("link", "")),
        ),
        platform=platform,
        content_type=content_type,
        deconstruct_text="",
    )


class TaskManager:
    def __init__(self) -> None:
        db.init_db()

    # ---------------- 调度 ----------------
    def create_batch(self, products: list[dict], platform: str, content_type: str) -> str:
        """为每个商品创建一个任务，返回 batch_id。"""
        batch_id = uuid.uuid4().hex[:12]
        for p in products:
            db.insert_task(
                batch_id,
                p.get("name", "未命名商品"),
                {"product": p, "platform": platform, "content_type": content_type},
            )
        return batch_id

    def run_batch(self, batch_id: str, max_workers: int = 2,
                  progress_cb=None) -> dict:
        """线程池并发执行批内任务；结果落库；进度通过回调上报。"""
        tasks = db.get_tasks_by_batch(batch_id)
        total = len(tasks)
        done = 0

        def _work(task: dict):
            payload = json.loads(task["payload"])
            db.update_task(task["id"], status="running", started_at=db.now())
            try:
                state = build_state(payload["product"], payload["platform"], payload["content_type"])
                out = run_generate(state).to_output()
                db.insert_content(task["id"], out, db.now())
                db.update_task(task["id"], status="done", finished_at=db.now())
            except Exception as e:  # noqa: BLE001
                db.update_task(task["id"], status="failed", finished_at=db.now(), error=str(e))

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            for _ in ex.map(_work, tasks):
                done += 1
                if progress_cb:
                    progress_cb(done, total)
        return {"total": total, "done": done}

    # ---------------- 查询 ----------------
    def list_batches(self, limit: int = 20):
        return db.list_batches(limit)

    def get_tasks(self, batch_id: str):
        return db.get_tasks_by_batch(batch_id)

    def get_content(self, task_id: int):
        return db.get_content_by_task(task_id)
