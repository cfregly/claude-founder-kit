"""Research the product-qualified accounts: web search + fetch, batched, cited.

This step runs Claude every run. The synchronous path runs one web-search-and-fetch
turn per account (prompt-cached cohort context, citations kept), and the batch path
submits the same work through the Batch API for a half-price fan-out across a large
cohort. With no key or no SDK it raises a clear error, so a misconfiguration is loud
rather than a silent skip. It needs ANTHROPIC_API_KEY and the anthropic SDK.
"""

from __future__ import annotations

from ..platform import client as _client

WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]


def _error_brief(name: str, error: str) -> dict:
    """Annotate one account whose live research call failed, so a single failure
    does not lose the rest of the cohort. The step itself raises when the client
    is missing; this is only for a per-account API error after that."""
    return {"account": name, "brief": f"{name}: brief unavailable.",
            "citations": [], "live": False, "error": error}


def _system(cohort_name: str):
    return [{
        "type": "text",
        "text": ("You brief a GTM owner on one product-qualified account from a founder "
                 f"cohort ({cohort_name}). Reply with at most two sentences: what they are "
                 "building and the one reason now is the time to reach out, each factual "
                 "claim cited. If you find no public information, reply with exactly "
                 "'no public signal found.' Never explain your process and never ask for files."),
        # The cohort context is the stable prefix, cached across all accounts.
        "cache_control": {"type": "ephemeral"},
    }]


def _citations(resp) -> list:
    urls = []
    for block in getattr(resp, "content", []):
        for c in getattr(block, "citations", None) or []:
            url = getattr(c, "url", None)
            if url:
                urls.append(url)
    return urls


def _enrich_sync(c, pqas, cohort_name):
    briefs = {}
    system = _system(cohort_name)
    for name in pqas:
        try:
            resp = c.messages.create(
                model=_client.MODEL,
                max_tokens=1024,
                system=system,
                tools=WEB_TOOLS,
                messages=[{"role": "user", "content": f"Brief the account {name}."}],
            )
            text = "".join(getattr(b, "text", "") for b in resp.content
                           if getattr(b, "type", "") == "text").strip()
            briefs[name] = {"account": name, "brief": text, "citations": _citations(resp), "live": True}
        except Exception as e:
            briefs[name] = _error_brief(name, str(e))
    return {"live": True, "mode": "sync", "briefs": briefs}


def _enrich_batch(c, pqas, cohort_name):
    """Submit one research request per account through the Batch API (half cost).
    Returns the batch id; results land within the hour and are collected later."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    system = _system(cohort_name)
    requests = [
        Request(
            custom_id=f"pqa-{name}",
            params=MessageCreateParamsNonStreaming(
                model=_client.MODEL, max_tokens=1024, system=system, tools=WEB_TOOLS,
                messages=[{"role": "user", "content": f"Brief the account {name}."}],
            ),
        )
        for name in pqas
    ]
    batch = c.messages.batches.create(requests=requests)
    return {"live": True, "mode": "batch", "batch_id": batch.id, "submitted": len(requests)}


def enrich_pqas(pqas, *, cohort_name: str = "", use_batch: bool = False) -> dict:
    """Brief each product-qualified account with live web research. Runs Claude
    every run; raises when the SDK or the key is missing. With no accounts there
    is nothing to research."""
    if not pqas:
        return {"live": True, "briefs": {}}
    c = _client.require_client()
    return _enrich_batch(c, pqas, cohort_name) if use_batch else _enrich_sync(c, pqas, cohort_name)
