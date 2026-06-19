# Scale, the data moat and the GTM motion

[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

The Scale stage of Anthropic's Founder's Playbook: build a go-to-market function,
compound usage into a data moat, and turn workflow lock-in into a switching cost a
competitor cannot copy fast. It scores a cohort into a moat readout and writes the
one GTM motion to run next.

- The Scale stage is not about finding the first users. It is about widening the
  gap: how many of a customer's systems the product is wired into, how many of their
  recurring workflows run through it, and how much proprietary data has accrued. The
  moat score is a switching-cost proxy built from exactly those signals.
- The deterministic moat core is stdlib only. It carries the receipt and the CI
  gate, so the `--json` readout and the `--min-moat` gate run offline with no key and
  no install.
- The Claude layer runs on every human readout: it reads the deterministic numbers
  and writes the GTM motion (which accounts to target, the one play) and the moat
  narrative (why a well-funded incumbent copying this product today would not catch
  up within two years). It raises a clear error with no key, so a misconfiguration
  is loud, not a silent downgrade.
- It is a command-line tool, not a dashboard or UI.

## Run it

```bash
make demo    # the live moat readout and GTM motion from the sample cohort (needs ANTHROPIC_API_KEY)
make test    # the test suite
make check   # the doc-correctness gate
```

`make demo` runs `python3 -m scale examples/cohort.json`, the human readout plus the
Claude GTM motion and moat narrative, so it needs `ANTHROPIC_API_KEY` and fails fast
without it. Add `--json` for the raw deterministic readout with no key. On the sample
cohort of 10 accounts the top account scores a moat of 100, the median moat is 60,
the distribution is 5 / 3 / 2 across the deep, forming, and shallow bands, and 3
accounts are expansion-ready: a deep moat, rising spend, and sustained weekly use.
These numbers come from the deterministic core, so re-run before changing one.

## The deterministic core is the gate

The moat score for each account is a switching-cost proxy: integration depth (the
systems Claude is wired into, capped), plus workflow lock-in (the recurring
workflows that run through it, capped), plus a usage-depth term (capped), summed to
0..100. An account is expansion-ready when it clears a deep moat, its spend is
rising, and its weekly use is sustained. A deep moat that is not expanding is
retained, not pushed.

The readout is the moat distribution, the compounding-data set, the expansion-ready
set, and the one number: the count of expansion-ready accounts. It is deterministic,
so the same cohort gives the same readout every run, which is why it is the receipt
and the CI gate. `python3 -m scale examples/cohort.json --min-moat 40` fails the
build when the median moat falls below the bar, and it runs offline before any
Claude call.

## The Claude layer runs on the readout

The human readout, `python3 -m scale examples/cohort.json`, prints the
deterministic core and then runs Claude (`claude-opus-4-8`) on those numbers to add:

- The GTM motion: which accounts to target from the expansion-ready set, the one
  play to run, and why, tied to the numbers.
- The moat narrative: the case, grounded in the integration depth, the workflow
  lock-in, and the compounding data, for why an incumbent copying the product today
  would not catch up within two years.

This step needs `ANTHROPIC_API_KEY` and the anthropic SDK. It runs on every human
readout and raises a clear error without the key or the SDK, so a missing key fails
loud rather than degrading. The `--json` output never calls Claude, so the receipt
and the gate stay offline.

## The cohort shape

Each account carries the Scale-stage signals: the integrations built, the workflows
embedded, the weekly-active depth, a spend trend (up, flat, down), a data volume
(none, low, medium, high), and a contract tier (pilot, team, business, enterprise).

```json
{
  "cohort": "Scale cohort",
  "accounts": [
    {"name": "acct_01", "integrations_built": 5, "workflows_embedded": 4,
     "weekly_active_depth": 6, "spend_trend": "up", "data_volume": "high",
     "contract_tier": "enterprise"}
  ]
}
```

## Where things are

| Path | What it holds |
| --- | --- |
| `scale/contracts.py` | the Scale-stage signals, the moat weights, the GTM-ready rule |
| `scale/measure/metrics.py` | the deterministic moat scoring and the readout |
| `scale/generate/gtm.py` | the Claude GTM motion and moat narrative, run every readout |
| `scale/platform/client.py` | the shared Claude client and the run guard |
| `scale/__main__.py` | the CLI: the readout, the JSON, the `--min-moat` gate |
| `scripts/check_docs.py` | the doc-correctness gate |
| `skills/scale/` | the packaged Claude Skill |

## Limitations

- The sample cohort is fictional, and the moat score is a proxy, not a contract
  value. Point it at a real cohort export, and use the data-integrity flags to catch
  a messy export before its scores get trusted.
- The Claude layer needs `ANTHROPIC_API_KEY` and a current anthropic SDK. With no
  key or no SDK it raises a clear error rather than degrade. `make demo` runs that
  layer, so it needs both. The deterministic core alone (`--json`, `--min-moat`)
  needs neither.
- `PYTHON_DOTENV_DISABLED=1` is only for fail-fast tests that need to prove a
  missing-key path ignores the local `.env`.

## Where this fits

This is the **Scale** module of [claude-founder-kit](../README.md). The full journey runs as modules in one repo: first_hour, idea, mvp, launch, scale, quality, cost. The playbook names what a founder does at each stage, and these are the runnable tools that do it. Claude runs the judgment on every stage, and a deterministic gate verifies the output before it ships. One `make demo` from the repo root runs the whole arc live.

## License

MIT. See [LICENSE](LICENSE).
