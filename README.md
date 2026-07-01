# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![SDK Demo Test](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/sdk-demo-test.yml/badge.svg)
![Formal Route](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/formal-testing-route-validate.yml/badge.svg)
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
```

Local verification:

```bash
pytest tests/test_governed_llm.py
pytest tests/test_governed_llm_session.py
pytest tests/test_governed_llm_session_intake.py
pytest tests/test_governed_llm_manifest.py
pytest tests/test_governed_llm_receipt.py
python scripts/smoke_governed_llm_sdk.py
```

---

## Primary routes

| Route | Purpose | Key files |
|---|---|---|
| SDK Demo Test | Package install, imports, adapter behavior, demo path checks | `.github/workflows/sdk-demo-test.yml` |
| Formal Testing Route | Receipt-bound testing-data loop and route result validation | `.github/workflows/formal-testing-route-validate.yml`, `docs/FORMAL_TESTING_ROUTE.md` |
| Dynamic Admissibility | Boundary and admissibility fixture checks | `.github/workflows/dynamic-admissibility-tests.yml` |
| Ecosystem Chat Intake | Site-facing three-layer intake validation | `stegverse/ecosystem_chat_http.py` |

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
