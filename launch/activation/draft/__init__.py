"""Step 5, draft: write the founder message for each proposed action, and render.

`nudges` drafts the message for every ask-gated motion with structured output and
grades it against the brand bar. It runs Claude every run and raises with no key.
`render` writes the report to a shippable file: Markdown always, and a
code-execution PDF retrieved through the Files API when a key is present. Neither
ever sends anything: the gate still waits on a human.
"""
