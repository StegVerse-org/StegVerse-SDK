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

## Completion boundary

Source completion requires focused tests, exact-head package validation including installed CLI discovery, merge, and retained validation evidence. Runtime/end-to-end production completion remains separate and requires a real POST_RETURN packet.
