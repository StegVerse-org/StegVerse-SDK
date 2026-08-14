# Independent Authority-Boundary Preservation Experiment

Status: executable fixture candidate
Tracking: #25

## Question

Given an explicit authority/handling declaration at T0, can an independent reviewer determine from retained manifests, receipts, route transitions, replay, and reconstruction whether that declaration remained unchanged across downstream actions?

This experiment extends `Manifest_and_Receipt_Governance_Boundary.md` without naming or attributing any external reviewer or framework.

## Participant boundary

The fixture is intentionally participant-neutral. Inspection of the artifacts grants no agreement, validation, endorsement, acceptance, attribution, public-association, compatibility, or interoperability standing.

## Canonical execution target

The experiment is designed for the canonical sovereign public inspection path described by `SDK_MIRROR_HANDOFF.md`:

```text
SDK entry
-> Core-Lite manifested route carrier
-> Master Records checkpoint custody
-> canonical StegCore manifested transaction
-> canonical StegGate evaluation
-> Master Records exact-run custody
-> return ingestion/CGE
-> Master Records return custody
-> SDK return
```

The fixture itself grants no execution authority and requires no protected credential material.

## T0 declaration

The baseline separates visibility, review, acknowledgement, and authority:

```text
visibility.public = true
review.permitted = true
understanding.acknowledged = false
agreement = false
validation = false
endorsement = false
acceptance = false
claim_authority = false
publication_authority = false
attribution_authority = false
public_association_authority = false
delegation_authority = false
```

## Adversarial sequence

The machine-readable fixture applies five downstream events:

1. `ACKNOWLEDGE_UNDERSTANDING` — understanding may become true; every authority dimension must remain unchanged.
2. `INFER_ENDORSEMENT_FROM_UNDERSTANDING` — attempted state collapse; must be rejected.
3. `ATTEMPT_ATTRIBUTION_AND_PUBLIC_ASSOCIATION` — attempted widening of authority; must be rejected.
4. `REPLAY_ORIGINAL_RUN` — may create replay operation history; must not widen original authority or re-execute consequence.
5. `RECONSTRUCT_ORIGINAL_RUN` — may create reconstruction operation history; must not widen original authority or re-execute consequence.

## Primary invariant

```text
UNDERSTANDING == TRUE
!= AGREEMENT
!= VALIDATION
!= ENDORSEMENT
!= ACCEPTANCE
!= ATTRIBUTION AUTHORITY
!= PUBLICATION AUTHORITY
!= PUBLIC ASSOCIATION AUTHORITY
```

The validator fails if any forbidden authority bit becomes true, if replay/reconstruction claim consequence re-execution, or if a rejected attempted mutation is represented as accepted.

## Reconstructability criterion

A run is independently reconstructable only if a reviewer can determine, from retained evidence and without relying on private explanation:

- the exact T0 declaration;
- the ordered downstream events;
- which mutations were requested;
- which mutations were admitted or rejected;
- the final authority state;
- whether replay/reconstruction widened authority;
- whether replay/reconstruction re-executed consequence.

A verbal assertion that the boundary was preserved is not sufficient.

## Files

- `fixture.json` — participant-neutral T0 state and adversarial transitions.
- `validate_fixture.py` — deterministic fixture validator.
- `tests/test_authority_boundary_preservation_experiment.py` — repository test wrapper.

## Run

```bash
python experiments/authority_boundary_preservation/validate_fixture.py
python -m pytest -q tests/test_authority_boundary_preservation_experiment.py
```

Expected deterministic local fixture result:

```text
AUTHORITY_BOUNDARY_PRESERVED
```

This validates the experiment contract and fixture. A subsequent sovereign SDK execution must replace fixture-only evidence with retained `manifest_receipt_id`, MRR/MR transition custody, replay receipts, and reconstruction receipts before an external execution result may be claimed.