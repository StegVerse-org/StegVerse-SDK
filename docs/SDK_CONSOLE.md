# StegVerse SDK Console

The console is the generic entry point for developers, testers, and evaluators. It exposes only locally callable SDK surfaces and does not create person-specific routes.

## Install the current canonical demo

Use a repository checkout when evaluating the current code so the console, examples, tests, and documentation are at the same revision:

```bash
git clone https://github.com/StegVerse-org/StegVerse-SDK.git
cd StegVerse-SDK
python -m pip install -e ".[dev]"
```

The published package can lag the repository between releases. A PyPI install should only be treated as equivalent after the corresponding release identifies the console feature.

## Enter the SDK

```bash
stegverse
```

Equivalent:

```bash
python -m stegverse
```

## Discover callable surfaces

```bash
stegverse surfaces
```

For help:

```bash
stegverse help-surface <surface>
```

For a machine-readable view of the callable console registry:

```bash
stegverse capabilities
```

The repository-level `sdk.capabilities.json` is broader. It records implementation and integration posture, including disabled or unobserved dependencies; it is not the same thing as the callable console registry.

## Run a surface

```bash
stegverse run <surface> [options]
```

Current runnable local surfaces:

```text
admissibility
llm-admissibility
math-admissibility
admittedcode
universal-entry
bridges
entry-points
```

Always use `stegverse help-surface <surface>` to see the exact input contract.

## AdmittedCode receipt verification

Discover it generically:

```bash
stegverse help-surface admittedcode
```

Repository checkout examples:

```bash
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.allow.json
stegverse run admittedcode --input examples/governed_llm_demo/admittedcode/admissibility_receipt.deny.json
```

A result of SDK `ACCEPTED` validates the receipt boundary. It does not alter the receipt's underlying `ALLOW`, `DENY`, or `FAIL_CLOSED` decision.

## LLM admissibility

```bash
stegverse run llm-admissibility \
  --provider fixture-provider \
  --model fixture-model \
  --prompt "Draft a research note." \
  --output "A bounded research note."
```

Optional:

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

This evaluates what posture the artifact may take. It does not certify mathematical correctness or proof closure.

## Generic admissibility packet

```bash
stegverse run admissibility --input <tester-packet.json>
```

The input must be a JSON object in the SDK tester-packet family.

## Universal-entry routing

```bash
stegverse run universal-entry \
  --input <universal-entry-envelope.json> \
  --registry <capability-registry.json>
```

The registry is explicit because routing must not silently assume capabilities. Unsupported or unavailable lanes fail closed according to the universal-entry contract.

## Inspect bridge and entry-point registries

```bash
stegverse run bridges
stegverse run entry-points
```

These commands are useful for determining what adapter bridges and entry-point roles the installed SDK recognizes.

## Credential boundary

The public console does not require GitHub tokens for these local tasks.

Do not supply GitHub tokens, provider keys, private keys, passwords, or bearer tokens to the SDK console. Production credential semantics and route authority are owned by TV/TVC. Any protected or live execution route must cross that governed authority boundary instead of acquiring credentials through the SDK.

Private-source access is not a public SDK-console capability. Public source reads are non-authorizing and should be credential-free.

## Repository control files are not console surfaces

Files such as `SDK_MIRROR_HANDOFF.md` and other `*_MIRROR_HANDOFF.md` files preserve implementation continuity, validation state, and task ownership. They are repository control records, not SDK user commands and not artifacts generated merely by accessing the SDK.

## Validate the checkout

```bash
pytest tests/ -v
```

Hosted validation is defined by `.github/workflows/sdk-demo-test.yml`.

## Authority boundary

The console never converts discovery or successful local evaluation into execution authority, deployment authority, publication authority, custody, standing, or admissibility beyond the explicit result contract returned by the selected SDK surface.
