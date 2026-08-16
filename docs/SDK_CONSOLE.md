# StegVerse SDK Console

The console is the public entry point for developers, testers, evaluators, humans, and assisting LLMs.

## Install

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

## Governance navigation

```bash
stegverse governance
```

```text
[000] worked transparency/demo
[00]  user-defined return/explanation preferences
[0]   ordinary governed submission
[1]   replay by manifest_receipt_id
[2]   reconstruction by manifest_receipt_id
```

Direct help:

```bash
stegverse governance --select 000
stegverse governance --select 00
stegverse governance --select 0
stegverse governance --select 1
stegverse governance --select 2
```

`000` and `00` are optional. Machines that already understand the canonical manifest profile can use ordinary governed ingress directly.

## Evaluator-defined testing boundary

The SDK public-inspection manifest supports an optional `evaluation_declaration` that lets an evaluator record the experiment's WHAT, HOW, and WHY at submission time. This is intentionally separate from the canonical StegGate decision input under `input.steggate_request`.

```text
evaluator declares experiment
-> SDK validates only published capability/evidence identifiers
-> canonical route remains unchanged
-> StegGate evaluates submitted governing inputs
-> Master Records retains exact-run evidence
-> replay/reconstruction remain separately callable by receipt locator
```

The declaration may include:

```text
what
how
why
expected_observation
requested_capabilities
requested_evidence
```

Published evaluator capability identifiers are currently:

```text
commit_time_admissibility
bounded_consequence
master_records_custody
replay
reconstruction
```

The contract is **configuration, not augmentation**. A manifest cannot install a missing capability, hot-patch the route, or change semantics for a particular evaluator. Unknown requested capabilities are rejected before execution. Evaluator identity and `expected_observation` are retained as declaration/evidence context but are not StegGate decision inputs.

The sovereign runtime returns SHA-256 bindings for the normalized submitted manifest, the exact StegGate request, and the returned result. The manifest and governance-request hashes are also placed in retained transaction metadata before exact-run custody.

See:

```text
inspection/request.schema.json
inspection/examples/governed-test-request.json
```

## Portable S / NS ecosystem packages

SDK early access is the initial distribution surface for portable StegVerse Micro-Ecosystems.

The user explicitly chooses one deployment class:

```text
S  = StegVerse S Ecosystem / isolated Sovereign deployment
NS = StegVerse NS Ecosystem / Node Sovereign profile
```

There is no default. Installing an NS package does not create Node Sovereign membership.

Discover the package choices:

```bash
stegverse-portable list
stegverse-portable inspect --deployment-class S
stegverse-portable inspect --deployment-class NS
```

Verify a downloaded or otherwise supplied package before installation:

```bash
stegverse-portable verify --archive ./stegverse-sdk-s-micro-ecosystem-v0.zip
```

Install a verified package without executing it:

```bash
stegverse-portable install \
  --archive ./stegverse-sdk-s-micro-ecosystem-v0.zip \
  --destination ./portable-ecosystems
```

Installation produces `INSTALLATION_RECEIPT.json` and reports `INSTALLED_NOT_ACTIVATED`.

Remote download is already represented in the console contract:

```bash
stegverse-portable download \
  --deployment-class S \
  --output ./stegverse-sdk-s-micro-ecosystem-v0.zip
```

Until an exact governed release artifact and expected archive SHA-256 are bound in the SDK catalog, this command deliberately fails closed with:

```text
NO_GOVERNED_RELEASE_ARTIFACT
```

The console never guesses a mutable `latest` URL or treats GitHub hosting as runtime authority.

Package verification requires an inspectable `PACKAGE_RECEIPT.json`, verifies every declared file hash and size, rejects undeclared files and unsafe paths, prohibits provider-account/non-TV/TVC-secret requirements, and rejects any NS package that claims installation itself confers node membership.

The portable-product lifecycle is intentionally staged:

```text
SDK_EARLY_ACCESS
-> SDK_COMMUNITY
-> APP_PRODUCT_CANDIDATE
-> PAID_PRODUCT_CANDIDATE
```

The transition timing is governed by actual reliability, security, recovery, usage, community, and support evidence rather than a hard-coded date.

## Run the sovereign governed TEST

Install the pinned canonical test components:

```bash
python -m pip install -e ".[dev,governed-test]"
```

Run:

```bash
python -m stegverse.public_inspection_runtime run inspection/examples/governed-test-request.json
```

The default runtime is local and uses canonical pinned Core-Lite, StegCore/StegGate, and Master Records implementations. Its consequence is simulated and produces no external side effect. The test records the governance and route evidence locally before reporting success.

Default local custody file:

```text
./stegverse-master-records-validation.db
```

The sovereign evaluator path does not require a hosted evaluator or a GitHub token as runtime authority.

## Replay

```bash
python -m stegverse.public_inspection_runtime replay MR-<SHA256>
```

Replay preserves the original run and does not invoke the original consequence. Its own operation history is recorded before return.

## Reconstruction

```bash
python -m stegverse.public_inspection_runtime reconstruct MR-<SHA256>
```

Reconstruction preserves the original run and does not re-execute the original consequence. Its own operation history is recorded before return.

## Frozen evaluator evidence

See:

```text
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
```

The retained T0/T1-A/T1-B validation records exact-run custody, manifested-route custody, replay custody, and reconstruction custody as PASS on the sovereign path.

## Focused subsystem tests

```bash
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

Focused surfaces include `admittedcode`, `admissibility`, `llm-admissibility`, `math-admissibility`, `universal-entry`, `bridges`, and `entry-points`.

AdmittedCode example:

```bash
stegverse demo admittedcode
```

LLM-output example:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

## Public inspection request preparation

```bash
python scripts/validate_public_inspection_request.py inspection/examples/example-request.json
python -m stegverse.public_inspection inspection/examples/example-request.json
```

Preparation does not claim a governed run or produce a receipt locator. The standalone validation script delegates to the same manifest validator used by the SDK runtime so the documented preflight contract does not drift from executable validation.

## Authority boundary

```text
submission != execution
validation != authority
receipt locator != authority
SDK package install != activation
NS package install != Node Sovereign membership
package verification != StegGate ALLOW
replay != historical rewrite
reconstruction != consequence re-execution
provider output != authority
configuration != route augmentation
evaluator identity != decision input
expected observation != decision input
GitHub != StegVerse runtime authority
```

The current README is the primary public quick-start document and should remain synchronized with this console reference.
