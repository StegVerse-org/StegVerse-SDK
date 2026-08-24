# POST_RETURN Release Coherence Mirror Handoff

Updated: 2026-08-24
Repository: `StegVerse-org/StegVerse-SDK`

## Purpose

Prevent a historically valid release set from being used to certify a later proof implementation that is not contained in that release set.

The full POST_RETURN production proof now depends on source added after the frozen R3 coordinates:

```text
R3 SDK coordinate:
  StegVerse-org/StegVerse-SDK@922d6c5235229e854c36e1a194dc99ed15a31b51

post-R3 SDK POST_RETURN implementation:
  merge 0a3690c4624f53f268980fd582d4a3baf492b8fc

R3 StegCore coordinate:
  StegVerse-Labs/StegCore@23b388ce23b08097593b5b5593eb4061e0ff5242

required canonical standing implementation:
  StegVerse-Labs/StegCore#146
  current exact head 9e30638048b7ce117d9081ec9f8bfd7be2352710
```

Therefore a verified R3 aggregate receipt remains valid evidence for the frozen R3 release set, but it is **not sufficient release evidence for the later full POST_RETURN proof path**.

## Fail-closed contract

`stegverse.proof_release_gate.verify_release_proof_capabilities()` requires the release receipt used by the full proof to carry explicit `stegverse.release-proof-capability.v1` entries for:

```text
SDK_POST_RETURN_EVIDENCE_V1
STEGCORE_SPE_STANDING_BINDING_V1
MASTER_RECORDS_OPERATION_CUSTODY_V1
```

Each entry must bind:

```text
capability_id
repository
exact release_commit_sha
feature_commit_sha
feature_in_release_commit = true
containment_verification = ANCESTOR_OR_EQUAL | TREE_EQUIVALENT
authority_effect = NONE
```

The capability's `release_commit_sha` must equal the exact component coordinate in the release receipt. Missing capability evidence, a mismatched release commit, a feature not proven contained, or any authority escalation fails closed.

## Consequence for R3

```text
R3 release execution: still independently useful and should complete under TV/TVC authority
R3 proves the newer POST_RETURN implementation: FALSE
R3 may be relabeled to imply newer source is released: FALSE
```

A successor release set is required after the exact StegCore standing implementation is validated/merged and the SDK development line carrying POST_RETURN is frozen through its own release process. The successor release authority must verify feature-commit containment before emitting the capability entries.

## Authority boundary

```text
release verification != runtime authority
capability containment evidence != execution authority
GitHub != TV/TVC release authority
moving main != released source
historical release receipt != proof of later source
```

## Completion

This lane is complete only when:

1. the release-coherence gate is source validated and merged;
2. a successor immutable release receipt contains and verifies all required proof capabilities;
3. the exact sovereign POST_RETURN runner consumes that receipt and refuses historical/incoherent receipts;
4. the resulting governed run, custody, reciprocal ACK, exchange, replay and reconstruction evidence is retained.
