# SDK Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
credential_authority: TV/TVC
GitHub token runtime authority: NONE
non-TV/TVC secret or runtime token required: FALSE
```

Live repository state, immutable commits, retained validation evidence, scoped mirror handoffs, and this file supersede prior chat claims.

## Canonical SDK goal state

```text
SDK-PUBLIC-CONSOLE-001: COMPLETE_RELEASED
SDK-GENERAL-EVALUATION-RELATIONSHIP-001: COMPLETE_RELEASED
SDK-NO-GITHUB-AUTHORITY-003: COMPLETE_RELEASED
SDK-PUBLIC-INSPECTION-ENTRY-001: COMPLETE_VALIDATED_MERGED
SDK-PUBLIC-INSPECTION-GOVERNED-BINDING-002: COMPLETE_STATIC_VALIDATED_MERGED
SDK-PUBLIC-INSPECTION-GOVERNED-TEST-004: SUPERSEDED_BY_CUSTODY_BACKED_RUNTIME
SDK-PUBLIC-INSPECTION-CUSTODY-REPLAY-005: COMPLETE_SOVEREIGN_VALIDATION
SDK-SOVEREIGN-PRODUCTION-VALIDATION-008: COMPLETE_VALIDATION_EVIDENCE_RETAINED
SDK-PREFORMATTED-MANIFEST-INGRESS-0B: COMPLETE_SOURCE_VALIDATED_MERGED_PRIMARY_CLI
SDK-AUTHORITY-BOUNDARY-PRESERVATION-001: ACTIVE_RUNNER_SOURCE_VALIDATED_PENDING_SOVEREIGN_EXECUTION
SDK-AUTHORITY-BOUNDARY-SOVEREIGN-RUN-002: COMPLETE_RELEASED_TO_MACHINE_EXECUTION
SDK-USAGE-GOVERNED-OPERATION-WIRING-002: COMPLETE_VALIDATED_MERGED
SDK-MCP-PORTABLE-AUTHORITY-001: SOURCE_VALIDATED_DEFECTS_CORRECTED_EXACT_SOVEREIGN_ARTIFACT_RUN_PENDING
SDK-README-PUBLIC-SHARE-001: COMPLETE_VERIFIED_MERGED
SDK-ADMISSIBILITY-MATRIX-MATURITY-001: COMPLETE_VALIDATED_MERGED_CONSOLIDATED
SDK-ADMISSIBILITY-COMPOSITION-002: COMPLETE_VALIDATED_MERGED_CONSOLIDATED
```

No person-specific evaluator route is canonical.

## Governing invariants

```text
every successful governed SDK transition is retained through canonical Master Records custody
manifest establishes intended route
recorded checkpoint receipt clears the next manifest leg
successful governed SDK run without Master Records custody: PROHIBITED
successful replay/reconstruction return without operation-transition custody: PROHIBITED
caller projection may suppress Master Records custody: FALSE
manifest_receipt_id grants authority: FALSE
third_party_host_required: FALSE
GitHub grants runtime authority: FALSE
credential authority: TV/TVC
```

## Canonical governance navigation

```text
000 -> optional worked transparency/demo
00  -> optional return/explanation configuration
0   -> ordinary governed submission selector
0A  -> raw/user request manifested by SDK
0B  -> preformatted stegverse.ingress-manifest.v1 validation/canonicalization/execution
1   -> replay by manifest_receipt_id
2   -> reconstruction by manifest_receipt_id
```

`000` and `00` are optional human inspection surfaces and are not prerequisites for machine-to-machine evaluation.

Primary executable 0B entry after PR #48:

```bash
stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>
```

The existing standalone executable entry remains:

```bash
python -m stegverse.governance_ingress_cli 0B <manifest.json>
```

0B reuses the existing evaluator-neutral manifest validator and canonical sovereign runtime binding. It does not create a second evaluator, route implementation, governance engine, credential authority, or custody path. A supplied manifest is validated/canonicalized when representable; invalid, incomplete, conflicting, or unsupported input fails closed.

## Sovereign SDK route

```text
SDK entry
-> Core-Lite manifested route carrier
-> Master Records MRR-* checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate + commit-coherence evaluation
-> Master Records MR-* exact-run custody
-> return ingestion/CGE
-> Master Records MRR-* return custody
-> SDK return
```

Replay and reconstruction are separately recorded operations and do not re-execute the original consequence.

## MCP production-artifact testing

Scoped source of truth:

```text
MCP_PORTABLE_AUTHORITY_MIRROR_HANDOFF.md
tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
reports/mcp-production-artifact/local-integration-diagnostic-20260815.json
StegVerse-org/StegVerse-SDK#30
```

The MCP lane is now source-complete and defect-corrected on main. Active testing found and corrected two actual canonical-intake defects rather than leaving the integration requirement descriptive:

```text
PR #32 merge: 8b7d2f81591a1388277ba55e5e64210de65dc877
validation run/job: 31889450763 / 95023440401 SUCCESS
focused tests: 9/9 PASS

PR #33 merge/current tested source: e4733a41805bcb546b97ad079d9fa75d26ef266d
validation run/job: 31889542545 / 95023659790 SUCCESS
```

The corrected authority boundary is:

```text
caller MCP request external_consequence_enabled=false
caller authority_claim=false
public input carries exact MCP contract/call hashes, tool label, and phase only
full MCP packet is bounded-consequence metadata, not caller authority
actual MCP tools/call is injected only as the canonical consequence executor
StegCore invokes that executor only after StegGate ALLOW + commit-coherence ALLOW
```

A credential-sanitized source-equivalent local integration diagnostic traversed the full executable logic and produced ALLOW, verified transaction continuity, RECORDED MR/MRR/MRO-equivalent custody, replay/reconstruction no-reexecution, and a governed bounded-write `UPDATED / bounded_value=42` result. The process carried no GitHub/token/secret credential-like environment keys.

That diagnostic is intentionally **not** promoted to canonical exact-artifact PASS because this chat execution surface did not materialize the private Master Records package through an authorized TV/TVC path. The exact sovereign run remains the final activation gate. No GitHub/private-repository token workaround is authorized.

## Authority-boundary preservation extension

Tracking issue: `#25`.

Source implementation and non-authorizing source validation are complete and released to its own canonical sovereign execution lane:

```text
workflow: Authority Boundary Source Validation (Non-Authorizing)
run: 31838347112
job: 94889598424
head: e629fa05f14a7b09a393417b179895e18095dcaf
result: SUCCESS
fixture validator: AUTHORITY_BOUNDARY_PRESERVED
tests: 3 passed
process GITHUB_TOKEN present: false
process GH_TOKEN present: false
production_activation_role: NONE
```

The exact participant-neutral fixture still requires sovereign MR/MRR/MRO execution/custody before that extension is complete. This work remains a repository-native SDK/Master Records workstream; it is not an archive dependency of the superseding current-session v7 inventory unless a new user goal explicitly reopens it.

Do not conflate this extension with the original frozen T0/T1-A/T1-B evaluator run. The canonical Master Records custody handoff separately records retained sovereign exact-run, manifested-route, replay, and reconstruction evidence for the frozen run.

## Local model/runtime convergence

The descriptive local-runtime-selection step and formal local-model-development requirement are complete/released under:

```text
StegVerse-002/micro-node-runtime/docs/SOVEREIGN_LOCAL_MODEL_RUNTIME_MIRROR_HANDOFF.md
formal model: stegverse-reference-lm-v1 COMPLETE_RELEASED
local discovery/private launch/real inference/usage/proof: COMPLETE_RELEASED
canonical validation: 31339534741 SUCCESS
persistent endpoint validation: 31384116055 SUCCESS
github_token_required: false
third_party_inference_required: false
credential authority: TV/TVC
```

No SDK/chat implementation claim remains for that source work. Live activation is separately machine-owned.

## SDK usage observability

Actual governed option `0`/`1`/`2` observation wiring is validated and merged. Explicit primary-console `0A` and `0B` selections normalize to the existing option-`0` navigation observation code; actual governed operation identity remains determined by returned canonical evidence rather than menu selection.

Canonical continuation remains:

```text
SDK_USAGE_OBSERVABILITY_MIRROR_HANDOFF.md
-> StegVerse-Labs/StegCore/docs/MANIFEST_RECEIPT_ID_MIRROR_HANDOFF.md / #85
-> StegVerse-Labs/TVC/tasks/TVC-SDK-USAGE-NOTIFICATION-RELAY-001.json / PR #24
-> StegVerse-Labs/StegCore#117
```

Menu selection remains distinct from actual `GOVERNED_OPERATION`. Historical totals remain `OBSERVED_ONLY` unless deterministic provenance backfill exists. The SDK holds no GitHub credential; TV/TVC owns any notification dispatch credential.

## Trade-readiness convergence

The explicitly added trade-ready goal is canonical outside the SDK:

```text
StegVerse-Labs/stegfin-governance/docs/STEGFIN_MIRROR_HANDOFF.md
StegVerse-Labs/.github/docs/STEGFIN_CONTINUITY_MACHINE_EXECUTOR_MIRROR_HANDOFF.md
StegVerse-Labs/.github/handoffs/STEGFIN-CONTINUITY-CARRIER-007.json
StegVerse-Labs/TVC/tasks/TVC-CAPABILITY-RUNTIME-002.json
```

Current product truth remains governed by those canonical owners. Wallet signing and broadcast authority remain `USER_ONLY`; TV/TVC remains credential authority. This SDK/session must not introduce a non-TV/TVC provider secret or token and must not sign or broadcast a wallet transaction.

## Admissibility relation maturity and composition — 2026-08-17

Two session-specific admissibility findings are now implemented, validated, merged, propagated where pertinent, and consolidated.

### Matrix maturity

```text
task: SDK-ADMISSIBILITY-MATRIX-MATURITY-001
handoff: ADMISSIBILITY_MATRIX_MATURITY_MIRROR_HANDOFF.md
PR: #42
merge: 7008d9702dec6318752e0f136f519a2102099f29
validation run/job: 32072609323 / 95518918887
focused tests: 29/29 PASS
claim: RELEASED_COMPLETE
```

The SDK now distinguishes an intentional `research_only` note from an unresolved consequential relation. An otherwise-complete high-consequence relation with no explicit relation coverage is `under_development` and `FAIL_CLOSED`; it no longer silently falls back to `ALLOW_AS_NOTE / research_note`.

### Composition / non-separability

```text
task: SDK-ADMISSIBILITY-COMPOSITION-002
handoff: ADMISSIBILITY_COMPOSITION_MIRROR_HANDOFF.md
PR: #43
merge: 3b0ded7a4966d52390f4623c0867721dbd84cf0f
validation run/job: 32073057367 / 95520275236
focused tests: 25/25 PASS
claim: RELEASED_COMPLETE
```

Formal invariant:

```text
Adm(A)=true
Adm(B)=true
DOES NOT IMPLY Adm(A composed_with B)=true
```

Component receipt integrity is checked before composition reasoning, component ALLOW dispositions are never lifted automatically, and absent explicit joint-relation coverage is represented as unresolved/under-development and fails closed. A validated joint-relation positive control remains non-authorizing.

Credential boundary for both validation lanes:

```text
GITHUB_TOKEN absent
GH_TOKEN absent
TV_IDENTITY_KEY absent
TVC_SECRET absent
credential authority: TV/TVC
GitHub runtime authority: NONE
```

### Downstream propagation assessment

Canonical handoffs were inspected before mutation decisions:

```text
StegVerse-Labs/Site/PWC002_MIRROR_HANDOFF.md -> VERIFIED_NO_CHANGE
GCAT-BCAT-Engine/Publisher/PWC002_MIRROR_HANDOFF.md -> VERIFIED_NO_CHANGE
StegVerse-Labs/admissibility-wiki/ADMISSIBILITY_WIKI_MIRROR_HANDOFF.md + orchestration state + issue #50 -> TRANSFERRED_TO_CANONICAL_WORKSTREAM via issue #50 comment 5320865381
StegVerse-002/stegguardian-wiki/STEGGUARDIAN_WIKI_MIRROR_HANDOFF.md -> VERIFIED_NO_CHANGE
master-records/core-lite/MASTER_RECORDS_MIRROR_HANDOFF.md -> VERIFIED_NO_CHANGE
```

Only admissibility-wiki directly required semantic transfer. The evaluator was not duplicated there. Site/Publisher do not currently establish direct consumption of the changed SDK relation contract; Guardian is downstream of bounded admissibility interpretation; Master Records custody/reconstruction contracts were not changed by this goal.

Archive-purpose session source of truth:

```text
docs/SESSION_CONSOLIDATION_2026-08-17_ADMISSIBILITY_RUNTIME_TRADE_MIRROR_HANDOFF.md
```

That record preserves the local-runtime/model convergence, trade-readiness ownership boundary, both admissibility implementations, validation evidence, downstream decisions, claim releases, and archive determination.

## Current-session scope supersession

The prior SDK session-support classification in `docs/SESSION_GOAL_INVENTORY_2026-08-14_AUTHORITY_BOUNDARY_LOCAL_RUNTIME.md` is superseded for archive purposes by the newer organization-control-plane v7 records:

```text
MERGED INTO: StegVerse-Labs/.github/docs/SESSION_ASSISTANCE_SCOPE_MIRROR_HANDOFF.md
current inventory: StegVerse-Labs/.github/control/session-goal-inventory-2026-08-14-admissible-existence-core-local-runtime-v7.json
archive receipt: StegVerse-Labs/.github/receipts/session-consolidation/SESSION-ARCHIVE-TRANSFER-G08-MACHINE-CONTINUATION-20260815.json
```

The v7 inventory defines the goals of that prior conversation as G01-G08, records local runtime/model source completion, TV/TVC-only credential authority, durable consolidation and worker assistance as complete/released, and transfers the incomplete G08 trade-ready product goal to named machine/authority owners.

The present MCP goal is separately scoped by `MCP_PORTABLE_AUTHORITY_MIRROR_HANDOFF.md` and must not be conflated with those older session workstreams or with the completed 2026-08-17 admissibility session consolidation.

## Preformatted manifest ingress reconciliation — 2026-08-18

The older README public-share audit correctly described the state that existed at the audit checkpoint, but that historical statement was later stale relative to live source. Repository history proves the generic 0B binding was installed on 2026-08-15 and subsequently exposed through its standalone executable entry:

```text
27db574578b92638f82e7d8e06fb82c37a698a1e  Install canonical 0B and 000 sovereign runtime binding
0ea923b93b2c1cbca72aebe60f0ccd69e5d67c66  Test canonical 0B and 000 sovereign runtime binding
2fceb484bb972ec9c63fd071c0a476c825facd76  Expose executable SDK 000 and 0B canonical runtime entry
b48fdaa217cf1e613d7caa6667084fe07b00155e  Reconcile SDK navigation handoff with executable 000 and 0B binding
```

PR #48 then completed the remaining primary-console integration and removed the stale public claim that 0B was unavailable:

```text
PR: #48
merge: 2e290522cc0f588308d647b8a11140316bbb8bd8
Evaluator Manifest Source Validation: 32188709072 SUCCESS
Evaluator Contract Console Validation: 32188708980 SUCCESS
SDK Usage Observability Validation: 32188708972 SUCCESS
```

The evaluator-manifest source validation explicitly exercised the existing public-inspection tests, existing 0B runtime tests, new primary-CLI 0B tests, and evaluator-boundary tests without granting runtime or release authority.

Current truth:

```text
0B canonical stegverse.ingress-manifest.v1 validation/canonicalization: INSTALLED
0B canonical sovereign runtime binding: INSTALLED
0B standalone executable module entry: INSTALLED
0B primary stegverse governance CLI entry: VALIDATED_MERGED
README 0B availability disclosure: CORRECTED
person-specific evaluator route introduced: FALSE
```

Scoped continuation: `docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md`.

## README public-share verification — historical checkpoint 2026-08-16

Canonical historical evidence remains:

```text
validation/README_PUBLIC_SHARE_VERIFICATION_2026-08-16.md
README correction commit: bff85fe5323fc6c5ab772f0f1456e8a449d8c701
verification retention commit: b9847be00423a8b49ff5099b95875ae3d938dd32
status_at_checkpoint: PASS_AFTER_CORRECTION
```

Its statement that 0B was not installed is retained as historical evidence of that audit checkpoint only and is superseded for current product status by the 2026-08-15 implementation commits and PR #48 reconciliation above.

## Session consolidation / archive condition

For the 2026-08-17 admissibility/runtime/trade session:

```text
unique session goals durable: 5/5
session-owned active claims: 0
unassigned session work: 0
propagation targets assessed: 5/5
chat-only requirements remaining: 0
canonical continuation recorded: true
archive state: COMPLETE_ARCHIVE_READY
```

Canonical archive-purpose continuation:

```text
docs/SESSION_CONSOLIDATION_2026-08-17_ADMISSIBILITY_RUNTIME_TRADE_MIRROR_HANDOFF.md
ADMISSIBILITY_MATRIX_MATURITY_MIRROR_HANDOFF.md
ADMISSIBILITY_COMPOSITION_MIRROR_HANDOFF.md
tasks/SDK-ADMISSIBILITY-MATRIX-MATURITY-001.json
tasks/SDK-ADMISSIBILITY-COMPOSITION-002.json
```

Separately existing SDK exact MCP artifact execution remains owned by:

```text
MCP_PORTABLE_AUTHORITY_MIRROR_HANDOFF.md
tasks/SDK-MCP-CANONICAL-VALIDATION-009.json
reports/mcp-production-artifact/local-integration-diagnostic-20260815.json
issue #30
```

Do not mark MCP activation complete until the exact declared production artifacts produce retained MR/MRR/MRO evidence. Do not use GitHub/private-repository credentials to manufacture that proof. That separate machine/authority-owned workstream is not an archive dependency of the completed 2026-08-17 session.


## Evaluator-neutral R3 response/run surface — 2026-08-26

The active R3 evaluation-boundary continuation now has a neutral repository-facing execution and packet surface. External evaluator identity is not encoded into route IDs, task IDs, packet schemas, active filenames, test names, or runtime modules.

Active scoped handoff:

\`docs/EVALUATION_BOUNDARY_RESPONSE_PACKET_MIRROR_HANDOFF.md\`

Active task:

\`tasks/SDK-EVALUATION-BOUNDARY-R3-RUN-002.json\`

Neutral tooling:

\`\`\`text
scripts/run_evaluation_boundary_r3.py
scripts/build_evaluation_boundary_response_packet.py
scripts/build_evaluation_boundary_owner_packet.py
tests/test_evaluation_boundary_r3_run_harness.py
tests/test_evaluation_boundary_response_packet.py
docs/EVALUATION_BOUNDARY_PACKET_README_REPRODUCE.md
docs/EVALUATION_BOUNDARY_LICENSE_ACCESS_NOTES.md
\`\`\`

The evaluator supplies the manifest for the run. The manifest is validated/canonicalized at SDK ingress, its declared route is resolved against installed published routes, current governing state is bound to that route, and the exact submitted/normalized manifest is retained with the run evidence. A repository-local evaluator-specific manifest is not an architectural prerequisite.

Historical evaluator-specific artifacts may remain immutable for reconstruction of earlier work, but they are not active execution/coordination surfaces and must not be propagated into new repository artifacts.

Current R3 runtime state remains nonterminal:

\`\`\`text
aggregate release set EVALUATION-BOUNDARY-2026-08-19-R3: NOT RELEASED
verified aggregate receipt: NOT PRESENT
exact governed SDK-ingress run: NOT EXECUTED
custody/reconstruction/replay packet: NOT PRESENT
\`\`\`

Source neutralization does not satisfy release, runtime, custody, independent verification, deployment, activation, or propagation gates.


## Active Evaluation Boundary R3 release/runtime dependency — 2026-08-26

Scoped continuation:

\`\`\`text
handoff: docs/EVALUATION_BOUNDARY_RESPONSE_PACKET_MIRROR_HANDOFF.md
task: tasks/SDK-EVALUATION-BOUNDARY-R3-RUN-002.json
tracking: #47
frozen SDK coordinate: stegverse-sdk 1.1.0
frozen commit: 922d6c5235229e854c36e1a194dc99ed15a31b51
neutral harness source: COMPLETE_VALIDATED_MERGED
governed R3 execution: NOT_EXECUTED
\`\`\`

The upstream TVC resident progression wrapper is source-complete/validated/merged (TVC PR #122, run/job 32808276832 / 97682545418 SUCCESS, 50 PASS, merge f4b5d83b57e12c8d83bd25a68a12d93496de2074), and TVC has reverified frozen component lineage plus current-main identity of the guarded release source.

That source completion does not satisfy the SDK run gate. Still required before the real evaluator-supplied manifest may execute:

\`\`\`text
current bounded TV/TVC grant + resident credential
exact admitted TVC source-validation report
four exact immutable tag/release bindings
stegverse-sdk 1.1.0 wheel/sdist + Trusted Publisher provenance
verified TVC aggregate release receipt
\`\`\`

Once the aggregate receipt exists, the SDK lane proceeds with the already-pinned neutral harness, exact evaluator manifest retention, canonical route execution, Master Records custody, reconstruction, independent verification, and tamper-negative evidence. Moving current main or substituting another runtime does not satisfy that proof.
