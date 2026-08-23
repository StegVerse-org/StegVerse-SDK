# Governed Application Spine Mirror Handoff

## Source of truth

```text
repository: StegVerse-org/StegVerse-SDK
issue: #61
branch: feat/governed-application-spine-61-r1
role: non-authorizing composition contract for SDK -> SPE -> StegGate -> return/reconstruction
```

Live repository state, issue/PR state, workflow results, and canonical downstream handoffs supersede prose summaries.

## Goal

Make SDK, SPE, and canonical StegGate/AdmittedCode operate as one reusable application-neutral lifecycle while preserving each component's authority boundary.

## Canonical order

```text
external/user/model/tool/OSS capability
  -> SDK manifestation / DECLARED candidate
  -> SPE fresh standing determination
  -> canonical StegGate present-tense admissibility + commit coherence
  -> bounded executor only when all required gates allow
  -> return ingestion
  -> replay/reconstruction/discovery
  -> custody only where separately admitted
```

This ordering is derived from the existing live contracts:

- SDK-to-SPE candidates retain `admissibility_result=PENDING` and `commit_time_validity=PENDING` and require a fresh standing determination.
- SPE ALLOW grants standing only and explicitly does not authorize execution.
- StegCore admissibility requires current standing when applicable together with current authority, continuity, governing conditions, attributable consequence, and reconstructability.

## Slice 1 installed on this branch

```text
schemas/governed_application_spine.v1.schema.json
stegverse/governed_application_spine.py
tests/test_governed_application_spine.py
docs/GOVERNED_APPLICATION_SPINE_MIRROR_HANDOFF.md
```

The SDK validator is deliberately non-authorizing. It does not evaluate SPE, run StegGate, execute an action, create custody, or mint standing/admissibility.

## Enforced invariants

```text
SDK candidate authorizing == false
SDK authority == NONE
SPE execution authority == NONE
model output authority == NONE
historical AdmittedCode/code-admit-gate runtime authority == NONE
canonical StegGate runtime identity == stegverse:steggate:canonical:three-layer:v1
```

If `execution.performed == true`, the contract requires all of:

```text
standing.state == ALLOW
standing.standing_current == true
admissibility.state == ALLOW
admissibility.commit_time_validity == CURRENT
admissibility.commit_coherence == ALLOW
executor_ref present
result_hash present
```

Therefore an SPE ALLOW receipt cannot be interpreted as execution authority, and a stale standing result cannot cross the consequence boundary.

## Open-source / commodity capability rule

Applications should prefer:

```text
adopt -> adapter -> govern -> verify
```

for commodity OCR, document parsing, RAG, vector search, chat UI primitives, image decoding, model serving, math parsing/solving, and file-upload mechanics.

OSS/provider output is a candidate or interpretation state only. It acquires no standing, admissibility, execution, custody, legal, financial, publication, deployment, or other authority by being produced successfully.

A bespoke StegVerse implementation should be retained only where no suitable implementation exists, licensing/security/privacy requires it, governance cannot be preserved through an adapter, sovereign/offline requirements cannot be met, or a deliberately small conformance/reference/fallback implementation is useful.

## Collision boundaries

- `StegVerse-Labs/StegCore` remains canonical StegGate/admissibility owner.
- `StegVerse-Labs/Standing-Proof-Engine` remains standing owner.
- `master-records/*` remains custody/reconstruction authority where applicable.
- SDK remains intake/compatibility/composition only.
- StegCore PR #141 is active on manifested transaction/capability context; do not mutate its transaction-lifecycle paths from this SDK slice.
- AdmittedCode/code-admit-gate is historical/reference only; current runtime is StegCore.
- TV/TVC only for credentials; GitHub-token runtime authority NONE.
- no new heartbeat, provider runtime, scheduler, evaluator, custody service, or receipt authority.

## Remaining source slices

1. Validate/merge this composition schema + SDK validator.
2. Add SDK SPE-return consumer that verifies receipt identity/hash/scope/currentness and constructs a **non-authorizing canonical StegGate request candidate**.
3. After StegCore PR #141 is reconciled, add the StegCore bridge consuming the exact SPE receipt/hash and failing closed on missing/stale/mismatched standing when required.
4. Preserve `package_id`, `transition_id`, `run_id`, SPE receipt, StegGate decision, and bounded-execution evidence through return ingestion/discovery and Master Records handoff.
5. Add application adapter interface for commodity capabilities: source state -> candidate interpretation/action -> governed spine.
6. Migrate Ecosystem Chat/VACC/Math/HIL first.
7. Add portable independent verifier.
8. Demonstrate one OSS-backed interpretation capability and one consequence-bearing capability end-to-end with replay/reconstruction PASS.

## Completion boundary

This goal is not complete on schema merge. Full completion requires a real capability to traverse the composed live lifecycle with fresh SPE standing, canonical StegGate evaluation, bounded consequence only when allowed, return ingestion, replay/reconstruction PASS, and portable independent verification.
