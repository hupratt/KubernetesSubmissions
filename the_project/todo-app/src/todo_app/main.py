import logging
import os
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import httpx
from fastapi import FastAPI, HTTPException, Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PORT = int(os.getenv("UVICORN_PORT", "8000"))
PICSUM_URL = "https://picsum.photos/1200"
TTL_SECONDS = 600  # 10 minutes

# Single cached image: bytes, content type, and monotonic expiry time.
_cache: dict = {"body": None, "content_type": "image/jpeg", "expires_at": 0.0}
_lock = asyncio.Lock()  # prevents several requests refetching at once

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server started in port %s", PORT)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}


async def _refresh() -> None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        r = await client.get(PICSUM_URL)
        r.raise_for_status()
    _cache["body"] = r.content
    _cache["content_type"] = r.headers.get("content-type", "image/jpeg")
    _cache["expires_at"] = time.monotonic() + TTL_SECONDS


@app.get("/api/image")
async def get_image() -> Response:
    async with _lock:
        if _cache["body"] is None or time.monotonic() >= _cache["expires_at"]:
            try:
                await _refresh()
            except httpx.HTTPError:
                # Serve the stale image if Picsum is down; fail only if we have nothing.
                if _cache["body"] is None:
                    raise HTTPException(status_code=502, detail="Could not fetch image")

        remaining = max(0, int(_cache["expires_at"] - time.monotonic()))
        body, content_type = _cache["body"], _cache["content_type"]

    return Response(
        content=body,
        media_type=content_type,
        # Lets the browser keep the same image until the server-side cache expires.
        headers={"Cache-Control": f"public, max-age={remaining}"},
    )
