import os
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg
from psycopg_pool import ConnectionPool

# Configuration & Environment Variables
PORT = int(os.environ.get("PORT", "8000"))
VERSION = os.environ.get("VERSION", "unknown")
MESSAGE = os.environ.get("MESSAGE", "empty message")
LOG_FILE = os.environ.get("LOG_FILE", "./info.log")
INFO_FILE = os.environ.get("INFO_FILE", "information.txt")

# Database Connection URL
DSN = os.environ.get("DATABASE_URL", "postgresql://postgres:strongpw@localhost:5432/pingpong")

# Initialize PostgreSQL Connection Pool
pool = ConnectionPool(DSN, min_size=1, max_size=10, open=False)


def init_db(retries=30, delay=2):
    """Wait for Postgres to be ready and initialize the counter table."""
    for attempt in range(1, retries + 1):
        try:
            pool.open(wait=True, timeout=5)
            with pool.connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS counter (
                        id    INTEGER PRIMARY KEY CHECK (id = 1),
                        value BIGINT NOT NULL
                    )
                    """
                )
                conn.execute(
                    "INSERT INTO counter (id, value) VALUES (1, 0) ON CONFLICT (id) DO NOTHING"
                )
            return
        except Exception as e:
            print(f"DB not ready ({attempt}/{retries}): {e}", flush=True)
            time.sleep(delay)
    raise SystemExit("Could not connect to the database")


def increment():
    """Atomically increment and return the value before the increment."""
    with pool.connection() as conn:
        row = conn.execute(
            "UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value - 1"
        ).fetchone()
    return row[0]


def read_counter():
    """Read the current counter value from the database."""
    with pool.connection() as conn:
        row = conn.execute("SELECT value FROM counter WHERE id = 1").fetchone()
    return row[0] if row else 0


def read_file(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default


def produce():
    """Background producer loop writing logs and tracking pongs."""
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    tmp = LOG_FILE + ".tmp"
    env_message = f"env variable: MESSAGE={MESSAGE}"
    greeting_message = f"greetings: Hello from version {VERSION}"
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        file_message = f"file content: {read_file(INFO_FILE, 'missing')}"
        
        # Safely fetch current counter value locally
        try:
            current_count = read_counter()
            pong_message = f"Ping / Pongs: {current_count}"
        except Exception:
            pong_message = "Ping / Pongs: unavailable"

        with open(tmp, "w", encoding="utf-8") as f:
            f.write(
                f"{line}\n{file_message}\n{env_message}\n"
                f"{greeting_message}\n{pong_message}\n"
            )
        os.replace(tmp, LOG_FILE)

        print(line, flush=True)
        print(file_message, flush=True)
        print(env_message, flush=True)
        print(greeting_message, flush=True)
        print(pong_message, flush=True)
        time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def respond(self, text, status=200, content_type="text/plain; charset=utf-8"):
        body = text.encode() if isinstance(text, str) else text
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        try:
            if path == "/":
                # Root path returns log file contents
                body = read_file(LOG_FILE) or "no entries yet"
                self.respond(body)
            elif path == "/pingpong":
                # Returns incremented pong text & version
                self.respond(f"pong {increment()}\ngreetings: Hello from version {VERSION}")
            elif path == "/pings":
                # Returns just the raw counter value
                self.respond(str(read_counter()))
            elif path == "/healthz":
                # Checks database health
                with pool.connection(timeout=2) as conn:
                    conn.execute("SELECT 1")
                self.respond("ok")
            else:
                self.send_error(404)
        except psycopg.Error as e:
            print(f"DB error: {e}", flush=True)
            self.respond("database error", status=503)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    init_db()
    threading.Thread(target=produce, daemon=True).start()
    print(f"Starting unified server on port {PORT}...", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()