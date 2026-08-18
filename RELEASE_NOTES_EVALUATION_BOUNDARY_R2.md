# StegVerse SDK 1.0.13 — Evaluation Boundary R2

This release candidate preserves the generalized evaluator-neutral SDK testing surface and incorporates the manifest-declared route-resolution correction required before an exact governed evaluation-boundary run.

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

An exact governed evaluation run must use an immutable verified release set. Moving `main` is not a substitute for a tag-bound release candidate, and source validation is not runtime proof or activation.
