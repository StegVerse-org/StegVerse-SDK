# Reproducible StegVerse SDK Release Candidate

## Why this exists

`main` is a moving development branch. It is not a release identity.

The artifact-validated StegVerse SDK 1.1.0 release candidate is frozen at:

```text
commit: 922d6c5235229e854c36e1a194dc99ed15a31b51
tree:   d9ddda3dbe942324c921051d89ec19eec3970b16
target tag: v1.1.0
artifact validation: PASS / run 32251339936
```

Post-freeze development is identified as `1.2.0.dev0`. A checkout of moving `main` must not be reported as the frozen 1.1.0 candidate.

## Exact evaluator checkout

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
git checkout --detach 922d6c5235229e854c36e1a194dc99ed15a31b51
```

Verify the exact commit:

```bash
test "$(git rev-parse HEAD)" = "922d6c5235229e854c36e1a194dc99ed15a31b51"
```

Verify the exact Git tree:

```bash
test "$(git rev-parse HEAD^{tree})" = "d9ddda3dbe942324c921051d89ec19eec3970b16"
```

Verify the package identity:

```bash
python - <<'PY'
from pathlib import Path
import tomllib
value = tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))
assert value['project']['name'] == 'stegverse-sdk'
assert value['project']['version'] == '1.1.0'
print('SDK_1_1_0_FROZEN_SOURCE_IDENTITY_PASS')
PY
```

## Install the frozen evaluator candidate

Basic SDK and development validation dependencies:

```bash
python -m pip install -e ".[dev]"
```

Canonical governed-test dependencies are deliberately pinned to exact public repository commits:

```bash
python -m pip install -e ".[dev,governed-test]"
```

The governed-test installation therefore requires Git plus network access to the pinned public repositories. That source-distribution requirement does not grant GitHub runtime authority.

## Moving development source

After the 1.1.0 freeze, new SDK capabilities continued to land on `main`, including portable governance verification and communication-edge work. Current moving development therefore uses the successor identity:

```text
1.2.0.dev0
```

This development identity is not a tag, release, PyPI publication, production activation, or substitute for the frozen 1.1.0 candidate.

## Authority boundary

```text
moving branch != release identity
commit freeze != tag publication
artifact validation != release
PyPI publication != runtime activation
GitHub != StegVerse runtime authority
credential authority = TV/TVC
```

The authoritative release state remains `VERSION.json` plus `PRODUCTION_RELEASE_SET_MIRROR_HANDOFF.md`.
