# Hugging Face Space 部署镜像：一个容器内同时运行 FastAPI + Streamlit
# 前端监听 7860（HF 要求），后端监听 8000（仅容器内访问）
FROM python:3.13-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 依赖（含 FastAPI + LangGraph + Streamlit）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 业务代码（由 deploy/sync.sh 同步）
COPY app ./app
COPY frontend ./frontend
COPY start.sh ./start.sh
RUN chmod +x start.sh

# 默认 Mock 兜底（零成本离线）；切 DeepSeek 用 Space 环境变量覆盖
ENV LLM_PROVIDER=mock \
    LLM_TIMEOUT=120 \
    MAX_REVIEW_RETRIES=2

EXPOSE 7860
ENTRYPOINT ["./start.sh"]
