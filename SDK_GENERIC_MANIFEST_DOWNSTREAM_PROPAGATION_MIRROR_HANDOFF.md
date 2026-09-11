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
coordination_state: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
```

This handoff is the current root source of truth for processor-generic downstream propagation, public governed-runtime distribution remediation, and the WorkSpace continuation at `docs/SHARED_DOCS_EPHEMERAL_MANIFEST_WORKSPACE_MIRROR_HANDOFF.md`.

## Canonical processor-generic semantics

```text
payload class != processing capability
processing capability != runtime route
processing selection != authority
route selection != authority
caller projection != canonical custody
governance-specific fields are not universal manifest requirements
unsupported or uninstalled processor/route execution fails closed
```

Current executable processor remains governance on `stegverse.route.canonical-governed.v1`; processor-specific governance request state remains under `extensions.stegverse_governance_request`.

## Completed package and WorkSpace source work

```text
Generic manifest package PR #138: MERGED
State-transition evidence PR #174: MERGED at ee8f7023d74d70fa762e3982776c27c1e372a1f7
Canonical ingress -> external Interlock binding PR #176: MERGED at 7047e67d21173e800f78d4468519dba87992b16d
Collision-prevention coordination PR #178: MERGED at 8a2dfe07294daacaa5d44d4777e94def182d8d78
Provider-neutral WorkSpace resource consumer PR #179: MERGED at 07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c
Organization generic endpoint dispatch PR StegVerse-org/.github#9: MERGED at d8baefb8674ebed00bbbf9784c54e092a5b1a04d
Organization-local WorkSpace endpoint binding PR StegVerse-org/.github#10: MERGED at b851996afc5c5323d0d0db970dd46e511bd36338
Provider-neutral active probe execution PR #181: MERGED at 5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c
```

Validation evidence for the two newest units:

```text
StegVerse-org/.github#10 exact head 7fb6783ec7bbfbdc249dfdba45b7c454ae0beed4
WorkSpace Internal Endpoint Binding Validation 34545811959: PASS
Internal Endpoint Dispatch Validation 34545811830: PASS

SDK #181 code head 9c2153ef9ecd14d4985ea697bcc2e326b58faa31
WorkSpace Active Probe Validation 34545991378: PASS
Manifest Builder Source Validation 34545991321: PASS
SDK Package Artifact Validation 34545991339: PASS
```

The organization registry now exposes `stegverse-org.workspace-resource-consumer` as a generic `INTERNAL_ENDPOINT`. Its local adapter delegates to the installed canonical SDK WorkSpace consumer instead of duplicating projection semantics. `MATERIALIZE`/`REFRESH` may now use a runtime-supplied active probe executor when represented state is `PROBE_REQUIRED`; probe results must bind the exact derived reason, carry current evidence metadata, remain `authority_effect: NONE`, and readiness is re-derived by the canonical state-transition normalizer. Caller assertions cannot directly turn `PROBE_REQUIRED` into `READY`.

This remains source/CI evidence only. Authentic provider access, live synchronization, StegOS/StegNode projection runtime, MIR reporting, Master Records custody/reconstruction, expiry/revocation runtime enforcement, and one-device end-to-end execution remain unproven.

## Public runtime distribution boundary

```text
StegCore public distribution: stegverse-stegcore
StegCore target version: 0.3.0
StegCore rename PR #197: MERGED
Master Records public distribution: stegverse-master-records
Master Records target version: 0.2.0
Master Records Trusted Publishing PR #85: MERGED
SDK successor PR #165: SOURCE_CANDIDATE / DRAFT
SDK successor version: 1.3.0
first proven anonymous-install blocker: stegverse-stegcore==0.3.0 NOT PUBLISHED
release/tag/publication claim: NONE
```

Actual SDK 1.3.0 release still requires TV/TVC release authorization, required SKAP resident evidence, immutable tag/release, public Trusted Publisher provenance, anonymous governed-runtime install PASS, and ELAN custody/replay/reconstruction PASS. Do not weaken the anonymous installation gate.

## Downstream ownership and collision prevention

```text
StegVerse-Labs/Site: REQUIRED / MACHINE_OWNED / completion FALSE
StegVerse-Labs/admissibility-wiki: REQUIRED / Worker D OWNED / completion FALSE
GCAT-BCAT-Engine/Publisher: NO_DIRECT_CONTRACT_CHANGE
StegVerse-002/stegguardian-wiki: NO_DIRECT_CONTRACT_CHANGE
```

Site Conectrr contamination remains resolved. External sessions must not duplicate Site or Worker D-owned implementation. Canonical collision rule: a narrower/coincident session whose remaining scope is owned by a broader/global task must transfer unique evidence, transition to `INACTIVE`, identify the controlling Global Task ID and Handoff Task ID, and stop progressing overlap unless ownership is explicitly transferred back.

## Public surfaces

```text
canonical public domain: https://stegverse.org/
current Ecosystem Chat route: https://stegverse.org/ecosystem-chat.html
dedicated processor-generic route: NOT YET OBSERVED
```

## Next executable sequence

1. Reconcile canonical COSV/task evidence for the merged organization-local WorkSpace binding and active-probe unit.
2. Search the ecosystem for an existing provider-specific Shared Docs/Drive adapter before creating another provider authority path.
3. If no suitable provider adapter exists, create the narrow provider binding without adding a provider-specific universal manifest class or weakening active-probe evidence rules.
4. Execute authentic provider-backed `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY` transitions once provider access is explicitly available.
5. Retain MIR transition reporting and independent Master Records custody/reconstruction evidence.
6. Verify the complete path on one current mobile device.
7. Continue observing Site/Worker D and public-runtime publication dependencies without colliding with their owners.

## Current status

```text
SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003: ACTIVE
coordination state: DOWNSTREAM_WORK_DURABLY_TRANSFERRED_DEPENDENCY_EXECUTION_PENDING
provider-neutral WorkSpace consumer: IMPLEMENTED / VALIDATED / MERGED
organization-local WorkSpace consumer binding: IMPLEMENTED / VALIDATED / MERGED
active probe execution: IMPLEMENTED / VALIDATED / MERGED
authentic provider probe: NOT PROVEN
Site completion predicate: FALSE / MACHINE_OWNED
admissibility completion predicate: FALSE / WORKER_OWNED
propagation complete: FALSE
manual user work: NONE
```

README review remains current. These source units do not introduce a new public processing capability identifier, universal ingress class, CLI/runtime route, or user-facing WorkSpace product surface. README must be changed when an externally observable WorkSpace/provider surface is introduced.
