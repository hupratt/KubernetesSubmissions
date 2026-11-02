import os
import threading
import time
import uuid
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG_FILE = os.environ.get("LOG_FILE", "./info.log")
MESSAGE = os.environ.get("MESSAGE", "empty message")
INFO_FILE = "/config/information.txt"

PINGPONG_URL = os.environ.get("PINGPONG_URL", "http://localhost:8001/pings")
PORT = int(os.environ.get("PORT", "8000"))


def produce():
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    tmp = LOG_FILE + ".tmp"
    env_message = f"env variable: MESSAGE={MESSAGE}"
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        # Read ConfigMap file
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            file_content = f.read().strip()
        file_message = f"file content: {file_content}"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(line + "\n")
            f.write(file_message + "\n")
            f.write(env_message + "\n")
        os.replace(tmp, LOG_FILE)  # atomic swap, readers never see a partial line
        print(line, flush=True)    # history stays available via kubectl logs
        print(file_message, flush=True)
        print(env_message, flush=True)
        time.sleep(5)


def read_latest(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def fetch_pongs():
    try:
        with urllib.request.urlopen(PINGPONG_URL, timeout=2) as r:
            return r.read().decode().strip()
    except Exception:
        return "unavailable"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0].rstrip("/") != "":
            self.send_error(404)
            return
        line = read_latest(LOG_FILE) or "no entries yet"
        body = f"{line}\npongs: {fetch_pongs()}".encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    threading.Thread(target=produce, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
