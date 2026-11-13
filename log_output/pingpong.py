import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg
from psycopg_pool import ConnectionPool

PORT = int(os.environ.get("PORT", "8001"))
VERSION = os.environ.get("VERSION", "unknown")

# Either DATABASE_URL, or the standard PG* variables (PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)
DSN = os.environ.get("DATABASE_URL", "postgresql://pingpong:pingpong@localhost:5432/pingpong")

pool = ConnectionPool(DSN, min_size=1, max_size=10, open=False)


def init_db(retries=30, delay=2):
    """Wait for Postgres (useful in Docker/Kubernetes) and create the table."""
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
    with pool.connection() as conn:
        row = conn.execute("SELECT value FROM counter WHERE id = 1").fetchone()
    return row[0]


class Handler(BaseHTTPRequestHandler):
    def respond(self, text, status=200):
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        try:
            if path == "/":
                self.respond(
                    f"pong {increment()}\ngreetings: Hello from version {VERSION}"
                )
            elif path == "/pings":
                self.respond(str(read_counter()))
            elif path == "/healthz":
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
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()