# StegVerse SDK Mirror Handoff

## Current source of truth

This file is the handoff source of truth for `StegVerse-org/StegVerse-SDK` until superseded.

## Active goal

Goal 3: Governed LLM end-to-end demonstrator SDK intake sync.

The repository should prove:

```text
LLM-adapter governed session packet
-> SDK session validation
-> SDK intake routing
-> SDK manifest binding
-> SDK receipt handoff
-> demo packet verification
```

No live ingestion, sandbox execution, runtime execution, commit-time standing determination, execution approval, or production trust-kernel execution is added by this path.

## Installed baseline already present

```text
sdk.capabilities.json
docs/GOVERNED_LLM_SDK_ACTIVATION.md
docs/GOVERNED_LLM_SESSION_PACKETS.md
scripts/smoke_governed_llm_sdk.py
stegverse/governed_llm_session.py
stegverse/governed_llm_session_intake.py
stegverse/governed_llm_manifest.py
stegverse/governed_llm_receipt.py
tests/test_governed_llm_session.py
tests/test_governed_llm_session_intake.py
tests/test_governed_llm_manifest.py
tests/test_governed_llm_receipt.py
```

## Files to install for Goal 3

```text
examples/governed_llm_demo/session_packet.simple_query.json
examples/governed_llm_demo/README.md
scripts/verify_governed_llm_demo_packet.py
tests/test_governed_llm_demo_packet.py
```

## Required invariant

```text
sdk_validation_is_execution == false
sdk_intake_is_authority == false
manifest_binding_is_persistence == false
receipt_handoff_is_master_record_installation == false
demo_packet_source == LLM-adapter
```

## Verification commands

```bash
python scripts/smoke_governed_llm_sdk.py
python scripts/verify_governed_llm_demo_packet.py
pytest tests/test_governed_llm_demo_packet.py -v
pytest tests/test_governed_llm_session.py tests/test_governed_llm_session_intake.py tests/test_governed_llm_manifest.py tests/test_governed_llm_receipt.py -v
```

## Upstream sync target

```text
StegVerse-org/LLM-adapter
  -> emits the governed session demo packet
```

## Downstream sync target

```text
StegVerse-Labs/admissibility-wiki
  -> documents the public demo overview and verification path
```

## Archive posture

Not archive-ready until demo packet verification is installed and the wiki handoff reflects the demonstrator.
