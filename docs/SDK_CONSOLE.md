# StegVerse SDK Console

The console is the generic public entry point for developers, testers, evaluators, humans, and assisting LLMs. It exposes discoverable SDK guidance and locally callable surfaces without creating person-specific routes or authority.

## Install the current checkout

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

A published package may lag the repository between releases. Use the checkout when evaluating current code and documentation.

## Canonical governance navigation

```bash
stegverse governance
```

```text
[000] Demo test sequence without user-supplied manifest
[00]  User-defined run parameters
[0]   Submit data for governance
[1]   Replay previously run set
[2]   Reconstruct previously run set
```

Options `000` and `00` are optional transparency/configuration surfaces. Machines and LLMs that already understand `stegverse.ingress-manifest.v1` can use ordinary governed ingress directly.

### 0 — ordinary governed submission

```text
0A — raw/user data; SDK constructs the manifest
0B — preformatted machine manifest conforming to the accepted profile
```

Submission and structural manifest validity do not grant authority.

### 1 and 2 — retained evidence

`1` replays by `manifest_receipt_id` without overwriting the original. `2` reconstructs by the same locator without re-executing consequential side effects. The locator is not authority.

## Public inspection preparation

A public inspection request is a bounded declarative request described by `inspection/request.schema.json`. An ordinary pull request may carry the request as a visible submission/discussion record, but the PR is not the evaluator/runtime and is not Master Records custody.

Validate and prepare the example:

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

`python -m stegverse.public_inspection` converts the validated request into the ordinary option `0A` descriptor. It does **not** claim a governed run occurred. Until a trusted processor actually uses the admitted path, the prepared output remains `runtime_processing_status: NOT_RUN`, `master_records_custody_status: NOT_CLAIMED`, and `manifest_receipt_id: null`.

```text
public request
-> bounded validation
-> option 0A descriptor
-> trusted governed ingress
-> canonical governance / consequence boundary
-> canonical custody
-> caller projection
-> manifest_receipt_id may be associated with the public record
```

Detailed instructions: `docs/PUBLIC_INSPECTION_ENTRY.md`.

## Return projection, labels, and custody

`return_projection` controls user-disclosable transition evidence. `manifest_labels` controls explanatory labels. Neither can suppress canonical transitions or Master Records custody.

## Lower-level callable surfaces

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
stegverse run <surface> [options]
```

Focused surfaces include admissibility, LLM-output admissibility, math/formalism posture, AdmittedCode receipt verification, universal entry, bridge discovery, and entry-point discovery. These are not replacements for the canonical governance navigation.

## LLM and agent boundary

An LLM may explain or construct a conforming request or manifest. It does not receive a privileged governance path. Schema discovery, local validation, demo outcomes, labels, and receipt identifiers do not grant authority.

## Validation

```bash
pytest tests/ -v
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m unittest tests.test_public_inspection_request
python -m unittest tests.test_public_inspection_governed_binding
python -m stegverse.public_inspection inspection/examples/example-request.json
```

## Authority boundary

```text
000 grants authority: false
00 grants authority: false
public PR grants runtime authority: false
public PR creates custody: false
manifest structural validity grants authority: false
manifest_receipt_id grants authority: false
return projection changes custody: false
replay overwrites history: false
reconstruction re-executes consequence: false
```
