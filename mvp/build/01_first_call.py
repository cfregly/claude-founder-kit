"""
ACT 1 — The first call (minutes 0-2 of the live demo)
=====================================================
Goal on stage: a founder watches tokens stream in under two minutes,
and sees exactly what a request costs before minute three.

Run:  python 01_first_call.py "your question here"
"""

import sys

from anthropic import Anthropic
from dotenv import load_dotenv

from models import SENIOR  # the workhorse rung (ladder in models.py)

load_dotenv()

SYSTEM = (
    "You are a pragmatic co-pilot for startup founders. Be concrete, be brief, "
    "and say 'I don't know' when you don't. Write plain prose: no em-dashes, no "
    "buzzwords (leverage, seamless, game-changing), no 'it's not X, it's Y' framing."
)

def main() -> None:
    question = " ".join(sys.argv[1:]) or (
        "We're a 23-person seed-stage robotics startup. In three bullets, what should "
        "we instrument before launching an AI feature to customers?"
    )

    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    print(f"\n>>> {question}\n")
    with client.messages.stream(
        model=SENIOR,
        max_tokens=512,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        final = stream.get_final_message()

    u = final.usage
    print(
        f"\n\n--- usage: {u.input_tokens} input tokens, {u.output_tokens} output tokens "
        f"(stop_reason={final.stop_reason}) ---"
    )
    print("Next: python 02_agent_with_tools.py  # give the model hands\n")

if __name__ == "__main__":
    main()
