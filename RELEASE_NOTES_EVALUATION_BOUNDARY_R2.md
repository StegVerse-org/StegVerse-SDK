# StegVerse SDK 1.1.0 — Evaluation Boundary R2

This release candidate preserves the generalized evaluator-neutral SDK testing surface and incorporates the manifest-declared route-resolution correction required before an exact governed evaluation-boundary run.

## Version identity correction

`stegverse-sdk` version `1.0.13` and Git tag `v1.0.13` are historical April 2026 identities and must not be replaced or retargeted. The modern SDK source had continued to declare the already-consumed package version while accumulating substantial new public functionality. The unpublished `v1.0.13-evaluation-r2` candidate is therefore superseded before publication.

The corrected public package identity is `1.1.0`, with target release tag `v1.1.0`. This minor-version increment reflects the large backward-oriented expansion of public SDK capabilities since the historical 1.0.13 package without asserting an intentional breaking API redesign. `pyproject.toml` is the sole canonical package metadata source; `setup.py` is metadata-free compatibility glue so legacy setuptools invocation cannot advertise a conflicting version or dependency surface.

## Included corrections

- Preformatted `stegverse.ingress-manifest.v1` submissions declare their intended route through `extensions.stegverse_route`.
- The SDK resolves that declaration against published installed routes and rejects missing, unsupported, unavailable, or conflicting route declarations.
- Accepted preformatted manifests are no longer silently mapped to a hard-coded route.
- Governance-relevant request state is hashed and bound to the resolved route.
- The sovereign runtime independently re-resolves the route and verifies the state binding before execution.
- Exact-run metadata retains the declared route identifier, route declaration hash, state-binding hash, and explicit no-substitution evidence.
- Existing raw public-inspection requests remain compatible only when their legacy route tuple identifies exactly one published installed route.

## Testing boundary

The manifest configures already-published capabilities and evidence requests. It does not install a new evaluator, alter StegGate semantics, create a new custody path, grant execution authority, or create a route dynamically.

## Authority boundary

Credential authority remains TV/TVC. GitHub Actions and generic GitHub tokens are not production, runtime, control-plane, signing, or release authority. No non-TV/TVC secret or token is required by the SDK source path.

## Aggregate-run requirement

An exact governed evaluation run must use an immutable verified release set. Moving `main` is not a substitute for a tag-bound release candidate, and source validation is not runtime proof or activation. The candidate must be frozen again after this version-identity repair; previously frozen 1.0.13-derived release coordinates are evidence of superseded pre-publication candidates, not valid 1.1.0 release identity.
