# StegVerse SDK Console

The SDK console is the generic entry point for developers, testers, and evaluators. It does not provide person-specific routes.

## Install

From the published package:

```bash
python -m pip install stegverse-sdk
```

Or from a repository checkout:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e .
```

## Enter the SDK

```bash
stegverse
```

The equivalent module invocation is:

```bash
python -m stegverse
```

## Discover what is available

Do not assume a capability exists because another StegVerse repository mentions it. Ask the SDK:

```bash
stegverse surfaces
```

For the complete machine-readable state:

```bash
stegverse capabilities
```

For help on a discovered surface:

```bash
stegverse help-surface <surface>
```

## AdmittedCode / admissibility

AdmittedCode is not a special-user mode. Any SDK user looking for admissibility or governed receipt integration can discover the relevant contracts from the SDK:

```bash
stegverse help-surface admittedcode
stegverse capabilities | grep -i admiss
```

The SDK remains non-authorizing. Discovery, routing, manifests, receipts, provider output, and progression results do not by themselves grant execution, delegation, mutation, publication, custody, standing, deployment, or activation authority.

## Allowed demo/test workflow

1. Install the SDK.
2. Run `stegverse surfaces`.
3. Use `stegverse help-surface <surface>` to understand the selected surface.
4. Inspect `stegverse capabilities` for its implemented/connected/disabled status.
5. Follow the repository documentation/examples for that surface.
6. Run only operations that the capability registry and documentation identify as available. Disabled, unconfigured, or authority-gated integrations remain unavailable until their governing boundary is satisfied.

## Developer checkout validation

```bash
python -m pip install -e ".[dev]"
pytest tests/
```

The canonical repository state and restrictions are recorded in `SDK_MIRROR_HANDOFF.md` and `sdk.capabilities.json`; these are project-control records, not separate user-specific entry points.
