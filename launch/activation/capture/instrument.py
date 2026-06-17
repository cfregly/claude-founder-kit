"""emit(): the one call a tool makes to record a milestone or a volume event.

Server-side, keyed on org_id, opt-out and transparent. Telemetry is on by
default and turns off with ACTIVATION_TELEMETRY=off or the --no-telemetry flag,
because a developer audience resents silent tracking. When off, emit is a no-op
and says so once. A content-hash insert_id makes a re-sent event idempotent in a
backend that dedups.
"""

import hashlib
import json
import os
import sys
import time

from .. import contracts
from .backends import get_backend

_OFF = {"0", "off", "false", "no"}
_SAID_OFF = False


def telemetry_on():
    """On by default. Off via ACTIVATION_TELEMETRY in {0, off, false, no}."""
    return os.environ.get("ACTIVATION_TELEMETRY", "on").strip().lower() not in _OFF


def emit(org_id, event, *, ts=None, variant=None, backend=None, **props):
    """Record one event for org_id. Returns the stored event, or None when off.

    event is a raw tool signal (api_call, build_succeeded, api_key_created, ...).
    Its first occurrence crosses a milestone stage, and every occurrence can also
    count as depth or consumption. variant carries the experiment arm.
    """
    global _SAID_OFF
    if not telemetry_on():
        if not _SAID_OFF:
            print(
                "[capture] telemetry is off (ACTIVATION_TELEMETRY/--no-telemetry); "
                "emit is a no-op.",
                file=sys.stderr,
            )
            _SAID_OFF = True
        return None
    record = {
        "ts": float(ts if ts is not None else time.time()),
        "org_id": org_id,
        "event": event,
        "stage": contracts.stage_for(event),
        "variant": variant,
        "props": dict(props),
    }
    # A content hash makes the event idempotent: re-sending the same (org, event,
    # ts, props) carries the same id, so a backend that dedups never double-counts.
    record["insert_id"] = hashlib.sha1(
        "|".join([record["org_id"], record["event"], repr(record["ts"]),
                  json.dumps(record["props"], sort_keys=True)]).encode()
    ).hexdigest()
    get_backend(backend).send(record)
    return record
