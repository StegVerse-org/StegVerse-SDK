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

## One-command SDK execution

After installing the SDK with the governed-test dependencies, the complete package-level path is:

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

This one command builds and validates `stegverse.ingress-manifest.v1`, binds governance to the installed `stegverse.route.canonical-governed.v1`, executes the canonical local governed test, records custody, returns the `manifest_receipt_id`, and performs replay plus reconstruction against that receipt by default.

Use `--no-replay` or `--no-reconstruct` only when deliberately requesting a reduced local run. Caller-facing return depth does not suppress canonical custody.

## Real test substitution rule

The included governance request is a runnable SDK-path example. For the actual ELAN experiment, replace its example governance facts with the represented facts applicable to the experiment. Do not duplicate, reinterpret, or invent ELAN-native internal semantics inside the governance request.

## Completion proof

The SDK completion gate requires exact-head evidence that the external-framework runner and public fixtures validate, source-native data remains unchanged, preregistration metadata remains outside the decision request, the route fails closed on invalid declarations, and a real governed-test installation can produce custody, receipt, replay, and reconstruction evidence.
