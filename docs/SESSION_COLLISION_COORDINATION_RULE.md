# Session Collision Coordination Rule

Updated: 2026-09-10
Applies to: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003` and any coincident child/session workstreams that overlap a broader canonical/global task.

## Purpose

Prevent duplicate implementation, conflicting pull requests, duplicate runtime tests, stale handoffs, and parallel sessions from progressing the same owned scope after canonical ownership has moved to a broader task.

## Coordination invariant

A narrower task/session MUST NOT continue implementation merely because its original Goal Task ID remains known locally.

Before progressing overlapping work, reconcile the session against the GitHub Task Registry and applicable canonical mirror handoff. If a broader/global canonical task now owns the remaining scope, the narrower session becomes coordination-inactive and MUST stop progressing that work.

Required disposition:

```text
STATUS: INACTIVE
coordinated_with_global_task_id: <canonical broader/global Goal Task ID>
coordinated_with_handoff_task_id: <canonical broader/global *_MIRROR_HANDOFF.md path>
work_progression_allowed: false
```

The session summary MUST state that its remaining scope has been subsumed/coordinated, identify the controlling Global Task ID and Handoff Task ID, and state that the work in that session should not be progressed.

## When INACTIVE is required

Set the narrower coincident task/session to `INACTIVE` when all of the following are true:

1. the broader/global task canonically owns the overlapping remaining scope;
2. any unique completed changes, evidence, findings, failure analysis, or prerequisites from the narrower session have been durably transferred to the controlling task/handoff or otherwise referenced there;
3. continuing independently would duplicate work, create ownership ambiguity, collide with an active branch/PR/worker, or risk divergent runtime evidence.

`INACTIVE` is a coordination state, not a claim that the underlying work is complete. The work may remain ACTIVE in the controlling global task.

## When a session must remain active

Do not mark the narrower session `INACTIVE` until unique untransferred work has been durably handed off. Examples include an unreferenced failing run, unmerged repair, unique runtime receipt, unresolved predicate, externally supplied evidence, or a change that the global task has not yet incorporated.

Transfer that information first, then transition the narrower session to `INACTIVE`.

## Re-activation

An `INACTIVE` coincident session may resume only if canonical ownership is explicitly transferred back or the broader task decomposes a genuinely separable scope into a new canonical Goal Task ID and handoff. Merely reopening the ChatGPT conversation does not reactivate it.

## Reporting contract

A coincident session that is subsumed should return a handoff block equivalent to:

```text
Goal Task ID: <narrower Goal Task ID>;
Handoff Task ID: <narrower applicable handoff>;
STATUS: INACTIVE;
Summary of work: Coordinated with Global Task ID <global Goal Task ID> and Handoff Task ID <global handoff>; unique work/evidence transferred; remaining scope is owned there and work in this session should not be progressed.;
```

The controlling global session remains responsible for its own canonical STATUS and evidence claims.

## Current SDK lane application

For `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`, coincident sessions covering already-subsumed generic-manifest, Shared Docs WorkSpace, downstream propagation, or related runtime-distribution work must reconcile against the current Task Registry and the applicable SDK mirror handoff before progressing. If the broader/global lane owns their remaining scope, they should transition to `INACTIVE` under this rule rather than continue in parallel.

## README review

This rule changes repository/task coordination semantics only. It does not change the public SDK manifest schema, runtime route, processing capability, CLI, user-facing WorkSpace behavior, or authority model. Therefore no public README contract change is required for this coordination-only update.