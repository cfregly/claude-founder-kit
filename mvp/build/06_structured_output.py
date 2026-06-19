"""
The output contract: structured outputs
=======================================
A technique that complements Act 2 (tools). When you need reliable data back, constrain the
response to a JSON schema instead of parsing prose and hoping. The schema is the
contract and the API validates against it, so the caller gets typed fields, not a
paragraph to regex. This is the output half of the tool contract.

Run:  python 06_structured_output.py
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from models import JUNIOR  # extraction is a cheap, low-consequence rung

if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
    load_dotenv()

# The schema is the contract. The model must return exactly these fields.
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "plan": {"type": "string"},
        "seats": {"type": "integer"},
    },
    "required": ["name", "plan", "seats"],
    "additionalProperties": False,
}

def main() -> None:
    client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    note = "Jane signed up for the Pro plan with 12 seats."
    print(f"\n>>> extract structured fields from: {note}\n")
    r = client.messages.create(
        model=JUNIOR,
        max_tokens=128,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": f"Extract the account fields: {note}"}],
    )
    text = next(b.text for b in r.content if b.type == "text")
    data = json.loads(text)  # schema-valid by construction, so this never parse-fails
    print("schema-validated JSON:")
    print(json.dumps(data, indent=2))
    u = r.usage
    print(f"\n--- usage: {u.input_tokens} input tokens, {u.output_tokens} output tokens ---")

if __name__ == "__main__":
    main()
