#!/usr/bin/env bash
# 容器入口：后台起 FastAPI(8000)，前台起 Streamlit(7860)
set -e

uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

cleanup() { kill "$API_PID" 2>/dev/null || true; }
trap cleanup EXIT

# 前端指向本容器内后端
STREAMLIT_API_URL=http://127.0.0.1:8000 \
streamlit run frontend/app.py \
  --server.port 7860 \
  --server.address 0.0.0.0 \
  --server.headless true
