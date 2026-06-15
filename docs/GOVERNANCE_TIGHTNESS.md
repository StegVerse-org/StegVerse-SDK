# Governance Tightness

Generated: `2026-06-14`

## Purpose

Governance tightness is the sliding-scale control used by ingestion workers when processing cross-repo and cross-org tasks.

It gives ingestion a shared vocabulary for how restrictive a task should be without hard-coding that behavior into every downstream repository.

## Input forms

```python
resolve_tightness("observe")
resolve_tightness("assist")
resolve_tightness("balanced")
resolve_tightness("strict")
resolve_tightness("fail_closed")
resolve_tightness(55)
resolve_tightness({"scale": 75})
resolve_tightness({"label": "strict"})
```

## Scale

```text
0-20    observe
21-40   assist
41-60   balanced
61-80   strict
81-100  fail_closed
```

## Result fields

```text
schema
label
scale
allow_threshold
review_threshold
fail_closed_threshold
require_receipt
require_replay
require_human_review
allow_cross_repo_write
allow_cross_org_write
default_route
```

## Cross-repo and cross-org behavior

Lower tightness permits more automated movement.

Higher tightness requires more receipts, replay, and review before writes.

The strictest level routes to fail-closed by default.

## Example

```bash
python examples/governance_tightness_profile.py
```

## Schema

```text
schemas/admissibility/governance-tightness.schema.json
```
