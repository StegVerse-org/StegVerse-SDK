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

The optional governed-test dependencies are pinned to exact repository commits, but the complete governed-test dependency set is **not anonymously installable from current repository source visibility**. At least the Master Records source dependency is private in current live repository metadata.

```bash
python -m pip install -e ".[dev,governed-test]"
```

That command is therefore a source-repository installation path for callers that already have access to every pinned dependency. It must not be described as a credential-free public installation path. The public SDK `--prepare-only` external-framework submission path remains credential-free and does not require the private governed runtime dependency set.

The canonical public-distribution target is an immutable TVC-admitted artifact/package path whose acquisition does not depend on source-repository visibility. Until that publication path is verified, repository privacy and anonymous governed-test installation remain separate concerns.

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

Public-distribution privacy/repository-visibility continuation is tracked in `SDK_PUBLIC_DISTRIBUTION_PRIVACY_MIRROR_HANDOFF.md` and must be satisfied before claiming anonymous installation of the complete governed-test runtime dependency set.
