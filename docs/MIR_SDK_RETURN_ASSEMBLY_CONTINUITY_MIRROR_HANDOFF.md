# MIR SDK return assembly continuity mirror handoff

Updated: 2026-09-14
Goal Task ID: `MIR-SDK-RETURN-ASSEMBLY-CONTINUITY-001`
Parent Goal Task ID: `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`
COSV ID: `50000000100000`
Canonical registry issue: `StegVerse-Labs/.github#1888`
Canonical registry PR: `StegVerse-Labs/.github#1889`
Canonical registry merge: `StegVerse-Labs/.github@e4ef0adf25c30f1da42bdc9c3df8d6d1f08ffd32`
Parent canonical issue: `StegVerse-Labs/Site#1277`
Parent canonical handoff: `StegVerse-Labs/Site/docs/MIR_CONNECTION_ROUNDTRIP_TECHNICAL_GUIDE_MIRROR_HANDOFF.md`
Publisher source binding: `GCAT-BCAT-Engine/Publisher#71`, merge `40018e94a04e794e35dd499b4adc4296edb4b34c`
SDK completion capsule source: `StegVerse-org/StegVerse-SDK#240`, merge `233632c35b0093166c16bdc660aa08e4ee1fe95a`
SDK return assembly PR: `StegVerse-org/StegVerse-SDK#242`
SDK return assembly exact validated head: `fe8b01cd3ad9f6b54f124883e3e2c2d869302e6f`
SDK return assembly merge: `StegVerse-org/StegVerse-SDK@b4927ed277c4993662f9e7e4ffd717f677ad5459`
Status: `SOURCE_BUILD_TEST_COMPLETE / READY_TO_RETIRE_AFTER_REGISTRY_RECONCILIATION / DOWNSTREAM RUNTIME NOT CLAIMED`

## Goal and decomposition truth

This successor was created because parent `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001` reached Goal Prompt Count 20/20 while reusable `RTC-SDK-RETURN-006` remained independently incomplete. The split is genuine rather than counter-only: SDK return assembly has its own stable input/output contract, SDK-owned implementation surface, fail-closed evidence predicate, and reusable component identity.

The source/build-test goal is now satisfied. PR `#242` binds Publisher's exact canonical `stegverse.publisher.artifact-return/v1` bytes back to the original admitted manifest and independently retained SDK downstream completion capsule when Publisher carries `stegverse.publisher.mir-roundtrip-binding/v1`.

## Implemented continuity

For MIR Publisher returns, `assemble_publisher_return()` now requires the original `stegverse.sdk.downstream-completion-capsule/v1` independently of the Publisher-carried copy and fails closed unless:

- Goal Task ID is `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`;
- COSV ID is `50000000100000`;
- Publisher transition is `PUBLISHER_ARTIFACT_RETURN_PRODUCED` and observed true;
- the original manifest SHA-256 equals capsule `manifest_hash`;
- the original manifest completion block and its recomputed SHA-256 equal capsule `completion` / `completion_hash`;
- the Publisher-carried downstream completion capsule exactly equals the original SDK capsule;
- `response_to` and `retained_packet_sha256` remain continuous;
- SDK processor state is `SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED` with `processor_result_observed = true`;
- Publisher return schema, source-export ID/hash, generation ID, and artifact-manifest SHA-256 bind to the exact returned envelope;
- all post-Publisher downstream predicates in the carried binding remain false;
- `authority_effect = NONE` throughout.

The emitted `stegverse.sdk.publisher-return-binding/v1` records `sdk_return_binding_observed = true` for the SDK source-level assembly transition it represents and remains `READY_FOR_FINAL_STEGVERSE_EGRESS_TRANSITION`. It does not promote later transitions.

Legacy/non-MIR Publisher returns remain supported without a completion-capsule argument. One-sided MIR state fails closed.

## Validation evidence

Exact PR head `fe8b01cd3ad9f6b54f124883e3e2c2d869302e6f` completed:

```text
Publisher SDK Return Binding Validation (Non-Authorizing) #2: SUCCESS
SDK Package Artifact Validation (Non-Authorizing) #193: SUCCESS
```

PR `#242` was squash-merged as `b4927ed277c4993662f9e7e4ffd717f677ad5459`.

Tests cover successful exact capsule continuity and fail-closed rejection for missing original capsule, carried capsule mutation, original-manifest mutation, Publisher identity mutation, downstream-state promotion, noncanonical return bytes, artifact mutation, incomplete Publisher declaration, and attempted terminal completion mutation.

## README and contract maintenance

`docs/PUBLISHER_SDK_RETURN_BINDING.md` was updated in PR `#242`. The repository `README.md` was reviewed against this transition. Its canonical SOUTH lifecycle already states that SDK binds Publisher/result output to the original initiating request/entity before final StegVerse-side egress, Interlock/InTr, and the far-side transition; no contradictory or stale README claim was found, so no README byte change was required for this bounded successor.

## Scope boundary after merge

The following remain **not claimed** by this successor:

- live SDK runtime assembly against an authentic external MIR packet;
- final governed StegVerse-side egress execution;
- Interlock/InTr egress execution;
- far-side transition or caller receipt;
- authentic external MIR endpoint substitution;
- release or deployment;
- communication completion;
- any new credential, transition, governance, or runtime authority.

## Handoff

The successor can retire after its canonical task record is reconciled with PR `#242` validation/merge evidence. Control then returns to the parent choreography at the genuinely separable next reusable component:

```text
RTC-STEGVERSE-EGRESS-007
-> EXECUTE_REUSED_RTC_STEGVERSE_FINAL_EGRESS_TRANSITION
```

Because the parent Goal Task is exhausted at 20/20, further egress/authentic-MIR work must use a new canonical successor Goal Task ID rather than adding prompts to the parent.
