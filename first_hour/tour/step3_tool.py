"""Step 3 - give it an action: one tool, one round trip."""
from setup import client, model

# A tool is a NAME + DESCRIPTION + JSON SCHEMA. Claude never runs it. It asks you to.
tools = [{
    "name": "get_exchange_rate",
    "description": "Get the USD exchange rate for a 3-letter currency code. "
                   "Call this when the user converts an amount from US dollars.",
    "input_schema": {
        "type": "object",
        "properties": {"code": {"type": "string", "description": "ISO code, e.g. EUR"}},
        "required": ["code"],
    },
}]


def get_exchange_rate(code):                       # your real implementation would hit an API
    return {"EUR": 0.92, "JPY": 156.3, "GBP": 0.79}.get(code.upper(), 1.0)


c = client()
m = model()
messages = [{"role": "user", "content": "How many euros is 50 US dollars?"}]

resp = c.messages.create(model=m, max_tokens=500, tools=tools, messages=messages)
print("STEP 3  one tool round trip")
print("first stop:", resp.stop_reason)             # -> tool_use
tool_use = next(b for b in resp.content if b.type == "tool_use")
print("Claude asked for:", tool_use.name, tool_use.input)

rate = get_exchange_rate(**tool_use.input)         # WE run it

messages.append({"role": "assistant", "content": resp.content})
messages.append({"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": tool_use.id, "content": str(rate)}]})

final = c.messages.create(model=m, max_tokens=500, tools=tools, messages=messages)
print("second stop:", final.stop_reason)           # -> end_turn
print("answer:", next(b.text for b in final.content if b.type == "text"))
