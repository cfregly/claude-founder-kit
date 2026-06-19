#!/usr/bin/env python3
"""Reverse-engineered "morning review": the ~25 charts a Claude-startups growth
operator would read every morning, modeled on the public description of Anthropic's
CASH loop in a 2026 public growth-team podcast: Claude reads 20 to 25 charts
every morning and surfaces what moved.

HONESTY: this is INFERENCE from a public podcast, on a FICTIONAL cohort. It is not
Anthropic's actual dashboards, metrics, or internal tooling. The chart SET is the
reverse-engineering. The numbers are sample data, kept consistent with the seed-7
cohort in the launch module so the kit tells one story.

Run:
  python3 morning_read.py            # render morning.html + print the table
  python3 morning_read.py --read     # also run the Claude morning read (needs ANTHROPIC_API_KEY)
  python3 morning_read.py --json      # dump the 25 charts as JSON
"""
import json, os, sys, html
from pathlib import Path

try:  # honor launch/.env before the optional live read checks the key
    from dotenv import load_dotenv

    if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
        load_dotenv(Path(__file__).resolve().parent / ".env")
except Exception:  # pragma: no cover - dotenv is a setup helper
    pass

# The morning-review set: 25 charts in five groups (Relationship, Activation,
# Retention, Monetization, Operating). Each carries this-week and last-week values
# so the read can speak to deltas, plus the reason it earns a morning slot.
# higher_is_better drives the status color; "watch"/"concern" are set where the
# sample data warrants an operator's eye.
CHARTS = [
  # group, id, title, value, last, unit, higher_is_better, status, why
  ("Relationship", "founders_reached", "Founders reached (wk)", 12, 9, "", True, "good", "top of the loop, the cohort the rest measures"),
  ("Relationship", "events_run", "Founder days / build-a-thons", 1, 1, "", True, "good", "the relationship motion that fills the room"),
  ("Relationship", "source_top", "Top acquisition source", "Accelerator 42%", "Community 38%", "", True, "good", "where the next room comes from"),
  ("Relationship", "partner_arch_review", "Partner portfolio to arch review", 60, 55, "%", True, "good", "VC/accelerator partner activation"),

  ("Activation", "signups", "Signups (wk)", 12, 9, "", True, "good", "the funnel mouth"),
  ("Activation", "first_call_rate", "Signup to first API call", 83, 78, "%", True, "good", "day-zero experience, the first lever"),
  ("Activation", "first_build_rate", "First call to first build", 80, 72, "%", True, "good", "the build that proves intent"),
  ("Activation", "activation_rate", "Activation rate", 67, 61, "%", True, "good", "reached the activation bar"),
  ("Activation", "ttfv_days", "Time-to-first-value (median)", 2.0, 2.6, "d", False, "good", "the aha clock, shorter is better"),
  ("Activation", "day01_dropoff", "Day-0/Day-1 drop-off", 17, 22, "%", False, "good", "the first friction point to watch"),
  ("Activation", "activation_by_pod", "Activation, best vs worst pod", "Code 78% / API 50%", "Code 74% / API 47%", "", True, "watch", "which audience pod is leaking"),

  ("Retention", "ttsb_days", "Time-to-second-build (median)", 8, 9, "d", False, "good", "the leading indicator of retention"),
  ("Retention", "second_build_rate", "Second-build rate (unprompted)", 42, 38, "%", True, "watch", "curiosity became habit, or did not"),
  ("Retention", "wab_w4", "Weekly-active builder, week 4", 33, 30, "%", True, "watch", "engagement retention curve"),
  ("Retention", "d7_d30", "Day-7 / Day-30 retention", "62% / 48%", "58% / 45%", "", True, "watch", "the benchmarks set before launch"),
  ("Retention", "leaky_bucket", "Leaky-bucket gap (act minus ret)", 5, 3, "pts", False, "watch", "activation without retention is the AI-tourist trap"),
  ("Retention", "nrr_proxy", "Credits-to-paid (NRR proxy)", 70, 68, "%", True, "good", "the verified retention outcome"),
  ("Retention", "ai_tourist_churn", "AI-tourist churn (no 2nd build)", 58, 62, "%", False, "concern", "signups that churn before habit"),

  ("Monetization", "logo_retention", "Logo retention vs AI-native bar", "~70% (good band 65-75)", "~68%", "", True, "good", "judged against the AI-native bar, not enterprise"),
  ("Monetization", "run_rate_wow", "Cohort run-rate trend (WoW)", 14, 9, "%", True, "good", "shown log-linear, linear charts are not cool"),
  ("Monetization", "cost_per_activated", "Cost per activated dev", "$0.03/task (-86%)", "$0.04/task", "", False, "good", "the unit economics of activation"),
  ("Monetization", "pqas_ready", "Product-qualified accounts ready", 2, 1, "", True, "good", "the GTM handoff currency, net-new logos"),

  ("Operating", "biggest_leak", "Biggest single leak (wk)", "2nd build 62% conv", "1st build 72% conv", "", True, "concern", "where to point the one motion today"),
  ("Operating", "handoff_sla", "PQA handoff within 5 days", "1 of 2", "1 of 1", "", True, "watch", "the success-disaster: leads stalling unhandled"),
  ("Operating", "experiment_board", "CASH loop: proposed / shipped / won", "3 / 1 / 1", "2 / 1 / 0", "", True, "good", "the growth-experiment flywheel, human-gated"),
]

GROUPS = ["Relationship", "Activation", "Retention", "Monetization", "Operating"]
CAVEAT = ("Inference from the public CASH description in a 2026 growth-team podcast, "
          "on a fictional cohort consistent with the launch module (seed 7). "
          "Not Anthropic's actual dashboards or internal tools.")

def charts_as_dicts():
    out = []
    for g, cid, title, val, last, unit, hib, status, why in CHARTS:
        out.append({"group": g, "id": cid, "title": title, "value": val,
                    "last_week": last, "unit": unit, "higher_is_better": hib,
                    "status": status, "why_morning_review": why})
    return out

def _delta(val, last, hib):
    if isinstance(val, (int, float)) and isinstance(last, (int, float)):
        d = val - last
        arrow = "=" if d == 0 else ("up" if d > 0 else "down")
        good = (d >= 0) == hib if d != 0 else True
        return f"{arrow} {abs(round(d,2))}", ("pos" if good else "neg")
    return "vs last wk", "neu"

def render_html(charts):
    color = {"good": "#1a7f4b", "watch": "#b07d00", "concern": "#b3261e"}
    badge = {"good": "#e6f4ea", "watch": "#fff4d6", "concern": "#fce8e6"}
    cards_by_group = {g: [] for g in GROUPS}
    for c in charts:
        dtxt, dcls = _delta(c["value"], c["last_week"], c["higher_is_better"])
        val = c["value"]
        valstr = f"{val}{c['unit']}" if c["unit"] and isinstance(val,(int,float)) else f"{html.escape(str(val))}"
        dcolor = {"pos": "#1a7f4b", "neg": "#b3261e", "neu": "#6b6b6b"}[dcls]
        st = c["status"]
        cards_by_group[c["group"]].append(f"""
      <div class="card" style="border-left:3px solid {color.get(st,'#999')}">
        <div class="t">{html.escape(c['title'])}</div>
        <div class="v">{valstr}</div>
        <div class="m"><span class="d" style="color:{dcolor}">{dtxt}</span>
          <span class="b" style="background:{badge.get(st,'#eee')};color:{color.get(st,'#333')}">{st}</span></div>
        <div class="w">{html.escape(c['why_morning_review'])}</div>
      </div>""")
    sections = ""
    for g in GROUPS:
        sections += f'<h2>{g}</h2>\n<div class="grid">{"".join(cards_by_group[g])}</div>\n'
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Founder activation, the morning review</title>
<style>
:root{{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif}}
body{{margin:0;background:#faf9f7;color:#1a1a1a}}
header{{padding:22px 28px;background:#0d0d0d;color:#fafafa}}
header h1{{margin:0;font-size:20px}}
header p{{margin:6px 0 0;font-size:12px;color:#b9b9b9;max-width:900px}}
h2{{margin:26px 28px 8px;font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:#6b6b6b}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;padding:0 28px}}
.card{{background:#fff;border:1px solid #ececec;border-radius:8px;padding:12px 14px}}
.t{{font-size:12px;color:#555}}
.v{{font-size:21px;font-weight:650;margin:3px 0}}
.m{{display:flex;justify-content:space-between;align-items:center;font-size:11px}}
.b{{padding:1px 7px;border-radius:9px;font-size:10px;text-transform:uppercase;letter-spacing:.04em}}
.w{{margin-top:7px;font-size:11px;color:#8a8a8a;line-height:1.35}}
footer{{margin:30px 28px;font-size:11px;color:#9a9a9a}}
</style></head><body>
<header><h1>Founder activation, the morning review</h1>
<p>{html.escape(CAVEAT)} The read below is what Claude would surface (the CASH-style morning read): a human gates every outward move.</p></header>
{sections}
<footer>25 charts, five groups, one durable org_id. The runnable analog of the read Anthropic's growth team described on the record.</footer>
</body></html>"""

def read_client():
    try:
        from anthropic import Anthropic
    except Exception:
        raise RuntimeError("anthropic SDK is required for --read: pip install anthropic")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is required for --read. Put it in .env or export it.")
    return Anthropic()


def claude_read(charts, client):
    prompt = (
      "You are the morning growth read for a Claude-for-startups activation operator, the human-gated "
      "analog of the CASH loop Anthropic's growth team described publicly. Below are this morning's 25 "
      "charts with week-over-week deltas (fictional cohort). In an operator's terse voice, give exactly four "
      "short sections: WHAT MOVED, WHAT IS CONCERNING, WHAT IS INTERESTING, and THE ONE MOTION TODAY "
      "(a single experiment against the biggest leak, with the metric it should move). You PROPOSE; a human "
      "approves before anything goes out. No preamble.\n\nCHARTS:\n" + json.dumps(charts, indent=0)
    )
    msg = client.messages.create(model="claude-opus-4-8", max_tokens=900,
                                 messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")

def main(argv):
    charts = charts_as_dicts()
    if "--json" in argv:
        print(json.dumps(charts, indent=2)); return 0
    client = None
    if "--read" in argv:
        try:
            client = read_client()
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    html_out = render_html(charts)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "morning.html"), "w") as f:
        f.write(html_out)
    print(f"Wrote morning.html ({len(charts)} charts across {len(GROUPS)} groups).")
    print("\nThe morning review (sample cohort, reverse-engineered set):")
    for g in GROUPS:
        print(f"\n  {g.upper()}")
        for c in charts:
            if c["group"] != g: continue
            dtxt, _ = _delta(c["value"], c["last_week"], c["higher_is_better"])
            v = f"{c['value']}{c['unit']}" if c['unit'] and isinstance(c['value'],(int,float)) else c['value']
            flag = "" if c["status"] == "good" else f"  [{c['status'].upper()}]"
            print(f"    - {c['title']}: {v}  ({dtxt}){flag}")
    if "--read" in argv:
        print("\n" + "=" * 70 + "\nTHE CLAUDE MORNING READ (claude-opus-4-8, proposes, you gate)\n" + "=" * 70)
        print(claude_read(charts, client))
    else:
        print("\n(run with --read to add the Claude morning read; needs ANTHROPIC_API_KEY)")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
