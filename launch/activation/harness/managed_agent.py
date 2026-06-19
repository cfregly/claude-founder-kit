"""The cloud harness: a Managed Agents deployment that runs the report on a cron.

Anthropic runs the agent loop and the container; a scheduled deployment fires a
session every Monday that produces the report. The gate is a permission policy:
the read-and-measure tools run on their own, the two outward tools (the founder
nudge, the GTM handoff) are always_ask, and spend, credits, and public posts are
simply not tools the agent has. The agent is created once and referenced by id;
the deployment fires it on the schedule.

Guarded: with no key or no managed-agents beta in the SDK, `apply` returns the
plan instead of creating anything, so `make deploy` shows exactly what would be
created without creating it.
"""

from __future__ import annotations

import json

from ..platform import client as _client

ENVIRONMENT = {
    "name": "activation-env",
    "config": {"type": "cloud",
               "networking": {"type": "limited",
                              "allow_mcp_servers": True,
                              "allow_package_managers": True}},
}

SYSTEM = (
    "You are a growth operator for a founder cohort. Each Monday you produce the "
    "weekly startup-signal report: the activation and retention funnel, the biggest "
    "leak, time-to-second-build, the product-qualified accounts ready for handoff, "
    "and the one motion that moves the biggest leak. Measurement and drafting are "
    "yours to do unattended. You never send a founder email, grant credits, spend "
    "on any channel, post in public, or hand off an account without explicit "
    "approval. State every line as a decision."
)

# The two outward tools are gated always_ask. Spend, credits, and public posts are
# deliberately absent: the NEVER gate is the absence of the capability, not a flag.
OUTWARD_TOOLS = [
    {"type": "custom", "name": "send_founder_nudge",
     "description": "Send a drafted nudge to a founder. Requires your approval.",
     "input_schema": {"type": "object",
                      "properties": {"account": {"type": "string"},
                                     "subject": {"type": "string"},
                                     "body": {"type": "string"}},
                      "required": ["account", "subject", "body"]}},
    {"type": "custom", "name": "gtm_handoff",
     "description": "Hand a product-qualified account to a named GTM owner. Requires your approval.",
     "input_schema": {"type": "object",
                      "properties": {"account": {"type": "string"},
                                     "owner": {"type": "string"}},
                      "required": ["account", "owner"]}},
]

SCHEDULE = {"type": "cron", "expression": "0 13 * * 1", "timezone": "America/Los_Angeles"}

# The rubric the grader scores the report against on a graded run (sent as a
# user.define_outcome event). Every line is checkable.
RUBRIC = (
    "The weekly startup-signal report must:\n"
    "- have ACTIVATION, RETENTION, PIPELINE, THE ONE MOTION, and the gate-ledger sections\n"
    "- name the single biggest funnel leak with the percent lost\n"
    "- give time-to-second-build as the retention leading indicator\n"
    "- name the product-qualified accounts ready for handoff\n"
    "- propose exactly one motion tied to the biggest leak, with the metric it moves\n"
    "- send nothing: every outward action is proposed for approval, not taken\n"
)

VAULT = {
    "note": "PostHog and Stripe credentials live in a vault, attached by id. The "
            "sandbox sees an opaque placeholder; the real secret is substituted at egress.",
    "credentials": ["posthog_api_key (environment_variable)",
                    "stripe_api_key (environment_variable)"],
}

WEBHOOK = {
    "event": "session.status_idled",
    "note": "Register a webhook so a finished weekly run notifies you instead of polling.",
}


def agent_def(mcp_url: str = "https://activation.example.com/mcp") -> dict:
    return {
        "name": "activation-operator",
        "model": _client.MODEL,
        "system": SYSTEM,
        "mcp_servers": [{"type": "url", "name": "activation", "url": mcp_url}],
        "tools": [
            {"type": "agent_toolset_20260401",
             "default_config": {"enabled": True, "permission_policy": {"type": "always_allow"}},
             "configs": [{"name": "bash", "permission_policy": {"type": "always_ask"}}]},
            {"type": "mcp_toolset", "mcp_server_name": "activation"},
            *OUTWARD_TOOLS,
        ],
        "skills": [{"type": "custom", "skill_id": "activation", "version": "latest"}],
    }


def deployment_def(agent_id: str, environment_id: str, vault_ids=None) -> dict:
    return {
        "name": "activation-monday",
        "agent": agent_id,
        "environment_id": environment_id,
        "initial_events": [{"type": "user.message", "content": [{"type": "text", "text": (
            "Produce this week's startup-signal report. Measure the cohort, name the "
            "biggest leak and the one motion, list the PQAs ready for handoff, and "
            "propose the outward motions for my approval. Send nothing yourself.")}]}],
        "schedule": SCHEDULE,
        "vault_ids": vault_ids or [],
    }


def plan(mcp_url: str = "https://activation.example.com/mcp") -> dict:
    """The full deployment plan as payloads, for inspection and the dry run."""
    return {
        "environment": ENVIRONMENT,
        "agent": agent_def(mcp_url),
        "deployment": deployment_def("<agent_id>", "<environment_id>", ["<vault_id>"]),
        "outcome_rubric": RUBRIC,
        "vault": VAULT,
        "webhook": WEBHOOK,
    }


def apply(*, mcp_url: str = "https://activation.example.com/mcp", vault_ids=None) -> dict:
    """Create the environment, agent, and scheduled deployment for real. Needs a key
    and a current SDK with the managed-agents beta. Returns created ids with
    live=True, or a live=False plan/error payload that the CLI treats as a failed
    apply."""
    c = _client.client()
    beta = getattr(c, "beta", None)
    if c is None or beta is None or not hasattr(beta, "deployments"):
        return {"live": False, "plan": plan(mcp_url)}
    try:
        env = beta.environments.create(**ENVIRONMENT)
        agent = beta.agents.create(**agent_def(mcp_url))
        dep = beta.deployments.create(**deployment_def(agent.id, env.id, vault_ids))
        return {"live": True, "environment_id": env.id, "agent_id": agent.id,
                "deployment_id": dep.id}
    except Exception as e:
        return {"live": False, "plan": plan(mcp_url), "error": str(e)}


def render_plan(mcp_url: str = "https://activation.example.com/mcp") -> str:
    p = plan(mcp_url)
    L = ["Managed Agents weekly deployment plan (dry run)", ""]
    L.append("environment ... " + json.dumps(p["environment"]["config"]["networking"]))
    L.append(f"agent ......... {p['agent']['name']} on {p['agent']['model']}")
    L.append("  tools ....... agent_toolset + activation MCP + 2 outward tools")
    L.append("  gated (ask) . " + ", ".join(t["name"] for t in OUTWARD_TOOLS))
    L.append("  never ....... spend, grant credits, public post (absent by design)")
    L.append(f"deployment .... {p['deployment']['name']}, cron {SCHEDULE['expression']} ({SCHEDULE['timezone']})")
    L.append("outcome ....... rubric-graded; " + RUBRIC.splitlines()[0].rstrip(":"))
    L.append("vault ......... " + ", ".join(p["vault"]["credentials"]))
    L.append("webhook ....... " + p["webhook"]["event"])
    L += ["", "Run `activation deploy --apply` with a key and a current SDK to create these."]
    return "\n".join(L) + "\n"
