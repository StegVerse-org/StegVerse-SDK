# AI Entry SDK Receipt Capture Boundary

## Goal 6 role

`StegVerse-SDK` is the SDK-side receipt capture boundary for the StegVerse AI Entry Point.

The SDK may validate request and return-path shapes, prepare receipt capture previews, and explain what would be recorded. It must not persist master records, grant authority, expose credentials, or issue real receipts by default.

## Boundary contract

```text
Site AI Entry / LLM-adapter boundary result
-> SDK receipt capture boundary
-> receipt capture preview
-> no master-record persistence
-> no execution authority
-> no credential exposure
```

## Required default state

```text
receipt_capture_enabled == false
real_receipt_issued == false
master_record_persisted == false
execution_authority_granted == false
credential_surface_enabled == false
preview_only == true
```

## Activation requirements

Live SDK receipt capture must not be enabled until the following are installed:

1. governed SDK activation approval;
2. receipt service endpoint or master-record handoff;
3. per-request input hash binding;
4. provider comparison capture rules where external LLM panes are present;
5. reconstruction metadata path;
6. failure/rollback behavior for rejected receipt capture.

## Non-claims

This boundary does not install master records, does not issue real receipts, does not grant execution authority, and does not activate live provider calls.
