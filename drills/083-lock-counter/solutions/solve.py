#!/usr/bin/env python3
"""083-lock-counter - threads plus flock; the counter is re-read inside the lock."""

import fcntl
import json
import os
import threading
from pathlib import Path

out = Path(os.environ["OUT"])
out.mkdir(parents=True, exist_ok=True)

counter = out / "counter.txt"
events = out / "events.log"
lock_path = out / ".counter.lock"
WORKERS = 4
PER_WORKER = 50

counter.write_text("0\n", encoding="utf-8")
events.write_text("", encoding="utf-8")


def worker(worker_id: int) -> None:
    for _ in range(PER_WORKER):
        with lock_path.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                current = int(counter.read_text(encoding="utf-8").strip() or 0)
                counter.write_text(f"{current + 1}\n", encoding="utf-8")
                with events.open("a", encoding="utf-8") as log:
                    log.write(f"{worker_id}\n")
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


threads = [threading.Thread(target=worker, args=(index,)) for index in range(WORKERS)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

lock_path.unlink(missing_ok=True)
summary = {"workers": WORKERS, "per_worker": PER_WORKER, "total": WORKERS * PER_WORKER}
(out / "summary.json").write_text(json.dumps(summary) + "\n", encoding="utf-8")
