import os
import time
import uuid
from datetime import datetime

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")
PING_FILE = os.environ.get("PING_FILE", "/var/log/pingpong.log")


def read_counter(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    tmp = LOG_FILE + ".tmp"
    while True:
        line = (
            f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
            f" pongs: {read_counter(PING_FILE)}"
        )
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(line + "\n")
        os.replace(tmp, LOG_FILE)  # atomic swap, readers never see a partial line
        print(line, flush=True)    # history stays available via kubectl logs
        time.sleep(5)


if __name__ == "__main__":
    main()