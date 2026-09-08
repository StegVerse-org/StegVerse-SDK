# Generic manifested-data processing contract

## Purpose

The StegVerse SDK is a machine-to-machine processing boundary for external frameworks. An external framework may submit its own manifested data without converting that native data into a StegVerse semantic class, declare the StegVerse processing capability it wants, bind that request to an installed runtime route, and receive a bounded artifact describing the result.

Canonical abstraction:

```text
external framework
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> caller-facing processing capability
-> declared installed runtime route
-> processor-specific request/evidence
-> canonical processing runtime
-> canonical custody
-> caller-selected artifact projection
-> returned StegVerse artifact + manifest_receipt_id
```

The submitted data class, processing capability, runtime route, authority, caller projection, and custody are separate dimensions.

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
```

A relational-state object, scientific observation, financial event, agent output, device event, legal artifact, image-derived observation, or another source-native class remains the source framework's manifested object. Selecting governance does not redefine that object as a StegVerse-native action.

## Universal ingress envelope

The universal `stegverse.ingress-manifest.v1` envelope carries source identity, one source-native payload or payload commitment, declared processing intent, route declaration, integrity bindings, and return controls. Processor-specific fields are conditional rather than globally mandatory.

For new manifests, caller-facing processing intent is explicit:

```json
{
  "processing": {
    "capability": "governance",
    "route_id": "stegverse.route.canonical-governed.v1"
  }
}
```

`processing.capability` says **what StegVerse capability the caller wants**. `processing.route_id` binds that request to the exact route declaration in `extensions.stegverse_route`. Runtime route fields such as lane class, containment, routing surface, sandbox posture, and consequence posture are route mechanics, not the caller-facing processing abstraction.

Existing v1 governance manifests that predate the `processing` object remain compatible: omission is derived as `governance` only when the declared route is the canonical governed v1 route. Future/non-governance processors must declare `processing` explicitly. This compatibility rule does not generalize route authority and does not permit silent processor substitution.

## Semantic custody

The source framework owns the meaning of its native payload. StegVerse evaluates only what the manifest asks the selected installed processor to evaluate and only from evidence actually supplied or canonically available.

```text
payload class != processing class
manifest validity != processing result
processing selection != authority
returned artifact != source-framework semantic ownership
```

The universal envelope does not require a governance `candidate`. A `candidate` becomes required only when the selected processor requires one.

For governance processing, `candidate` is the governance proposition being evaluated about or in relation to the manifested data. It is separate from `payload`. The SDK does not require the payload itself to adopt action semantics.

## Payload commitments

A caller may submit an inline JSON-representable payload or a payload commitment, but never both.

Inline payloads are bound by canonical `payload_sha256`.

Commitment-only payloads must also declare how an independent implementation verifies the commitment:

```text
payload_commitment_profile = sha256
payload_commitment = <64 lowercase hexadecimal characters>
```

`sha256` is the currently published commitment profile. Additional commitment profiles require an explicit future contract; an opaque unprofiled commitment is not accepted as independently verifiable evidence.

## Processing-path and route selection

The universal envelope declares the caller-facing capability under:

```text
processing.capability
```

and the route binding under:

```text
processing.route_id
extensions.stegverse_route.route_id
```

The two route identifiers must match. Structural ingress validation does not claim that a route is installed. Executable routing separately resolves the declaration against the published route registry and fails closed when a route is unknown, incomplete, conflicting, unavailable, or lacks an installed processor binding.

The currently installed executable 0B processor/route is:

```text
processing.capability = governance
processing.route_id = stegverse.route.canonical-governed.v1
```

A route declaration cannot install a processor, hot-patch governance, substitute an unavailable route, or grant authority.

Governance-specific input is carried separately at:

```text
extensions.stegverse_governance_request
```

It is required only for governance processing. The complete canonical governance request is required for executable governance. The SDK does not synthesize missing judgment, signal, execution, capability, continuity, approval, permission, or authority evidence from the source payload merely because governance was selected.

This separation is intentional:

```text
source-native object
+ processing capability
+ installed route binding
+ processor-specific evidence/state
= executable processing request
```

If required processor-specific state is absent, the correct result is rejection/fail-closed rather than semantic invention.

## Processor-generic structural validation vs executable support

The manifest envelope is processor-generic even though only governance is currently installed as the 0B executable processor.

For example, a structurally valid future verification request may declare:

```json
{
  "processing": {
    "capability": "verification",
    "route_id": "stegverse.route.example-verification.v1"
  }
}
```

Such a manifest does **not** need a governance `candidate` or `stegverse_governance_request`. But until that route and processor binding are published and installed, executable submission fails closed. Structural acceptance is not runtime availability.

This prevents the first installed processor—governance—from defining the universal manifest semantics for every future SDK processor.

## Caller-selected artifact depth

Canonical Master Records custody is independent of what is projected back to the caller. The caller chooses how much user-disclosable transition evidence is returned with `return_projection`.

The three useful artifact-depth profiles are:

| Requested artifact | `return_projection` | Meaning |
|---|---|---|
| Governance artifact only | `SELECTED` with governance/result classes | Governance disposition, basis, receipt identity/integrity, and selected governance evidence without the complete transition trajectory |
| Governance + transition result | `SELECTED` with governance plus transition/result classes | Governance artifact plus the selected state-transition/result evidence |
| Full state-transition artifact | `ALL` | All user-disclosable transition evidence, route receipts, result evidence, and reconstructable transition material permitted for the run |

`NONE` is a minimal/locator return mode. It is not the governance-artifact-only mode. It suppresses caller-facing transition detail while preserving canonical custody and the `manifest_receipt_id` locator.

The precise selected transition-class names remain bounded by the installed runtime's published evidence vocabulary. Asking for a projection does not create evidence that the run did not produce and does not alter the processing result.

## Example: external relational framework

An external relational framework such as ÉLAN can keep its relational interpretation in its own data model and submit only the manifested representation it elects to expose.

Conceptually:

```text
ÉLAN native event/state
-> ÉLAN manifests exposed relational data as payload
-> ÉLAN binds payload/candidate hashes
-> ÉLAN selects processing.capability=governance
-> ÉLAN binds the request to stegverse.route.canonical-governed.v1
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

Processor-generic Python validator:

```python
from stegverse.manifest_contract import validate_ingress_manifest
```

## Invariants

```text
arbitrary manifested payload class: permitted
payload class forced into action semantics: false
governance fields globally required: false
processing capability selected independently of payload class: true
processing capability separated from route mechanics: true
route selection grants authority: false
manifest validity grants authority: false
missing processor evidence synthesized: false
unsupported processor/route executed: false
caller projection suppresses Master Records custody: false
replay/reconstruction re-executes original consequence: false
GitHub runtime authority: none
credential authority: TV/TVC
```
