# SDK Governance Product Mirror Handoff (gate, tier pricing, cost registry)

Updated: 2026-10-17
Repository: `StegVerse-org/StegVerse-SDK`
Coordination issue: `StegVerse-org/StegVerse-SDK#484`. Parent: `StegVerse-Labs/.github#3183`.

## Owning canonical tasks

| Surface | Goal Task ID | COSV | Registry state |
|---|---|---|---|
| Governance gate (`stegverse/governance_gate.py`, `.github/workflows/governance-gate.yml`) | `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001` | `60200000013002` | REGISTERED (`.github` #3181) |
| Tier pricing and cost registry (`stegverse/tier_pricing.py`, `stegverse/cost_registry.py`, `pricing/`) | `SDK-COST-DERIVED-TIER-PRICING-001` | `10300000011002` | Proposed in `StegVerse-Labs/.github` #3214, open and awaiting owner merge |

Until #3214 merges, pricing dispositions name `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001` as `owning_existing_goal`. After the merge, that field moves to the pricing task in a separate change.

## Evidence class per surface (2026-10-17)

- **Governance gate.**
  - SDK #523 is MERGED at `c0ef2db` and CI_VALIDATED: 23 checks on its exact head, including the reusable-workflow self-test.
  - Adoption outside the SDK: `StegVerse-org/LLM-adapter#420` was merged by the owner. CI_VALIDATED there: PASS / `NO_GOVERNANCE_BUNDLES_FOUND`, with 17 of 21 schemas compatible with contract 1.6.
  - Not runtime-observed.
- **Tier pricing.** SDK #527 is MERGED at `376512c`.
- **Six-field actionable dispositions, cost-component registry, and the MAX rule.** SDK #538 is open at head `00fc13a`. It is SOURCE_IMPLEMENTED and CI_VALIDATED: 21 checks succeeded, deploy and live were skipped. Not merged.

No surface here is SANDBOX_RUNTIME_OBSERVED, EXTERNAL_PROVIDER_OBSERVED, MASTER_RECORDS_RECONSTRUCTED or END_TO_END. Nothing here is complete in the terminal sense.

## Contracts

- **Gate.**
  - It is standard library only and loads SDK modules by path. It is read-only (`contents: read`).
  - It verifies portable governance bundles and classifies JSON Schemas (informational only).
  - Free-tier limits are 25 bundles and 200 schemas.
  - Every `FAIL_CLOSED` carries the six-field `actionable_disposition`.
  - It grants no authority.
  - It runs on the caller's runner, so StegVerse bears no marginal compute cost for it.
- **Cost registry** (`pricing/cost-component-registry.v1.json`, version `SV-COST-COMPONENTS-2026-10-17`).
  - Components are context-sensitive (`INTERNAL` first, or `EXTERNAL_PROVIDER` per provider).
  - Rates are cited and carry their currency; any other currency needs a cited FX rate.
  - Shared costs are allocated over a declared basis.
  - Double counting fails closed.
  - An externally billed provider call must name the `attributable_outcome_id` it serves.
  - UNKNOWN is never zero.
- **Pricing basis (owner invariant).**
  - `C_pricing = max(C_estimated, C_authentically_observed)`, applied for the same scope, currency, unit and `cost_basis_version`.
  - Both operands are preserved.
  - With one operand the result is `PROVISIONAL_SCENARIO`.
  - `final_price_approved` is always false.
- **Foundation.**
  - `SV-COST-FIVE-LANE-RESULTS-001` (GCAT-BCAT-Engine/workflows@85109c9). Its four provider-lane costs are reproduced exactly by `tests/test_cost_registry.py`.
  - Expansion: `SV-COST-ELEVEN-LANE-RESULTS-001`. Lanes 10 and 11 (GLM) are pending, and Z.ai is excluded until a request-bound rate card is verified.

## Authority separation

Cost calculation, commercial price and execution authority are separate:
- No result approves a price, issues a TV/TVC entitlement, or yields an InTr ALLOW.
- GitHub Actions has no runtime authority.
- No external machine, second device or always-on receiver is a predicate.
- No new dependency.

## Open items and next actions

| Item | Owner | Retry entrypoint / next action |
|---|---|---|
| Authentically observed cost per task class | `ORGANIZATION-BATCH-CUSTODY-REPLAY-001` | Receipt-backed `stegverse.cost-observation.v1` records, passed as `tier_pricing.py --observations`. Until they exist, every price is `PROVISIONAL_SCENARIO`. |
| Compute-unit definition, 75% margin, tier composition, final rate | Owner | Approve once there is validated cost coverage. A GitHub runner-minute is a cited costing proxy only. |
| Network egress rate and market comparables | Owner (sources) | Cited `https` sources with `observed_at`. The Organization tier stays `UNKNOWN_RATE_NOT_SOURCED` until then. |
| Gate and pricing invoked directly by CI, not selected by a manifest | Review query (#3183 acknowledgement) | Neither changes state. Expose them as manifest capabilities if the review requires it. |
| Merge #538 and `.github` #3214 | Owner | Owner approves merges (#3183). |
