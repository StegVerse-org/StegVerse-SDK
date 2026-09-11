# Shared Docs Ephemeral Manifest WorkSpace Mirror Handoff

Updated: 2026-09-10
Organization: `StegVerse-org`
Repository: `StegVerse-SDK`
Goal Task ID: `SDK-GENERIC-MANIFEST-DOWNSTREAM-PROPAGATION-003`
Parent handoff: `SDK_GENERIC_MANIFEST_DOWNSTREAM_PROPAGATION_MIRROR_HANDOFF.md`
Status: `ACTIVE / TVC PROVIDER EVIDENCE BRIDGE MERGED / AUTHENTIC PROVIDER PROBE NEXT`

## Canonical architecture

```text
source-native external resource observation
  -> stegverse.ingress-manifest.v1
       -> stegverse.state-transition-evidence.v1
  -> external Interlock/InTr binding
  -> organization federation boundary
  -> registry-selected INTERNAL_ENDPOINT
  -> provider-neutral WorkSpace resource consumer
  -> runtime-supplied active probe executor when PROBE_REQUIRED
  -> secret-free TVC-owned provider evidence bridge
```

Provider observations and probe evidence remain non-authorizing. Provider credential/OAuth authority remains outside the SDK.

## Completed implementation chain

```text
SDK PR #174: state-transition evidence MERGED at ee8f7023d74d70fa762e3982776c27c1e372a1f7
SDK PR #176: canonical ingress -> external Interlock binding MERGED at 7047e67d21173e800f78d4468519dba87992b16d
StegVerse-org/.github PR #9: generic INTERNAL_ENDPOINT dispatch MERGED at d8baefb8674ebed00bbbf9784c54e092a5b1a04d
SDK PR #178: collision-prevention coordination MERGED at 8a2dfe07294daacaa5d44d4777e94def182d8d78
SDK PR #179: provider-neutral WorkSpace resource consumer MERGED at 07ceb1f131dd8fd27b3b8c89ab747e58aa55e55c
StegVerse-org/.github PR #10: WorkSpace endpoint binding MERGED at b851996afc5c5323d0d0db970dd46e511bd36338
SDK PR #181: provider-neutral active probe execution MERGED at 5c8a3c0246a0ae48e498c10f85d9eee0a2d1ba2c
SDK PR #182: TVC Google Drive result evidence bridge MERGED at 43519567d036d1d87d5866ae825ffee54acec08f
```

PR #182 exact head `960a272e205883b98e02b8c245ae8c092200d8da` passed:

```text
WorkSpace TVC Provider Probe Bridge Validation 34546368572: PASS
Manifest Builder Source Validation 34546368470: PASS
SDK Package Artifact Validation 34546368416: PASS
WorkSpace Active Probe Validation 34546368390: PASS
```

## Existing Google Drive authority — reuse, do not duplicate

The ecosystem already contains a TVC Google Drive owner-consent/credential path. `StegVerse-Labs/TVC:tvc_personal_kv_google_drive_runtime.py` performs bounded `personal_kv_materialize` through a TVC capability lease and non-exportable vault broker. Its current lease remains deliberately Personal-KV-specific (`kvpb_*`, consumer `StegVerse-Labs/.github`, approved scope including `_System/Workspace/**`). This WorkSpace lane does not broaden that lease.

The related Service Gateway query-secret-safe source hardening is owned by `StegVerse-org/LLM-adapter#271`; implementation PR #328 has merged. Authentic deployed-ingress evidence remains separate and must not be inferred from source merge.

## TVC provider evidence bridge

Merged SDK source:

```text
stegverse/tvc_provider_probe_bridge.py
tests/test_tvc_provider_probe_bridge.py
.github/workflows/workspace-tvc-provider-probe-bridge-validation.yml
```

The bridge accepts only an already-produced, secret-free TVC Google Drive materialization result and projects it into `stegverse.active-probe-result.v1`. It does not issue leases, perform OAuth, request credentials, call Google, or execute TVC provider operations.

Fail-closed rules include:

```text
exact TVC result schema required
provider == GOOGLE_DRIVE
credential_authority == TV/TVC
credential_material_exported == false
provider_operation_authority_transferred == false
runtime_activation_claimed == false
authority_effect == NONE_RESULT_EVIDENCE_ONLY
broker decision == ALLOW_OPERATION_RESULT
protected fields/values rejected
active-probe output authority_effect == NONE
```

The canonical active-probe engine still verifies the exact derived probe reason and re-derives readiness. A valid TVC result therefore cannot directly assign `READY`.

## Current proof boundary

```text
Generic ingress architecture: IMPLEMENTED / MERGED
State-transition evidence: IMPLEMENTED / VALIDATED / MERGED
Ingress -> external Interlock binding: IMPLEMENTED / VALIDATED / MERGED
Generic INTERNAL_ENDPOINT dispatch: IMPLEMENTED / VALIDATED / MERGED
WorkSpace resource consumer: IMPLEMENTED / VALIDATED / MERGED
Organization-local WorkSpace endpoint binding: IMPLEMENTED / VALIDATED / MERGED
Provider-neutral active probe execution: IMPLEMENTED / VALIDATED / MERGED
TVC secret-free provider evidence bridge: IMPLEMENTED / VALIDATED / MERGED
Authentic Google provider probe: NOT PROVEN
Shared Docs live synchronization: NOT PROVEN
MIR transition reporting: NOT PROVEN
Master Records authentic custody/reconstruction: NOT PROVEN
One-device authentic end-to-end execution: NOT PROVEN
```

## README maintenance

README was reviewed. This bridge is an internal evidence adapter and does not create a new public CLI, processing capability, universal manifest class, runtime route, or user-facing WorkSpace surface. No README source change is required for this bounded unit. A public provider/WorkSpace interface must update README when introduced.

## Next executable sequence

1. Reconcile root task/COSV evidence for PR #182.
2. Determine whether TVC can expose an admitted read/probe operation for the exact Shared Docs experiment without broadening the Personal-KV lease incorrectly.
3. Keep Service Gateway deployed-ingress evidence as a separate prerequisite for owner-present Google authorization.
4. Once authentic provider access exists, execute `OBSERVE -> MATERIALIZE -> live edit -> REFRESH -> authorization/probe change -> REVOKE/EXPIRE -> DESTROY`.
5. Retain MIR transition reporting and independent Master Records custody/reconstruction evidence.
6. Verify the complete path on one current mobile device.

## Human action

None for source and coordination work. Owner-present Google authorization becomes necessary only at the authentic provider-backed execution boundary.
