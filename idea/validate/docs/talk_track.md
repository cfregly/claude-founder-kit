# Opinionated technical takes for the demo

## 1. Model routing is product architecture

Treat Haiku/Sonnet/Opus-style routing as a product decision, not a cost hack. Route based on risk, ambiguity, tool complexity, and whether the output can safely be corrected downstream.

## 2. Evals must measure behavior, not prompt beauty

A startup eval should include task success, tool-call success, latency, token cost, regression rate, refusal correctness, and data-boundary adherence. The eval that matters is whether the user comes back with real data.

## 3. Context engineering beats prompt engineering for agents

For serious agents, the hard problem is context shape: progressive disclosure of tools, code execution for transformations, prompt caching for stable context, and state that persists outside the model.

## 4. Platform risk is not a footnote

If your product is "a UI on top of a foundation model," the platform will compress your margin. The answer has to be workflow ownership, proprietary feedback loops, eval history, distribution, or a data boundary the platform cannot casually own.
