# HPS SDK Integration

## Purpose

This document defines how `StegVerse-org/StegVerse-SDK` participates in the corrected Harmonic Principle of Standing (HPS) runtime/bridge/delegation architecture.

HPS formalism is canonical in:

```text
Admissible-Existence/HPS
```

Executable runtime semantics are owned by:

```text
StegVerse-org/HPS-runtime
```

Sibling input route normalization is owned by:

```text
StegVerse-Labs/hybrid-collab-bridge
```

Governed authority delegation evaluation is owned by:

```text
StegVerse-Labs/Ecosystem-Delegation
```

Ecosystem-wide cycle records and reconstruction receipts are owned by:

```text
master-records/orchestration
```

The SDK does not own ecosystem-wide HPS integration. The SDK is an SDK-origin input nest that reads runtime standing state, emits SDK-origin route candidates, and preserves non-authority through the next governed boundary.

## Corrected architecture

```text
Admissible-Existence/HPS
  -> standing-vector formalism

StegVerse-org/HPS-runtime
  -> runtime state, standing-vector registers, phases, epochs, capability windows

SDK input            \
LLM-adapter input     \
Site input             -> hybrid-collab-bridge -> Ecosystem-Delegation -> next governed boundary
External adapter      /
Manual review        /
```

## Core rule

```text
SDK is a sibling input nest.
SDK route ALLOW is not execution authority.
SDK route ALLOW is not delegation authority.
SDK does not make LLM-adapter subordinate to SDK.
```

The SDK must not allow a route merely because the system is online, a workflow passed, or a receipt exists. A route may proceed only when current HPS runtime state and downstream bridge/delegation evaluation support the specific capability window.

## Route decision model

SDK-facing HPS route decisions are bounded to:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

A decision of `ALLOW` means the SDK-origin route is permitted to continue to the next governed boundary. It does not grant execution authority, publication authority, endorsement, compatibility recognition, delegation authority, or admissibility outside the route.

## Required support for ALLOW

A route may return `ALLOW` only when:

```text
heartbeat_result == PASS
standing_class satisfies standing_required
capability_window_state == OPEN
authority_valid == true
policy_current == true
delegation_current == true
evidence_fresh == true
coordinate_valid == true
reconstruction_available == true
expiration_triggers == []
```

## Expired or degraded support

If a capability window is expired, the SDK must not borrow standing from a prior heartbeat.

```text
Prior standing cannot authorize a route after the current capability window closes.
```

If standing is degraded, the SDK may return `REVIEW` for reviewable routes or `DENY`/`FAIL_CLOSED` for routes requiring restored standing.

## Fail-closed conditions

The SDK should return `FAIL_CLOSED` when any of these occur:

```text
heartbeat_result is missing or UNKNOWN
standing_class is FAILED
reconstruction_available == false
coordinate_valid == false for routes requiring coordinate continuity
authority_valid == false for authority-bound routes
```

## Deny conditions

The SDK should return `DENY` when the route is understood but current support does not meet the capability requirement.

Examples:

```text
capability window expired
policy no longer current
evidence stale
standing degraded but route requires restored standing
```

## Review conditions

The SDK should return `REVIEW` when the route is not allowed automatically but the condition is not necessarily a fail-closed condition.

Examples:

```text
standing degraded and route allows review
policy requires human review
capability is review-bound
```

## Non-authority statement

```text
The SDK HPS route decision is not execution authority.
The SDK HPS route decision is not delegation authority.
The SDK is not upstream authority for the LLM-adapter.
It is a bounded SDK-origin route decision for the next governed boundary.
```

## Minimal SDK-origin route object

```json
{
  "route_type": "hps_sdk_route",
  "route_id": "route_example_001",
  "capability": "memory.commit",
  "heartbeat_result": "PASS",
  "standing_class": "RESTORED",
  "standing_required": "RESTORED",
  "capability_window_state": "OPEN",
  "supports": {
    "authority_valid": true,
    "policy_current": true,
    "delegation_current": true,
    "evidence_fresh": true,
    "coordinate_valid": true,
    "reconstruction_available": true
  },
  "expiration_triggers": [],
  "expected_decision": "ALLOW"
}
```

## Relationship to LLM-adapter

`StegVerse-org/LLM-adapter` is a sibling input nest, not a downstream consumer of SDK authority.

```text
SDK-origin request -> bridge -> delegation -> next governed boundary
LLM-origin request -> bridge -> delegation -> next governed boundary
```

Both input paths consume shared runtime, bridge, delegation, and orchestration contracts.

## Relationship to Ecosystem Chat

Ecosystem Chat should display HPS state using the HPS visualization payload. Site-origin requests are also sibling route candidates that should be normalized by the bridge and evaluated by delegation before consequence.

## Canonical SDK statement

```text
The SDK consumes HPS as an SDK-origin sibling input nest.
It reads runtime standing state, emits bounded SDK-origin route candidates, and does not grant execution, delegation, or publication authority.
A route opens only while current heartbeat, standing, authority, evidence, coordinate, and reconstruction support remain valid.
When those supports decay, the SDK route closes, expires, denies, reviews, or fails closed.
```
