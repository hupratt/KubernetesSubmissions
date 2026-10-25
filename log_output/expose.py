import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")
PING_FILE = os.environ.get("PING_FILE", "/var/log/pingpong.log")

lock = threading.Lock()


def read_latest(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def load_counter(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_counter(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"{value}\n")
    os.replace(tmp, path)


counter = load_counter(PING_FILE)


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
            self.respond(read_latest(LOG_FILE) or "no entries yet")
        elif self.path == "/pingpong":
            with lock:
                text = f"pong {counter}"
                counter += 1
                save_counter(PING_FILE, counter)
            self.respond(text)
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()