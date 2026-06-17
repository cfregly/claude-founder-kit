"""PostHog backend over stdlib urllib. Falls back to the local log on failure.

PostHog collapses capture, funnels, retention, and feature flags into one tool,
free to roughly 1M events a month and self-hostable, which matters because data
boundaries are a trust feature. Reads POSTHOG_API_KEY and POSTHOG_HOST (default
the US cloud). Verified against a live endpoint in production use; here it stays
import-safe with no key so the offline demo never touches the network.
"""

import json
import os
import urllib.request

from . import local


def _config():
    return os.environ.get("POSTHOG_API_KEY"), os.environ.get("POSTHOG_HOST", "https://us.i.posthog.com")


def send(event):
    key, host = _config()
    if not key:
        return local.send(event)
    payload = {
        "api_key": key,
        "event": event["event"],
        "distinct_id": event["org_id"],
        # insert_id keys idempotency in PostHog (uuid); the content hash is stable.
        "properties": {"stage": event.get("stage"), "variant": event.get("variant"),
                       "$insert_id": event["insert_id"], **event.get("props", {})},
        "timestamp": event["ts"],
    }
    try:
        req = urllib.request.Request(
            f"{host.rstrip('/')}/capture/",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5).read()
        return event
    except Exception:
        # Telemetry must not break the product it measures: keep the local trail.
        return local.send(event)
