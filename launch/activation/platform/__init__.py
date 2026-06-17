"""The platform layer: the shared Claude client and the coverage map.

Every step that calls a model goes through `client` here, so there is one place
that holds the model id, opts into betas, and answers `available()` before any
network call. `coverage` is the verifiable scorecard of which platform surface
each step exercises.
"""
