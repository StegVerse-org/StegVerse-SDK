# Tier pricing (cost-derived)

`stegverse/tier_pricing.py` derives paid-tier prices from the ecosystem's existing
task-class cost basis (`StegVerse-Labs/.github/cost-basis/worker-runtime`,
`stegverse.worker-runtime-cost-basis/v0.1`) and positions them against market comparables.

- **Cost per action** = Σ cost-basis quantity × cited unit rate. `compute_units` and
  `failure_recovery_units` are priced at the compute-unit rate, `storage_bytes` per GB, `network_bytes` per GB,
  plus `external_cost_usd`.
- **Cost floor** = cost ÷ (1 − target gross margin). A plan is priced at its costliest admitted task class.
- **Market**: if the median of cited comparables is at or above the floor, the price is the median
  (`AT_MARKET_MEDIAN`). Otherwise the floor holds (`ABOVE_MARKET_COST_BOUND`). With no comparables the
  result is `NO_MARKET_EVIDENCE`.
- **Every USD figure needs an `https` source and `observed_at`.** A missing rate gives `UNKNOWN_RATE_NOT_SOURCED`.
  A missing class gives `UNKNOWN_COST_BASIS`. Malformed input fails closed. Nothing is invented.
- **Non-PRICED results** (`INCOMPLETE`, `FAIL_CLOSED`) carry an `actionable_disposition` with the six fields: failure code, failed predicate, required evidence or repair, retry entrypoint, owning goal and next attempt.
- **Free tier**: the governance gate (`docs/GOVERNANCE_GATE.md`) runs on the caller's own runner, so StegVerse
  bears no marginal compute cost for it.
- **Authority**: the output is a pricing candidate only. Entitlements are issued by TV/TVC.

```bash
python3 -I stegverse/tier_pricing.py \
  --cost-basis-dir <StegVerse-Labs/.github checkout>/cost-basis/worker-runtime \
  --rate-card pricing/rate-card.candidate.json --policy pricing/policy.candidate.json \
  [--market comparables.json] --output pricing/candidate-report.json
```

`pricing/` holds the current **candidate** inputs and report (2026-10-14):

- **Rate card.** Rates are cited from GitHub's published Actions pricing:
  - $0.006 per Linux 2-core runner-minute;
  - $0.25 per GB-month of shared storage.
- **Team tier.** It covers three governance observation classes, with 1,000 actions at a 75% margin. That comes to **$72.27 per period** at the cost floor, with no market evidence yet.
- **Organization tier.** It is `UNKNOWN_RATE_NOT_SOURCED` because no network-egress rate is cited.

Open owner decisions are tracked on StegVerse-org/StegVerse-SDK#484:

- the compute-unit definition;
- the target margin;
- the plan composition;
- the cited market comparables.
