# ELAN Test 1 Runbook

This runbook documents how to execute the first external-framework interoperability test through the SDK. The experiment-specific protocol is not an SDK behavior and is not hardcoded by this runbook. It is supplied as caller-authored manifest data.

## Experiment manifest is the source of protocol truth

The exact controlled sequence, evaluated condition, continuity rule, non-interference declarations, requested processing, and requested evidence for this experiment are declared in:

```text
inspection/examples/elan-test1-experiment-manifest.json
```

The SDK does not infer or rewrite those experiment-specific values. `stegverse external-run --experiment-manifest ...` retains the caller-authored object unchanged under `extensions.experiment_manifest` in the resulting `stegverse.ingress-manifest.v1`.

Changing the experiment therefore means changing the experiment manifest, not editing SDK code or adding a special-case runtime path.

## Source-framework boundary

ELAN remains source-native. Only observable output/state that ELAN legitimately exposes may be placed in the source payload. Missing internal state must not be inferred or invented.

The experiment manifest may define stimuli, timing, state-establishment labels, the evaluated condition, and continuity requirements. Those declarations do not authorize the SDK to pre-compose ELAN interpretation, internal state, behavior, or comparative outcome.

Externally returned source-native evidence must be preserved before StegVerse-derived interpretation is added downstream.

## Public inputs

```text
inspection/examples/elan-test1-experiment-manifest.json
inspection/examples/elan-relational-state-test1.json
inspection/examples/elan-governance-request.example.json
inspection/examples/elan-evaluation-declaration-test1.json
```

Their roles are distinct:

- `elan-test1-experiment-manifest.json` declares the experiment protocol and evidence requirements.
- `elan-relational-state-test1.json` is source-native/example payload data only.
- `elan-governance-request.example.json` is processor-specific governance input.
- `elan-evaluation-declaration-test1.json` records evaluator WHAT/HOW/WHY metadata.

None of these files changes SDK runtime semantics merely because a particular experiment uses them.

## External tester: one-command public preparation

```bash
stegverse external-run \
  --prepare-only \
  --input inspection/examples/elan-relational-state-test1.json \
  --governance-request inspection/examples/elan-governance-request.example.json \
  --evaluation-declaration inspection/examples/elan-evaluation-declaration-test1.json \
  --experiment-manifest inspection/examples/elan-test1-experiment-manifest.json \
  --source-framework ELAN \
  --source-output-id elan-emotional-ambiguity-silence-test-001 \
  --data-class elan.relational-state.v1 \
  --return-depth full-trace \
  --output elan-test1-submission.json
```

The result is `stegverse.sdk.external-framework-submission.v1` with `status=SUBMISSION_READY`. The generated ingress manifest contains the source-native payload, processing/route declaration, evaluator metadata, caller-authored experiment manifest, and return projection. Preparation does not fabricate governed execution evidence.

## Governed execution

In an environment where the pinned governed-test dependencies are installed, remove `--prepare-only` and use the same manifest-declared protocol with the exact externally produced source-native evidence:

```bash
stegverse external-run \
  --input <externally-produced-source-native-evidence.json> \
  --governance-request <experiment-applicable-governance-request.json> \
  --evaluation-declaration <evaluation-declaration.json> \
  --experiment-manifest <experiment-manifest.json> \
  --source-framework ELAN \
  --source-output-id <external-source-output-id> \
  --data-class <external-source-data-class> \
  --return-depth full-trace \
  --output elan-test1-complete-run.json
```

This path builds and validates `stegverse.ingress-manifest.v1`, binds the declared installed processor route, executes the canonical local governed test, records custody, returns `manifest_receipt_id`, and performs replay plus reconstruction by default.

## Completion proof

Completion requires evidence that the SDK retained the submitted experiment manifest unchanged, preserved source-native payload bytes/semantics, kept evaluator metadata outside the governance decision request, bound the declared processing route deterministically, and produced the required custody/replay/reconstruction evidence after authentic execution.

For this experiment, the specific Event-3 protocol and continuity predicate are read from the experiment manifest. They are not SDK constants and must not be implemented as experiment-specific SDK logic.
