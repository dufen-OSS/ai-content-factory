#!/usr/bin/env bash
# Render 启动脚本：后台起 FastAPI(8000)，前台起 Streamlit（监听 Render 注入的 $PORT）
set -e

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

cleanup() { kill "$API_PID" 2>/dev/null || true; }
trap cleanup EXIT

PORT="${PORT:-8501}"
STREAMLIT_API_URL=http://127.0.0.1:8000 \
streamlit run frontend/app.py \
  --server.port "$PORT" \
  --server.address 0.0.0.0 \
  --server.headless true
