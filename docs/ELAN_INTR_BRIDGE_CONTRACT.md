# ELAN ↔ StegVerse Interlock/InTr Bridge Contract

Status: Draft implementation contract for `ELAN-INTR-BRIDGE-001`

## Purpose

Define the interoperable data-transport and admission boundary between ELAN-originated evidence and StegVerse Interlock/InTr without allowing semantic interpretation to silently become governed fact.

## Interoperability classes

The bridge records one of four transport classes:

- `HUMAN_MEDIATED_EVIDENCE_EXCHANGE`
- `ELAN_SHAPED_SDK_SUBMISSION`
- `AUTHENTIC_ELAN_RUNTIME_SUBMISSION`
- `BIDIRECTIONAL_RUNTIME_INTEROPERABILITY`

A receipt MUST NOT claim a higher class than the observed transport evidence supports.

## Envelope

Every submission MUST include:

- `bridge_version`
- `transport_class`
- `source_framework`
- `source_instance_id` when known
- `source_event_id`
- `observed_at`
- `payload_sha256`
- `facts[]`
- `assertions[]`
- `interpretation_candidates[]`
- `resolution_state`
- `provenance[]`

Each fact MUST be directly observable or externally evidenced. Each assertion MUST identify its asserting actor/source. Each interpretation candidate MUST remain distinguishable from both facts and assertions.

## Resolution rule

Semantic resolution proceeds by elimination, not simple preference.

Candidate interpretations may be removed only with an explicit elimination reason referencing one or more facts, assertions, constraints, historical observations, or human clarification events.

Terminal resolution states are:

- `SINGLE_SURVIVING_INTERPRETATION`
- `UNRESOLVED_INTERPRETATION_SET`

Human clarification is additional evidence. It does not automatically become truth and does not automatically force a single surviving interpretation.

## Consequence-divergence gate

Before admission to InTr, the bridge MUST evaluate whether surviving interpretation candidates can produce materially different governance consequences.

- If surviving candidates are consequence-equivalent, the bridge MAY admit the shared governed representation while preserving unresolved semantics in the receipt.
- If surviving candidates are consequence-divergent, the bridge MUST NOT collapse them into one governed state. It MUST return `RESOLUTION_REQUIRED` and identify the unresolved candidates and the additional evidence or clarification needed to eliminate alternatives.

## InTr admission

The bridge may produce `READY_FOR_INTR_ADMISSION` only when either:

1. one materially plausible interpretation survives; or
2. multiple surviving interpretations are consequence-equivalent for the requested governed transition.

Transport itself grants no governance, execution, transition, publication, custody, or semantic authority.

## Receipt

Every bridge execution MUST return a reconstruction receipt containing:

- exact input envelope hash;
- normalized fact/assertion/candidate sets;
- eliminated candidates and reasons;
- surviving candidates;
- consequence-equivalence/divergence result;
- resolution state;
- admission disposition;
- transport-class evidence;
- output hash.

## Independence from Run 3

Run 3 is independent of machine-to-machine interoperability. It is not gated by this bridge and does not require this bridge to be complete, active, or used.

This bridge work may proceed in parallel with Run 3. If a Run 3 or later experiment elects to use the bridge, the receipt MUST record the transport class actually observed. Human-mediated and ELAN-shaped SDK experiments remain valid experimental modes in their own right and MUST NOT be promoted to authentic ELAN-runtime or bidirectional interoperability claims.
