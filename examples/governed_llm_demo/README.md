# Governed LLM Demo Example

This directory contains the static governed LLM session packet emitted by the fixture-first LLM-adapter Goal 3 demonstration.

## Contents

```text
session_packet.simple_query.json
```

## Verification

```bash
python scripts/verify_governed_llm_demo_packet.py --session examples/governed_llm_demo/session_packet.simple_query.json
pytest tests/test_governed_llm_demo_packet.py -v
```

## Boundary

SDK validation is not execution, SDK intake is not authority, manifest binding is not persistence, and receipt handoff is not master-record installation.
