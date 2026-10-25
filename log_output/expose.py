import os
import threading
import time
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")

counter = 0
lock = threading.Lock()


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

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
                text = read_file(LOG_FILE) or "no entries yet"
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
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()