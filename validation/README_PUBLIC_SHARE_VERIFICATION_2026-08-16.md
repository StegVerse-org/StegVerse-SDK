# SDK README Public-Share Verification — 2026-08-16

## Scope

Verify `README.md` on `StegVerse-org/StegVerse-SDK` against the live public SDK implementation before external sharing with an ecosystem builder.

## Result

```text
status: PASS_AFTER_CORRECTION
share_readiness: READY
verified_branch: main
README correction commit: bff85fe5323fc6c5ab772f0f1456e8a449d8c701
credential authority: TV/TVC
GitHub runtime authority: NONE
```

## Material correction made

The prior README stated that a machine understanding `stegverse.ingress-manifest.v1` could directly construct an ordinary governed submission. The live CLI currently keeps the separate `0B` preformatted machine-manifest path fail-closed until the canonical ingress binding is installed.

The README now accurately distinguishes:

```text
0A / public-inspection request contract: available
stegverse.public_inspection_runtime: available
0B preformatted stegverse.ingress-manifest.v1 binding: fail-closed / not installed
```

No conversion or route is claimed where the implementation does not provide one.

## Claims cross-checked

The public README was checked against the following live implementation surfaces:

```text
pyproject.toml
stegverse/cli.py
stegverse/governance_navigation.py
stegverse/public_inspection.py
stegverse/public_inspection_runtime.py
stegverse/sovereign_validation_runtime.py
inspection/request.schema.json
validation/SOVEREIGN_FROZEN_EVALUATOR_VALIDATION_2026-08-13.md
SDK_MIRROR_HANDOFF.md
```

Verified public claims include:

- governed-test dependencies are pinned to public repository commits;
- the public inspection runtime defaults to the sovereign/local runtime;
- canonical Core-Lite, StegCore/StegGate, and Master Records packages are loaded rather than a parallel evaluator;
- evaluator WHAT/HOW/WHY is retained as evidence metadata and is not a StegGate decision input;
- evaluator identity and expected observation are not decision inputs;
- unsupported requested capability identifiers reject before execution;
- the five published evaluator-facing capability identifiers match schema/runtime validation;
- successful run output includes governance state, transaction/route identity, route receipts, manifest receipt locator, chain verification, custody status, and binding hashes;
- replay and reconstruction record new operation history and do not re-execute the original consequence;
- public caller runtime credential authority is none and GitHub grants no runtime authority;
- frozen T0/T1-A/T1-B validation claims and receipt identifiers match retained validation documentation.

## Public-share boundary

This verification establishes that the README accurately describes the currently published SDK behavior. It does not claim that every future/adjacent SDK feature is complete. In particular, `0B` remains intentionally unavailable until its canonical binding is installed, and the README now says so explicitly.

## Remaining installation relevant to this README

```text
StegVerse-org/StegVerse-SDK
  0B canonical stegverse.ingress-manifest.v1 execution binding: NOT INSTALLED
  public README disclosure of that state: COMPLETE
```

The missing 0B binding does not block sharing the SDK README because the currently usable external machine path is explicitly documented as the public-inspection/0A contract.
