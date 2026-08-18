# Manifest Receipt Navigation Mirror Handoff

## Canonical authority

```text
goal_id: SDK-MANIFEST-RECEIPT-NAVIGATION-001
repository: StegVerse-org/StegVerse-SDK
branch: main
issue: #16
parent_handoff: SDK_MIRROR_HANDOFF.md
credential_authority: TV/TVC
github_token_runtime_authority: NONE
non-TV/TVC secret_or_token_required: false
release_task: tasks/SDK-SOVEREIGN-RELEASE-ACTIVATION-004.json
```

Live repository state, this handoff, and directly inspectable validation evidence supersede older descriptive-only navigation notes.

## Goal

Provide one public SDK governance vocabulary:

```text
000 -> SDK-owned governed demo
00  -> caller run/return preferences
0   -> neutral governed-submission selector
0A  -> raw/user public-inspection request -> canonical sovereign StegGate runtime
0B  -> stegverse.ingress-manifest.v1 -> validate/canonicalize -> canonical sovereign StegGate runtime
1   -> exact-run replay by manifest_receipt_id
2   -> exact-run reconstruction by manifest_receipt_id
```

Every executable path remains non-authorizing at the SDK boundary. Canonical governance is StegCore/StegGate and canonical exact-run custody is Master Records.

## Installed execution surfaces

```text
stegverse/governance_navigation.py
stegverse/governance_fallback.py
stegverse/governed_operations.py
stegverse/governance_ingress_runtime.py
stegverse/governance_ingress_cli.py
stegverse/cli.py
stegverse/demo_data/manifest_000_governance_outcomes.json
```

Focused tests:

```text
tests/test_governance_navigation.py
tests/test_governance_fallback.py
tests/test_governance_fallback_cli.py
tests/test_governed_operations.py
tests/test_governance_public_execution.py
tests/test_governance_ingress_runtime.py
tests/test_cli_preformatted_manifest.py
```

## 0A / 0B / 1 / 2 primary console

The primary `stegverse governance` console is source-wired to the canonical sovereign runtime for both submission forms and subsequent replay/reconstruction:

```bash
stegverse governance --select 0A --input <public-inspection-request.json>
stegverse governance --select 0B --manifest <stegverse.ingress-manifest.v1.json>
stegverse governance --select 1 --manifest-receipt-id <MR-...>
stegverse governance --select 2 --manifest-receipt-id <MR-...>
```

The umbrella `--select 0` remains a neutral chooser and does not select either input representation implicitly.

Explicit `0A` and `0B` menu selections normalize to option `0` for navigation-usage observation. Menu observation remains distinct from the actual governed operation and cannot become authority.

The permanent degraded-mode fallback remains separate and may be selected only for pre-governance runtime/transport failure. A genuine `ALLOW`, `DENY`, `REVIEW`, or `FAIL_CLOSED` result is never reinterpreted by fallback selection.

## Option 0B — executable ingress binding

The 0B implementation predates the primary-console integration and is evaluator-neutral:

```text
27db574578b92638f82e7d8e06fb82c37a698a1e  Install canonical 0B and 000 sovereign runtime binding
0ea923b93b2c1cbca72aebe60f0ccd69e5d67c66  Test canonical 0B and 000 sovereign runtime binding
2fceb484bb972ec9c63fd071c0a476c825facd76  Expose executable SDK 000 and 0B canonical runtime entry
```

`validate_external_manifest()` validates and canonicalizes the published `stegverse.ingress-manifest.v1` structure. Executable 0B input uses the existing profile `extensions` surface for the complete canonical StegGate request:

```text
extensions.stegverse_governance_request
```

The SDK does not synthesize missing judgment/signal/execution evidence or invent alternate routing semantics.

Before execution:

1. `validate_external_manifest()` validates/canonicalizes the ingress manifest.
2. The governance-request candidate hash must exactly equal the ingress-manifest candidate hash.
3. Source framework, source instance/output ID, ingress profile/version, and canonical manifest hash are copied into non-authorizing `declared_context.sdk_ingress_manifest_identity` and public input metadata.
4. `authority_claim=false`; external consequence remains disabled by this public validation surface.
5. The resulting public request is delegated to `stegverse.sovereign_validation_runtime`.

Accepted profile defaults/canonical forms may be normalized. Invalid, incomplete, conflicting, or unsupported manifests fail closed. Structural validity never means `ALLOW` and never grants execution authority.

Standalone executable entry remains:

```bash
python -m stegverse.governance_ingress_cli 0B <manifest.json> \
  --custody-db ./stegverse-master-records-validation.db
```

## Option 000 — executable safe canonical demo

The SDK-owned dataset remains:

```text
stegverse.000-demo-dataset.v1
```

It contains exactly one teaching example each of `ALLOW`, `DENY`, `REVIEW`, and `FAIL_CLOSED`. Those examples remain data, not four actual decisions.

`build_000_public_request()` constructs an explicit complete bounded StegGate request for the demo-only candidate. It declares:

```text
demo_only=true
external_side_effect=false
authority_effect=NONE
continuity.required=false
approval.required=false
```

The actual run is delegated to the same canonical sovereign runtime used by the ordinary path. The static `demo_output_manifest_shape()` intentionally remains `PENDING_RUNTIME_BINDING`; only `run_000_demo()` replaces that state after it receives a canonical runtime result with receipt/custody fields.

Executable entry:

```bash
python -m stegverse.governance_ingress_cli 000 \
  --custody-db ./stegverse-master-records-validation.db
```

This preserves the anti-false-completion invariant: embedding a dataset is not represented as processing it.

## Caller projection / custody separation

```text
return_projection -> user-disclosable transition receipt projection
manifest_labels   -> user-facing explanatory labels
Master Records    -> canonical custody independent of both
```

Neither projection control grants authority or suppresses canonical custody.

## Cross-repository owners

```text
StegVerse-Labs/StegCore
  canonical StegGate evaluation and receipt semantics

master-records/orchestration
  exact-run custody and reconstruction

StegVerse-org/LLM-adapter
  governed machine ingress/transport where applicable

StegVerse-Labs/TV + StegVerse-Labs/TVC
  credential/release/route authority where credentials are required
```

No second evaluator, custody registry, credential authority, or receipt-ID authority is created here.

## Primary-console completion — 2026-08-18

PR #48 closed the remaining primary-console integration gap without creating a duplicate ingress implementation:

```text
PR: #48
merge: 2e290522cc0f588308d647b8a11140316bbb8bd8
primary CLI 0B selector: INSTALLED_MERGED
primary CLI --manifest operand: INSTALLED_MERGED
0A explicit selector: INSTALLED_MERGED
0A/0B usage-observation normalization: INSTALLED_MERGED
README stale 0B-unavailable statement: CORRECTED_MERGED
person-specific route/processor/capability introduced: FALSE
```

The first attempted validation exposed a test-fixture defect rather than a production-code defect: the explicit-0A unit mock omitted fields required by `GovernedOperations`. The fixture was corrected, and the exact final PR head then passed all three triggered non-authorizing workflows.

Validation on PR head `aedc5e21629739f36fefa62f8185fae211800a73`:

```text
Evaluator Manifest Source Validation (Non-Authorizing)
  run: 32188709072
  result: SUCCESS
  public inspection request tests: PASS
  public inspection governed binding tests: PASS
  governance ingress runtime tests: PASS (6)
  primary CLI preformatted-manifest tests: PASS (3)
  evaluator boundary contract tests: PASS
  compile ingress/evaluator modules: PASS

Evaluator Contract Console Validation
  run: 32188708980
  result: SUCCESS

SDK Usage Observability Validation
  run: 32188708972
  result: SUCCESS
```

These workflows validate source behavior only. They do not constitute runtime, release, custody, or evaluator authority.

## Remaining executable tasks

The generic 0B implementation and primary-console integration are no longer open source tasks. Remaining downstream proof/release work is distinct:

```text
1. obtain an actual canonical 000 run receipt when that demo evidence is required;
2. obtain an actual external 0B canonical run receipt when an external test is executed and retain ingress identity in exact-run evidence;
3. TV/TVC-authorized release/package flow publishes and verifies any distribution release that is required for a frozen aggregate test/replay set;
4. replay/reconstruction uses the retained manifest_receipt_id and exact historical run provenance rather than substituting a later release.
```

An external 0B test run is itself a valid way to produce item 2; absence of a prior external run does not mean the generic ingress source is unimplemented.

## Completion accounting

Current navigation/execution source denominator:

```text
1 000/00/0/0A/0B/1/2 navigation: COMPLETE
2 0A canonical source execution: COMPLETE_VALIDATED
3 0B canonical source execution: COMPLETE_VALIDATED_MERGED_PRIMARY_CLI
4 1 replay source execution: COMPLETE_VALIDATED
5 2 reconstruction source execution: COMPLETE_VALIDATED
6 permanent canonical fallback: COMPLETE_SOURCE
7 000 complete bounded runtime binding: COMPLETE_SOURCE
8 generic ingress focused source validation: COMPLETE
9 distributed TV/TVC-authorized release verification: SEPARATE_RELEASE_STATE
10 exact external/evaluator execution evidence: PRODUCED_BY_ACTUAL_EXTERNAL_RUN
```

```text
developed files required for current generic ingress source scope: COMPLETE
scaffolding/stubs for generic 0B ingress: 0
primary CLI integration: COMPLETE_VALIDATED_MERGED
generic 0B source validation: PASS
external exact-run evidence: NOT PRETENDED; produced when the external manifest is actually run
release/tag identity: separate from ingress readiness and retained with exact-run/replay/reconstruction provenance
```

## Archive / continuation boundary

Generic preformatted-manifest ingress no longer requires a chat-owned implementation continuation. Future external runs supply their own manifests through the published generic path. Any release/tag, exact-run custody, replay, reconstruction, or product activation state remains governed by its own evidence and authority and must not be inferred from this source completion.