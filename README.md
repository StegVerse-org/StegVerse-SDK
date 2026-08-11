# StegVerse SDK

The StegVerse SDK is the developer-facing, non-authorizing Python interface for local governance testing, admissibility evaluation, receipt verification, bounded routing, and integration development.

It is not an execution authority. It does not grant deployment, mutation, publication, custody, standing, or admissibility simply because a request, route, receipt, or result is accepted.

## Start here

The current canonical demo is the repository checkout. This guarantees that the console, examples, tests, and documentation match the exact code being evaluated:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse
```

The equivalent entry command is:

```bash
python -m stegverse
```

The published `stegverse-sdk` package may lag the repository between releases. Do not assume a package release contains a console feature until that release identifies it.

## Discover the SDK from the console

Every developer, tester, and evaluator uses the same interface. There are no person-specific routes.

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

`stegverse surfaces` lists only user-facing surfaces that are callable from the installed SDK. `stegverse capabilities` prints that same public surface registry as JSON.

## Run an allowed local surface

```bash
stegverse run <surface> [options]
```

Current generic console surfaces are:

| Surface | What it does | Example |
|---|---|---|
| `admissibility` | Evaluate a governed tester packet locally | `stegverse run admissibility --input packet.json` |
| `llm-admissibility` | Evaluate LLM text under the SDK admissibility bridge | `stegverse help-surface llm-admissibility` |
| `math-admissibility` | Evaluate a math/formalism artifact | `stegverse help-surface math-admissibility` |
| `admittedcode` | Verify a portable AdmittedCode receipt | `stegverse run admittedcode --input receipt.json` |
| `universal-entry` | Route an envelope against an explicit capability registry | `stegverse help-surface universal-entry` |
| `bridges` | List registered dynamic-admissibility bridges | `stegverse run bridges` |
| `entry-points` | List canonical StegVerse entry-point roles | `stegverse run entry-points` |

Full console documentation is in `docs/SDK_CONSOLE.md`.

## AdmittedCode

AdmittedCode is a normal SDK surface, not a special evaluator mode. Any SDK user can discover it:

```bash
stegverse help-surface admittedcode
```

Then verify a receipt:

```bash
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json
```

The SDK validates the portable receipt boundary and preserves the underlying decision. SDK `ACCEPTED` means the receipt is structurally and cryptographically acceptable to the SDK consumer; it does not convert a `DENY` into an `ALLOW`.

## Dynamic admissibility

A local LLM-output example:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

A local formalism example:

```bash
stegverse run math-admissibility \
  --formalism RTG-STCM \
  --artifact-type solver_artifact \
  --summary "Candidate derivation for bounded review."
```

These SDK evaluations are local and non-authorizing. They do not certify domain correctness or create execution proof.

## Universal entry

The SDK includes deterministic universal-entry routing. Supply both the request envelope and the capability registry explicitly:

```bash
stegverse run universal-entry \
  --input <universal-entry-envelope.json> \
  --registry <capabilities.json>
```

Routing is capability-bounded and can fail closed. A routing result does not grant execution authority or custody.

## Credentials and TV/TVC boundary

The public SDK console does not require GitHub tokens for its local test and verification surfaces.

Production credential semantics and route authority belong to TV/TVC. Do not place GitHub tokens, provider keys, private keys, or other credential material into SDK packets, examples, receipts, or console arguments. Protected or live execution routes must cross the separately governed TV/TVC authority boundary rather than acquiring credentials inside the SDK.

Public repository source inspection, when used by SDK support code, is non-authorizing and should remain credential-free. Private-source access is not a public SDK-console capability.

## What the SDK is for

The canonical SDK role is developer-native programmatic intake, testing, integration, and observation. Existing modules include dynamic admissibility, governed LLM contracts, receipt handling, system-boundary contracts, universal-entry routing, SDK-to-SPE progression contracts, comparison contracts, and bounded integration helpers.

The repository contains internal handoffs and project-control records as well as product code. Files such as `*_MIRROR_HANDOFF.md` are development continuity records; they are not user entry points and are not created by someone merely accessing the SDK.

## Validate the checkout

```bash
pytest tests/ -v
```

The canonical hosted validation workflow is:

```text
.github/workflows/sdk-demo-test.yml
```

The workflow tests Python compatibility, public imports, the complete test suite, route fixtures, dynamic admissibility examples, package build, and wheel installation.

## Machine-readable repository state

`sdk.capabilities.json` records repository implementation and integration posture. It can contain internal or not-yet-live integration state and therefore is not the same thing as the console's callable-surface list.

`SDK_MIRROR_HANDOFF.md` is the canonical repository work handoff. It is a project-control record, not SDK usage documentation.

## Authority boundary

```text
submission != execution
routing != execution
validation != authority
receipt acceptance != action approval
SPE ALLOW != execution
local persistence != custody
provider output != authority
```

The SDK should fail closed rather than silently convert missing authority, unavailable capability, invalid evidence, or unsupported input into success.
