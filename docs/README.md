# SDK Wrapper Reference — AaCT-E Integration

> **Reference implementation of the SDK read-only contract.**

## Contract Summary

The SDK may:
- Clone the demo at a specific tag
- Run `verify_demo.py` or `python -m access.cli`
- Parse JSON traces
- Display results through SDK UI/API
- Archive traces with provenance

The SDK must NOT:
- Modify scenario files or engine code
- Change thresholds
- Suppress verification failures
- Reference `main` branch for evidence

## Usage

```python
from demo_runner import DemoRunner

with DemoRunner(repo="AaCT-E/demo", tag="v0.2.0") as runner:
    result = runner.verify()

    if result.passed:
        print("All assertions passed")
    else:
        print("Verification failed — see result.stderr")

    # Provenance is preserved
    print(result.provenance)
    # {'repo': 'AaCT-E/demo', 'tag': 'v0.2.0', 'commit_sha': 'abc123...'}
```

## Isolation

- Process: Demo runs in subprocess, not imported
- Filesystem: Cloned to temp directory, cleaned up on exit
- Network: Demo requires no network; SDK must not inject dependencies

## Full Contract

See [AaCT-E/docs/SDK_INTEGRATION.md](https://github.com/AaCT-E/demo/blob/main/docs/SDK_INTEGRATION.md)
