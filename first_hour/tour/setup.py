"""Shared helpers for the tour: load a local .env, build a client, resolve the model."""
import os
import pathlib
from anthropic import Anthropic

DEFAULT_MODEL = "claude-sonnet-4-6"   # fast and low cost for a tour. Override with TOUR_MODEL.


def _load_local_env():
    if os.environ.get("PYTHON_DOTENV_DISABLED") == "1":
        return
    env = pathlib.Path(__file__).resolve().parent.parent / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def model():
    _load_local_env()
    return os.environ.get("TOUR_MODEL", DEFAULT_MODEL)


def client():
    _load_local_env()
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        raise SystemExit(
            "No ANTHROPIC_API_KEY found. Copy .env.example to .env and add your key, "
            "or export it before running the live tour."
        )
    return Anthropic()


def usage(resp):
    return "tokens in %d / out %d" % (resp.usage.input_tokens, resp.usage.output_tokens)
