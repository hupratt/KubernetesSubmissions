# app, lifespan, /health, includes routers, static mount
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import image, todos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("UVICORN_PORT", "8000"))
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    image.load_from_disk()
    logger.info("Server started on port %s", PORT)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(image.router)
app.include_router(todos.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Must stay LAST: a mount at "/" matches every path registered after it.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    logger.warning("No static dir at %s; frontend not served", STATIC_DIR)