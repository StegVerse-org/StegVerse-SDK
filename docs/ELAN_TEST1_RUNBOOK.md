# ELAN Test 1 Runbook

This runbook defines the first external-framework interoperability test for the SDK completion gate.

## Fixed human-event sequence

1. Emotional ambiguity statement.
2. Follow-up: `I don't know.`
3. Silence for the preregistered interval.

## Source-framework boundary

ELAN remains source-native. Only observable output/state that ELAN legitimately exposes may be placed in the source payload. Missing internal state must not be inferred or invented.

## Required evidence fields

1. human event/state
2. ELAN interpretation
3. ELAN proposed or withheld behavior
4. represented state submitted for processing
5. StegVerse governance disposition and resulting transition/non-transition
6. retrospective reconstruction

## Public fixtures

```text
inspection/examples/elan-relational-state-test1.json
inspection/examples/elan-governance-request.example.json
inspection/examples/elan-evaluation-declaration-test1.json
```

The first file is source-native ELAN-observable data only. The governance request is a separate processor-specific input. The evaluator declaration is preregistered evidence metadata and is not inserted into the governance decision request.

## External tester: one-command public preparation

An external framework creator can install the public SDK surface and produce the exact validated submission bundle without access to StegCore or Master Records repositories:

```bash
stegverse external-run \
  --prepare-only \
  --input inspection/examples/elan-relational-state-test1.json \
  --governance-request inspection/examples/elan-governance-request.example.json \
  --evaluation-declaration inspection/examples/elan-evaluation-declaration-test1.json \
  --source-framework ELAN \
  --source-output-id elan-emotional-ambiguity-silence-test-001 \
  --data-class elan.relational-state.v1 \
  --return-depth full-trace \
  --output elan-test1-submission.json
```

The result is `stegverse.sdk.external-framework-submission.v1` with `status=SUBMISSION_READY`. It contains the source-native payload, processing/route declaration, preregistration metadata, and return projection. It does not fabricate a receipt or claim governed execution.

## StegVerse runtime: one-command governed execution

In an environment where the canonical pinned governed-test dependencies are installed, remove `--prepare-only` and use the same inputs:

```bash
stegverse external-run \
  --input inspection/examples/elan-relational-state-test1.json \
  --governance-request inspection/examples/elan-governance-request.example.json \
  --evaluation-declaration inspection/examples/elan-evaluation-declaration-test1.json \
  --source-framework ELAN \
  --source-output-id elan-emotional-ambiguity-silence-test-001 \
  --data-class elan.relational-state.v1 \
  --return-depth full-trace \
  --output elan-test1-complete-run.json
```

This path builds and validates `stegverse.ingress-manifest.v1`, binds governance to `stegverse.route.canonical-governed.v1`, executes the canonical local governed test, records custody, returns `manifest_receipt_id`, and performs replay plus reconstruction by default.

The canonical governed runtime currently depends on pinned StegCore and Master Records repositories that are not anonymous-public Git dependencies. That affects who can execute the private canonical runtime locally; it does not prevent an external tester from preparing the exact portable SDK submission. The SDK must not claim that `--prepare-only` is governance execution.

## Real test substitution rule

The included governance request is a runnable SDK-path example. For the actual ELAN experiment, replace its example governance facts with the represented facts applicable to the experiment. Do not duplicate, reinterpret, or invent ELAN-native internal semantics inside the governance request.

## Completion proof

The SDK completion gate requires exact-head evidence that the public external-framework preparation path works anonymously, the source-native payload remains unchanged, preregistration stays outside the governance decision request, return projection and route binding are deterministic, and unsupported/incomplete declarations fail closed. Canonical governed execution evidence remains receipt/custody/replay/reconstruction evidence from a runtime environment with the pinned dependencies installed.
