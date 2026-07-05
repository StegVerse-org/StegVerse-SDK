# Free Tier Metadata Ingestion

## Purpose

This document defines the SDK-side ingestion contract for `StegVerse-org/LLM-adapter` free-tier trust metadata.

The SDK may validate the shape and non-claim posture of `free_tier_trust` metadata so Site, adapter, and SDK surfaces can remain aligned.

## Source Contract

```text
Source repository: StegVerse-org/LLM-adapter
Response field: free_tier_trust
Capability manifest: adapter.capabilities.json
Site mirror: StegVerse-Labs/Site/ecosystem-chat.html
```

## SDK Boundary

```text
LLM-adapter free_tier_trust metadata
  -> SDK metadata ingestion contract
  -> deterministic validation result
  -> non-authorizing SDK status
  -> downstream compatibility signal
```

## Required Fields

```text
schema_version
preview_only
bounded_live_use
static_demo_only
quota
receipt_replay_limits
trust_window
upgrade_for
non_claims
```

## Required Non-Claims

```text
quota_allow_is_admissibility == false
quota_allow_is_execution_authority == false
limit_allow_is_execution_authority == false
free_tier_response_is_authority == false
upgrade_changes_admissibility_requirements == false
```

The SDK must not infer that replay or reconstruction grants commit-time standing, that receipt export is permanent retention, or that upgrade status changes admissibility requirements.

## Activation State

This is an ingestion contract only. It does not call a provider, mutate a repository, persist records, issue receipts, export audit packets, replay sessions, reconstruct sessions, or grant execution authority.
