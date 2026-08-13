# StegVerse SDK

The StegVerse SDK is the public developer interface for **local, non-authorizing governance testing**: governed submission, replay/reconstruction guidance, admissibility evaluation, receipt verification, bounded routing, integration development, and inspection of supported StegVerse entry surfaces.

It does **not** grant execution, deployment, mutation, publication, custody, standing, or authority merely because a request, route, receipt, or result validates successfully.

## 90-second quick start

Use the repository checkout when evaluating current code so the console, examples, tests, and documentation are at the same revision.

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse
```

The console now points first to the governed workflow:

```bash
stegverse governance
```

That opens the canonical human-facing navigation:

| Option | Meaning |
|---|---|
| `000` | Optional worked transparency/demo sequence using the SDK-owned dataset |
| `00` | Optional user-defined return/explanation parameters |
| `0` | Ordinary governed submission |
| `1` | Replay a previously run set by `manifest_receipt_id` |
| `2` | Reconstruct a previously run set by `manifest_receipt_id` |

You can enter the interactive guide or request one option directly:

```bash
stegverse governance
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
```

`000` and `00` are **optional human/LLM transparency and configuration surfaces**. They are not prerequisites for ordinary evaluation or machine-to-machine use. A machine or LLM that already understands the accepted `stegverse.ingress-manifest.v1` profile can construct a conforming manifest and use the ordinary governed ingress path directly.

> The published `stegverse-sdk` package may lag the repository between releases. Do not assume a package release contains the current console until that release explicitly identifies the console revision.

## What the five governance options mean

### 000 — worked transparency/demo sequence

`000` explains the governed shape by worked example. The SDK-owned demo dataset contains one labeled teaching example of each active governance disposition:

```text
ALLOW
DENY
REVIEW
FAIL_CLOSED
```

The **entire dataset** is the demo payload. Those labeled examples are data, not prior authority or executable instructions. The demo is not allowed to claim canonical processing until the ordinary runtime supplies the corresponding admission, governance, return-ingestion, custody, and exact-run receipt evidence.

Option `000` requests full caller-visible receipt projection and explanatory labels so a human or assisting LLM can inspect what was submitted, which fields are editable, which transition/receipt classes exist, what is returned, what remains in canonical custody, and what is observation rather than authority.

### 00 — user-defined return/explanation parameters

`00` explains permitted caller-return preferences before an ordinary run. Two manifest controls are intentionally separate:

- `return_projection` controls which **user-disclosable transition receipts** are returned.
- `manifest_labels` controls whether returned sections carry explanatory titles/descriptions, transition-class labels, receipt-class labels, editability labels, and authority-boundary labels.

Both support `ALL`, `SELECTED`, and `NONE` modes where allowed by the manifest profile. Neither changes whether canonical ecosystem transitions occurred or were retained. **Master Records custody is independent of caller-facing return projection and explanatory labeling.**

### 0 — ordinary governed submission

`0` is the ordinary governed submission path.

The guide distinguishes:

```text
0A — submit raw/user data; the SDK constructs the governance manifest
0B — submit a preformatted machine manifest conforming to the accepted profile
```

A machine/LLM that already knows the canonical profile does not need to invoke `000` or `00` first.

### 1 — replay

`1` accepts the `manifest_receipt_id` from an earlier governed run as the canonical locator for replay. The identifier is a locator, **not an authority token**. Replay must preserve the original historical run and produce linked replay evidence rather than overwrite history.

### 2 — reconstruction

`2` uses a prior `manifest_receipt_id` to guide reconstruction of the retained historical trajectory from manifests, hashes, receipts, state records, and lineage. Reconstruction does not re-execute consequential side effects and must distinguish native historical evidence from evidence reconstructed later.

## The manifest and receipt boundary

Every governed run is represented by a manifest that separates:

1. profile and provenance;
2. governed subject, candidate, intent, consequence, and context;
3. integrity and attestation;
4. generated governance/consequence trajectory;
5. caller-return receipt projection; and
6. caller-return explanatory labels.

The completed exact run is identified by `manifest_receipt_id`. That identifier remains the handle for replay/reconstruction even when caller-facing transition detail or explanation-label projection is `NONE`.

Core invariants:

```text
submission != execution
manifest validity != ALLOW
manifest_receipt_id != authority
return_projection != custody
manifest_labels != authority
replay != historical rewrite
reconstruction != re-execution
provider output != authority
```

Detailed governance semantics: `docs/OPTIONAL_TRANSPARENCY_SURFACES.md` and the console's own `stegverse governance` guidance.

## Discover the rest of the SDK

The governance navigator is the easiest human entry point. The lower-level callable SDK surfaces remain available for developers, integrations, and focused tests:

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Current local console surfaces:

| Surface | Purpose | Fastest way to try it |
|---|---|---|
| `admittedcode` | Verify portable AdmittedCode provider-harness receipts | `stegverse demo admittedcode` |
| `admissibility` | Evaluate a governed tester packet locally | `stegverse help-surface admissibility` |
| `llm-admissibility` | Evaluate supplied LLM text under the dynamic-admissibility bridge | `stegverse help-surface llm-admissibility` |
| `math-admissibility` | Evaluate a math/formalism artifact posture | `stegverse help-surface math-admissibility` |
| `universal-entry` | Route an envelope against an explicit capability registry | `stegverse help-surface universal-entry` |
| `bridges` | List registered dynamic-admissibility bridges | `stegverse run bridges` |
| `entry-points` | List canonical StegVerse entry-point roles | `stegverse run entry-points` |

These focused surfaces are **not replacements for the 000/00/0/1/2 governance navigation**. AdmittedCode, for example, is a portable receipt-verification surface; it is not the five-option experiment workflow.

Full console documentation: `docs/SDK_CONSOLE.md`.

## LLM / agent use

The SDK and LLM-adapter environments intentionally meet at a manifest boundary rather than by giving an LLM special authority.

```text
Human <-> optional 000/00 assistance
             |
External LLM/framework
             |
             +-> construct stegverse.ingress-manifest.v1
             |
             -> ordinary governed ingress
             -> canonical governance/consequence boundary
             -> governed result + manifest_receipt_id
```

An assisting LLM may use the same `000` and `00` semantics available to a human to explain or configure a request. There is no privileged AI-only explanation path. Demo outcomes, labels, schema discovery, structural validity, and receipt identifiers do not become authority merely because an LLM consumed them.

For a simple local LLM-output posture test that does **not** call a hosted model:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

This evaluates supplied model output locally. It does not create provider execution authority or replace the ordinary manifest-governance path.

The separate `StegVerse-org/LLM-adapter` repository owns provider/runtime translation and transport boundaries. The public SDK does not expose protected model/runtime credentials or acquire LLM execution authority.

## AdmittedCode

AdmittedCode remains a first-class SDK surface for portable provider-harness receipt verification.

```bash
stegverse help-surface admittedcode
stegverse demo admittedcode
```

The bundled demo verifies both a portable `ALLOW` receipt and a portable `DENY` receipt. `ACCEPTED` means the SDK validated the portable receipt boundary; it does **not** rewrite the underlying decision.

## Credentials and TV/TVC

The public SDK console requires no GitHub token for local discovery, demos, tests, guidance, or receipt verification.

Do not place GitHub tokens, provider keys, private keys, bearer tokens, passwords, or other secret material in SDK packets, fixtures, receipts, or console arguments. Production credential semantics and protected route authority belong to TV/TVC. The SDK does not acquire those credentials on behalf of a user.

## Validate the checkout

```bash
pytest tests/ -v
```

For evaluator-facing changes, validation should include the public discovery path itself:

```bash
stegverse
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
stegverse surfaces
```

## Repository control files

Files matching `*_MIRROR_HANDOFF.md` preserve implementation continuity, validation state, and task ownership. They are project-control records, not SDK user commands and not part of the evaluator's required path.

The public evaluator should be able to understand the current ordinary SDK from this README plus the installed console/help output without a private instruction channel.
