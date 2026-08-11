# StegVerse SDK

The StegVerse SDK is the public developer interface for **local, non-authorizing governance testing**: admissibility evaluation, receipt verification, bounded routing, integration development, and inspection of supported StegVerse entry surfaces.

It does **not** grant execution, deployment, mutation, publication, custody, standing, or authority merely because a request, route, receipt, or result validates successfully.

## 90-second quick start

The canonical current demo is the repository checkout so the console, examples, tests, and documentation are guaranteed to match the code you are evaluating.

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
stegverse surfaces
```

Then run the bundled AdmittedCode demonstration:

```bash
stegverse demo admittedcode
```

That command verifies both a portable `ALLOW` receipt and a portable `DENY` receipt locally. The expected posture is:

```text
ALLOW receipt -> SDK ACCEPTED + underlying decision ALLOW
DENY receipt  -> SDK ACCEPTED + underlying decision DENY
```

`ACCEPTED` means the SDK validated the portable receipt boundary. It **does not** rewrite the underlying decision and it creates no execution authority.

The equivalent console entry command is:

```bash
python -m stegverse
```

> The published `stegverse-sdk` package may lag the repository between releases. Do not assume a package release contains the current console until that release explicitly identifies it.

## Discover the SDK

Every developer, tester, and evaluator uses the same generic interface. There are no person-specific routes.

```bash
stegverse
stegverse surfaces
stegverse help-surface <surface>
stegverse capabilities
```

`stegverse surfaces` lists callable user-facing surfaces. `stegverse capabilities` returns the same public registry as JSON.

Current local console surfaces:

| Surface | Purpose | Fastest way to try it |
|---|---|---|
| `admittedcode` | Verify portable AdmittedCode provider-harness receipts | `stegverse demo admittedcode` |
| `admissibility` | Evaluate a governed tester packet locally | `stegverse help-surface admissibility` |
| `llm-admissibility` | Evaluate LLM text under the dynamic-admissibility bridge | `stegverse help-surface llm-admissibility` |
| `math-admissibility` | Evaluate a math/formalism artifact posture | `stegverse help-surface math-admissibility` |
| `universal-entry` | Route an envelope against an explicit capability registry | `stegverse help-surface universal-entry` |
| `bridges` | List registered dynamic-admissibility bridges | `stegverse run bridges` |
| `entry-points` | List canonical StegVerse entry-point roles | `stegverse run entry-points` |

Full console documentation: `docs/SDK_CONSOLE.md`.

## AdmittedCode

AdmittedCode is a normal first-class SDK surface. No special reviewer package, named-user route, private credential, or separate instruction channel is required to discover it.

Discover the contract:

```bash
stegverse help-surface admittedcode
```

Run the bundled self-contained proof:

```bash
stegverse demo admittedcode
```

Run only one case if desired:

```bash
stegverse demo admittedcode --case allow
stegverse demo admittedcode --case deny
```

Or verify the repository fixtures explicitly:

```bash
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json
```

The SDK checks the receipt schema, decision vocabulary, refusal/key-request boundary, authority escalation, and canonical receipt hash. A valid `DENY` receipt is expected to return SDK `ACCEPTED` while preserving `decision: DENY`.

## Dynamic admissibility

LLM output can be evaluated locally without calling a hosted model:

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

Math/formalism artifacts can be evaluated similarly:

```bash
stegverse run math-admissibility \
  --formalism RTG-STCM \
  --artifact-type solver_artifact \
  --summary "Candidate derivation for bounded review."
```

These are posture evaluations. They do not certify domain correctness or create execution proof.

## Universal entry

Universal-entry routing requires both the envelope and the capability registry to be supplied explicitly:

```bash
stegverse run universal-entry \
  --input <universal-entry-envelope.json> \
  --registry <capabilities.json>
```

The route is capability-bounded and may fail closed. Routing is not execution authority and is not custody.

## Credentials and TV/TVC

The public SDK console does not require GitHub tokens for its local test, demo, discovery, or verification surfaces.

Do not place GitHub tokens, provider keys, private keys, bearer tokens, passwords, or other secret material in SDK packets, fixtures, receipts, or console arguments. Production credential semantics and protected route authority belong to TV/TVC. The SDK does not acquire those credentials on behalf of a user.

Public repository inspection used by SDK support code is non-authorizing and credential-free. Private-source access is not a public SDK-console capability.

## Python API

The CLI is a discoverable front door, not a replacement for direct Python use. Public modules include dynamic admissibility, governed LLM contracts, receipt handling, AdmittedCode receipt consumption, system-boundary contracts, universal-entry routing, SDK-to-SPE progression contracts, comparison contracts, and bounded integration helpers.

Use `stegverse help-surface <surface>` to identify the module backing a console surface.

## Validate the checkout

```bash
pytest tests/ -v
```

Canonical hosted validation is defined in:

```text
.github/workflows/sdk-demo-test.yml
```

It covers supported Python versions, public imports, the complete test suite, route fixtures, dynamic-admissibility examples, package build, and wheel installation.

## Repository control files

The repository also contains internal continuity and project-control records. Files matching `*_MIRROR_HANDOFF.md` are not product entry points and are not generated when someone uses the SDK.

- `sdk.capabilities.json` records broader repository implementation/integration posture, including disabled or unobserved integrations.
- `SDK_MIRROR_HANDOFF.md` is the canonical repository work handoff.
- `stegverse/sdk_surfaces.py` is the callable public console registry.

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

The SDK fails closed rather than silently converting missing authority, unavailable capability, invalid evidence, unsupported input, or receipt corruption into success.
