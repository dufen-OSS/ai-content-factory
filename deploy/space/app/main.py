"""服务入口：uvicorn app.main:app"""
import logging

import uvicorn

from .api import create_app
from .config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = create_app()


if __name__ == "__main__":
    s = get_settings()
    uvicorn.run("app.main:app", host=s.app_host, port=s.app_port, reload=False)
