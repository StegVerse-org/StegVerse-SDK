# HPS SDK Integration

## Purpose

This document defines how `StegVerse-org/StegVerse-SDK` consumes the Harmonic Principle of Standing (HPS) as a dynamic route governor.

HPS is canonical in:

```text
Admissible-Existence/HPS
```

The SDK does not own the HPS formalism. The SDK owns the first StegVerse-org integration boundary: converting HPS heartbeat, standing score, capability-window, and expiration information into deterministic route decisions.

## Core rule

```text
HPS is not a status flag.
HPS is a capability-window governor.
```

The SDK must not allow a route merely because the system is online, a workflow passed, or a receipt exists. A route may proceed only when current HPS standing supports the specific capability window.

## Route decision model

SDK HPS route decisions are bounded to:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

A decision of `ALLOW` means the SDK route is permitted to continue to the next governed boundary. It does not grant execution authority, publication authority, endorsement, compatibility recognition, or admissibility outside the route.

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
It is a bounded route decision for the next governed boundary.
```

## Minimal route object

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

`StegVerse-org/LLM-adapter` should consume this SDK route contract before:

- tool use;
- memory commit;
- publication handoff;
- execution handoff;
- external API action;
- long-lived retention;
- public attribution or claim production.

## Relationship to Ecosystem Chat

Ecosystem Chat should display HPS state using the HPS visualization payload, but SDK route decisions determine whether a user request may proceed through an SDK-governed route.

## Canonical SDK statement

```text
The SDK consumes HPS as a dynamic capability-window governor.
A route opens only while current heartbeat, standing, authority, evidence, coordinate, and reconstruction support remain valid.
When those supports decay, the SDK route closes, expires, denies, reviews, or fails closed.
```
