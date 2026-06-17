"""Amplitude backend over stdlib urllib. Falls back to the local log on failure.

Amplitude is the category leader for retention-and-activation analysis, the
alternative to name when the question is the analysis UI. Reads AMPLITUDE_API_KEY
and AMPLITUDE_HOST (default the US endpoint). The insert_id dedups on Amplitude's
side. Import-safe with no key so the offline demo never touches the network.
"""

import json
import os
import urllib.request

from . import local


def _config():
    return os.environ.get("AMPLITUDE_API_KEY"), os.environ.get("AMPLITUDE_HOST", "https://api2.amplitude.com")


def send(event):
    key, host = _config()
    if not key:
        return local.send(event)
    payload = {"api_key": key, "events": [{
        "user_id": event["org_id"],
        "event_type": event["event"],
        "time": int(event["ts"] * 1000),
        "insert_id": event["insert_id"],
        "event_properties": {"stage": event.get("stage"), "variant": event.get("variant"),
                             **event.get("props", {})},
    }]}
    try:
        req = urllib.request.Request(
            f"{host.rstrip('/')}/2/httpapi",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5).read()
        return event
    except Exception:
        return local.send(event)
