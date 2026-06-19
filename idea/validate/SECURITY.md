# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Use GitHub's private reporting: on the repository's **Security** tab, choose
**Report a vulnerability**. If that is unavailable, open a minimal public issue
asking for a private reporting channel without disclosing details.

Include the version or commit, what you found, and a minimal way to reproduce
it. Expect an acknowledgement within a few days.

## Scope

The deterministic scorers read the files and specs you point them at and do not
transmit your content anywhere. The founder intervention sends the pitch you
analyze to the Anthropic API, so it runs only when you supply a key. Keep keys in
a local `.env` that git ignores, and never commit one.
