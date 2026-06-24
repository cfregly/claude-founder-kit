"""The Scale stage of a founder playbook for Claude builders.

A deterministic moat core (stdlib only, the receipt and the CI gate) plus a
mandatory Claude layer that reads the moat readout and writes the GTM motion and
the moat narrative. The core runs offline; the Claude layer raises a clear error
without a key, so a misconfiguration is loud, not a silent downgrade.
"""
