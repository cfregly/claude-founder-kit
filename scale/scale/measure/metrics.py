"""Score a Scale-stage cohort into a moat readout. Deterministic and explainable.

Input is a cohort dict of accounts, each carrying the Scale-stage signals:

    {"cohort": "...", "accounts": [
        {"name": "acct_01", "integrations_built": 4, "workflows_embedded": 3,
         "weekly_active_depth": 6, "spend_trend": "up", "data_volume": "high",
         "contract_tier": "business"}]}

For each account it computes a moat score (a switching-cost proxy from the
integrations built and the workflows embedded, plus a usage-depth term), flags the
accounts with a compounding-data signal, and flags the expansion-ready set (a deep
moat, rising spend, and sustained usage). The readout is the moat distribution,
the GTM-ready set, and the one number: the count of expansion-ready accounts.
Everything here is stdlib only and runs offline.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import statistics
from typing import Any

from .. import contracts

HIGH_MOAT = contracts.HIGH_MOAT


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _int(account: dict, key: str) -> int:
    """A non-negative integer signal, defaulting to 0 when absent or malformed."""
    try:
        return max(0, int(account.get(key, 0)))
    except (TypeError, ValueError):
        return 0


@dataclass(frozen=True)
class MoatScore:
    name: str
    integration_depth: int   # the switching cost from systems Claude is wired into
    workflow_lockin: int     # the switching cost from embedded recurring workflows
    usage_depth: int         # the stickiness term from weekly-active depth
    moat: int                # the total switching-cost proxy, 0..100
    compounding_data: bool   # the account accrues proprietary data that widens the moat
    gtm_ready: bool          # deep moat + rising spend + sustained usage
    band: str                # deep / forming / shallow


def _band(moat: int) -> str:
    if moat >= HIGH_MOAT:
        return "deep"
    if moat >= HIGH_MOAT // 2:
        return "forming"
    return "shallow"


def score_account(account: dict) -> MoatScore:
    """The moat score for one account. The moat is a switching-cost proxy: the
    integration depth (capped) plus the workflow lock-in (capped) plus a usage
    term (capped). A rising spend trend, a deep moat, and sustained weekly use
    together flag the account as expansion-ready for a GTM owner."""
    integrations = _int(account, "integrations_built")
    workflows = _int(account, "workflows_embedded")
    depth = _int(account, "weekly_active_depth")

    integration_depth = int(_clamp(integrations * contracts.INTEGRATION_POINTS,
                                   0, contracts.INTEGRATION_CAP))
    workflow_lockin = int(_clamp(workflows * contracts.WORKFLOW_POINTS,
                                 0, contracts.WORKFLOW_CAP))
    usage_depth = int(_clamp(depth * contracts.DEPTH_POINTS, 0, contracts.DEPTH_CAP))
    moat = integration_depth + workflow_lockin + usage_depth

    compounding = account.get("data_volume") in contracts.COMPOUNDING_DATA
    gtm_ready = (
        moat >= HIGH_MOAT
        and account.get("spend_trend") == contracts.RISING
        and depth >= contracts.HIGH_DEPTH
    )
    return MoatScore(
        name=account.get("name", "<unnamed>"),
        integration_depth=integration_depth,
        workflow_lockin=workflow_lockin,
        usage_depth=usage_depth,
        moat=moat,
        compounding_data=compounding,
        gtm_ready=gtm_ready,
        band=_band(moat),
    )


def data_integrity(accounts: list[dict]) -> list[str]:
    """Flag a messy cohort export before its scores get trusted: an account
    missing a Scale-stage signal, or an unknown spend, data, or contract value.
    The readout is only as honest as the export."""
    issues: list[str] = []
    missing: list[str] = []
    bad_enum: list[str] = []
    for a in accounts:
        name = a.get("name", "<unnamed>")
        if any(s not in a for s in contracts.SIGNALS):
            missing.append(name)
        if a.get("spend_trend") not in contracts.SPEND_TRENDS:
            bad_enum.append(f"{name} (spend_trend)")
        if a.get("data_volume") not in contracts.DATA_TIERS:
            bad_enum.append(f"{name} (data_volume)")
        if a.get("contract_tier") not in contracts.CONTRACT_TIERS:
            bad_enum.append(f"{name} (contract_tier)")
    if missing:
        shown = ", ".join(missing[:3]) + (" ..." if len(missing) > 3 else "")
        issues.append(
            f"{len(missing)} account(s) are missing a Scale-stage signal ({shown}). "
            "A missing signal scores as zero, which understates the moat. Fix the export.")
    if bad_enum:
        shown = ", ".join(bad_enum[:3]) + (" ..." if len(bad_enum) > 3 else "")
        issues.append(
            f"{len(bad_enum)} unknown enum value(s) ({shown}). Use the documented "
            "spend, data, and contract values so the GTM-ready rule is honest.")
    return issues


def summarize(cohort: dict) -> dict[str, Any]:
    """The moat readout: the per-account scores, the moat distribution, the
    compounding-data set, the GTM-ready set, and the one number (the count of
    expansion-ready accounts). Deterministic: the same cohort gives the same
    readout every run, which is why this is the receipt and the CI gate."""
    accounts = cohort.get("accounts", [])
    scores = [score_account(a) for a in accounts]
    moats = [s.moat for s in scores]

    bands = {"deep": 0, "forming": 0, "shallow": 0}
    for s in scores:
        bands[s.band] += 1

    gtm_ready = [s.name for s in scores if s.gtm_ready]
    compounding = [s.name for s in scores if s.compounding_data]
    median_moat = round(statistics.median(moats), 1) if moats else 0.0

    flags = data_integrity(accounts)
    if gtm_ready:
        flags.append(
            f"{len(gtm_ready)} expansion-ready account(s): a deep moat, rising spend, "
            "and sustained weekly use. Hand each to a named GTM owner with the expansion case.")
    deep_not_ready = [s.name for s in scores
                      if s.band == "deep" and not s.gtm_ready and s.name not in gtm_ready]
    if deep_not_ready:
        shown = ", ".join(deep_not_ready[:3]) + (" ..." if len(deep_not_ready) > 3 else "")
        flags.append(
            f"{len(deep_not_ready)} deep-moat account(s) not expanding ({shown}). "
            "Retain the lock-in and find the next workflow to embed before pushing expansion.")
    if compounding:
        flags.append(
            f"{len(compounding)} account(s) accrue compounding data. The moat widens on "
            "its own here; instrument the data so the switching cost is visible at renewal.")
    if not flags:
        flags.append("No deep moats yet. Embed a second workflow per account before chasing expansion.")

    return {
        "cohort": cohort.get("cohort", "unnamed cohort"),
        "accounts": len(accounts),
        "scores": [asdict(s) for s in scores],
        "moat_distribution": bands,
        "median_moat": median_moat,
        "compounding_data_accounts": compounding,
        "gtm_ready_accounts": gtm_ready,
        "the_number": {
            "primary": "expansion-ready accounts",
            "value": len(gtm_ready),
            "deep_moats": bands["deep"],
            "median_moat": median_moat,
        },
        "flags": flags,
    }
