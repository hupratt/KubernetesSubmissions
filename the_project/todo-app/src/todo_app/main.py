import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import db, events, image, todos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("UVICORN_PORT", "8000"))
STATIC_DIR = Path(__file__).parent / "static"

# Flipped by POST /api/break. Lives in process memory, so a restart resets it.
is_healthy = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.pool.open(wait=True, timeout=30)
    db.init_schema()
    image.load_from_disk()
    await events.connect()
    logger.info("Server started on port %s", PORT)
    yield
    await events.close()
    db.pool.close()


app = FastAPI(lifespan=lifespan)

app.include_router(image.router)
app.include_router(todos.router)


@app.get("/healthz")
def healthz():
    """Liveness: is this process OK? Deliberately does not touch the DB."""
    if not is_healthy:
        return JSONResponse({"status": "unhealthy"}, status_code=500)
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness: healthy AND able to reach the database."""
    if not is_healthy:
        return JSONResponse({"status": "unhealthy"}, status_code=503)
    try:
        with db.pool.connection(timeout=2) as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Readiness check failed: %s", exc)
        return JSONResponse({"status": "database unavailable"}, status_code=503)
    return {"status": "ok"}


@app.post("/api/break")
def break_app():
    global is_healthy
    is_healthy = False
    logger.error("App deliberately broken; liveness probe will now fail")
    return {"status": "broken"}


# Must stay LAST: a mount at "/" matches every path registered after it.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    logger.warning("No static dir at %s; frontend not served", STATIC_DIR)