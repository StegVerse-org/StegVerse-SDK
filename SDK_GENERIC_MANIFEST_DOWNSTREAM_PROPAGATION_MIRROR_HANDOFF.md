# SDK Generic Manifest Downstream Propagation Mirror Handoff

## Source of truth

```text
organization: StegVerse-org
repository: StegVerse-SDK
canonical_branch: main
parent_handoff: GENERIC_MANIFEST_PROCESSING_MIRROR_HANDOFF.md
source_goal: SDK-PROCESSOR-GENERIC-MANIFEST-002
source_cosv: 71000000100110
continuation_goal: SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003
credential_authority: TV/TVC
GitHub runtime authority: NONE
```

This handoff records the downstream propagation assessment required after the processor-generic manifest correction merged in PR #126. It does not duplicate the SDK processor, evaluator, route resolver, runtime, credential authority, or Master Records custody path in downstream repositories.

## Canonical propagated semantics

Downstream surfaces that document or consume SDK interoperability must preserve these public invariants:

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
```

Current executable processor:

```text
processing.capability: governance
processing.route_id: stegverse.route.canonical-governed.v1
processor-specific request: extensions.stegverse_governance_request
```

Future processors must not inherit governance-only input requirements merely because governance is the currently installed processor.

## Downstream assessment

### StegVerse-Labs/Site

```text
pertinent: YES
reason: Site exposes an explicit Ecosystem Chat SDK browser/backend contract and SDK payload/response fixtures.
current source: docs/ECOSYSTEM_CHAT_SDK_BACKEND_HANDOFF.md
required propagation: align the Site SDK preview/backend-facing manifest description with stegverse.ingress-manifest.v1 processing.capability, processing.route_id, processor-specific extensions, return_projection, and manifest_receipt_id semantics.
implementation boundary: Site browser remains preview/submission UI; it must not become processor, evaluator, receipt authority, custody authority, or route authority.
current admission: DEFERRED_TO_SITE_MACHINE_ORCHESTRATION
```

Site repository orchestration currently declares `external_tasks_allowed=false` and `external_session_ownership_allowed=false`. Therefore this continuation must not mutate Site from the SDK session. The required change is recorded for Site-owned machine admission rather than forced cross-repository mutation.

### GCAT-BCAT-Engine/Publisher

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
reason: Publisher consumes bounded Site activation/publication projections; it does not consume or implement stegverse.ingress-manifest.v1 processor selection.
action: preserve existing projection-only boundaries; do not duplicate SDK manifest processor logic.
```

If Publisher later exposes an SDK interoperability publication page, only public contract semantics may be projected there; no processor, evaluator, route authority, custody, execution, or release authority is inherited.

### StegVerse-Labs/admissibility-wiki

```text
pertinent: YES
reason: the Wiki documents StegVerse-SDK interoperability and maintains first-class external-framework doctrine/evaluation surfaces.
current owner: docs/external-frameworks/EXTERNAL_FRAMEWORKS_MIRROR_HANDOFF.md + coordinator issue #66 + worker collision registry
required propagation: add bounded doctrine clarifying source-native payload class, independent processing capability, installed route binding, processor-specific conditional evidence, artifact-depth projection, and non-authority semantics.
implementation boundary: documentation/evaluation only; no SDK processor duplication and no promotion of framework evaluation state solely from SDK contract publication.
current admission: COLLISION_CONTROL_REQUIRED
```

The external-framework lane is active and worker-partitioned. The propagation is semantically required but must enter through that lane's collision controls instead of overwriting worker-owned framework analysis.

### StegVerse-002/stegguardian-wiki

```text
pertinent: NO_DIRECT_CONTRACT_CHANGE
reason: Guardian consumes bounded downstream interpretation/awareness after upstream evidence chains; it does not consume SDK ingress manifests directly.
action: preserve existing visibility/authority and non-enforcement boundaries; do not duplicate SDK processor semantics unless a future Guardian page explicitly documents SDK interoperability.
```

A generic manifest, route selection, processor selection, receipt, projection, publication, or reconstruction result cannot independently create Guardian enforcement or execution authority.

## Propagation disposition

```text
StegVerse-Labs/Site: REQUIRED_BUT_SITE_MACHINE_OWNED
GCAT-BCAT-Engine/Publisher: NO_DIRECT_CHANGE_REQUIRED
StegVerse-Labs/admissibility-wiki: REQUIRED_WITH_EXISTING_COLLISION_CONTROL
StegVerse-002/stegguardian-wiki: NO_DIRECT_CHANGE_REQUIRED
```

This assessment intentionally narrows propagation to the two repositories where the corrected SDK semantics are actually consumed or documented. It avoids copy-pasting processor logic into projection-only repositories.

## Remaining files/modules by destination

### StegVerse-Labs/Site

```text
docs/ECOSYSTEM_CHAT_SDK_BACKEND_HANDOFF.md
fixtures/ecosystem-chat/sdk-form-payload.example.json (only if manifest preview shape is stale)
fixtures/ecosystem-chat/sdk-backend-response.example.json (only if manifest_receipt_id/return projection response semantics are represented there)
associated Site SDK checker/schema only when required by the admitted Site-owned change
```

### StegVerse-Labs/admissibility-wiki

```text
docs/external-frameworks/EXTERNAL_FRAMEWORKS_MIRROR_HANDOFF.md or a subordinate SDK interoperability handoff
one bounded public doctrine/evaluation surface for the processor-generic SDK manifest contract
existing Goal-5/external-framework validation integration only if the new doctrine becomes a required public surface
worker-task registry/coordinator state only through existing collision-control rules
```

### GCAT-BCAT-Engine/Publisher

```text
none required for the current processor-generic correction
```

### StegVerse-002/stegguardian-wiki

```text
none required for the current processor-generic correction
```

## Validation requirements for downstream changes

Any admitted downstream change must demonstrate:

```text
no governance-specific universal ingress requirement reintroduced
no route-selection authority claim
no processing-selection authority claim
no caller-projection suppression of canonical custody
no downstream processor/evaluator duplication
no framework evaluation promotion from documentation alone
no Guardian enforcement promotion from SDK semantics alone
existing repository-native validators remain passing at exact changed head
```

## Release/tag determination

```text
SDK source correction: already COMPLETE_VALIDATED_MERGED via PR #126
new SDK tag solely for propagation assessment: NOT REQUIRED
Publisher tag/release: NOT TRIGGERED
admissibility-wiki tag/release: NOT TRIGGERED
StegGuardian tag/release: NOT TRIGGERED
Site tag/release: NOT TRIGGERED
```

If a downstream repository later reaches its own release/tag condition, that repository must independently verify whether pertinent state also needs projection into Site, Publisher, admissibility-wiki, and StegGuardian under its own handoff and authority boundaries.

## Next machine continuation

```text
1. Preserve this assessment as the SDK-side durable continuation record.
2. Site: wait for Site machine-owned admission, then update only the SDK preview/backend contract surfaces that are stale.
3. admissibility-wiki: enter through issue #66 / worker collision control and add bounded processor-generic SDK interoperability doctrine without altering worker-owned framework evaluations.
4. Publisher: no mutation unless a direct SDK-manifest consumer/publication surface is introduced.
5. StegGuardian: no mutation unless a direct SDK-interoperability awareness surface is introduced.
6. After each admitted downstream change, run that repository's exact-head native validation and update its handoff before closure.
```

## Status

```text
SDK-PROCESSOR-GENERIC-MANIFEST-002: COMPLETE_VALIDATED_MERGED
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ASSESSMENT_COMPLETE_IMPLEMENTATION_PARTIALLY_ADMITTED
manual user work: NONE
```
