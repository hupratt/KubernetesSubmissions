"""Publishes todo events to NATS. Failures are logged, never raised:
a broken message bus must not break saving todos."""
import json
import logging
import os
from datetime import datetime, timezone

import nats
from nats.aio.client import Client as NATS

logger = logging.getLogger(__name__)

NATS_URL = os.getenv(
    "NATS_URL", "nats://my-nats-0.my-nats-headless.nats.svc.cluster.local:4222"
)
NATS_SUBJECT = os.getenv("NATS_SUBJECT", "todos.events")

_nc: NATS | None = None


async def connect() -> None:
    """Called from main.py's lifespan. Does not fail startup if NATS is down;
    nats-py keeps retrying in the background."""
    global _nc
    try:
        _nc = await nats.connect(
            NATS_URL,
            name="todo-backend",
            connect_timeout=3,
            max_reconnect_attempts=-1,   # reconnect forever
            allow_reconnect=True,
        )
        logger.info("Connected to NATS at %s", NATS_URL)
    except Exception as exc:
        logger.warning("Could not connect to NATS at startup: %s", exc)
        _nc = None


async def close() -> None:
    if _nc is not None and not _nc.is_closed:
        await _nc.drain()


async def publish(event: str, todo: dict) -> None:
    """event is 'created' or 'updated'; todo is the row dict (id, text, done)."""
    if _nc is None or not _nc.is_connected:
        logger.warning("NATS not connected; dropping %s event for todo %s", event, todo.get("id"))
        return
    payload = {
        "event": event,
        "todo": {"id": todo["id"], "text": todo["text"], "done": todo["done"]},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await _nc.publish(NATS_SUBJECT, json.dumps(payload).encode())
        logger.info("Published %s event for todo %s", event, todo["id"])
    except Exception as exc:
        logger.warning("Failed to publish NATS message: %s", exc)
