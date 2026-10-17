# Tier pricing (cost-derived)

`stegverse/tier_pricing.py` derives paid-tier prices from the ecosystem's existing
task-class cost basis (`StegVerse-Labs/.github/cost-basis/worker-runtime`,
`stegverse.worker-runtime-cost-basis/v0.1`) and positions them against market comparables.

- **Cost per action** = Σ cost-basis quantity × cited unit rate. `compute_units` and
  `failure_recovery_units` are priced at the compute-unit rate, `storage_bytes` per GB, `network_bytes` per GB,
  plus `external_cost_usd`.
- **Pricing basis (owner invariant).** Each task class's unit cost is
  `C_pricing = max(C_estimated, C_authentically_observed)` for the same scope, currency, unit and
  `cost_basis_version`. Both operands and the selected basis are kept in `action_costs[].pricing_basis`.
  - An observation counts only with an authentic class, an `evidence_ref` and a 64-hex `evidence_sha256`;
    supply them with `--observations` (`stegverse.cost-observation-set.v1`).
  - UNKNOWN is never zero. With one operand the tier is a labelled `PROVISIONAL_SCENARIO` and the report is
    `PROVISIONAL`; a mismatched version is `NOT_COMPARABLE`. Only a complete basis on every class gives `PRICED`.
  - Even `PRICED` is a cost-derived candidate: `final_price_approved` is always false. The owner approves prices.
- **Cost floor** = C_pricing ÷ (1 − target gross margin). A plan is priced at its costliest admitted task class.
- **Market**: if the median of cited comparables is at or above the floor, the price is the median
  (`AT_MARKET_MEDIAN`). Otherwise the floor holds (`ABOVE_MARKET_COST_BOUND`). With no comparables the
  result is `NO_MARKET_EVIDENCE`.
- **Every USD figure needs an `https` source and `observed_at`.** A missing rate gives `UNKNOWN_RATE_NOT_SOURCED`.
  A missing class gives `UNKNOWN_COST_BASIS`. Malformed input fails closed. Nothing is invented.
- **Non-PRICED results** (`PROVISIONAL`, `INCOMPLETE`, `FAIL_CLOSED`) carry an `actionable_disposition` with the six fields: failure code, failed predicate, required evidence or repair, retry entrypoint, owning goal and next attempt.
- **Free tier**: the governance gate (`docs/GOVERNANCE_GATE.md`) runs on the caller's own runner, so StegVerse
  bears no marginal compute cost for it.
- **Authority**: the output is a pricing candidate only. Entitlements are issued by TV/TVC.

```bash
python3 -I stegverse/tier_pricing.py \
  --cost-basis-dir <StegVerse-Labs/.github checkout>/cost-basis/worker-runtime \
  --rate-card pricing/rate-card.candidate.json --policy pricing/policy.candidate.json \
  [--market comparables.json] [--observations observed.json] --output pricing/candidate-report.json
```

## Cost-component registry

`stegverse/cost_registry.py` is the generalized cost model the pricing basis rests on.

- **Versioned and extensible.** `pricing/cost-component-registry.v1.json` (`SV-COST-COMPONENTS-2026-10-17`)
  declares each component's quantity, cited rate key, divisor and the resource it `covers`. New providers,
  units and lanes are added as components; the version changes when they do.
- **Context-sensitive.** `applies_when` selects components by execution context (`execution_locus`
  `INTERNAL` or `EXTERNAL_PROVIDER`, `provider`, ...). Internal-first execution is preferred; an externally
  billed provider call must name the `attributable_outcome_id` it serves, so its cost is attributed, not omitted.
- **Shared costs** (`attribution: SHARED`) are divided by a declared allocation basis, such as the attributable
  outcomes in the period. An unknown basis leaves the component UNKNOWN.
- **Currencies.** Rates carry their currency; another currency needs a cited `FROM->TO` FX rate.
- **No double counting.** Two applicable components covering the same resource, a duplicate component id, or
  one rate key defined by two rate cards all fail closed.
- **Reproducible.** `pricing/rate-card.five-lane-declared.json` is the five-lane experiment's declared price card
  (`SV-COST-DECLARED-2026-08-03`); the tests reproduce the four provider-lane costs of
  `SV-COST-FIVE-LANE-RESULTS-001` exactly from retained token usage. The eleven-lane analysis is the intended expansion.
- **No authority.** No estimate or basis approves a price, issues a TV/TVC entitlement or an InTr ALLOW.

`pricing/` holds the current **candidate** inputs and report (rate card 2026-10-14, basis version 2026-10-17):

- **Rate card.** Rates are cited from GitHub's published Actions pricing:
  - $0.006 per Linux 2-core runner-minute;
  - $0.25 per GB-month of shared storage.
- **Team tier.** It covers three governance observation classes, with 1,000 actions at a 75% margin. That comes to **$72.27 per period** at the cost floor, with no market evidence yet. It is a
  `PROVISIONAL_SCENARIO`: no authentically observed cost exists yet, so it is not a final rate.
- **Organization tier.** It is `UNKNOWN_RATE_NOT_SOURCED` because no network-egress rate is cited.

Open owner decisions are tracked on StegVerse-org/StegVerse-SDK#484:

- the compute-unit definition (a GitHub runner-minute is at most a cited costing proxy, per the owner);
- the target margin;
- the plan composition;
- the cited market comparables.
