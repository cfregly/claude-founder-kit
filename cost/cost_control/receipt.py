"""Measured receipt: the same tool-using loop, three ways.

This is axis 2 of the cost story, "don't carry tokens you don't need", the counterpart to the
caching receipt in the kit's mvp module, which is axis 1, "don't pay for the same tokens twice". A
short research loop calls a lookup tool that returns a large document every turn. By the last turn
the naive run is resending every earlier document on every call, so its input grows turn over turn.
Three arms over the identical workload:

  naive    keep every full tool result in history forever
  trimmed  client side: once a result has been used, carry only a one-line stub forward
  edited   server side: the context-management beta clears stale tool_uses past a token trigger

It measures, it does not assert. Every number is summed from usage.input_tokens on the real calls.
There is no offline mode and no fallback. The edited arm uses the context-management beta, so the
run needs a key whose org has that beta enabled.
"""

import json
from pathlib import Path

from .client import FAST_MODEL

ROOT = Path(__file__).resolve().parent.parent
PRICING = json.loads((ROOT / "pricing.json").read_text())
RECEIPT = ROOT / "data" / "last_run_receipt.md"

MODEL = FAST_MODEL  # Haiku: the lesson is carried tokens, not the model, so keep the live run cheap
TURNS = 6
TRIGGER_TOKENS = 4000  # clear stale tool_uses once carried input crosses this
KEEP_TOOL_USES = 1

CONTEXT_MANAGEMENT = {
    "edits": [
        {
            "type": "clear_tool_uses_20250919",
            "trigger": {"type": "input_tokens", "value": TRIGGER_TOKENS},
            "keep": {"type": "tool_uses", "value": KEEP_TOOL_USES},
        }
    ]
}

LOOKUP_TOOL = {
    "name": "lookup",
    "description": "Look up a source document by its name and return the full text.",
    "input_schema": {
        "type": "object",
        "properties": {"name": {"type": "string", "description": "The document name."}},
        "required": ["name"],
    },
}

# One fact line per source, each answerable from a single line. The rest of every document is
# filler the model does not need on later turns, which is the whole point: trimming or clearing it
# is lossless for the task, not a quality cut.
SOURCES = [
    ("pricing", "The Growth plan costs 49 dollars per robot per month."),
    ("sla", "The Enterprise uptime SLA is 99.95 percent."),
    ("residency", "Data residency is supported in the US, the EU, and Australia."),
    ("onboarding", "Growth onboarding takes about two weeks end to end."),
    ("security", "Customer imagery is never used to train shared models."),
    ("support", "Growth-plan tickets get a first response within four business hours."),
]

_FILLER = ("This paragraph is background context that does not answer the question and is not "
           "needed on any later turn. ")


def _doc(i: int) -> str:
    """A large document (~2.5k tokens) whose first line carries the only fact that matters."""
    name, fact = SOURCES[i]
    return f"SOURCE {name}\nKEY FACT: {fact}\n\n" + (_FILLER * 320)


def _stub(i: int) -> str:
    """The trimmed carry-forward: keep the fact line, drop the filler."""
    name, fact = SOURCES[i]
    return f"[lookup {name} -> {fact}]"


def _question(i: int) -> str:
    name, _ = SOURCES[i]
    return f"Using the {name} document, answer in one short sentence."


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    p = PRICING["models"][MODEL]
    return (input_tokens * p["input_per_mtok"] + output_tokens * p["output_per_mtok"]) / 1_000_000


def _run_arm(client, mode: str) -> dict:
    """Run the TURNS-step loop once. mode is naive, trimmed, or edited. Sums the real usage."""
    messages: list = []
    in_tokens = out_tokens = 0

    for t in range(TURNS):
        messages.append({"role": "user", "content": _question(t)})
        tool_id = f"toolu_demo_{t}"
        messages.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_id, "name": "lookup", "input": {"name": SOURCES[t][0]}},
        ]})
        messages.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": tool_id, "content": _doc(t)},
        ]})

        kwargs = dict(model=MODEL, max_tokens=64, tools=[LOOKUP_TOOL], messages=messages)
        if mode == "edited":
            resp = client.beta.messages.create(
                betas=["context-management-2025-06-27"],
                context_management=CONTEXT_MANAGEMENT, **kwargs)
        else:
            resp = client.messages.create(**kwargs)

        in_tokens += resp.usage.input_tokens or 0
        out_tokens += resp.usage.output_tokens or 0

        # Close the turn with a short authored answer so the transcript grows like a real chat.
        messages.append({"role": "assistant", "content": "Noted."})

        # Trimming is the only arm that rewrites history: collapse the result just used to a stub
        # so later turns carry the fact, not the filler.
        if mode == "trimmed":
            messages[-2]["content"][0]["content"] = _stub(t)

    return {
        "mode": mode,
        "turns": TURNS,
        "input_tokens": in_tokens,
        "output_tokens": out_tokens,
        "cost_usd": round(cost_usd(in_tokens, out_tokens), 4),
    }


LABEL = {
    "naive": "naive (keep every full tool result)",
    "trimmed": "trimmed (carry a one-line stub)",
    "edited": "edited (context-management beta clears stale tool_uses)",
}


def _table(arms: list) -> str:
    base = next(a["cost_usd"] for a in arms if a["mode"] == "naive")
    lines = ["| strategy | model | turns | total input tokens | output tokens | cost | vs naive |",
             "|---|---|---|---|---|---|---|"]
    for a in arms:
        vs = "baseline" if a["mode"] == "naive" else f"{(a['cost_usd'] - base) / base:+.0%}"
        lines.append(f"| {LABEL[a['mode']]} | {MODEL} | {a['turns']} | {a['input_tokens']:,} | "
                     f"{a['output_tokens']:,} | ${a['cost_usd']:.4f} | {vs} |")
    return "\n".join(lines)


def context_management_receipt(client) -> str:
    """Run the three arms over the identical workload and measure the carried-token cost of each."""
    arms = [_run_arm(client, "naive"), _run_arm(client, "trimmed"), _run_arm(client, "edited")]
    table = _table(arms)
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(table + "\n")
    return table + "\n\nWrote data/last_run_receipt.md. Paste the measured table into the README."
