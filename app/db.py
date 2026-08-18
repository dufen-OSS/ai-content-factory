"""SQLite 持久化层：任务表 + 内容表。

- WAL 模式，支持多线程并发读写（配合模块级锁）。
- 数据文件位于项目 data/content_factory.db（已 gitignore）。
"""
import json
import sqlite3
import threading
import time
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "content_factory.db"
_lock = threading.Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    payload TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    error TEXT
);
CREATE TABLE IF NOT EXISTS contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    title TEXT DEFAULT '',
    script TEXT DEFAULT '',
    body TEXT DEFAULT '',
    storyboard TEXT DEFAULT '',
    stages TEXT DEFAULT '',
    image_prompts TEXT DEFAULT '',
    hashtags TEXT DEFAULT '',
    template_source TEXT DEFAULT '',
    review_passed INTEGER,
    review_feedback TEXT DEFAULT '',
    agent_trace TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_batch ON tasks(batch_id);
"""


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def init_db() -> None:
    with _lock:
        conn = _connect()
        try:
            conn.executescript(_SCHEMA)
            conn.commit()
        finally:
            conn.close()


# ---------------- tasks ----------------
def insert_task(batch_id: str, product_name: str, payload: dict) -> int:
    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(
                "INSERT INTO tasks(batch_id, product_name, payload, status, created_at) VALUES(?,?,?,?,?)",
                (batch_id, product_name, json.dumps(payload, ensure_ascii=False), "pending", now()),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def update_task(task_id: int, status: str = None, started_at: str = None,
                finished_at: str = None, error: str = None) -> None:
    fields, vals = [], []
    for col, val in (("status", status), ("started_at", started_at),
                     ("finished_at", finished_at), ("error", error)):
        if val is not None:
            fields.append(f"{col}=?")
            vals.append(val)
    if not fields:
        return
    vals.append(task_id)
    with _lock:
        conn = _connect()
        try:
            conn.execute(f"UPDATE tasks SET {','.join(fields)} WHERE id=?", vals)
            conn.commit()
        finally:
            conn.close()


def get_tasks_by_batch(batch_id: str) -> list:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM tasks WHERE batch_id=? ORDER BY id", (batch_id,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def list_batches(limit: int = 20) -> list:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT batch_id,
                   COUNT(*) AS total,
                   SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done,
                   SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed,
                   SUM(CASE WHEN status IN ('pending','running') THEN 1 ELSE 0 END) AS pending,
                   MIN(created_at) AS created_at
            FROM tasks
            GROUP BY batch_id
            ORDER BY MAX(id) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ---------------- contents ----------------
def insert_content(task_id: int, out: dict, created_at: str) -> int:
    with _lock:
        conn = _connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO contents(
                    task_id, title, script, body, storyboard, stages,
                    image_prompts, hashtags, template_source,
                    review_passed, review_feedback, agent_trace, created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    task_id,
                    out.get("title", ""),
                    out.get("script", ""),
                    json.dumps(out.get("body", []), ensure_ascii=False),
                    json.dumps(out.get("storyboard", []), ensure_ascii=False),
                    json.dumps(out.get("stages", []), ensure_ascii=False),
                    json.dumps(out.get("image_prompts", []), ensure_ascii=False),
                    json.dumps(out.get("hashtags", []), ensure_ascii=False),
                    out.get("template_source", ""),
                    1 if out.get("review", {}).get("passed") else 0,
                    json.dumps(out.get("review", {}).get("feedback", []), ensure_ascii=False),
                    json.dumps(out.get("agent_trace", []), ensure_ascii=False),
                    created_at,
                ),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def get_content_by_task(task_id: int) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM contents WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            return None
        r = dict(row)
        # 还原 JSON 字段
        for key in ("body", "storyboard", "stages", "image_prompts", "hashtags",
                    "review_feedback", "agent_trace"):
            try:
                r[key] = json.loads(r.get(key) or "[]")
            except json.JSONDecodeError:
                r[key] = []
        return r
    finally:
        conn.close()
