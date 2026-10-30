import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PING_FILE = os.environ.get("PING_FILE", "./pingpong.log")
PORT = int(os.environ.get("PORT", "8001"))

lock = threading.Lock()


def load_counter(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_counter(path, value):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
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
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/pingpong":
            with lock:
                text = f"pong {counter}"
                counter += 1
                save_counter(PING_FILE, counter)
            self.respond(text)
        elif path == "/pings":
            with lock:
                value = counter
            self.respond(str(value))
        else:
            self.send_error(404)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
