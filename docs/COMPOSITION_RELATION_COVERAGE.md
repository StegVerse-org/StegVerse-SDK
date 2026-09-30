# Composition relation coverage: from n=2 to N

## What this closes

Two modules compose N things and both refuse, by design, to lift *component*
admissibility into *composite* admissibility. A validated joint relation is a
separate prerequisite:

- `stegverse/admissibility_composition.py` — the general evaluator
- `stegverse/governed_composite_response.py` — the Test 6 product path

The relation record they required carried no statement of what it had been
validated over, and neither validator asked. One record reading
`relation_status: validated` satisfied a pair and a dozen equally, and satisfied
any `composition_id`.

That is the same separability error one level up: **a relation validated for a
subset was being lifted to a superset.**

It was invisible at n=2. `tasks/SDK-ADMISSIBILITY-COMPOSITION-002.json` records
its controls as `n2-negative-and-positive-controls` with marker
`ADMISSIBILITY_COMPOSITION_N2_NONSEPARABILITY_PASS`, and every test in that
suite composed exactly two components. The rule was demonstrated for a pair and
assumed for the rest. Going from 2 to N is what exposes it.

Measured before the change, with a single validated record reused:

| arity | decision | relation accepted |
|---|---|---|
| n=2 | `ALLOW_WITH_POSTURE` | yes |
| n=3 | `ALLOW_WITH_POSTURE` | yes |
| n=5 | `ALLOW_WITH_POSTURE` | yes |
| n=12 | `ALLOW_WITH_POSTURE` | yes |

The same record also satisfied `composition_id` values naming entirely different
compositions.

## The manifest is the binding

All actions and transitions are receipted and all data transport is by governed
manifest, so the manifest of an ask **already states which components will exist
before any of them runs**. That is the interlock property the journey work
established: the component set is determined, not observed.

So governance here is the simple kind. A manifested request either has the right
shape -- a journey whose declared branches are exactly the components composed --
or it does not. Nothing has to opt in for the binding to be checkable, and no
issuer handshake is needed to establish scope, because the manifest already
carries it.

`derive_component_ids_from_journey` reads the declared branch set: a branch of
journey `J` is component `"J:<branch_id>"`, the identity the composite already
uses. It returns nothing when the journey does not determine a set -- absent, no
branches, or a `branch_count` disagreeing with the branches enumerated, which is
a malformed manifest rather than a coverage question.

| coverage | basis | outcome |
|---|---|---|
| `BOUND_TO_THIS_COMPOSITION` | `GOVERNED_MANIFEST_DECLARED_THE_BRANCH_SET` | governed claim |
| `BOUND_TO_THIS_COMPOSITION` | `RELATION_ENUMERATED_THE_COMPONENT_SET` | governed claim |
| `COVERAGE_UNDECLARED` | — | claim withheld: nothing states what should exist |
| `DOES_NOT_COVER_THIS_COMPOSITION` | — | **fails closed** |

A relation may still enumerate coverage explicitly (`covers_composition_id` +
`covers_component_ids`), or name the journey (`covers_journey_id`). Every basis a
relation declares must hold. Enumerating stays all-or-nothing, because naming the
composition without the components leaves arity unpinned, which is the hole.

## A verified binding is required for a governed claim

Governance covers all output, so output is not labelled governed on a relation
nothing checked against these components. An unbound relation has the same
standing as no relation: the answer is still returned and still attributed, and
only the claim is withheld.

This is not a restriction on the ask path -- that path is manifested, so its
answers are governed from the request's own shape. It is what stops an
*unmanifested* composition from claiming governance it cannot demonstrate.

## Every outcome carries a verdict

Nothing from the ask path returns without one, which is what "govern all output"
requires:

| situation | verdict |
|---|---|
| manifested, branches returned, answer selected | `GOVERNED_ANSWER`, governed |
| a branch did not return | `FAN_INCOMPLETE`, claim withheld, no composite |
| components are not the declared branch set | `FAIL_CLOSED`, coverage mismatch |
| relation absent or unbound | `RELATION_UNRESOLVED`, answer returned, claim withheld |
| strategy selected no answer | `NOT_COMPOSED` |
| manifest shape wrong | rejected at intake, `ISSUANCE_BLOCKED`, never executed |

## What the composite now records

The composite carried two booleans about its relation — supplied, and valid — so
a verifier could not tell *which* relation to go and check. It now records
`joint_relation_id` and the full `relation_coverage` verdict.

Replay follows: `reconstruct_governed_response` rebuilds both the relation and
the declared branch set from what the composite recorded, rather than a generic
stand-in, so a coverage verdict replays as itself. The composite records the
declared set, which is all the check needs -- it does not have to carry the whole
manifest. A fail-closed composite reconstructs as the same failure, and
a composite edited to claim a binding its components do not support diverges —
the recorded coverage is inside the digest.

`authority_source` is not recorded and remains a stand-in on replay. It feeds
only the validity boolean, which the digest already covers.

## Boundary

This check reports whether a record covers a composition. It does not validate
the record's own authority, which is the issuer's, it does not certify that the
composition is correct, and it grants execution authority to nothing. A bound
relation means the record is pinned to this composition at this arity — no more
than that.

## Verification

- 16 new tests; `passing` 1589 → 1605, `new=3` unchanged (the container-only set
  already recorded in `data/test-suite-baseline.json` under `environment_notes`).
- Non-vacuity: neutralizing the gate fails exactly 8 tests, across both modules,
  and no others.
- Live surface, `POST` to the Chat endpoint with a real StegBrowser-backed
  executor: a manifested three-branch ask returns `200 GOVERNED_ANSWER`
  `RECONSTRUCTED` with `basis: GOVERNED_MANIFEST_DECLARED_THE_BRANCH_SET`, while
  the relation itself declares no coverage -- the manifest is the binding. A
  relation enumerating 2 of the 3 branches fails closed. A malformed manifest
  (repeated ephemeral endpoint, repeated response marker) is rejected at intake
  with `ISSUANCE_BLOCKED` and never executes. A branch that does not return gives
  `FAN_INCOMPLETE` before composition.
- The duplicated validator is gone: both modules now import one
  `validate_joint_relation`, so a change to it cannot reach one and miss the other.
