# Portable Governance Evidence Exchange Mirror Handoff

Updated: 2026-08-23
Repository: `StegVerse-org/StegVerse-SDK`

## Goal
Allow an evaluator or observer to share a bounded governed-evidence packet without sharing an entire local custody database and without converting copied evidence into custody or authority.

## Contract

```text
input: stegverse.portable-governance-verification-bundle.v1
transport: ZIP
members:
  EXCHANGE_MANIFEST.json
  governance_bundle.json
  verification_report.json
exchange authority: NONE
verification authority: NONE
execution authority: NONE
custody installation: FALSE
```

`create` first runs the existing independent portable governance verifier. An invalid governance bundle is not packageable.

`verify` checks the exact archive member set, rejects unsafe/duplicate paths, verifies file sizes and SHA-256 hashes, re-runs the portable governance verifier, requires exact equality with the retained verification report, verifies identity continuity in the exchange manifest, and verifies the non-transfer authority boundary.

`extract` runs full exchange verification before writing the bounded three-file packet. Extraction returns `EXTRACTED_VERIFIED_NOT_IMPORTED_AS_CUSTODY`. It never writes to Master Records and never treats copied evidence as canonical custody.

## CLI

```bash
stegverse-governance-exchange create governance_bundle.json evidence.zip
stegverse-governance-exchange verify evidence.zip
stegverse-governance-exchange extract evidence.zip ./shared-evidence
```

## Validation and merge evidence

```text
PR: #73
exact validated head: fabb2458cbe5f6fb25d4083ee384930337ed9a4c
merge: 9ef8ec991380b5fa7ae9f4af3d600ed4300422e6
SDK Package Artifact Validation: 32670023075 SUCCESS
Portable Package Source Validation: 32670023079 SUCCESS
SDK Output-Boundary Proof Validation: 32670023095 SUCCESS
Portable Release Index: 32670023103 SUCCESS
MCP Source Validation: 32670023074 SUCCESS
Evaluator Contract Console Validation: 32670023071 SUCCESS
Connect my LLM Source Validation: 32670023073 SUCCESS
Communication Edge SDK Demo Validation: 32670023086 SUCCESS
```

The package gate explicitly ran the portable verifier and exchange tests. Evidence includes:

```text
valid PRE_STEGGATE create -> verify -> extract round trip: PASS
retained verification report independently reproduced: PASS
tampered archive member detected before acceptance: PASS
authority-mutated governance bundle rejected before archive creation: PASS
wheel/sdist build and canonical metadata: PASS
isolated wheel install/import: PASS
installed stegverse-governance-exchange CLI smoke: PASS
credential/release authority introduced by validation: NONE
```

The validation run also exposed and repaired a pre-existing portability defect in `tests/test_portable_governance_verifier_cli.py`: the test had depended on a `capsys` fixture unsupported by this repository's bounded pytest shim. The verifier CLI fail-closed tests now use standard-library stream capture and are exercised by the package gate.

## State

```text
source implementation: COMPLETE_VALIDATED_MERGED
bounded evidence sharing without whole custody DB: IMPLEMENTED
copied evidence becomes Master Records custody: FALSE
PRE_STEGGATE exchange verification: PROVEN_IN_SOURCE_VALIDATION
POST_RETURN production exchange proof: PENDING_REAL_CANONICAL_EVIDENCE
```

## Non-claims

This exchange does not:
- create or reconstruct evidence that is absent;
- turn PRE_STEGGATE evidence into completed governance;
- establish participant truth;
- decide admissibility;
- execute a consequence;
- install or replace Master Records custody;
- make a copied receipt canonical merely because its hashes verify.

Full `POST_RETURN` production proof remains pending real canonical StegGate decision/consequence/return evidence, Master Records preservation, replay/reconstruction, and reciprocal participant acknowledgement.

## Next executable work

1. Produce a real canonical POST_RETURN bundle from the public reference interlock participant through StegGate/consequence/return and Master Records custody.
2. Package that exact bundle with `stegverse-governance-exchange create`.
3. Independently verify the archive and reproduce the POST_RETURN report.
4. Retain replay/reconstruction evidence while preserving the distinction between copied verification evidence and canonical custody.

## Authority boundary

```text
verified copy != canonical custody
verification != authority
receipt locator != authority
exchange archive != release artifact
GitHub != runtime/release authority
credential/release authority = TV/TVC
```
