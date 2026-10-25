import os
import threading
import time
import uuid
from datetime import datetime

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")

lock = threading.Lock()

def producer():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        with lock:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        time.sleep(5)


if __name__ == "__main__":
    threading.Thread(target=producer, daemon=True).start()