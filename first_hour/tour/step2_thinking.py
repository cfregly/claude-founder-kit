"""Step 2 - make it think: adaptive thinking and the effort dial."""
from setup import client, model, usage

resp = client().messages.create(
    model=model(),
    max_tokens=2000,
    thinking={"type": "adaptive", "display": "summarized"},  # Claude picks the depth, we see a summary
    output_config={"effort": "medium"},                      # low | medium | high | xhigh | max
    messages=[{"role": "user", "content":
        "A bat and a ball cost $1.10 total. The bat costs $1.00 more than the ball. "
        "How much is the ball? Give the final number after reasoning."}],
)

print("STEP 2  adaptive thinking + effort")
for block in resp.content:
    if block.type == "thinking":
        print("[thinking]", (block.thinking or "(omitted)"))
    elif block.type == "text":
        print("[answer]", block.text)
print("stop:", resp.stop_reason, "|", usage(resp))
