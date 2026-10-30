import asyncio
import hashlib
import json
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

# Where the cached image lives on disk. Point this at a mounted volume in Docker/K8s.
CACHE_DIR = Path(os.getenv("CACHE_DIR", Path(__file__).parent / "cache"))
IMAGE_FILE = CACHE_DIR / "image.bin"
META_FILE = CACHE_DIR / "meta.json"

# In-memory copy of the cached image. expires_at is wall-clock time (time.time())
# because time.monotonic() is meaningless after a restart.
_cache: dict = {
    "body": None,
    "content_type": "image/jpeg",
    "etag": None,
    "expires_at": 0.0,
}
_lock = asyncio.Lock()  # prevents several requests refetching at once


def _atomic_write(path: Path, data: bytes) -> None:
    """Write to a temp file, then rename, so readers never see a half-written file."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _save_to_disk() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_write(IMAGE_FILE, _cache["body"])
    meta = {
        "content_type": _cache["content_type"],
        "expires_at": _cache["expires_at"],
    }
    _atomic_write(META_FILE, json.dumps(meta).encode())


def _load_from_disk() -> None:
    try:
        body = IMAGE_FILE.read_bytes()
        meta = json.loads(META_FILE.read_text())
        _cache["body"] = body
        _cache["content_type"] = meta["content_type"]
        _cache["expires_at"] = float(meta["expires_at"])
        _cache["etag"] = f'"{hashlib.sha1(body).hexdigest()}"'
        logger.info("Loaded cached image from %s", IMAGE_FILE)
    except FileNotFoundError:
        logger.info("No cached image on disk yet")
    except (OSError, ValueError, KeyError) as exc:
        logger.warning("Ignoring unreadable cache on disk: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_from_disk()
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
    _cache["expires_at"] = time.time() + TTL_SECONDS
    try:
        await asyncio.to_thread(_save_to_disk)  # keep file IO off the event loop
    except OSError as exc:
        # Disk problems shouldn't break serving; the in-memory copy still works.
        logger.warning("Could not write cache to disk: %s", exc)


@app.get("/api/image")
async def get_image(request: Request) -> Response:
    async with _lock:
        if _cache["body"] is None or time.time() >= _cache["expires_at"]:
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