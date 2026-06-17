"""Statsig backend over stdlib urllib. Falls back to the local log on failure.

Statsig is named as the experimentation-and-flags option. Reads STATSIG_API_KEY.
Import-safe with no key so the offline demo never touches the network.
"""

import json
import os
import urllib.request

from . import local


def send(event):
    key = os.environ.get("STATSIG_API_KEY")
    if not key:
        return local.send(event)
    payload = {"events": [{
        "user": {"userID": event["org_id"]},
        "eventName": event["event"],
        "value": event.get("stage"),
        "metadata": {"variant": event.get("variant"), "insert_id": event["insert_id"],
                     **{k: str(v) for k, v in event.get("props", {}).items()}},
        "time": int(event["ts"] * 1000),
    }]}
    try:
        req = urllib.request.Request(
            "https://events.statsigapi.net/v1/log_event",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "STATSIG-API-KEY": key},
        )
        urllib.request.urlopen(req, timeout=5).read()
        return event
    except Exception:
        return local.send(event)
