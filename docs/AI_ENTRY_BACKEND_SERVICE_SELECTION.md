# AI Entry Backend Service Selection

## Purpose

The StegVerse AI Entry Point now has three local-ready pieces:

```text
StegVerse-Labs/Site
  -> one-window AI Entry UI and API response shape

StegVerse-org/LLM-adapter
  -> disabled provider comparison boundary

StegVerse-org/StegVerse-SDK
  -> disabled SDK receipt-capture preview boundary
```

No existing backend service repo has been selected in this build thread.

## Current recommendation

Create or select a dedicated governed backend service repo only after the following contract is accepted:

```text
Site request shape
-> backend route handler
-> LLM-adapter provider boundary
-> SDK receipt-capture preview
-> response contract returned to Site
```

## Backend service requirements

```text
live_provider_calls_enabled == false by default
live_sdk_calls_enabled == false by default
execution_authority_granted == false by default
credential_surface_enabled == false by default
comparison_provider_outputs_authority == false
receipt_capture_preview_available == true
real_receipts_require_later_governed_activation == true
```

## Candidate repo options

```text
Option A: create a new repo such as StegVerse-org/AI-entry-backend
Option B: extend StegVerse-org/LLM-adapter if the backend remains provider-adapter centered
Option C: extend StegVerse-org/StegVerse-SDK if the backend remains SDK-governance centered
Option D: use a future runtime/service repo if one is created for governed endpoints
```

## Next installation target

Until a backend service repo is selected, install only contracts, preview boundaries, and validators in the existing implementation repos.
