import os
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")

latest = "no entries yet"
counter = 0
lock = threading.Lock()


def producer():
    global latest
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        with lock:
            latest = line
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        time.sleep(5)


class Handler(BaseHTTPRequestHandler):
    def respond(self, text):
        body = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global counter
        if self.path == "/":
            with lock:
                text = latest
            self.respond(text)
        elif self.path == "/pingpong":
            with lock:
                text = f"pong {counter}"
                counter += 1
            self.respond(text)
        else:
            self.send_error(404)

    def log_message(self, *args):  # silence per-request access logs
        pass


if __name__ == "__main__":
    threading.Thread(target=producer, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()