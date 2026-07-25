# Review Visibility and Authority Governance

## Rule

Visibility and authority are independent state dimensions.

A publicly accessible artifact can invite inspection, discussion, and feedback
without granting authority to publish claims, attribute external participants,
assert endorsement, claim compatibility or interoperability, or create public
association.

## Installed implementation

- `schemas/review_authority_manifest.schema.json`
- `stegverse/review_authority.py`
- `tests/test_review_authority.py`

## Manifest dimensions

The manifest declares these dimensions separately:

- `visibility_state`
- `process_state`
- `claim_authority`
- `publication_authority`
- `attribution_authority`
- `public_association_authority`
- `endorsement`
- `compatibility`
- `interoperability`
- `external_references[].association_status`

`REVIEW_ONLY` fails closed unless every authority field is `false` and every
external claim field is `NONE`.

## Acknowledgement receipt

`build_acknowledgement_receipt()` records receipt, understanding, or feedback
without converting any of those events into endorsement, attribution,
association, compatibility, interoperability, or other authority.

Supported acknowledgement states:

- `RECEIVED_ONLY`
- `UNDERSTOOD_NOT_ENDORSED`
- `FEEDBACK_PROVIDED_NOT_ENDORSED`

## Review-to-adoption transition

`authorize_transition()` requires:

- stable transition identifier;
- explicit target state;
- authorizer identity;
- authorizer authority reference;
- declaration of every authority dimension.

Visibility is always recorded as **not** being the authority source. Missing or
partial authority declarations fail closed.

## External references

An external person or framework can be represented as:

- `REFERENCE_ONLY`
- `REVIEW_REQUESTED`
- `AUTHORIZED_ASSOCIATION`

`AUTHORIZED_ASSOCIATION` is rejected unless
`public_association_authority == true`.

## Verification

The repository's existing full `pytest tests/` workflow automatically discovers
`tests/test_review_authority.py`. The tests cover visibility non-inference,
review-only claim rejection, acknowledgement without endorsement, external
association restrictions, explicit adoption transitions, complete authority
dimension declarations, and tamper-detecting manifest hashes.

No claim of a canonical GitHub Actions pass is made until machine evidence is
observed.
