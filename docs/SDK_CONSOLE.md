# StegVerse SDK Console

The console is the generic public entry point for developers, testers, evaluators, humans, and assisting LLMs. It exposes discoverable SDK guidance and locally callable SDK surfaces without creating person-specific routes or authority.

## Install the current checkout

Use a repository checkout when evaluating current code so the console, examples, tests, and documentation are all at the same revision:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

The published package can lag the repository between releases. Treat a PyPI install as equivalent only after the corresponding release explicitly identifies the console revision.

## Enter the console

```bash
stegverse
```

Equivalent module entry:

```bash
python -m stegverse
```

The top-level console points to the canonical human-facing governance navigator:

```bash
stegverse governance
```

## Canonical governance navigation

```text
[000] Demo test sequence without user-supplied manifest
[00]  User-defined run parameters
[0]   Submit data for governance
[1]   Replay previously run set
[2]   Reconstruct previously run set
```

Use the interactive navigator or select one option directly:

```bash
stegverse governance
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
```

Options `000` and `00` are optional transparency/configuration surfaces. They are not prerequisites for ordinary governance or machine-to-machine use. A machine/LLM that already understands the accepted `stegverse.ingress-manifest.v1` profile may construct a conforming manifest and use the ordinary governed ingress path directly.

### 000 — worked transparency/demo sequence

`000` uses an SDK-owned dataset. The dataset begins with one labeled teaching example of each active governance disposition:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

The entire dataset is the submitted demo payload. The labeled outcomes are teaching data, not prior decisions or authority. The self-describing demo shape identifies the payload/dataset hash and the receipt classes required to prove manifest admission, governance processing, return ingestion, and exact-run custody. Runtime receipt values must remain explicitly pending until produced by the canonical runtime; they must not be fabricated.

`000` requests full explanatory manifest labels so a human or assisting LLM can see fields, transition classes, receipt classes, editability, return behavior, and authority boundaries.

### 00 — user-defined return/explanation parameters

`00` explains caller-facing run preferences.

```text
return_projection
  controls which user-disclosable transition receipts are returned

manifest_labels
  controls explanatory labels attached to returned sections
```

Both controls are caller-facing. Neither suppresses canonical ecosystem transitions or Master Records custody.

### 0 — ordinary governed submission

`0` is the ordinary submission path. The guide distinguishes:

```text
0A — raw/user data; SDK constructs the manifest
0B — preformatted machine manifest conforming to the accepted profile
```

Submission and structural manifest validity do not grant authority. A machine/LLM does not need `000` or `00` before `0B` if it already knows the canonical manifest contract.

### 1 — replay by manifest_receipt_id

Provide the `manifest_receipt_id` returned by an earlier exact governed run. The identifier is a canonical locator, not an authority token. Replay must link new replay evidence to the immutable original rather than overwrite history.

### 2 — reconstruction by manifest_receipt_id

Provide the `manifest_receipt_id` returned by the original run. Reconstruction uses retained manifests, hashes, receipts, state records, and lineage to rebuild the historical trajectory without re-executing consequential side effects. Native historical evidence must remain distinguishable from later reconstruction evidence.

## Return projection, labels, and custody

Every governed manifest can separately express caller-return receipt projection and caller-return explanation labels.

`return_projection.mode`:

```text
ALL      return all user-disclosable transition evidence
SELECTED return named transition classes
NONE     return no transition-detail receipt projection
```

`manifest_labels.mode`:

```text
ALL      explain/label all returned sections
SELECTED explain/label named sections
NONE     return no explanatory manifest labels
```

Required identity, integrity, governed-subject, and routing information remains part of the canonical run even when caller-facing projection is reduced. Neither `NONE` mode means StegVerse skipped, erased, or failed to retain underlying transitions. Master Records custody is independent of both controls.

The final `manifest_receipt_id` remains the canonical locator for the exact immutable run and the handle for later replay/reconstruction even when transition-detail or label projection is `NONE`.

## LLM and agent shape

An LLM/agent does not receive a privileged governance path:

```text
External LLM/framework
  -> optionally use 000 to explain the worked shape
  -> optionally use 00 to help configure caller preferences
  -> construct stegverse.ingress-manifest.v1
  -> ordinary manifest validation/canonicalization
  -> canonical governance
  -> consequence boundary if applicable
  -> return ingestion
  -> governed result + manifest_receipt_id
```

The same vocabulary and authority boundaries are visible to a human and an assisting LLM. Demo outcomes, labels, schema discovery, manifest validity, and receipt IDs grant no authority.

## Lower-level callable surfaces

The five governance options are navigation over the governed workflow. They are distinct from the lower-level focused SDK surfaces:

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Current callable surfaces:

```text
admissibility
llm-admissibility
math-admissibility
admittedcode
universal-entry
bridges
entry-points
```

General focused execution form:

```bash
stegverse run <surface> [options]
```

### LLM admissibility

A local posture test can evaluate supplied LLM output without calling a hosted provider:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

This does not create provider execution authority and is not a substitute for the ordinary governed manifest path.

### AdmittedCode

AdmittedCode is a focused portable receipt-verification surface, not the five-option governance workflow.

```bash
stegverse help-surface admittedcode
stegverse demo admittedcode
```

A valid `DENY` receipt being SDK `ACCEPTED` is intentional: acceptance means the portable receipt boundary validated. It does not convert the denied action into an allowed action.

## Credential boundary

The public console requires no GitHub token for local discovery, guidance, demos, tests, or receipt verification.

Do not supply GitHub tokens, provider keys, private keys, bearer tokens, passwords, or other secrets to the SDK console. Production credential semantics and protected route authority are owned by TV/TVC.

## Troubleshooting and validation

Useful commands:

```bash
stegverse
stegverse governance
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
stegverse surfaces
stegverse capabilities
pytest tests/ -v
```

If `stegverse` is not found after a repository checkout:

```bash
python -m pip install -e ".[dev]"
```

## Authority boundary

```text
000 grants authority: false
00 grants authority: false
manifest labels grant authority: false
schema discovery grants authority: false
manifest structural validity grants authority: false
manifest_receipt_id grants authority: false
return projection changes custody: false
replay overwrites history: false
reconstruction re-executes consequence: false
```

The console never converts discovery, explanation, configuration, or successful local evaluation into execution authority, deployment authority, publication authority, custody, standing, or broader admissibility.
