# SDK expected-capability matrix

This matrix binds the version roadmap's expected capabilities to the
evidence that establishes them in this repository. It is the
expectation the tests run against: an expectation is written first,
and no grade is claimed above the evidence named for it.

Source roadmap: `ECOSYSTEM_SDK_MANIFEST_PUBLISHER_VERSION_ROADMAP.md`
(revised 2026-09-25 from exact repository source; filed in the
StegVerse coordination record). Versions after the existing release
candidate are proposals until independently admitted and authorized
through the canonical Task Registry and native component owners.

## Grading ladder

| Grade | Meaning |
|---|---|
| DECLARED | The capability is written in the roadmap or source docs. |
| SOURCE_QUALIFIED | Source implementation exists and source-level tests pass against it. |
| RUN_ESTABLISHED | An authentic runtime run produced the capability's dispositions and receipts. |
| DEMO | The capability is packaged as a runnable, receipt-producing demonstration. |

A grade is per capability, never for a version as a whole, and no
overall PASS may conceal a missing requested capability.

## Version expectations

### SDK 1.3.0 — existing frozen release candidate

- Expected: existing generic manifests, published evaluator
  contracts, installed processor/route foundations, previously
  validated manifest-only experiments.
- Acceptance gate: exact authorized TV/TVC release/tag/package
  publication evidence.
- Evidence on file: `VERSION.json` — `version_stage` is
  `RELEASE_CANDIDATE`, `release.tag` is null, `release_evidence` is
  empty, `release_candidate.tag_publication` is
  `READY_PENDING_TV_TVC_EXECUTION`, and the candidate's artifact and
  four-stage manifest-only validation runs are recorded PASS at the
  candidate head.
- Grade: SOURCE_QUALIFIED at the candidate head. The release gate is
  OPEN: no tag or release exists, and GA must never be claimed until
  the gate's evidence exists. Current `main` is the 1.4 development
  line and is not the frozen candidate.

### SDK 1.4.0 — moving development line

- Expected: provider-neutral source-observation guards and
  preflight; the same public manifest/route path for arbitrary
  external observations; evidence-preserving failure semantics.
- Acceptance gate: two structurally different generic source
  fixtures, a deliberate false-attribution failure, valid
  public-builder output, an authentic route result or an exact
  runtime failure receipt, and preserved predecessor/replay/
  reconstruction at the actually observed scope.
- Evidence on file: source-observation extension merged (SDK PR
  #340); `tests/test_source_evidence_packet.py` covers forged
  authority rejection and multi-condition packets at source level.
- Grade: SOURCE_QUALIFIED in part. The gate fixture set has not been
  run as a set, and authentic cross-boundary execution is not
  thereby proven. `VERSION.json` carries the line as `1.4.0.dev0`
  with `release_identity: false`.

### SDK 1.5.0 — proposed: capability discovery and adaptation

- Expected: evaluator-defined multi-condition experiments;
  discoverable installed-capability matrix; per-requirement
  feasibility results; immutable manifest-derived execution plans;
  standardized evidence packets; repeatable independent
  verification; general adaptation without a bespoke processor for
  each framework.
- Required demonstration: two unrelated framework evaluators use
  the same public interface, and every requirement receives its own
  SUPPORTED, MISSING_INPUT, UNSUPPORTED, PROBE_REQUIRED, or
  VERSION_INCOMPATIBLE result with evidence.
- Evidence on file: `stegverse/capability_inventory.py`
  (`qualify_requirements`, schema
  `stegverse.sdk-capability-qualification/v1`),
  `stegverse/manifest_plan.py` (`derive_execution_plan`,
  `verify_plan_lineage`), `stegverse/source_evidence_packet.py`;
  tests `tests/test_capability_inventory.py`,
  `tests/test_manifest_plan.py`,
  `tests/test_source_evidence_packet.py`, and the demonstration
  binding in `tests/test_expected_capability_matrix.py`.
- Grade: SOURCE_QUALIFIED. RUN_ESTABLISHED is not claimed:
  `sdk.capabilities.json` records `current_main_result` as
  `not_observed`, `release_ready: false`, and
  `production_binding_enabled: false`, and those fields govern
  until an authentic run replaces them.

### SDK 1.6.0 — proposed: extensibility, interoperability, portability

- Expected: governed registration of versioned
  extensions/processors; broader protocol interoperability;
  portable, local-first evaluator deployment; full
  manifest-declared Publisher delivery and far-side evidence where
  available.
- Required demonstration: an independent third party reproduces a
  supported end-to-end workflow using public release artifacts and
  original evidence, without privileged internal scripts or a
  second user-controlled device.
- Grade: DECLARED. The demonstration has not been run.

### SDK 1.7.0 — UNDEFINED

- No feature allocation for 1.7.0 exists in the roadmap. Its
  expected capabilities must be defined first; only then test,
  freeze, tag, and release. Nothing in this matrix assigns 1.7.0 a
  capability.

## Current-main baseline (evidence, not a release claim)

Full test suite at `a3237c1f91a7a7b5ac80c7202f604e1e414ecaaa`
under pytest 9.2.0: 2365 passed, 12 failed, 45 skipped. The 12
failures are pre-existing on current main and are recorded here so
the freeze cycles start from the true state:

- `tests/test_000_governance_outcome_demo.py` (3)
- `tests/test_evaluator_atomic_task_worker_manifest.py` (3)
- `tests/test_github_fallback_boundary.py` (1)
- `tests/test_mir_destination_profile_propagation.py` (1)
- `tests/test_site_sdk_processing_handoff.py` (4)

The two receipt-producing demonstrations run clean at the same
head: `examples/admissibility_bundle_demo.py` (bundle valid) and
the Communication Edge SDK demo (hash-bound edge-execution
receipt, simulation bounds declared).
