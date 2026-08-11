# STEGVERSE SDK

![PyPI](https://img.shields.io/pypi/v/stegverse-sdk)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![SDK Validation](https://github.com/StegVerse-org/StegVerse-SDK/actions/workflows/sdk-demo-test.yml/badge.svg)
![License](https://img.shields.io/github/license/StegVerse-org/StegVerse-SDK)

> Submission is not execution. Execution is not authority. Authority is not admissibility.

`StegVerse-SDK` is the user-facing Python intake boundary for StegVerse governance testing. It binds submitted data to a manifest, preserves route intent, and prepares the package for downstream receipt-bound evaluation.

The SDK does not claim endorsement, compatibility, provenance, collaboration, or validation from any reviewer or external framework. It prepares artifacts for bounded testing routes.

## Console: start here

Any developer, tester, or evaluator uses the same generic SDK entry point. There are no person-specific routes.

```bash
python -m pip install stegverse-sdk
stegverse
stegverse surfaces
```

A repository checkout works the same way:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e .
stegverse surfaces
```

Use the console to discover what this installed SDK exposes rather than relying on private instructions:

```bash
stegverse capabilities
stegverse help-surface <surface>
```

The equivalent entry command is `python -m stegverse`. Full console help, including discovery of admissibility/AdmittedCode integration, is in `docs/SDK_CONSOLE.md`.

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

The SDK supports raw JSON and governed-data submission, LLM Adapter and governed-session contracts, Ecosystem Chat intake validation, trust-metadata ingestion, formal testing routes, dynamic admissibility tests, universal-entry routing, transition/SPE progression contracts, and receipt/system-boundary validation. `sdk.capabilities.json` is the machine-readable statement of what is built, connected, disabled, or authority-gated.

## Discovering a desired demo/test surface

1. Run `stegverse surfaces`.
2. Run `stegverse help-surface <surface>` for the desired area.
3. Run `stegverse capabilities` when exact implementation/connection status matters.
4. Follow the referenced repository docs/examples for that surface.
5. Do not treat a discovered or implemented route as execution authority. Disabled/unconfigured integrations remain unavailable until their governing boundary is satisfied.

For AdmittedCode/admissibility work, begin generically with:

```bash
stegverse help-surface admittedcode
stegverse capabilities | grep -i admiss
```

This is the same route for every SDK user; it is not an evaluator-specific or person-specific mode.

---

## Governed LLM SDK activation

Documentation:

```text
docs/GOVERNED_LLM_SDK_ACTIVATION.md
docs/GOVERNED_LLM_SESSION_PACKETS.md
docs/FREE_TIER_METADATA_INGESTION.md
sdk.capabilities.json
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

## Validation workflow

The canonical workflow is `.github/workflows/sdk-demo-test.yml`. It runs the Python compatibility matrix, complete test suite, formal-route validation, dynamic-admissibility examples, package build, and package/release gates.

## Primary routes

| Route | Purpose | Key files |
|---|---|---|
| Generic Console | Discover installed SDK surfaces and help | `stegverse/cli.py`, `docs/SDK_CONSOLE.md` |
| Universal Entry | Manifest-bound deterministic capability/lane routing | `stegverse/universal_entry*.py` |
| Formal Testing Route | Receipt-bound testing-data loop and route-result validation | `docs/FORMAL_TESTING_ROUTE.md`, `scripts/validate_formal_testing_route.py` |
| Dynamic Admissibility | Boundary and admissibility fixture checks | `stegverse/admissibility.py`, `tests/test_dynamic_admissibility.py` |
| SDK-to-SPE | Transition candidate and progression-only SPE receipt consumption | `docs/SDK_TO_SPE_COMMITMENT_INTAKE.md` |
| Ecosystem Chat Intake | Site-facing three-layer intake validation | `stegverse/ecosystem_chat_http.py` |
| Free-Tier Metadata Ingestion | LLM-adapter trust metadata validation | `stegverse/free_tier_metadata.py` |

## Developer validation

```bash
python -m pip install -e ".[dev]"
pytest tests/
```

Repository handoff and session-consolidation files preserve project governance/history. They are not SDK user entry points. `SDK_MIRROR_HANDOFF.md` remains the repository task source of truth; `sdk.capabilities.json` is the user/machine-readable capability state.
