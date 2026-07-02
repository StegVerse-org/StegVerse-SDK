# Governed LLM Demo Example

This directory contains a sample governed LLM session packet produced by the end‑to‑end demonstration in the LLM adapter.  The file `session_packet.simple_query.json` is a report generated from the simple informational query fixture.  The purpose of this example is to provide a static reference for verification scripts and tests in the StegVerse SDK.

## Contents

* `session_packet.simple_query.json` – The governed session packet for a simple informational query.  It includes the query, request hash, provider response, evidence pointers, action classification, authority decision, and placeholders for downstream governance fields.

## Usage

The accompanying script `scripts/verify_governed_llm_demo_packet.py` reads the session packet and performs a set of simple sanity checks.  To run the verification script from the root of the SDK repository:

```bash
python scripts/verify_governed_llm_demo_packet.py --session examples/governed_llm_demo/session_packet.simple_query.json
```

If the packet is well‑formed and matches the expected outcome for the simple informational query, the script prints a success message.  This script does **not** perform full SDK validation; it only checks that the demo packet adheres to the simplified demonstration schema.  For complete session validation, use the functions in the `stegverse.governed_llm_session` module on an adapter‑produced packet that conforms to the formal schema.
