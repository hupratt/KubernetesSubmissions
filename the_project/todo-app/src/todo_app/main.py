import logging
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PORT = int(os.getenv("PORT", "8000"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server started in port %s", PORT)
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")
def homepage():
    return {"message": "Hello, world!"}

@app.get("/health")
def health():
    return {"status": "ok"}