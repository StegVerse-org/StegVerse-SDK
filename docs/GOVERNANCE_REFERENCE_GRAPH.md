# Governance Reference Graph

The Governance Reference Graph (GRG) is the generic SDK representation for
governance-relevant relationships carried with a manifested input.

It is intentionally broader than a human-in-the-loop hierarchy. The same graph
contract can represent humans, AI systems, services, devices, organizations,
roles, datasets, sensors, constraints, credentials, and other referenced objects.

The graph is **not** a governance engine. It preserves structured relationships
and their evidence so downstream canonical governance surfaces can evaluate the
relationships that they recognize.

## Authority boundary

The SDK graph contract is explicitly non-authorizing:

```text
graph representation != authority
hierarchy != authority
graph composition != authority
unknown relation != authority
SDK validation != governance resolution
manifest validity != ALLOW
```

The canonical graph contains this boundary as machine-readable state:

```json
{
  "authority_boundary": {
    "graph_representation_grants_authority": false,
    "hierarchy_grants_authority": false,
    "composition_grants_authority": false,
    "sdk_resolves_governance": false,
    "unknown_relations_grant_authority": false
  }
}
```

TV/TVC remains the protected credential/scoped-authority issuance and
verification authority where applicable. StegCore/StegGate remains the
governance decision surface. Interlock/InTr remains governed transition
authority.

## Minimum graph primitives

A v1 graph contains:

- a stable `graph_id` and `graph_version`;
- the canonical relation-semantics profile identifier;
- an independent `graph_sha256` commitment;
- typed nodes;
- typed directed relationships;
- relationship applicability such as action, target, scope, status, time window,
  and condition references;
- evidence/source/basis references;
- optional canonical constraint references;
- scoped coverage/completeness declarations;
- graph-level source references and metadata;
- the fixed non-authorizing authority boundary.

The graph is also included inside the canonical manifest hash, so changing the
graph changes the manifested input binding.

## Nodes

Nodes describe referenced things, not permissions.

```json
{
  "node_id": "human:reviewer",
  "class": "human",
  "ref": "external:human:reviewer",
  "attributes": {
    "display_role": "case reviewer"
  }
}
```

`class` is intentionally generic. Examples may include `human`, `ai`,
`system`, `service`, `device`, `organization`, `role`, `dataset`,
`sensor`, `credential`, or `constraint`. Domain-specific classes may be
preserved as context.

## Relations

Relations are typed directed statements between declared nodes.

```json
{
  "relation_id": "r-escalation",
  "subject": "human:reviewer",
  "relation": "ESCALATES_TO",
  "object": "human:decision-authority",
  "applicability": {
    "actions": ["approve"],
    "targets": ["case:42"],
    "scopes": ["case:42"]
  },
  "constraint_ref": null,
  "source_ref": "external:governance:v1",
  "evidence_refs": ["external:evidence:escalation"],
  "basis_refs": []
}
```

The SDK validates and preserves a relation type; it does not decide that the
relation grants authority. Unknown/domain-specific relation names remain
non-authorizing evidence until a canonical governance surface has semantics for
them.

This allows one graph format to carry relationships such as:

```text
MEMBER_OF
SUPERVISED_BY
ESCALATES_TO
DERIVED_FROM
REQUIRES_CONSTRAINT
HAS_SCOPED_AUTHORITY
DELEGATED_TO
CORROBORATES
MAY_INFLUENCE
```

without requiring every relation to have SDK-native governance semantics.

## Applicability

A relation may be bounded to the exact circumstances in which it is asserted:

```json
{
  "actions": ["approve"],
  "targets": ["case:42"],
  "scopes": ["case:42"],
  "status": "ACTIVE",
  "valid_from": "2026-09-01T00:00:00Z",
  "valid_until": "2026-10-01T00:00:00Z",
  "condition_refs": ["external:condition:bounded-exception"]
}
```

These fields are representation inputs. The SDK does not invent missing scope,
time, or condition semantics.

## Canonical constraints

Where a relationship refers to an already-defined governance shape, it may carry
a `constraint_ref` instead of reimplementing that rule in the graph.

Example:

```json
{
  "relation": "REQUIRES_CONSTRAINT",
  "constraint_ref": "stegcore:policy-shape:quorum"
}
```

StegCore already defines structural governance shapes such as quorum, guardian,
veto, time-lock, and escalation. The graph references those shapes; the SDK does
not become another policy-shape evaluator.

## Coverage and completeness

Completeness is explicit and scoped. Absence of a relationship from an
incomplete graph must not be treated as proof that the relationship does not
exist.

```json
{
  "coverage_id": "authority-coverage-case-42",
  "relation": "HAS_SCOPED_AUTHORITY",
  "subject": "human:decision-authority",
  "selector": {
    "actions": ["approve"],
    "targets": ["case:42"],
    "scopes": ["case:42"]
  },
  "complete": false,
  "source_ref": "external:authority-register:v1",
  "evidence_refs": ["external:evidence:authority-register"]
}
```

This preserves the existing StegCore authority-basis rule:

```text
incomplete no-match -> UNKNOWN / fail closed
complete no-match   -> FALSE / deny where that canonical resolver applies
matching current evidence -> may establish the positive fact
```

The graph itself does not produce those decisions.

## Manifest integration

The graph is carried as:

```text
extensions.governance_reference_graph
```

The Python builder accepts:

```python
from stegverse import build_governance_reference_graph
from stegverse.manifest_builder import build_manifest

graph = build_governance_reference_graph(
    graph_id="my-governance-graph",
    nodes=[...],
    relations=[...],
    coverage=[...],
    source_refs=[...],
)

manifest = build_manifest(
    data=source_native_data,
    source_framework="MY_FRAMEWORK",
    source_output_id="output-001",
    processor_request=governance_request,
    process="governance",
    governance_reference_graph=graph,
)
```

The CLI accepts a prebuilt graph JSON file:

```bash
stegverse manifest build \
  --input source.json \
  --processor-request governance-request.json \
  --source-framework MY_FRAMEWORK \
  --source-output-id output-001 \
  --governance-reference-graph governance-reference-graph.json \
  --output manifest.json
```

The evaluator-safe builders accept the same optional
`governance_reference_graph` input.

## HITL is one projection

A human-in-the-loop structure is represented without creating a HITL-specific
schema:

```text
AI analysis
  --SUPERVISED_BY--> Human reviewer
  --ESCALATES_TO--> Decision authority
  --REQUIRES_CONSTRAINT--> quorum
```

The same graph contract can carry agent supervision, evidence provenance,
dataset influence, device/service dependencies, credential relationships, and
other governance-relevant structures.

A title or position in a hierarchy remains context. If authority is relevant, it
must be represented by the applicable governed authority evidence rather than
inferred from seniority.

## Current resolution boundary

The current SDK implementation validates, hash-binds, transports, and preserves
the graph. It does **not** independently convert arbitrary graph relations into
authority or transition decisions.

The existing structured authority path remains separate and canonical:

```text
structured authority/delegation evidence
-> canonical StegCore authority-basis resolver
-> actor_authority_current / delegation_current
-> StegGate
```

A future canonical StegCore graph projection may consume recognized GRG relation
types and project them into existing authority-basis, policy-shape, evidence, or
review inputs. That projection must reuse those canonical surfaces rather than
creating a second governance engine.
