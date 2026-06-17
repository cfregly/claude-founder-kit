"""Step 4 - the agent: a manual loop over tools until the task is done."""
import json
from setup import client, model

# A tiny backend with a SEQUENTIAL dependency: resolve the customer id before the orders.
CUSTOMERS = {"ada": {"id": "c_42", "tier": "gold"}}
ORDERS = {"c_42": 7}


def find_customer(name):
    return CUSTOMERS.get(name.lower(), {"error": "not found"})


def get_order_count(customer_id):
    return {"orders": ORDERS.get(customer_id, 0)}


IMPLS = {"find_customer": find_customer, "get_order_count": get_order_count}

tools = [
    {"name": "find_customer",
     "description": "Look up a customer by name. Returns id and tier. Call this first.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string"}},
                      "required": ["name"]}},
    {"name": "get_order_count",
     "description": "Get the order count for a customer id obtained from find_customer.",
     "input_schema": {"type": "object", "properties": {"customer_id": {"type": "string"}},
                      "required": ["customer_id"]}},
]

c = client()
m = model()
messages = [{"role": "user",
             "content": "How many orders does the customer named Ada have, and what tier is she?"}]

print("STEP 4  manual agent loop")
for turn in range(1, 8):
    resp = c.messages.create(model=m, max_tokens=600, tools=tools, messages=messages)
    print("turn %d stop: %s" % (turn, resp.stop_reason))
    if resp.stop_reason == "end_turn":
        print("answer:", next(b.text for b in resp.content if b.type == "text"))
        break
    messages.append({"role": "assistant", "content": resp.content})   # keep the tool_use blocks
    results = []
    for b in resp.content:
        if b.type == "tool_use":
            out = IMPLS[b.name](**b.input)
            print("  ran %s(%s) -> %s" % (b.name, b.input, out))
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)})
    messages.append({"role": "user", "content": results})
