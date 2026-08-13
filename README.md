# StegVerse SDK

The StegVerse SDK is the public developer interface for local, non-authorizing governance testing, governed submission preparation, replay/reconstruction guidance, receipt verification, bounded routing, and inspectable public requests.

A request, manifest, pull request, validation result, or receipt locator does not by itself grant execution, custody, release, standing, or other authority.

## Quick start

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse governance
```

Canonical governance navigation:

| Option | Meaning |
|---|---|
| `000` | Optional worked transparency/demo sequence |
| `00` | Optional return/explanation preferences |
| `0` | Ordinary governed submission |
| `1` | Replay by `manifest_receipt_id` |
| `2` | Reconstruction by `manifest_receipt_id` |

`000` and `00` are optional. A machine or LLM that already understands `stegverse.ingress-manifest.v1` can use ordinary governed ingress directly.

## Public inspection requests

A contributor can create a distinct, visible inspection request through an ordinary pull request using `.github/PULL_REQUEST_TEMPLATE/public-inspection-request.md` and `inspection/request.schema.json`.

The PR is a submission and discussion record only. It is not the evaluator implementation, execution authority, release authority, or Master Records custody.

Validate and prepare the example request locally:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

The preparation command binds the declarative request to the ordinary SDK **option 0A** raw-data submission descriptor. Preparation deliberately reports that runtime processing has not run, custody has not been claimed, and no `manifest_receipt_id` exists yet. Those facts may change only after a trusted processor actually runs the request through the admitted governed path.

```text
public PR or local request
  -> bounded declarative validation
  -> ordinary SDK option 0A descriptor
  -> trusted governed ingress
  -> StegGate governance / consequence boundary
  -> full canonical Master Records custody
  -> caller projection
  -> manifest_receipt_id may be posted back to the public record
```

Untrusted PR code is not used as the evaluator/runtime. Inspection requests must remain declarative and must not include secrets, credentials, executable instructions, workflow authority, or authority claims.

Detailed instructions: `docs/PUBLIC_INSPECTION_ENTRY.md`.

## Ordinary governed submission

Option `0` has two forms:

```text
0A — raw/user data; the SDK constructs the governance manifest
0B — preformatted machine manifest conforming to stegverse.ingress-manifest.v1
```

Public inspection requests bind to `0A`; they do not create a separate evaluator path.

Caller-facing controls remain separate from custody:

- `return_projection` controls which user-disclosable transition receipts are returned.
- `manifest_labels` controls explanatory labels on the returned package.
- Neither can suppress canonical transition recording or Master Records custody.

## Replay and reconstruction

`manifest_receipt_id` is the canonical locator for an exact retained run; it is not authority.

`1` replays without rewriting the original history. `2` reconstructs the retained trajectory without re-executing consequential side effects and must distinguish native historical evidence from later reconstruction material.

## Core invariants

```text
submission != execution
manifest validity != ALLOW
public PR != runtime authority
public PR != Master Records custody
manifest_receipt_id != authority
return_projection != custody
manifest_labels != authority
replay != historical rewrite
reconstruction != re-execution
```

## Other SDK surfaces

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Focused surfaces remain available for AdmittedCode receipt verification, admissibility evaluation, LLM-output admissibility, math/formalism posture, universal entry routing, bridge discovery, and entry-point discovery. They are not replacements for the canonical `000/00/0/1/2` navigation.

Console documentation: `docs/SDK_CONSOLE.md`.

## LLM / agent boundary

An LLM may help construct or explain a request. It does not receive special authority by doing so. Provider/runtime translation belongs to `StegVerse-org/LLM-adapter`; protected runtime authority remains outside the public request surface.

## Validate the checkout

```bash
pytest tests/ -v
python scripts/verify_github_fallback_boundary.py
python -m unittest tests.test_github_fallback_boundary
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
```

For the public inspection preparation path:

```bash
python -m stegverse.public_inspection inspection/examples/example-request.json
```

## Repository control files

Files matching `*_MIRROR_HANDOFF.md` preserve implementation continuity, validation state, and task ownership. They are project-control records, not evaluator commands. The public SDK should remain understandable from this README, installed help, and public documentation without a private instruction channel.
