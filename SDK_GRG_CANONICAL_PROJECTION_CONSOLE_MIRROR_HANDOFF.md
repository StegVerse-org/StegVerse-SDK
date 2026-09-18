# SDK GRG Canonical Projection Console Mirror Handoff

Goal Task ID: `SDK-GRG-CANONICAL-PROJECTION-CONSOLE-001`
Parent Goal Task ID: `SDK-EVALUATOR-GOVERNANCE-POSTURE-MANIFEST-001`
Repository: `StegVerse-org/StegVerse-SDK`
COSV ID: `71000000101110`
Status: `ACTIVE / HANDOFF_READY / SOURCE IMPLEMENTATION PENDING`

## Objective

Extend the already-merged generic Governance Reference Graph (GRG) source contract so recognized GRG relations can be projected through their existing canonical StegVerse semantic owners and exercised through the public SDK console, without turning the SDK into a second governance engine.

The public/evaluator-visible target is:

```text
submitted GRG
-> relation recognized
-> canonical semantic owner identified
-> canonical input derived
-> canonical governance evaluation
-> Interlock/InTr posture/transition binding where available
-> retained receipt/evidence lineage
```

Unknown or domain-specific relations must remain preserved, hash-bound, non-authorizing evidence and must not silently acquire StegVerse semantics.

## Current truth inherited from parent

The generic GRG source contract is already validated and merged. The SDK currently proves:

```text
graph schema validation
typed node/relation preservation
applicability/evidence/basis/constraint preservation
scoped coverage + explicit completeness
independent graph SHA-256 binding
canonical manifest binding
console discovery
hierarchy/composition/unknown relations do not grant authority
SDK does not resolve governance
```

Canonical parent references:

```text
PR #257 -> initial GRG integration
PR #258 -> console/public exposure
PR #260 -> HGAI HITL GRG example
PR #261 -> HGAI validation closeout
```

The parent task still has no authentic proof that arbitrary/recognized GRG relations are being consumed by a live StegCore/Interlock runtime.

## Required first implementation scope

Start with the smallest recognized relation set whose semantic owners already exist.

### HAS_SCOPED_AUTHORITY

The SDK must not interpret this as authority.

Projection target:

```text
GRG HAS_SCOPED_AUTHORITY relation
+ exact actor/action/target/scope/time applicability
+ source/evidence/basis references
+ scoped completeness declaration
-> existing canonical StegCore authority-basis request
-> existing authority-basis resolver
-> actor_authority_current / delegation_current facts as applicable
```

Preserve the established truth rules:

```text
matching current scoped basis -> may establish TRUE
incomplete no-match -> UNKNOWN / FAIL_CLOSED
complete applicable no-match -> may establish FALSE / DENY
role label / graph position -> never authority
```

### REQUIRES_CONSTRAINT

The SDK must not implement constraint semantics.

Projection target:

```text
GRG REQUIRES_CONSTRAINT
+ canonical constraint_ref
-> existing StegCore policy-shape semantic owner
```

Begin with an already-defined canonical policy-shape reference such as:

```text
stegcore:policy-shape:quorum
```

If the referenced canonical semantic surface is not callable from the current path, identify the first exact existing seam that must be exposed. Do not duplicate quorum, guardian, veto, time-lock, escalation, or other policy semantics in the SDK.

## Unknown relation behavior

A domain-specific relation such as:

```text
HGAI_CONTEXT_LINK
```

must remain:

```text
PRESERVED
HASH_BOUND
NON_AUTHORIZING
NO_CANONICAL_SEMANTICS
```

unless an existing canonical semantic owner explicitly recognizes it.

Unknown relation presence must not itself force ALLOW or DENY unless a separate canonical completeness/admissibility rule requires such an outcome.

## Console target

Preserve the existing discovery surface:

```text
stegverse governance-graph
stegverse governance-graph --schema
stegverse governance-graph --example
stegverse governance-graph --all
```

Add the smallest public console operation needed to inspect semantic projection of a supplied/example GRG.

The console result should expose at minimum:

```text
relation_id
relation_type
recognition_state
canonical_semantic_owner
projection_state
projected_input_hash/ref
governance_result when actually evaluated
authority_effect
transition/runtime binding state
evidence/receipt refs when authentic
```

The console must clearly distinguish:

```text
REPRESENTED_ONLY
RECOGNIZED_PROJECTED
CANONICALLY_EVALUATED
LIVE_RUNTIME_BOUND
UNKNOWN_RELATION_PRESERVED
```

Do not collapse source validation or a simulated resolver into `LIVE_RUNTIME_BOUND`.

## Runtime/evidence boundary

Source/unit/console validation may prove canonical projection behavior.

It does not prove live execution.

The live predicate requires authentic retained evidence showing the exact manifested GRG and projected canonical input reaching the existing live StegOS/StegCore/Interlock/InTr execution path and returning evidence bound to the same graph/manifest/request hashes.

Do not create another:

```text
governance engine
authority plane
runtime
scheduler
dispatcher
credential authority
Interlock/InTr substitute
StegCore substitute
second user-operated device dependency
```

Reuse existing runtime/receipt surfaces.

## Validation requirements

At minimum validate:

1. known `HAS_SCOPED_AUTHORITY` projects only to the existing authority-basis seam;
2. incomplete coverage preserves UNKNOWN/fail-closed semantics;
3. known `REQUIRES_CONSTRAINT` resolves only to its canonical policy-shape owner;
4. unknown relation survives unchanged and has no authority effect;
5. hierarchy or graph location never becomes authority;
6. graph hash and canonical manifest hash remain stable/bound through projection;
7. console output accurately distinguishes representation, projection, canonical evaluation, and live runtime evidence;
8. no pre-authored authority conclusion can bypass the canonical resolver;
9. no SDK code duplicates canonical StegCore/StegGate/Interlock semantics.

## Completion criteria

This goal is complete only when:

```text
recognized GRG semantic projection source is merged and validated
public console surface exposes the projection accurately
README and this handoff are current
canonical Task Registry is current
and either:
  authentic live runtime receipt lineage is proven
or:
  the exact first unsatisfied existing runtime predicate is retained without overclaiming
```

If live evidence is not available, do not claim runtime completion. Preserve the exact remaining predicate for continuation.

## Initial next action

Read current GRG implementation, authority-basis bridge, StegCore authority-basis resolver, existing canonical policy-shape surfaces, SDK Interlock/InTr posture bridge, and evaluator console. Identify the smallest existing-owner projection seam before changing code.
