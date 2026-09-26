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

`SINGLE_SURVIVING_INTERPRETATION` means that every other materially plausible interpretation represented by the resolution process has been eliminated with retained reasons. `UNRESOLVED_INTERPRETATION_SET` means that two or more materially plausible interpretations still survive. Consequence equivalence does not convert an unresolved interpretation set into semantic resolution.

## Consequence analysis

Before admission to InTr, the bridge MUST compare the consequence classes associated with all surviving interpretation candidates.

- If surviving candidates are consequence-divergent, the receipt MUST record that divergence because the unresolved semantics are already known to be consequential.
- If surviving candidates are consequence-equivalent, the receipt MUST record that equivalence as diagnostic evidence, but equivalence MUST NOT be used as a shortcut for semantic resolution.
- Whenever more than one materially plausible interpretation survives, the bridge MUST return `RESOLUTION_REQUIRED`, preserve the surviving set, and identify or request additional evidence or clarification capable of eliminating alternatives.

Consequence comparison therefore prioritizes and explains unresolved ambiguity; it does not select an interpretation and does not authorize admission by itself.

## InTr admission

The bridge may produce `READY_FOR_INTR_ADMISSION` only when exactly one materially plausible interpretation survives and the envelope declares `SINGLE_SURVIVING_INTERPRETATION`.

If zero candidates survive, the envelope is invalid because the represented candidate manifold is incomplete or internally exhausted and must be reconstructed. If two or more candidates survive, the state remains unresolved and the bridge MUST return `RESOLUTION_REQUIRED` whether their current consequence classes are equivalent or divergent.

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
