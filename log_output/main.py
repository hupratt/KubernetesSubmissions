import time
import uuid
from datetime import datetime

entries = []

while True:
    now = datetime.now().isoformat(timespec="seconds")
    entries.append(str(uuid.uuid4()))
    print(f"{now} {entries[-1]}")
    time.sleep(5)