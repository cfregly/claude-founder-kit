"""Swappable capture backends. Local JSONL is the default and needs nothing.

The backend is chosen by ACTIVATION_BACKEND (local, posthog, statsig, amplitude).
The remote backends talk over stdlib urllib, so there is no third-party
dependency, and each known remote backend falls back to the local log on send
failure: telemetry must never break the product it measures. An unknown backend
name fails loud because that is a configuration error.
"""

import os

from . import amplitude, local, posthog, statsig

_BACKENDS = {"local": local, "posthog": posthog, "statsig": statsig, "amplitude": amplitude}


def get_backend(name=None):
    name = (name or os.environ.get("ACTIVATION_BACKEND", "local")).lower()
    if name not in _BACKENDS:
        raise ValueError(
            f"unknown ACTIVATION_BACKEND {name!r}; choose one of {', '.join(sorted(_BACKENDS))}"
        )
    return _BACKENDS[name]
