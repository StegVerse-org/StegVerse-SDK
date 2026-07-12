# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![SDK Validation](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/sdk-demo-test.yml/badge.svg)
![License](https://img.shields.io/github/license/StegVerse-org/StegVerse-SDK)

> Submission is not execution. Execution is not authority. Authority is not admissibility.

`StegVerse-SDK` is the user-facing Python intake boundary for StegVerse governance testing. It binds submitted data to a manifest, preserves route intent, and prepares the package for downstream receipt-bound evaluation.

The SDK does not claim endorsement, compatibility, provenance, collaboration, or validation from any reviewer or external framework. It prepares artifacts for bounded testing routes.

---

## What it does

```text
User / SDK / LLM Adapter / Ecosystem Chat
→ manifest-bound intake
→ receipt-bound route package
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner bounded sandbox path
→ returned result / reconstruction packet
```

The SDK supports:

- raw JSON package submission;
- governed-data package submission;
- LLM Adapter submission;
- governed LLM session packet validation, intake routing, manifest binding, and receipt handoff;
- Ecosystem Chat intake validation;
- LLM Adapter free-tier trust metadata ingestion;
- formal testing route artifacts;
- dynamic admissibility tests;
- private boundary-review test packets.

---

## Governed LLM SDK activation

The governed LLM SDK contract layer is documented in:

```text
docs/GOVERNED_LLM_SDK_ACTIVATION.md
```

The session packet contract is documented in:

```text
docs/GOVERNED_LLM_SESSION_PACKETS.md
```

The free-tier metadata ingestion contract is documented in:

```text
docs/FREE_TIER_METADATA_INGESTION.md
```

The machine-readable capability manifest is:

```text
sdk.capabilities.json
```

Current SDK chain:

```text
adapter session packet
  -> SDK validation
  -> SDK intake routing
  -> SDK manifest binding
  -> SDK receipt handoff
  -> optional free_tier_trust metadata validation
```

Local verification:

```bash
pytest tests/test_governed_llm.py
pytest tests/test_governed_llm_session.py
pytest tests/test_governed_llm_session_intake.py
pytest tests/test_governed_llm_manifest.py
pytest tests/test_governed_llm_receipt.py
pytest tests/test_free_tier_metadata.py
python scripts/smoke_governed_llm_sdk.py
python scripts/verify_free_tier_metadata_ingestion.py
```

---

## LLM free-tier metadata ingestion

The SDK can validate the `free_tier_trust` response field emitted by `StegVerse-org/LLM-adapter` and displayed by `StegVerse-Labs/Site`.

```text
LLM-adapter free_tier_trust metadata
-> SDK metadata ingestion contract
-> deterministic validation result
-> non-authorizing SDK status
-> downstream compatibility signal
```

This contract validates shape, quota metadata, receipt/replay/reconstruction metadata, upgrade reasons, and explicit non-claims.

It does not call a provider, persist records, issue receipts, export audit packets, replay sessions, reconstruct sessions, grant execution authority, or convert quota availability into admissibility.

---

## Validation workflow

The repository uses one consolidated GitHub Actions workflow:

```text
.github/workflows/sdk-demo-test.yml
```

It runs the Python compatibility matrix, complete test suite, formal route validation, dynamic-admissibility examples, Goal 5 comparison verification, package build, release creation, and PyPI publication. Formal-route and dynamic-admissibility checks remain distinct jobs and commands inside this workflow rather than separate workflow files.

## Primary routes

| Route | Purpose | Key files |
|---|---|---|
| Consolidated SDK Validation | Package install, tests, formal-route checks, admissibility checks, build, and release | `.github/workflows/sdk-demo-test.yml` |
| Formal Testing Route | Receipt-bound testing-data loop and route-result validation | `docs/FORMAL_TESTING_ROUTE.md`, `scripts/validate_formal_testing_route.py` |
| Dynamic Admissibility | Boundary and admissibility fixture checks | `stegverse/admissibility.py`, `tests/test_dynamic_admissibility.py` |
| Ecosystem Chat Intake | Site-facing three-layer intake validation | `stegverse/ecosystem_chat_http.py` |
| Free-Tier Metadata Ingestion | LLM-adapter `free_tier_trust` metadata validation | `stegverse/free_tier_metadata.py` |

---

## Formal testing route

The canonical formal testing path is:

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ User
```

Every ingestion point is expected to emit an action receipt to `master-records`.

See:

```text
docs/FORMAL_TESTING_ROUTE.md
```

---

## Ecosystem Chat SDK intake

The SDK includes a pre-backend intake validator, transport-free backend handler, and HTTP adapter for the Site Ecosystem Chat form gateway.

```python
from stegverse.ecosystem_chat_http import handle_ecosystem_chat_http

status, response = handle_ecosystem_chat_http(
    "POST",
    "/api/ecosystem-chat",
    request_body,
)
```

The adapter accepts the Site three-layer payload only when `fields`, `manifest`, and `receipt_window` remain distinct and internally consistent. In this stage, `receipt_id` remains `None`; receipt issuance is not installed in the Site-facing intake path.

---

## Relationship to runtime demos

This repository is the intake and SDK boundary. Runtime comparison work is demonstrated separately in:

```text
StegVerse-org/core-node-runtime-demo
```

That runtime demo compares the same submitted package across cross-org ingestion and core-node / micro-node paths, emitting comparable result reports, closure artifacts, witness records, memory objects, terminal closure receipts, and kernel compatibility records.

---

## Install

```bash
pip install stegverse-sdk
```

For local development:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
pip install -e ".[dev]"
pytest tests/
```
