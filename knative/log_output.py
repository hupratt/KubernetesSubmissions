import os
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg
from psycopg_pool import ConnectionPool

# Configuration from Environment Variables
PORT = int(os.environ.get("PORT", "8000"))
LOG_FILE = os.environ.get("LOG_FILE", "./info.log")
MESSAGE = os.environ.get("MESSAGE", "empty message")
VERSION = os.environ.get("VERSION", "unknown")
INFO_FILE = os.environ.get("INFO_FILE", "information.txt")
DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://pingpong:pingpong@localhost:5432/pingpong",
)

# Initialize Database Connection Pool
pool = ConnectionPool(DSN, min_size=1, max_size=10, open=False)


def init_db(retries=30, delay=2):
  """Wait for Postgres and create the counter table."""
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
            "INSERT INTO counter (id, value) VALUES (1, 0) ON CONFLICT (id) DO"
            " NOTHING"
        )
      return
    except Exception as e:
      print(f"DB not ready ({attempt}/{retries}): {e}", flush=True)
      time.sleep(delay)
  raise SystemExit("Could not connect to the database")


def increment_counter():
  """Atomically increment and return the counter value."""
  with pool.connection() as conn:
    row = conn.execute(
        "UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value"
    ).fetchone()
  return row[0]


def get_counter():
  """Fetch current counter value."""
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
  """Background producer writing logs periodically."""
  os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
  tmp = LOG_FILE + ".tmp"
  env_message = f"env variable: MESSAGE={MESSAGE}"
  greeting_message = f"greetings: Hello from version {VERSION}"
  while True:
    line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
    file_message = f"file content: {read_file(INFO_FILE, 'missing')}"
    
    # Increment counter internally instead of making an HTTP call
    try:
      current_val = increment_counter()
      pong_message = f"Ping / Pongs: {current_val}"
    except Exception:
      pong_message = "Ping / Pongs: unavailable"

    content = (
        f"{line}\n{file_message}\n{env_message}\n"
        f"{greeting_message}\n{pong_message}\n"
    )
    with open(tmp, "w", encoding="utf-8") as f:
      f.write(content)
    os.replace(tmp, LOG_FILE)

    print(line, flush=True)
    print(file_message, flush=True)
    print(env_message, flush=True)
    print(greeting_message, flush=True)
    print(pong_message, flush=True)
    time.sleep(5)


class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
    path = self.path.split("?")[0].rstrip("/")
    try:
      if path == "/healthz":
        with pool.connection(timeout=2) as conn:
          conn.execute("SELECT 1")
        body = b"ok"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return

      if path == "/pings":
        body = str(get_counter()).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return

      if path == "" or path == "/":
        body = (read_file(LOG_FILE) or "no entries yet").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return

      self.send_error(404)
    except Exception as e:
      print(f"Error handling request: {e}", flush=True)
      body = b"database error"
      self.send_response(503)
      self.send_header("Content-Length", str(len(body)))
      self.end_headers()
      self.wfile.write(body)

  def log_message(self, *args):
    pass


if __name__ == "__main__":
  init_db()
  threading.Thread(target=produce, daemon=True).start()
  ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()