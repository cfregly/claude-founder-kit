"""One function per Claude cost lever, online.

Each function takes a real client and makes a real API call, then reports what came back, with the
numbers read from the usage object, never from memory. There is no offline mode. The REGISTRY at
the bottom maps a lever name to a one-line summary and its function, in the order you'd reach for
them: cut what you send, tune how hard it thinks, measure, then halve the rest with batch.
"""

from .client import FAST_MODEL, MAIN_MODEL
from .receipt import context_management_receipt


def prompt_caching(client):
    """Cache the stable prefix and prove the hit: the repeat reads the cache instead of re-paying."""
    prefix = "You are an expert on this document.\n" + ("lorem ipsum dolor sit amet. " * 700)
    blk = [{"type": "text", "text": prefix, "cache_control": {"type": "ephemeral"}}]
    a = client.messages.create(model=MAIN_MODEL, max_tokens=16, system=blk,
                               messages=[{"role": "user", "content": "Say OK."}])
    b = client.messages.create(model=MAIN_MODEL, max_tokens=16, system=blk,
                               messages=[{"role": "user", "content": "Say OK again."}])
    return (f"call 1  write={a.usage.cache_creation_input_tokens} read={a.usage.cache_read_input_tokens}\n"
            f"call 2  write={b.usage.cache_creation_input_tokens} read={b.usage.cache_read_input_tokens}"
            "  <- the repeat reads the cache")


def context_editing(client):
    """Prune stale tool results server-side, so every later turn carries fewer tokens."""
    cfg = {"edits": [
        {"type": "clear_tool_uses_20250919", "trigger": {"type": "input_tokens", "value": 35000},
         "keep": {"type": "tool_uses", "value": 5}},
    ]}
    r = client.beta.messages.create(model=MAIN_MODEL, max_tokens=16,
                                    betas=["context-management-2025-06-27"], context_management=cfg,
                                    messages=[{"role": "user", "content": "Say OK."}])
    return f"context_management accepted, stop_reason {r.stop_reason}"


def tool_search(client):
    """Defer most tool schemas and let the model search and load them on demand, keeping context lean."""
    deferred = [
        {"name": f"{svc}_lookup", "description": f"Look something up in the {svc} service.",
         "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
         "defer_loading": True}
        for svc in ("billing", "weather", "calendar", "github", "slack", "search", "maps", "email")
    ]
    tools = [{"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"}] + deferred
    r = client.messages.create(model=MAIN_MODEL, max_tokens=512, tools=tools,
                               messages=[{"role": "user", "content": "What is the weather in San Francisco? Use a tool."}])
    searches = getattr(getattr(r.usage, "server_tool_use", None), "tool_search_requests", 0) or 0
    return (f"deferred {len(deferred)} tool schemas out of context, tool_search_requests={searches}, "
            f"stop_reason {r.stop_reason}")


def programmatic_tool_calling(client):
    """Claude writes code in the execution container that calls your tool, so intermediate data stays out of context."""
    tools = [
        {"type": "code_execution_20260120", "name": "code_execution"},
        {"name": "get_number", "description": "Return the integer value stored for a given key.",
         "input_schema": {"type": "object", "properties": {"key": {"type": "string"}}, "required": ["key"]},
         "allowed_callers": ["code_execution_20260120"]},
    ]
    r = client.messages.create(model=MAIN_MODEL, max_tokens=1024, tools=tools,
                               messages=[{"role": "user", "content":
                                          "Call get_number for keys a, b, and c, then return their sum. Do it in code."}])
    code_ran = any(getattr(b, "type", "") == "server_tool_use" for b in r.content)
    return f"code execution engaged: {code_ran}, stop_reason {r.stop_reason}"


def thinking_effort(client):
    """Adaptive thinking plus effort tunes the thinking tokens you pay for. Save high effort for the turns that earn it."""
    r = client.messages.create(model=MAIN_MODEL, max_tokens=512,
                               thinking={"type": "adaptive", "display": "summarized"},
                               output_config={"effort": "high"},
                               messages=[{"role": "user", "content": "What is 27 * 453? Think it through."}])
    thought = any(b.type == "thinking" for b in r.content)
    return f"thinking block present: {thought}, output tokens {r.usage.output_tokens}"


def token_counting(client):
    """count_tokens gives the exact, model-specific count before you send and before you pay. Never tiktoken."""
    sample = "Count the tokens in this sentence, accurately, with the real tokenizer."
    n = client.messages.count_tokens(model=MAIN_MODEL,
                                     messages=[{"role": "user", "content": sample}]).input_tokens
    return f"count_tokens: {n} input tokens for the sample"


def batch(client):
    """The Batches API runs anything non-interactive async at 50% of the token price."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request
    batch_obj = client.messages.batches.create(requests=[
        Request(custom_id="demo-1", params=MessageCreateParamsNonStreaming(
            model=FAST_MODEL, max_tokens=16, messages=[{"role": "user", "content": "Say OK."}]))
    ])
    return f"created batch {batch_obj.id}, status {batch_obj.processing_status} (poll, then read results)"


REGISTRY = {
    "prompt_caching": ("cache the stable prefix, prove the hit", prompt_caching),
    "context_editing": ("prune stale tool results", context_editing),
    "context_receipt": ("measured: same tool loop, three ways", context_management_receipt),
    "tool_search": ("load tool schemas on demand, not all upfront", tool_search),
    "programmatic_tool_calling": ("keep big intermediate data out of context", programmatic_tool_calling),
    "thinking_effort": ("tune thinking depth to the turn", thinking_effort),
    "token_counting": ("exact counts before you pay, never tiktoken", token_counting),
    "batch": ("async at half the token price", batch),
}
