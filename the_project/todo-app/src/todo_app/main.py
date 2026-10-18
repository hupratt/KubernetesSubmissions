import logging
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PORT = int(os.getenv("UVICORN_PORT", "8000"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server started in port %s", PORT)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}