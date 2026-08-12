# 000 Governance Outcome Demo Mirror Handoff

## Authority

```text
goal_id: SDK-000-GOVERNANCE-OUTCOME-DEMO-001
repository: StegVerse-org/StegVerse-SDK
branch: main
parent_handoff: docs/MANIFEST_RECEIPT_NAVIGATION_MIRROR_HANDOFF.md
implementation_state: INSTALLED_UNVALIDATED
release_state: NOT_RELEASED
```

## Goal

Option `000` is the SDK-owned teaching lane. It requires no user-supplied manifest and must teach both the complete manifest/receipt shape and the complete active governance outcome vocabulary before presenting the demo transaction input.

## Installed dataset

```text
stegverse/demo_data/manifest_000_governance_outcomes.json
```

Schema:

```text
stegverse.000-demo-dataset.v1
```

The dataset is strictly `000`-only:

```text
demo_only: true
accepted_as_user_manifest: false
```

It intentionally places `governance_outcome_examples` before `demo_input`, so a human or LLM learns the governance outcome vocabulary before reading the example transaction.

## Active outcome coverage

Exactly one labeled teaching record is required for each active governance state:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

Every example declares:

```text
transition_class: governance
receipt_class: governance-decision
consequence_implied: false
authority_granted_by_example: false
```

These are explanatory records only. They are not persisted prior decisions, authority tokens, executable instructions, or substitutes for canonical runtime evaluation.

## Installed output behavior

`stegverse/governance_navigation.py` now loads and validates the SDK-owned dataset when `demo_output_manifest_shape()` is called. The demo output begins with:

```text
000_governance_outcome_dataset
```

before the canonical manifest example, labeled sections, process sequence, and reconstruction notes. The loader fails closed if the dataset is missing, malformed, not demo-only, or does not contain exactly one example of each active governance state in canonical order.

The canonical input example uses the dataset's `demo_input`, but the whole `000` dataset itself is not a valid `stegverse.ingress-manifest.v1` submission.

## Tests installed

```text
tests/test_000_governance_outcome_demo.py
```

The tests require:

```text
- the demo dataset is the first field in the self-describing output;
- ALLOW / DENY / REVIEW / FAIL_CLOSED each occur exactly once;
- every example is labeled as governance/governance-decision evidence;
- every example is explicitly non-authorizing and does not imply consequence;
- the dataset is demo-only and not accepted as a user manifest;
- the dataset cannot pass normal external-manifest validation;
- option 000 guidance names the complete active governance vocabulary.
```

## Installation commits

```text
b02f663ad0c7e6e80e867fe359e787c417d400d1  SDK-owned 000 demo outcome dataset
8c0ec2471529289eb2909d18a21cc59c529c0172  prepend and validate all active outcomes in 000 output
e408b9e492d7e33b6625cbcf1d7ea64dd78199b6  governance outcome demo tests
```

## Worker continuation boundary

Do not reuse this dataset as an ordinary submission fixture or authority source. Remaining work is bounded to:

```text
1. bind option 000 to an actual safe canonical manifested demo run;
2. replace runtime placeholders with generated hashes, receipts, and exact-run locator;
3. preserve the four outcome examples as a teaching prelude rather than pretending one run produced four mutually exclusive dispositions;
4. derive the public transition/receipt class registry from actual canonical receipt vocabulary;
5. prove a human/LLM can consume the 000 output and construct a fresh conforming manifest without copying demo outcomes as authority;
6. run sovereign/local validation and retain inspectable PASS evidence.
```

A single governed transaction still has one actual governance disposition at a given evaluated boundary. The four demo examples are deliberately separate teaching records prepended to the demo dataset so the complete vocabulary can be learned without falsifying transaction history.
