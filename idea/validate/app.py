from __future__ import annotations

import json
import os

import streamlit as st
from dotenv import load_dotenv

from startup_signal_lab.anthropic_client import analyze_pitch_with_claude
from startup_signal_lab.growth import classify_use_cases_as_dict, score_growth_as_dict

if os.environ.get("PYTHON_DOTENV_DISABLED") != "1":
    load_dotenv()

st.set_page_config(page_title="Claude Startup Linter", page_icon="🧠", layout="wide")

st.title("Claude Startup Linter")
st.caption("Value prop + product wedge + model routing + eval mindset in one founder-facing demo.")

sample = """Acme Reliability helps AI product teams continuously improve production agents. Today teams bolt a model-powered helper onto the side of their product, manually inspect traces, and miss edge cases in tool descriptions. Acme Reliability embeds recommendations directly in the workflow, exposes precise MCP tools, and keeps sensitive traces behind the customer's data boundary. The goal is always-on optimization like AppDynamics for AI systems, not a one-off prompt tuner."""

pitch = st.text_area("Paste a startup pitch, website copy, or README", value=sample, height=220)
st.caption("Runs Claude (claude-opus-4-8) on every analysis. Set ANTHROPIC_API_KEY first.")

if st.button("Analyze startup signal", type="primary"):
    result = analyze_pitch_with_claude(pitch)
    left, right = st.columns([1, 2])
    with left:
        st.subheader("Signal score")
        st.json(result["score"])
        st.subheader("Model route")
        st.json(result["route"])
        st.metric("Claude model", result["route"]["model"])
        if "usage" in result:
            st.caption("Usage")
            st.code(json.dumps(result["usage"], indent=2))
    with right:
        st.subheader("Founder intervention")
        st.markdown(result["response"])

    st.divider()
    st.subheader("Growth spine: Relationship -> Activation -> Retention")
    growth = score_growth_as_dict(pitch)
    gcols = st.columns(3)
    gcols[0].metric("Relationship", growth["relationship"])
    gcols[1].metric("Activation", growth["activation"])
    gcols[2].metric("Retention", growth["retention"])
    st.caption(f"Weakest stage: {growth['weakest_stage']}. {growth['stage_focus']}")
    for flag in growth["flags"]:
        st.markdown(f"- {flag}")
    st.markdown("**Use-case portfolio (Dot ships now / Dash retains / Star is the bet)**")
    st.json(classify_use_cases_as_dict(pitch))
else:
    st.info("Click Analyze startup signal to run the demo.")

st.divider()
st.markdown("""
### Talk track

This is the core job: turn a startup ecosystem touchpoint into an activated builder.
In a live founder room, the win is not that Claude writes nice prose. The win is that
Claude helps the founder make a sharper product and architecture decision inside the event.
""")
