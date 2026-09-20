# HGAI HITL Governance Reference Graph Example

This is a hypothetical HGAI ecosystem example that maps a human-in-the-loop review hierarchy into the generic StegVerse Governance Reference Graph (GRG). It is an illustrative fixture only: it does not claim an implemented HGAI integration, deployment, partnership, or production connection, and it is not a separate HGAI schema.

## What the graph represents

```text
AI analysis agent
  --SUPERVISED_BY--> Human reviewer
  --ESCALATES_TO--> Supervising reviewer
  --ESCALATES_TO--> Final decision authority

AI analysis agent
  --DERIVED_FROM--> Case evidence set

Final decision authority
  --REQUIRES_CONSTRAINT--> canonical quorum policy shape

Final decision authority
  --HAS_SCOPED_AUTHORITY--> case evidence set
```

Every edge is representation plus evidence. None of the hierarchy, labels, graph position, or composition grants authority.

The runnable JSON fixture is:

```text
inspection/examples/hgai-governance-reference-graph.json
```

## Why the hierarchy is useful without becoming authority

The graph can preserve HGAI's actual operating structure: which AI output is supervised by which human, where a reviewer escalates, what evidence an analysis was derived from, which canonical constraint applies, and what external authority evidence is asserted for the final decision role.

The important distinction is:

```text
hierarchy describes governance-relevant structure
hierarchy does not create authority
```

A title such as "Final decision authority" is therefore descriptive context. The `HAS_SCOPED_AUTHORITY` relation is also only a represented claim with source/evidence/basis references. Whether current authority is established for the exact actor/action/target/scope/time belongs to the canonical StegCore authority-basis resolver.

## Completeness behavior

The example deliberately marks authority coverage as incomplete:

```json
{
  "relation": "HAS_SCOPED_AUTHORITY",
  "complete": false
}
```

That means absence of another authority relation cannot be converted into a false negative. The existing canonical rule remains:

```text
matching current scoped basis -> may establish TRUE
incomplete no-match -> UNKNOWN / FAIL_CLOSED
complete no-match -> may establish FALSE / DENY
```

The GRG itself does not produce any of those decisions.

## Hypothetical HGAI-to-GRG mapping

| HGAI concept | GRG representation | Governance meaning |
| --- | --- | --- |
| AI analyst | `class: ai` node | identity/context only |
| Human reviewer | `class: human` node | identity/context only |
| Supervising reviewer | `class: human` node | identity/context only |
| Final decision authority | `class: human` node | label does not grant authority |
| AI human oversight | `SUPERVISED_BY` | preserved relationship, non-authorizing |
| Review escalation | `ESCALATES_TO` | preserved routing/governance context |
| Evidence provenance | `DERIVED_FROM` | provenance relationship |
| Quorum | `REQUIRES_CONSTRAINT` + `stegcore:policy-shape:quorum` | references canonical policy semantics |
| Scoped authority record | `HAS_SCOPED_AUTHORITY` + evidence/basis refs | candidate authority evidence, not a decision |
| Authority register coverage | scoped `coverage[]` | explicit completeness boundary |

## What is proven today

The merged SDK source contract can validate, preserve, hash-bind, manifest, and expose this class of graph through the SDK console and manifest builders.

The example must not be described as proof that live StegCore or Interlock/InTr already projects arbitrary GRG relations into governance decisions. That live projection has not been established by the current source evidence.

Current authority boundaries remain:

```text
SDK -> representation, validation, transport, hash binding
StegCore/StegGate -> recognized governance semantics/admissibility
TV/TVC -> protected credential/scoped-authority issuance and verification
Interlock/InTr -> governed transition authority
```

## Muhammad-facing explanation

A concise way to explain the design is:

> HGAI can keep its familiar HITL hierarchy, but StegVerse does not treat that hierarchy as authority. We manifest the hierarchy as a generic governance reference graph: AI supervision, human escalation, provenance, quorum references, delegation/authority evidence, scope, conditions, time bounds, and completeness can all travel with the input. The SDK preserves and hash-binds those relationships. Canonical governance surfaces decide what recognized relations mean, and authority still has to be established for the exact actor, action, target, scope, and time. So the graph describes the governance topology without becoming a second governance engine.

That distinction allows HGAI to express its hierarchy faithfully while keeping the implementation generic enough for non-hierarchical agent, provenance, quorum, device, dataset, and delegation structures.
