"""Step 5 - a Managed Agent end to end: environment, agent, session, event stream.

Same loop as step 4, but Anthropic runs the loop and hosts the container the tools run in.
"""
from setup import client, model


def text_of(content):
    return "".join(getattr(b, "text", "") for b in (content or []) if getattr(b, "type", "") == "text")


c = client()
m = model()
print("STEP 5  a Managed Agent end to end")

try:
    # 1) ENVIRONMENT - the container template (Anthropic-hosted).
    env = c.beta.environments.create(
        name="first-hour-env",
        config={"type": "cloud", "networking": {"type": "unrestricted"}})

    # 2) AGENT - persisted, versioned. model / system / tools live HERE, never on the session.
    agent = c.beta.agents.create(
        name="First Hour Agent", model=m,
        system="You are a terse helper. Use bash to do the work, then report plainly.",
        tools=[{"type": "agent_toolset_20260401"}])

    # 3) SESSION - references the agent id + environment. Provisions the container.
    session = c.beta.sessions.create(agent=agent.id, environment_id=env.id, title="first hour")
    print("env:", env.id, "| agent:", agent.id, "| session:", session.id)

    task = ("Use bash to print today's UTC date and the value of 17*23, "
            "then tell me both in one sentence.")

    # 4) STREAM-FIRST, then send. The stream only delivers events emitted after it opens.
    with c.beta.sessions.events.stream(session_id=session.id) as stream:
        c.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": task}]}])
        seen = 0
        for event in stream:
            seen += 1
            et = getattr(event, "type", "?")
            if et == "agent.message":
                t = text_of(getattr(event, "content", None))
                if t.strip():
                    print("AGENT :", t.strip())
            elif et == "agent.tool_use":
                print("TOOL  :", getattr(event, "name", "?"), getattr(event, "input", ""))
            elif et == "agent.tool_result":
                print("RESULT:", str(getattr(event, "content", ""))[:120])
            elif et == "session.status_idle":
                sr = getattr(getattr(event, "stop_reason", None), "type", None)
                print("[idle, stop_reason=%s]" % sr)
                if sr != "requires_action":
                    break
            elif et == "session.status_terminated":
                print("[terminated]")
                break
            if seen > 300:
                break

    # 5) Clean up the container. Keep the reusable agent and environment.
    c.beta.sessions.archive(session_id=session.id)
    print("session archived")

except Exception as e:
    print("Managed Agents not available:", type(e).__name__, str(e)[:200])
    print("This step needs the managed-agents beta enabled on your org. Steps 1-4 do not.")
