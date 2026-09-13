# Generic manifested-data processing contract

## Purpose

The StegVerse SDK is the canonical machine-to-machine manifested processing ingress and caller-return assembly surface. An external framework may submit its own source-native manifested data, declare the StegVerse processing capability it wants, bind that request to an installed route, declare the complete governed communication lifecycle, and receive the requested result only after the applicable manifested stages and governed egress transitions complete.

Canonical abstraction:

```text
initiating entity
-> source-native manifested data
-> stegverse.ingress-manifest.v1
-> processing.capability
-> processing.route_id
-> processor-specific request/evidence
-> canonical processing runtime
-> required governed transitions / declared external round trips
-> canonical custody
-> replay/reconstruction/evidence stages when declared
-> Publisher stage when presentation/evaluator evidence is declared
-> SDK return assembly bound to original request + initiator
-> applicable final StegVerse-side egress transition
-> Interlock/InTr egress
-> far-side Interlock/InTr transition
-> initiating entity receives requested projection
```

For an external-framework path using the LLM Adapter:

```text
... -> Publisher -> SDK return assembly -> LLM Adapter -> Interlock/InTr -> far-side transition
```

The LLM Adapter is the final **StegVerse-side** transition surface in that path. The terminal communication transition occurs on the far side of Interlock/InTr.

## Independent dimensions

The submitted data class, processing capability, route, authority, custody, Publisher requirements, caller projection, egress surface, and terminal communication state are separate dimensions.

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
Publisher rendering != communication completion
SDK return assembly != communication completion
adapter emission != communication completion
local InTr egress != far-side terminal transition
```

Source-native data remains owned semantically by the source framework. Selecting governance does not redefine that object as a StegVerse-native action.

## Manifest-driven processing invariant

New manifests declare caller-facing processing intent with:

```text
processing.capability
processing.route_id
```

`processing.route_id` must match `extensions.stegverse_route.route_id`. Runtime mechanics remain under `extensions.stegverse_route` and cannot silently substitute a processor.

Source identity, provider identity, framework identity, adapter identity, transport identity, model identity, interface identity, or prior-result identity may contribute provenance/policy evidence but cannot select processing semantics.

Existing v1 governance manifests that omit `processing` remain backward-compatible only for the canonical governed v1 route. Future/non-governance processors must declare processing explicitly.

## Semantic custody and processor-specific evidence

The source framework owns the meaning of its native payload. StegVerse evaluates only what the admitted manifest asks the selected installed processor to evaluate and only from supplied or canonically available evidence.

For governance, `candidate` is a separate proposition evaluated about or in relation to the payload. Governance-specific evidence remains under `extensions.stegverse_governance_request`.

Missing processor evidence is rejected; it is not synthesized.

## Payload commitments

A caller supplies either an inline payload or a commitment, never both. Inline payloads are bound by canonical `payload_sha256`. Commitment-only payloads must declare a published verification profile; the current profile is `sha256` with a 64-character lowercase hexadecimal commitment.

## Complete communication lifecycle

New builder-generated manifests carry a top-level `completion` object:

```json
{
  "completion": {
    "direction": "SOUTH",
    "initiator": {
      "class": "external_framework",
      "ref": "framework-instance-or-requester"
    },
    "publisher": {
      "stage": "PUBLISHER",
      "required": true,
      "package_profile": "stegverse.publisher.evidence-report-package/v1"
    },
    "egress": {
      "final_stegverse_transition_surface": "LLM_ADAPTER",
      "transport": "INTERLOCK_INTR",
      "far_side_transition_required": true
    }
  }
}
```

`SOUTH` denotes the complete governed communication path toward ecosystem egress. It is not a processor, runtime, or authority.

Legacy v1 manifests may omit `completion` for backward compatibility. The validator accepts those manifests but marks them `complete_communication_manifest = false`; they must not be represented as complete communication lifecycle declarations.

## Publisher as a manifest stage

When presentation, report, or evaluator evidence is required, Publisher is explicitly part of the complete manifest. It is not an out-of-band convenience after the governed run.

Publisher consumes authentic retained evidence and prepares only the presentation/evidence package declared by the manifest. Publisher does not create missing evidence and does not gain governance, processor-selection, transport, credential, or caller-routing authority.

Publisher output returns to SDK as the presentation/evidence result of the same manifested lifecycle. A new processing cycle exists only when a new admitted manifest explicitly requests more processing.

## SDK caller-return assembly

SDK binds the Publisher/result package to:

- original manifest/request identity;
- original initiating entity identity/correlation;
- package identity/digest or retained reference;
- requested `return_projection`;
- custody/evidence references;
- manifest-declared egress surface.

SDK return assembly does not itself complete an externally delivered communication.

## Governed southbound egress

The communication path remains governed through ecosystem egress. The applicable final StegVerse-side transition must occur before Interlock/InTr egress.

For an external-framework path using LLM Adapter, that transition surface is `LLM_ADAPTER`. LLM Adapter may perform the manifest-bound protocol/framing transformation only; it may not alter evidence semantics, select processing, or infer terminal completion.

The far-side Interlock/InTr transition is required for terminal communication state. Until it is authentically observed and correlated to the same manifest/request lineage, the result is not `COMMUNICATION_COMPLETE`.

## Caller-selected artifact depth

`return_projection` controls caller-visible evidence depth while canonical custody remains unchanged.

| Requested artifact | `return_projection` |
|---|---|
| Governance/result artifact only | `SELECTED` result classes |
| Governance + selected transition result | `SELECTED` result plus transition classes |
| Full user-disclosable state-transition artifact | `ALL` |
| Locator/minimal return | `NONE` |

A projection cannot create evidence that the run did not produce.

## Example: external relational framework

```text
ÉLAN native event/state
-> LLM Adapter frames source-native input for canonical SDK manifest ingress
-> admitted manifest selects governance + installed route
-> canonical governed processing
-> declared evaluator/counterparty round trip when required
-> custody/replay/reconstruction as declared
-> Publisher prepares declared evidence package
-> Publisher returns package to SDK
-> SDK binds package to original ÉLAN request
-> LLM Adapter performs final StegVerse-side egress transition
-> Interlock/InTr egress
-> far-side Interlock/InTr transition
-> ÉLAN receives the manifested projection
```

Neither architecture absorbs or redefines the other's private semantics.

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

Processor-generic validator:

```python
from stegverse.manifest_contract import validate_ingress_manifest
```

## Invariants

```text
arbitrary manifested payload class: permitted
payload class forced into action semantics: false
processing capability selected independently of payload class: true
processing capability separated from route mechanics: true
source/adapter identity selects processing: false
route selection grants authority: false
manifest validity grants authority: false
missing processor evidence synthesized: false
unsupported processor/route executed: false
caller projection suppresses Master Records custody: false
Publisher is out-of-band when required by manifest: false
Publisher creates missing evidence: false
new Publisher output automatically starts new processing: false
LLM Adapter is final StegVerse-side framework transition before InTr: true
LLM Adapter is terminal communication transition: false
far-side Interlock/InTr transition required for terminal communication: true
GitHub runtime authority: none
credential authority: TV/TVC
```

Global lifecycle contract:

```text
StegVerse-Labs/.github/docs/CANONICAL_SOUTHBOUND_COMMUNICATION_LIFECYCLE.md
```
