# StegVerse-SDK Integration Snippets

Add this section to the root `README.md` near governed LLM SDK activation.

```md
## Governed LLM demo packet verification

This repository includes a static governed LLM demo packet emitted from the LLM-adapter demonstrator and a verifier for SDK-side demo packet checks.

```text
LLM-adapter governed session packet
  -> SDK demo packet sanity check
  -> SDK validation/intake/manifest/receipt handoff boundary
```

Run:

```bash
python scripts/verify_governed_llm_demo_packet.py --session examples/governed_llm_demo/session_packet.simple_query.json
pytest tests/test_governed_llm_demo_packet.py -v
```

See:

```text
examples/governed_llm_demo/README.md
```

This verification does not execute actions, grant authority, persist master records, or perform live ingestion.
```
