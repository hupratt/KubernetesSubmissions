import os
import time
import uuid
from datetime import datetime

LOG_FILE = os.environ.get("LOG_FILE", "/var/log/info.log")


def main():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    while True:
        line = f"{datetime.now().isoformat(timespec='seconds')} {uuid.uuid4()}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print(line, flush=True)  # also visible via kubectl logs
        time.sleep(5)


if __name__ == "__main__":
    main()