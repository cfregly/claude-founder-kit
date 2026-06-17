"""Swappable capture backends. Local JSONL is the default and needs nothing.

The backend is chosen by ACTIVATION_BACKEND (local, posthog, statsig, amplitude).
The remote backends talk over stdlib urllib, so there is no third-party
dependency, and each falls back to the local log on any failure: telemetry must
never break the product it measures.
"""

import os

from . import amplitude, local, posthog, statsig

_BACKENDS = {"local": local, "posthog": posthog, "statsig": statsig, "amplitude": amplitude}


def get_backend(name=None):
    name = (name or os.environ.get("ACTIVATION_BACKEND", "local")).lower()
    return _BACKENDS.get(name, local)
