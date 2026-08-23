# Post-Freeze SDK Release Boundary Mirror Handoff

Updated: 2026-08-23
Repository: `StegVerse-org/StegVerse-SDK`

## Goal
Reduce public/evaluator ambiguity and portability limitations identified while preparing the SDK for public announcement, without mutating the frozen SDK 1.1.0 release candidate or transferring release/runtime authority to GitHub.

## Completed implementation

```text
PR: #72
merge: b8d763619290b2c9d6ea49aa1b46f3eea4e250eb
frozen SDK 1.1.0 candidate: 922d6c5235229e854c36e1a194dc99ed15a31b51
frozen tree: d9ddda3dbe942324c921051d89ec19eec3970b16
post-freeze moving development identity: 1.2.0.dev0
credential authority: TV/TVC
GitHub runtime authority: NONE
```

Implemented reductions:

1. `pyproject.toml` no longer identifies moving post-freeze source as `1.1.0`; current development is `1.2.0.dev0`.
2. `VERSION.json` keeps the immutable `1.1.0` release candidate and separately records the non-release moving development line.
3. `docs/REPRODUCIBLE_RELEASE_CANDIDATE.md` gives exact commit/tree verification and installation commands for independent evaluators.
4. `stegverse-verify-governance` exposes the portable governance verifier as an installed CLI rather than requiring direct Python integration.
5. The verifier CLI fails closed and explicitly retains `verification_authority=NONE`, `execution_authorized=false`, `standing_minted=false`, `admissibility_decided=false`, and `custody_claimed=false` on invalid input.
6. `.github/workflows/package-artifact-validation.yml` is generalized to validate package name/version/Requires-Python/entry points from canonical `pyproject.toml` instead of hard-coding `1.1.0`.
7. The package validator now smoke-tests the installed `stegverse-verify-governance` command.

## Validation evidence

PR #72 exact head before merge:

```text
head: 4502488a980644426bc711dc22d09ff09e2cb5e4
SDK Package Artifact Validation: 32669714496 SUCCESS
Portable Package Source Validation: 32669714469 SUCCESS
SDK Output-Boundary Proof Validation: 32669714510 SUCCESS
MCP Source Validation: 32669714494 SUCCESS
Connect my LLM Source Validation: 32669714459 SUCCESS
Portable Release Index: 32669714476 SUCCESS
Evaluator Contract Console Validation: 32669714474 SUCCESS
Communication Edge SDK Demo Validation: 32669714446 SUCCESS
```

The communication-edge validation passed its Python 3.9, 3.11, and 3.12 matrix. The artifact validator passed anonymous exact-source materialization, wheel/sdist build, metadata derivation from `pyproject.toml`, legacy setuptools convergence, isolated wheel install/import, primary console smoke, and portable verifier CLI smoke.

## Current public release truth

```text
SDK 1.1.0 artifact validation: PASS
SDK 1.1.0 frozen candidate: immutable
SDK 1.1.0 tag publication: NOT YET COMPLETE
SDK 1.1.0 PyPI publication: NOT YET COMPLETE
PyPI Trusted Publishing source path: MERGED
post-freeze main: 1.2.0.dev0 / NOT A RELEASE IDENTITY
```

The remaining 1.1.0 publication gap is not solved by relabeling moving source. TVC issue #78 remains the release authority path. Exact R3 admitted source validation, matching TV authorization/grant, short-lived TVC-managed publication capability, immutable release objects/tags, aggregate receipt, and exact governed run evidence remain required.

## Remaining observer limitations

```text
full POST_RETURN portable governance proof: PENDING real canonical StegGate/consequence/return + Master Records preservation
canonical exact R3 governed evaluator run: PENDING verified aggregate release receipt
Python 3.13+ compatibility: NOT YET CLAIMED
local custody sharing: explicit export/share remains required; custody is not a global lookup service
unsupported evaluator capability: FAIL_CLOSED by design
external real-world consequence in canonical public governed TEST: intentionally disabled unless a separately authorized consequence lane exists
```

## Next executable work

1. Complete the canonical `POST_RETURN` portable governance bundle using real StegGate decision/consequence evidence and reciprocal interlock acknowledgement.
2. Retain Master Records custody plus replay/reconstruction evidence for that bundle and verify it with `stegverse-verify-governance`.
3. Add a portable evidence-export/import surface so an evaluator can share a bounded verification bundle without sharing an entire local custody database.
4. Add Python 3.13 validation only after the full package/runtime matrix passes; do not advertise it before evidence exists.
5. Continue TV/TVC R3 release execution independently of moving-main development.

## Authority boundary

```text
moving branch != release identity
source complete != activated
artifact validation != released
published package != runtime activation
verification != authority
receipt locator != authority
GitHub != runtime/release authority
credential/release authority = TV/TVC
```
