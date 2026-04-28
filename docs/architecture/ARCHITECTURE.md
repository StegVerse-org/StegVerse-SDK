# StegVerse SDK Architecture

## Overview

The StegVerse SDK provides external integration with the StegVerse governed execution ecosystem. It enables users to submit intents, validate actions through LLM adapters, and retrieve confidence-scored execution artifacts.

## Components

| Component | Purpose |
|-----------|---------|
| `submit_intent()` | Submit governance intent to demo-suite |
| `StegVerseLLMAdapter` | LLM output governance wrapper |
| `govern_llm_output()` | Classify LLM output as ALLOW/DENY/FAIL_CLOSED |
| `get_demo_status()` | Retrieve execution status + confidence score |

## Data Flow

```
User Intent
    |
    v
SDK.submit_intent()
    |
    v
demo-suite-runner (StegVerse-org)
    |
    v
Governed Execution → Receipt → Confidence Score
    |
    v
SDK.get_demo_status() → User sees result
```

## Integration Points

| Point | Repo | Method |
|-------|------|--------|
| Intent submission | demo-suite-runner | GitHub Actions trigger |
| Status retrieval | demo-suite-runner | Artifact download |
| LLM governance | TV/TVC (StegVerse-Labs) | Policy check |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-28 | Initial release |
