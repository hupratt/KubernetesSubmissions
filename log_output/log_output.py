import os
import threading
import time
import uuid
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG_FILE = os.environ.get("LOG_FILE", "./info.log")
MESSAGE = os.environ.get("MESSAGE", "empty message")
INFO_FILE = os.environ.get("INFO_FILE", "information.txt")
PINGPONG_URL = os.environ.get("PINGPONG_URL", "http://localhost:8001/pings")
PORT = int(os.environ.get("PORT", "8000"))


def fetch_pongs():
    try:
        with urllib.request.urlopen(PINGPONG_URL, timeout=2) as r:
            return r.read().decode().strip()
    except Exception:
        return "unavailable"
    
def pingpong_ok():
    try:
        with urllib.request.urlopen(PINGPONG_URL, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False

def read_file(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default


def produce():
    os.makedirs(os.path.dirname(LOG_FILE) or ".", exist_ok=True)
    tmp = LOG_FILE + ".tmp"
    env_message = f"env variable: MESSAGE={MESSAGE}"
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        file_message = f"file content: {read_file(INFO_FILE, 'missing')}"
        pong_message = f"Ping / Pongs: {fetch_pongs()}"

        with open(tmp, "w", encoding="utf-8") as f:
            f.write(f"{line}\n{file_message}\n{env_message}\n{pong_message}\n")
        os.replace(tmp, LOG_FILE)  # atomic swap, readers never see a partial write

        print(line, flush=True)
        print(file_message, flush=True)
        print(env_message, flush=True)
        print(pong_message, flush=True)
        time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")
        if path == "/healthz":
            ok = pingpong_ok()
            body = b"ok" if ok else b"pingpong unavailable"
            self.send_response(200 if ok else 503)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path != "":
            self.send_error(404)
            return
        body = (read_file(LOG_FILE) or "no entries yet").encode()
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