"""Steps 4, 6, 8, operate: decide the next motion, gate every outward step,
remember last week, and render the report.

The contract that makes it honest: only measurement and drafting run unattended
(the `always` set, never outward-facing). Every outward step is `ask` (proposed,
waits for you) or `never` (refused by design). `audit` proves the boundary held,
and the same readout gives the same plan every run.
"""
