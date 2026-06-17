"""Step 3, enrich: research each product-qualified account before the handoff.

A PQA handed to sales should arrive with context, not a warm name. This step runs
Claude every run: each account gets a short brief from web search and web fetch
with citations, and the Batch API fans the research out across many accounts at
half cost. With no key or no SDK it raises a clear error, not a placeholder.
"""
