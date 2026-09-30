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

## What a relation may now declare

Two optional fields, in `stegverse/joint_relation.py`:

- `covers_composition_id` — the composition it was validated over
- `covers_component_ids` — the component set, hence the arity

A declared coverage is checked against the composition in front of it. Component
identity is the module's existing one: input object ids for admissibility
composition, branch journey ids for a governed composite response. The comparison
is on the set, so component order cannot change the verdict.

| state | meaning | outcome |
|---|---|---|
| `BOUND_TO_THIS_COMPOSITION` | declared, and matches | governed claim, `relation_binding_verified: true` |
| `COVERAGE_UNDECLARED` | declares nothing | accepted as before, `relation_binding_verified: false` |
| `DOES_NOT_COVER_THIS_COMPOSITION` | declared, does not match | **fails closed** |

Opting in is all-or-nothing. A record naming the composition but not the
components still does not pin arity, which is the hole, so a partial declaration
is a mismatch rather than a weaker kind of binding.

## Why an undeclared relation is still accepted

Withdrawing acceptance would make the existing three-LLM governed composition
ungoverned — Test 6's own product. That is a call for the goal owner, not a
detail of a coverage check. So the historical shape stays admissible and the
result stops implying more than it has: `relation_binding_verified: false`,
`maturity_class: known_composition_with_unbound_relation`, and a follow-up step
naming what was not established.

A relation that *declares* a coverage and does not match is different, and fails
closed. It asserts a binding that does not hold, which is worse than asserting
none.

## What the composite now records

The composite carried two booleans about its relation — supplied, and valid — so
a verifier could not tell *which* relation to go and check. It now records
`joint_relation_id` and the full `relation_coverage` verdict.

Replay follows: `reconstruct_governed_response` rebuilds the relation from what
the composite recorded, rather than a generic stand-in, so a coverage verdict
replays as itself. A fail-closed composite reconstructs as the same failure, and
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
  executor: an unbound relation returns `200 GOVERNED_ANSWER` `RECONSTRUCTED` as
  before; a bound one returns the same plus `BOUND_TO_THIS_COMPOSITION`; a
  relation validated over 2 of the 3 branches returns `422 NOT_COMPOSED` with no
  governed claim.
- The duplicated validator is gone: both modules now import one
  `validate_joint_relation`, so a change to it cannot reach one and miss the other.
