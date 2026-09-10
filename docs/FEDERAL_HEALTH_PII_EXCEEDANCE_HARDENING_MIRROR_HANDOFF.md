# Federal Health / PII Exceedance Hardening — SDK Mirror Handoff

Updated: 2026-09-10

```text
goal_id: FEDERAL-HEALTH-PII-EXCEEDANCE-HARDENING-001
repository: StegVerse-org/StegVerse-SDK
state: ACTIVE
branch: security-posture-stack-ui-001
posture_resolution_authority: Interlock/InTr
credential_authority: TV/TVC
sdk_authority_effect: NONE
```

## SDK role

The SDK describes posture-resolution inputs and renders authoritative results. It does not compute or mint the authoritative automatic/effective posture for a transition.

`build_security_posture_request()` emits the explicit selected tier plus organization minimum, data classification, channel, task identity and selected posture identity/digest as `stegverse.sdk.security-posture-request.v1`, with `authority_effect=NONE_REQUEST_INPUT_ONLY` and `resolution_authority=INTERLOCK_INTR`.

`project_intr_posture_resolution()` accepts only an Interlock/InTr-authoritative resolution, verifies that selected posture is not below the automatic floor and that effective posture is consistent, and returns an SDK/UI projection without reinterpretation.

The reusable selector UI displays selected request state immediately. Automatic and Effective remain `Awaiting InTr` until authoritative resolution evidence is supplied. After resolution, the selector disables choices below the automatic floor while preserving Automatic / Selected / Effective provenance.

## Evidence boundary

SDK validation proves request/projection and UI semantics. It does not establish a live InTr resolution, transition admission, TV/TVC credential event, or runtime packet transfer.

## Next

Consume the merged InTr authoritative posture-resolution object and preserve its posture instance reference/digest through admitted transfer receipts and downstream UI/evidence projections.
