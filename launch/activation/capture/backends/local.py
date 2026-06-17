"""The local backend: append one JSON object per line. Zero dependencies.

This is the default so the whole pipeline runs offline with no key. The log path
is ACTIVATION_EVENT_LOG (default events.jsonl in the working directory).
"""

import json
import os
import threading

_LOCK = threading.Lock()


def log_path():
    return os.environ.get("ACTIVATION_EVENT_LOG", "events.jsonl")


def send(event):
    line = json.dumps(event, sort_keys=True)
    with _LOCK:
        with open(log_path(), "a") as f:
            f.write(line + "\n")
    return event
