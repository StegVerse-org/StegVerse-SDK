# SDK Governance Product Mirror Handoff (gate, tier pricing, cost registry)

Updated: 2026-10-17
Repository: `StegVerse-org/StegVerse-SDK`
Coordination issue: `StegVerse-org/StegVerse-SDK#484`. Parent: `StegVerse-Labs/.github#3183`.

## Owning canonical tasks

| Surface | Goal Task ID | COSV | Registry state |
|---|---|---|---|
| Governance gate (`stegverse/governance_gate.py`, `.github/workflows/governance-gate.yml`) | `SDK-STRUCTURAL-VALIDATOR-CONSOLIDATION-001` | `60200000013002` | REGISTERED (`.github` #3181) |
| Tier pricing and cost registry (`stegverse/tier_pricing.py`, `stegverse/cost_registry.py`, `pricing/`) | `SDK-COST-DERIVED-TIER-PRICING-001` | `10300000011002` | ACTIVE, UNCLAIMED (registered by `StegVerse-Labs/.github` #3214, `60d90c48`) |

Pricing dispositions name `SDK-COST-DERIVED-TIER-PRICING-001` as `owning_existing_goal`. The goal is registered via StegVerse-Labs/.github#3214 (`60d90c48`).

## Evidence class per surface (2026-10-17)

- **Governance gate.**
  - SDK #523 is MERGED at `c0ef2db` and CI_VALIDATED: 23 checks on its exact head, including the reusable-workflow self-test.
  - Adoption outside the SDK: `StegVerse-org/LLM-adapter#420` was merged by the owner. CI_VALIDATED there: PASS / `NO_GOVERNANCE_BUNDLES_FOUND`, with 17 of 21 schemas compatible with contract 1.6.
  - Not runtime-observed.
- **Tier pricing.** SDK #527 is MERGED at `376512c`.
- **Gate disposition rework.** Open draft SDK #534 (head `4f3916a`) carries it:
  - `ALLOW` replaces `PASS`;
  - an empty bundle glob becomes `FAIL_CLOSED`;
  - the six disposition fields are emitted on every `FAIL_CLOSED`;
  - actions are pinned by commit SHA;
  - the version is 1.3.0.
  It supersedes the gate part originally in #538, which was removed from #538 to avoid a conflict.
- **Cost-component registry, the MAX rule, and pricing six-field dispositions.** These are in SDK #538, merged at `07a6a90a` (2026-10-17 16:21:47Z). Gate changes were dropped in favour of #534.

No surface here is SANDBOX_RUNTIME_OBSERVED, EXTERNAL_PROVIDER_OBSERVED, MASTER_RECORDS_RECONSTRUCTED or END_TO_END. Nothing here is complete in the terminal sense.

## Contracts

- **Gate.**
  - It is standard library only and loads SDK modules by path. It is read-only (`contents: read`).
  - It verifies portable governance bundles and classifies JSON Schemas (informational only).
  - Free-tier limits are 25 bundles and 200 schemas.
  - Dispositions: `main` still emits `PASS`/`FAIL_CLOSED` without the six fields. #534 changes this to `ALLOW`/`FAIL_CLOSED`, with the six fields and an empty glob treated as `FAIL_CLOSED`.
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
| Merge order | Owner | Owner approves merges (#3183). Lane C's suggested order was #539, #536, #534, #538, pin follow-up, #535. #538 merged at `07a6a90a` without the gate files (those stayed with #534). `StegVerse-Labs/.github` #3214 merged at `60d90c48`. |
