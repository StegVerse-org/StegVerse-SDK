# Artifacts are named by capability, not by originating framework

## The rule

A module, schema identifier, fixture, demo, script, test or workflow is named by
the capability it implements. It is never named after the framework, product or
person that first exercised it.

An evaluator's identity is manifest data. `source_framework` is a required field
of `stegverse.ingress-manifest.v1`, and `external-framework-generic-manifest.json`
already carries `"source_framework": "ELAN"` — identity as a value, in the field
built for it. Encoding that same identity in a filename or a schema id says the
artifact belongs to one counterpart, and the next evaluator has to reverse-engineer
a neutral shape out of someone else's name.

```text
ARTIFACTS_ARE_NAMED_BY_CAPABILITY_NOT_BY_ORIGINATING_FRAMEWORK
```

## Ours versus theirs

The rule turns on who owns the identifier.

| | example | disposition |
| --- | --- | --- |
| an identifier the SDK **owns** | `stegverse.sdk.mir-run2-replay/v1` | violation — rename to capability |
| a scheme a counterpart **owns and emits** | `mir.leaf.v3`, `elan.relational-state.v1` | recognized as data, not a violation |

Recognizing a counterpart's wire format is the same class of act as accepting
`source_framework: ELAN`. Naming *our* vocabulary after them is not.

## Detection is by segment, never substring

`scripts/check_framework_naming.py` tokenizes each path and identifier on
non-alphanumeric boundaries and compares whole segments. `MIRROR_HANDOFF`
tokenizes to `mirror`, which is not `mir`, so the eighty-five mirror-handoff
documents in this repository are not swept up by a search for MIR. A substring
search would have flagged every one of them.

A document that is *both* MIR-named and a mirror handoff —
`docs/MIR_SDK_RETURN_MATERIALIZATION_MIRROR_HANDOFF.md` — is still detected,
because it carries `MIR` as its own segment. The test suite asserts both halves.

## History is declared, not erased

Framework-named artifacts that predate the organization receipt chains are
provenance: they are how this ecosystem was built, and deleting them would
destroy the record. They are declared in
`data/framework-named-historical-baseline.json`, each with the reason it is
retained, and they pass.

Two dispositions:

```text
HISTORICAL_PRE_ORG_RECEIPT   retained as provenance
PENDING_CAPABILITY_RENAME    to be renamed; must state capability_name
```

`PENDING_CAPABILITY_RENAME` without a `capability_name` is rejected — a standing
intention with no edge that would satisfy it is exactly the bare unknown this
ecosystem forbids elsewhere. A `capability_name` that itself carries a framework
token is rejected too.

## The set can only shrink

```text
framework-named and declared     -> passes, and is counted
framework-named and undeclared   -> UNDECLARED_FRAMEWORK_NAMED_ARTIFACT
declared but no longer present   -> STALE_HISTORICAL_BASELINE_ENTRY
```

New framework-named material fails even when similar material is already
declared: a historical disposition covers the artifact it names and nothing else.
And a declared entry whose artifact has gone also fails, so the baseline cannot
rot into a list of things nobody checks. Renaming an artifact to its capability
is the only way to shrink the count, and the count is printed on every run.

## Authority

The guard is source naming only. It renames nothing, installs nothing, admits
nothing and observes no runtime (`authority_effect: NONE_SOURCE_NAMING_ONLY`).
A baseline entry grants no permanence — it records that an artifact was present
when the guard was installed and why it is retained, not that it may stay.
