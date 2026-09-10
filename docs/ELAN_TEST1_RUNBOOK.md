# ELAN Test 1 Runbook

This runbook defines the first external-framework interoperability test for the SDK completion gate while preserving the distinction between controlled state establishment and the condition actually under evaluation.

## Experimental structure

The three-event protocol is not three independent behavioral tests.

```text
S0 -> Event 1 -> S1 -> Event 2 -> S2 -> Event 3 (no new human input for the preregistered interval) -> observe resulting state/behavior
```

Events 1 and 2 are controlled state-establishment conditions. Their purpose is to establish the relational trajectory required to reach S2. Event 3 is the experimental condition: the passage of the preregistered interval with no new conversational input after S2 has been established.

A different or independently chosen lead-in is not equivalent unless it demonstrably establishes the same source-native state entering Event 3. The fixed lead-in is therefore part of the protocol, not an expected result.

## Fixed human-event sequence

1. Emotional ambiguity statement.
2. Follow-up: `I don't know.`
3. No further conversational input for the preregistered interval.

## Event 3 continuity requirement

Event 3 is valid for this protocol only when the source framework begins the silence interval from the state produced by Events 1 and 2.

If Event 3 is performed in a separate session, the evidence must state whether that session preserves/resumes the exact relevant source-native continuity from S2 or starts from a reset/reconstructed state. A reset or unverified reconstruction must not be silently treated as continuous execution.

This requirement does not prescribe what the external framework should do during silence. It only establishes which prior state is being tested.

## Source-framework boundary

ELAN remains source-native. Only observable output/state that ELAN legitimately exposes may be placed in the source payload. Missing internal state must not be inferred or invented.

The SDK must not pre-author or inject any of the following into the authentic experiment path:

- an expected ELAN interpretation;
- an expected ELAN behavior during Event 3;
- an expected internal state not supplied by ELAN;
- an expected agreement or disagreement with StegVerse governance;
- post-hoc semantics presented as source-native evidence.

Controlled stimuli are permitted when they are required to establish the state under test. Controlled stimuli are not permission to pre-compose the expected source-framework response.

## Evidence separation

For the authentic experiment, preserve the evidence in distinct layers:

1. controlled human events and timing;
2. source-native output/state actually exposed by ELAN;
3. continuity evidence establishing the state entering Event 3;
4. represented source-native evidence submitted for processing;
5. StegVerse governance disposition and resulting transition/non-transition;
6. retrospective reconstruction.

Source-owner architectural descriptions and expectations may be retained as provenance, but they are not source-native runtime observations unless independently emitted by the source framework during the run.

## Public fixtures and experiment integrity

```text
inspection/examples/elan-relational-state-test1.json
inspection/examples/elan-governance-request.example.json
inspection/examples/elan-evaluation-declaration-test1.json
```

These files exercise the SDK submission surface and protocol shape. They are not evidence that ELAN produced any particular interpretation, internal state, Event-3 behavior, or comparative outcome.

The governance request is a processor-path example only. The evaluator declaration is retained as evidence metadata and is not inserted into the governance decision request. The declaration must remain outcome-neutral for the authentic run.

An externally returned source-native trace must be preserved before StegVerse interpretation. Do not rewrite that trace to match the example fixtures. Bind the original artifact or exact source-native representation first; downstream StegVerse-derived interpretation remains downstream evidence.

## External tester: one-command public preparation

An external framework creator can install the public SDK surface and produce a validated submission bundle without access to StegCore or Master Records repositories:

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

For the authentic ELAN experiment, substitute the exact externally produced source-native evidence for the example input. Do not populate expected ELAN interpretation/behavior fields from StegVerse assumptions.

## StegVerse runtime: one-command governed execution

In an environment where the canonical pinned governed-test dependencies are installed, remove `--prepare-only` and use the same externally supplied inputs:

```bash
stegverse external-run \
  --input <externally-produced-source-native-evidence.json> \
  --governance-request <experiment-applicable-governance-request.json> \
  --evaluation-declaration <outcome-neutral-evaluation-declaration.json> \
  --source-framework ELAN \
  --source-output-id <external-source-output-id> \
  --data-class <external-source-data-class> \
  --return-depth full-trace \
  --output elan-test1-complete-run.json
```

This path builds and validates `stegverse.ingress-manifest.v1`, binds governance to `stegverse.route.canonical-governed.v1`, executes the canonical local governed test, records custody, returns `manifest_receipt_id`, and performs replay plus reconstruction by default.

The SDK must not claim that `--prepare-only` is governance execution.

## Real test substitution rule

The included governance request is a runnable SDK-path example. For the actual ELAN experiment, replace its example governance facts with the represented facts applicable to the experiment. Do not duplicate, reinterpret, or invent ELAN-native internal semantics inside the governance request.

The test result is not whether the architectures agree. The result is the evidence produced by each architecture while preserving the separation between source-native behavior and independently derived StegVerse governance.

## Completion proof

The SDK completion gate requires exact-head evidence that the public external-framework preparation path works anonymously, the source-native payload remains unchanged, evaluator metadata stays outside the governance decision request, return projection and route binding are deterministic, and unsupported/incomplete declarations fail closed.

For ELAN Test 1 specifically, completion additionally requires evidence of the Event-3 continuity basis, the externally produced source-native trace, canonical governed execution, custody, replay, and reconstruction. No expected Event-3 behavior or expected comparative disposition may be substituted for observed evidence.
