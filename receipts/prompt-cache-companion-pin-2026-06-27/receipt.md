# Prompt-Cache Companion Pin Receipt, 2026-06-27

The value bar is adversarially-confirmed to add value.

## Pin

- Companion: `prompt-cache`
- Repo: `https://github.com/cfregly/claude-prompt-cache`
- Old pin: none
- New pin: `dfa874e93d4e42f3f968f13fca3a0c9014fee6c0`
- Tag: `founder-kit-prompt-cache-2026-06-27`
- Ledger: `docs/confirmed-improvements.md`

## What Changed

Founder-kit now points to the prompt-cache diagnostics utility as a cost-stage companion. The
implementation stays in the companion repo. Founder-kit stores only the pin, commands, ledger link,
and this receipt.

## Commands Run

```bash
cd /Users/admin/dev/anthropic/claude-prompt-cache
make ci
set -a; source /Users/admin/dev/anthropic/.env; set +a; make check
git commit -m "Add confirmed improvements ledger"
git tag founder-kit-prompt-cache-2026-06-27
git push origin main
git push origin founder-kit-prompt-cache-2026-06-27
```

## Why Founder-Kit Should Move

Prompt-cache diagnostics are a day-zero cost and reliability control. The utility shows the typed
Claude cache-miss reason when the beta returns it, keeps an app-side request diff baseline visible,
and avoids presenting the diagnostic as a competitive feature hit.
