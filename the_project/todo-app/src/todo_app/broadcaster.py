"""Subscribes to todo events on NATS and forwards them to a Discord webhook."""
import asyncio
import json
import logging
import os
import signal

import httpx
import nats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcaster")

NATS_URL = os.getenv(
    "NATS_URL", "nats://my-nats-0.my-nats-headless.nats.svc.cluster.local:4222"
)
NATS_SUBJECT = os.getenv("NATS_SUBJECT", "todos.events")
# Queue group: with several replicas, each message is delivered to only ONE of
# them, so Discord doesn't get duplicates.
QUEUE_GROUP = os.getenv("NATS_QUEUE", "broadcaster")
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]  # required; from a Secret

COLORS = {"created": 0x2ECC71, "updated": 0x3498DB}  # green / blue
MAX_RETRIES = 3


def to_discord(event: dict) -> dict:
    """Translate our event into Discord's webhook format (an embed)."""
    kind = event["event"]
    todo = event["todo"]
    status = "✅ done" if todo["done"] else "⬜ not done"
    return {
        "username": "Todo Broadcaster",
        # Never let todo text ping @everyone, roles or users.
        "allowed_mentions": {"parse": []},
        "embeds": [
            {
                "title": f"Todo {kind}",
                # Embed descriptions allow 4096 chars; todos are max 140.
                "description": todo["text"],
                "color": COLORS.get(kind, 0x95A5A6),
                "fields": [
                    {"name": "ID", "value": str(todo["id"]), "inline": True},
                    {"name": "Status", "value": status, "inline": True},
                ],
                "timestamp": event.get("timestamp"),
            }
        ],
    }


async def send_to_discord(client: httpx.AsyncClient, body: dict) -> None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = await client.post(DISCORD_WEBHOOK_URL, json=body)
            if r.status_code == 429:  # rate limited; Discord says how long to wait
                wait = float(r.json().get("retry_after", 1))
                logger.warning("Discord rate limit, retrying in %.1fs", wait)
                await asyncio.sleep(wait)
                continue
            r.raise_for_status()
            return
        except httpx.HTTPError as exc:
            logger.warning("Discord send failed (attempt %d/%d): %s", attempt, MAX_RETRIES, exc)
            await asyncio.sleep(2 ** attempt)
    logger.error("Giving up on message after %d attempts", MAX_RETRIES)


async def main() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    async with httpx.AsyncClient(timeout=10) as http:

        async def handler(msg) -> None:
            try:
                event = json.loads(msg.data)
                body = to_discord(event)
            except (ValueError, KeyError, TypeError) as exc:
                logger.warning("Ignoring malformed message %r: %s", msg.data[:200], exc)
                return
            logger.info("Forwarding %s event for todo %s", event["event"], event["todo"]["id"])
            await send_to_discord(http, body)

        async def on_error(exc):
            logger.error("NATS error: %s", exc)

        nc = await nats.connect(
            NATS_URL,
            name="broadcaster",
            error_cb=on_error,
            max_reconnect_attempts=-1,
        )
        await nc.subscribe(NATS_SUBJECT, queue=QUEUE_GROUP, cb=handler)
        logger.info("Subscribed to %r (queue %r) on %s", NATS_SUBJECT, QUEUE_GROUP, NATS_URL)

        await stop.wait()
        logger.info("Shutting down")
        await nc.drain()  # finish in-flight handlers before exiting


if __name__ == "__main__":
    asyncio.run(main())
