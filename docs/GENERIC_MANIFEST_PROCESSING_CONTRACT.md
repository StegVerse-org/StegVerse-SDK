# Generic manifested-data processing contract

## Purpose

The StegVerse SDK is a machine-to-machine processing boundary for external frameworks. An external framework may submit its own manifested data without converting that native data into a StegVerse semantic class, select an installed StegVerse processing path, and receive a bounded artifact describing the result.

Canonical abstraction:

```text
external framework
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> declared installed processing route
-> processor-specific evaluation
-> canonical custody
-> caller-selected artifact projection
-> returned StegVerse artifact + manifest_receipt_id
```

The submitted data class and the selected processing path are orthogonal. A relational-state object, scientific observation, financial event, agent output, device event, legal artifact, image-derived observation, or another source-native class remains the source framework's manifested object. Selecting governance does not redefine that object as a StegVerse-native action.

## Semantic custody

The source framework owns the meaning of its native payload. StegVerse evaluates only what the manifest asks the selected installed processor to evaluate and only from evidence actually supplied or canonically available.

```text
payload class != processing class
manifest validity != governance decision
processing selection != authority
returned artifact != source-framework semantic ownership
```

For governance processing, `candidate` is the governance proposition being evaluated about or in relation to the manifested data. It is separate from `payload`. The payload may be any JSON-representable manifested class or may be supplied as a commitment. The SDK does not require the payload itself to adopt action semantics.

## Processing-path selection

A preformatted manifest selects the installed processing route through:

```text
extensions.stegverse_route
```

The currently installed production route is:

```text
stegverse.route.canonical-governed.v1
```

A route declaration selects among published, installed processing semantics. It cannot install a processor, hot-patch governance, substitute an unavailable route, or grant authority. Unsupported, unavailable, incomplete, or conflicting route declarations fail closed.

Governance-specific input is carried separately at:

```text
extensions.stegverse_governance_request
```

The complete canonical governance request is required for executable governance. The SDK does not synthesize missing judgment, signal, execution, capability, continuity, approval, permission, or authority evidence from the source payload merely because governance was selected.

This separation is intentional:

```text
source-native object
+ selected processing route
+ processor-specific evidence/state
= executable processing request
```

If required processor-specific state is absent, the correct result is rejection/fail-closed rather than semantic invention.

## Caller-selected artifact depth

Canonical Master Records custody is independent of what is projected back to the caller. The caller chooses how much user-disclosable transition evidence is returned with `return_projection`.

The three useful artifact-depth profiles are:

| Requested artifact | `return_projection` | Meaning |
|---|---|---|
| Governance artifact only | `SELECTED` with governance/result classes | Governance disposition, basis, receipt identity/integrity, and selected governance evidence without the complete transition trajectory |
| Governance + transition result | `SELECTED` with governance plus transition/result classes | Governance artifact plus the selected state-transition/result evidence |
| Full state-transition artifact | `ALL` | All user-disclosable transition evidence, route receipts, result evidence, and reconstructable transition material permitted for the run |

`NONE` is a minimal/locator return mode. It is not the governance-artifact-only mode. It suppresses caller-facing transition detail while preserving canonical custody and the `manifest_receipt_id` locator.

The precise selected transition-class names remain bounded by the installed runtime's published evidence vocabulary. Asking for a projection does not create evidence that the run did not produce and does not alter the governance disposition.

## Example: external relational framework

An external relational framework such as ÉLAN can keep its relational interpretation in its own data model and submit only the manifested representation it elects to expose.

Conceptually:

```text
ÉLAN native event/state
-> ÉLAN manifests exposed relational data as payload
-> ÉLAN binds payload/candidate hashes
-> ÉLAN selects stegverse.route.canonical-governed.v1
-> ÉLAN supplies the complete governance-request evidence/state required for that evaluation
-> ÉLAN requests governance-only, governance+transition, or full transition projection
-> StegVerse performs the canonical governed run
-> StegVerse returns the selected artifact projection and manifest_receipt_id
```

Neither architecture must absorb or redefine the other's private history. A relational judgment may differ from the governance disposition; disagreement is valid evidence rather than an integration failure.

## Executable entry

```bash
stegverse governance --select 0B --manifest external-manifest.json
```

Equivalent module entry:

```bash
python -m stegverse.governance_ingress_cli 0B external-manifest.json
```

Machine-readable schema:

```text
schemas/stegverse.ingress-manifest.v1.schema.json
```

## Invariants

```text
arbitrary manifested payload class: permitted
payload class forced into action semantics: false
processing route selected independently of payload class: true
route selection grants authority: false
manifest validity grants authority: false
missing processor evidence synthesized: false
caller projection suppresses Master Records custody: false
replay/reconstruction re-executes original consequence: false
GitHub runtime authority: none
credential authority: TV/TVC
```
