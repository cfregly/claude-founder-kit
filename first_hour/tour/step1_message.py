"""Step 1 - the foundation: a single Messages API call. Everything else builds on this."""
from setup import client, model, usage

resp = client().messages.create(
    model=model(),
    max_tokens=300,
    system="You are a concise teacher.",
    messages=[{"role": "user", "content": "In one sentence, what is the Claude Messages API?"}],
)

print("STEP 1  one Messages call")
for block in resp.content:            # the response is a LIST of typed blocks, not a string
    if block.type == "text":
        print(block.text)
print("stop:", resp.stop_reason, "|", usage(resp))
