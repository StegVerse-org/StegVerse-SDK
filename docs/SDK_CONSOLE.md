# StegVerse SDK Console

The console is the generic public entry point for developers, testers, and evaluators. It exposes only locally callable SDK surfaces and does not create person-specific routes.

## Install the canonical current demo

Use a repository checkout when evaluating current code so the console, examples, tests, and documentation are all at the same revision:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

The published package can lag the repository between releases. Treat a PyPI install as equivalent only after the corresponding release explicitly identifies the console revision.

## Enter and discover

```bash
stegverse
stegverse surfaces
```

Equivalent module entry:

```bash
python -m stegverse
```

For detailed help on any callable surface:

```bash
stegverse help-surface <surface>
```

For the machine-readable public registry:

```bash
stegverse capabilities
```

The repository-level `sdk.capabilities.json` is intentionally broader. It records implementation and integration posture, including disabled or unobserved dependencies, and is not the same thing as the callable console registry.

## Runnable surfaces

```text
admissibility
llm-admissibility
math-admissibility
admittedcode
universal-entry
bridges
entry-points
```

General execution form:

```bash
stegverse run <surface> [options]
```

Always use `stegverse help-surface <surface>` to inspect the exact local contract, backing module, documentation pointer, examples, and authority posture.

## AdmittedCode

AdmittedCode is a first-class generic SDK surface for portable provider-harness receipt verification.

Discover it:

```bash
stegverse help-surface admittedcode
```

Run the bundled credential-free demonstration:

```bash
stegverse demo admittedcode
```

The demo exercises both canonical repository fixtures. Expected semantics:

```text
allow fixture -> verification.status = ACCEPTED; verification.decision = ALLOW
deny fixture  -> verification.status = ACCEPTED; verification.decision = DENY
authority_effect = NONE
```

A valid `DENY` receipt being SDK `ACCEPTED` is intentional: acceptance means the portable receipt boundary validated. It does not convert the denied action into an allowed action.

Run a single bundled case:

```bash
stegverse demo admittedcode --case allow
stegverse demo admittedcode --case deny
```

Or verify a receipt directly:

```bash
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json
```

The SDK consumer validates required fields, supported schema, allowed decision vocabulary, the refusal/key-request boundary, authority escalation, and the canonical receipt hash. Corrupt, unsupported, or authority-escalating receipts return `REJECTED` rather than being coerced into success.

## LLM admissibility

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

Optional fields:

```text
--intent <declared-intent>
--consequence <level>
```

This is local SDK evaluation. It does not call a hosted provider and does not create provider execution authority.

## Math/formalism admissibility

```bash
stegverse run math-admissibility \
  --formalism RTG-STCM \
  --artifact-type solver_artifact \
  --summary "Candidate derivation for bounded review."
```

This evaluates allowed posture. It does not certify mathematical correctness or proof closure.

## Generic admissibility packet

```bash
stegverse run admissibility --input <tester-packet.json>
```

The input must be a JSON object in the SDK tester-packet family. Missing or malformed input fails closed with a nonzero exit code.

## Universal-entry routing

```bash
stegverse run universal-entry \
  --input <universal-entry-envelope.json> \
  --registry <capability-registry.json>
```

The registry is explicit because routing must not silently assume capabilities. Unsupported or unavailable lanes fail closed according to the universal-entry contract.

## Inspect registries

```bash
stegverse run bridges
stegverse run entry-points
```

These commands show the dynamic-admissibility bridges and canonical entry-point roles recognized by the installed SDK.

## Credential boundary

The public console requires no GitHub token for local discovery, demos, tests, or receipt verification.

Do not supply GitHub tokens, provider keys, private keys, bearer tokens, passwords, or other secrets to the SDK console. Production credential semantics and protected route authority are owned by TV/TVC. Any protected or live execution route must cross that governed authority boundary instead of acquiring credentials through the SDK.

Private-source access is not a public console capability. Public source reads used by support code are non-authorizing and credential-free.

## Exit behavior and troubleshooting

Successful local commands return exit code `0`. Invalid input, unknown surfaces, unsupported demos, malformed JSON, and missing required arguments return a nonzero code and an `ERROR:` or explicit failure message.

Useful recovery commands:

```bash
stegverse surfaces
stegverse help-surface admittedcode
stegverse capabilities
pytest tests/test_cli.py -v
```

If `stegverse` is not found after a repository checkout, reinstall the editable package from the repository root:

```bash
python -m pip install -e ".[dev]"
```

## Repository control files are not product surfaces

`SDK_MIRROR_HANDOFF.md` and other `*_MIRROR_HANDOFF.md` files preserve implementation continuity, validation state, and task ownership. They are project-control records, not SDK user commands, and they are not generated by someone merely accessing the SDK.

## Validate the checkout

```bash
pytest tests/ -v
```

Hosted validation is defined by `.github/workflows/sdk-demo-test.yml`.

## Authority boundary

The console never converts discovery or successful local evaluation into execution authority, deployment authority, publication authority, custody, standing, or broader admissibility beyond the explicit result contract returned by the selected SDK surface.
