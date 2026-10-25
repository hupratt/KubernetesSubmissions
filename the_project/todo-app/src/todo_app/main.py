import asyncio
import hashlib
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PORT = int(os.getenv("UVICORN_PORT", "8000"))
PICSUM_URL = "https://picsum.photos/1200"
TTL_SECONDS = 600  # 10 minutes
STATIC_DIR = Path(__file__).parent / "static"

# Single cached image: bytes, content type, ETag, and monotonic expiry time.
_cache: dict = {
    "body": None,
    "content_type": "image/jpeg",
    "etag": None,
    "expires_at": 0.0,
}
_lock = asyncio.Lock()  # prevents several requests refetching at once


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server started on port %s", PORT)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


async def _refresh() -> None:
    async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
        r = await client.get(PICSUM_URL)
        r.raise_for_status()
    _cache["body"] = r.content
    _cache["content_type"] = r.headers.get("content-type", "image/jpeg")
    _cache["etag"] = f'"{hashlib.sha1(r.content).hexdigest()}"'
    _cache["expires_at"] = time.monotonic() + TTL_SECONDS


@app.get("/api/image")
async def get_image(request: Request) -> Response:
    async with _lock:
        if _cache["body"] is None or time.monotonic() >= _cache["expires_at"]:
            try:
                await _refresh()
            except httpx.HTTPError:
                # Serve the stale image if Picsum is down; fail only if we have nothing.
                if _cache["body"] is None:
                    raise HTTPException(status_code=502, detail="Could not fetch image")

        body = _cache["body"]
        content_type = _cache["content_type"]
        etag = _cache["etag"]

    # no-cache = browser must revalidate every time; the ETag makes that cheap
    # and means the browser can never hold an image longer than the server does.
    headers = {"Cache-Control": "no-cache", "ETag": etag}

    if request.headers.get("if-none-match") == etag:
        return Response(status_code=304, headers=headers)

    return Response(content=body, media_type=content_type, headers=headers)


# Must stay LAST: a mount at "/" matches every path registered after it.
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    logger.warning("No static dir at %s; frontend not served", STATIC_DIR)