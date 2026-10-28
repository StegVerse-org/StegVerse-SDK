# Universal InTr route installer (Fix 4, SDK half)

Goal: StegVerse-org/.github#162 (Lane B), reclassification comment 6245620387 §3.
Owning goal: `INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001`; re-adoption: `STEGDB-ORGANIZATION-ROLE-VERSION-PROPAGATION-002`.
Evidence class: SOURCE_IMPLEMENTED. No installer was run, no listener started, no receipt is claimed and no credential exists here.

## What it replaces

StegVerse-Labs/.github main `bfcf0318` carries seven `scripts/install_*_universal_intr_route.py`
installers. Each splices its own route into `workers/universal_intr_profiled_ingress.py`
(blob `0fb63cec`) and refuses with a bare `SystemExit("FAIL_CLOSED: ...")`. That makes them
`ORGANIZATION_ROLE_CONFORMANCE_NOT_DECLARED` (ORRD L63), and they have to be updated (ORRD L53).
No exemption applies (ORRD L69), because a manifest-bound transition is possible through the SDK.

## The component: `stegverse/universal_intr_route_installer.py`

| Part | What it does | Decided by |
|---|---|---|
| `evaluate_installation` | Treats an installation as an attempted transition. It records the predecessor (router sha256), the proposed successor (sha256), the capability and route, the constraints, the evidence and a disposition. It never writes source. | ORRD L57; Labs `organization_role_conformance.py` L18-22 (a source change is a separate transition) |
| Route resolution | Only `stegverse.route_resolution.resolve_route_declaration` resolves a route, and it never substitutes one. An unpublished route, conflicting fields or an uninstalled runtime gives DENY. | `route_resolution.py` L3-5, L274-285, L295 |
| `EDGE_CONSUMERS` | Lists the seven consumers. Only StegBrowser has a published route on `EXISTING_UNIVERSAL_INTR`. The other six give `FAIL_CLOSED EDGE_CONSUMER_ROUTE_NOT_PUBLISHED`, with the repair that publishes their route. | `route_resolution.py` L46-230 (`PUBLISHED_ROUTES`) |
| `transform_router` | Splices one import and one wrapped branch per consumer. It is idempotent, and anchor drift gives a six-field FAIL_CLOSED. | the seven installers' own anchors; ORRD L61 |
| `admit_edge_submission` | Admits only a manifest-bearing payload on the consumer's published route. The ALLOW is a `SUBMIT_MANIFEST` submission to the organization's own `sdk-manifest-ingress`, which it reads from `org-runtime/interlock-intr.json` and never from the payload. It delivers nothing and waits on nothing. | Labs `capability_ingress.py` `declared_manifest` (`SUBMISSION_CARRIES_A_MANIFEST`); ORRD L58-60 |
| `supplied_epoch_failure` | Time comes only from the supplied `hb_epoch`. This is a byte copy of the shared rule (segment sha256 `7f36f0e6…`). | SEF, StegVerse-org/.github `organization_egress_boundary.py` |
| `role_version_file_entry`, `extend_role_version_files` | Compute a target-role-version file entry and its contract digest in the form Labs `check_target_version` recomputes. | Labs `organization_role_conformance.py` L91-101, L193-215 |
| `plan_readoption` | Plans what follows a conformance DENY or FAIL_CLOSED. A DENY is a request defect that adoption cannot repair. A parity FAIL_CLOSED re-adopts a file only when the file is absent or still equals the predecessor version. Any other difference gives `FAIL_CLOSED ORG_SPECIFIC_BEHAVIOUR_UNRECONCILED`. | Labs `organization_role_conformance.py` L24-32, L276-279 ("preserving this organization's own valid changes") |
| Reusable workflow `universal-intr-route-installation.yml` | Organizations reference the installer by parameters (`request_path`, `sdk_ref`). It runs evaluation only, with `permissions: {}` and anonymous archives. | `scripts/verify_github_fallback_boundary.py` |

## Open items (each non-ALLOW, six fields)

1. **Labs adoption.** The seven installers are not yet retired.
   - failure_code: `ORGANIZATION_ROLE_CONFORMANCE_NOT_DECLARED`
   - failed_predicate: `EDGE_CONSUMER_ENTERS_THROUGH_SDK_PUBLISHED_ROUTE_WITH_ORG_LEDGER_RECEIPT`
   - required_evidence_or_repair: a Labs draft that pins this SDK commit. It retires `install_stegbrowser_universal_intr_route.py` in favour of a committed installation request plus a caller of the reusable workflow. Each of the other six follows once its route is published.
   - retry_entrypoint: `stegverse/universal_intr_route_installer.py::evaluate_installation`
   - owning_existing_goal: `INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001`
   - next_attempt: after this SDK draft lands on SDK main
2. **Six consumers have no published route.** These are `EDGE_CONSUMER_ROUTE_NOT_PUBLISHED`. Route publication was checked against the invariants at SDK `c138cad4` and Labs main `978b8880`. A route is published only when existing manifests, registry rows and runtime declarations supply every field the StegBrowser entry carries (`route_resolution.py` L117-128): `route_id`, `processor_capability`, `lane_class`, `routing_surface`, `containment`, `sandbox_required`, `external_consequence_enabled`, `state_graph_adapter_binding`, `runtime_binding` and `runtime_installed`. None of the six meets that bar, so `PUBLISHED_ROUTES` is unchanged and no field is invented (`route_resolution.py` L3-5). See [Route publication evidence](#route-publication-evidence-six-consumers).

## Route publication evidence (six consumers)

The consumer list comes from `EDGE_CONSUMERS` (`universal_intr_route_installer.py` L86-107), not from a prose list. Each Labs profile is cited from the router `workers/universal_intr_profiled_ingress.py` and its installer, at Labs `978b8880`.

The missing evidence is the same for all six:
- **Processor:** no `stegverse/*_processor.py` defines `derive_state_graph` for the capability. That supplies `processor_capability` and `state_graph_adapter_binding`. The SDK has processors only for atomic_task_worker, collab_ingress, organization_role_conformance, purpose_bound_worker, remediation_fork, stegbrowser and svg_governance_cycle.
- **Route fields:** no Labs manifest, registry row or runtime declaration states `lane_class`, `containment`, `sandbox_required` or `external_consequence_enabled` for the profile. `git grep` finds the profile string only in the files listed below, and none of them carries a route field.
- **Registry row:** Labs `org-boundary/registry/services.json` (blob `00c6580e`) has no service row whose `admits_processing` names the capability.

| consumer_id | Labs profile | Labs evidence present (profile-bearing files) |
|---|---|---|
| `canonical_work` | `CanonicalWork:Coordination` | installer, `scripts/run_canonical_work_event_bootstrap.py`, `scripts/consume_stegbrowser_runtime_connection_ingress_request.py`; SDK `manifest_state_transition_adapters.py` L30-31 declares the bootstrap mode, not a processor |
| `erl_active_research` | `ERL:ActiveResearch` | installer, `workers/erl_active_research_intr_profile.py` |
| `kv_ai_memory` | `KV:AI-MemoryPacketAdmission` | installer only (plus tests) |
| `site_publication` | `StegOS:SitePublicationRuntime` | installer, `workers/site_publication_intr_ingress.py`, `scripts/consume_site_publication_intr_materialization_request.py`, `docs/SITE_PUBLICATION_INTR_CONSUMER_MIRROR_HANDOFF.md` |
| `stegsocials_bounded` | `StegSocials:BoundedSocialIngress` | installer, `workers/stegsocials_bounded_intr_ingress.py`, `scripts/build_stegsocials_bounded_intr_materialization.py` |
| `tvc_recipient_admission_sign` | `TVC:RecipientAdmissionAuthoritySign` | installer, `scripts/build_tvc_recipient_admission_sign_intr_request.py`, `docs/TVC_RECIPIENT_ADMISSION_SIGN_INTR_ROUTE_MIRROR_HANDOFF.md` |

Six fields, the same for each consumer except the named profile:
- disposition: `FAIL_CLOSED`
- failure_code: `EDGE_CONSUMER_ROUTE_NOT_PUBLISHED`
- failed_predicate: `EDGE_CONSUMER_ENTERS_THROUGH_SDK_PUBLISHED_ROUTE_WITH_ORG_LEDGER_RECEIPT`
- required_evidence_or_repair: needs all three of the following, then a `PUBLISHED_ROUTES` entry and an `EDGE_CONSUMERS` `route_id` in the same generation.
  - The consumer owner declares `lane_class`, `containment`, `sandbox_required` and `external_consequence_enabled` for the profile in an existing manifest or runtime declaration.
  - An SDK processor module provides `derive_state_graph` for the capability.
  - A Labs `org-boundary/registry/services.json` row has `admits_processing` `{capability, route_id}`.
- retry_entrypoint: `stegverse/universal_intr_route_installer.py::evaluate_installation`, with the consumer's committed request through the Labs caller `.github/workflows/universal-intr-route-installation.yml`
- owning_existing_goal: `INTERLOCK-INTR-RUNTIME-INDEPENDENT-PROTOCOL-001`
- next_attempt: once those declarations exist for the consumer. Nothing waits on a receiver (ORRD L59).

There is also a finding for StegBrowser. Its route is published, but Labs `services.json` has no `admits_processing` row for `stegbrowser` either. So the repair text's registry-row condition (`_route_not_published`) does not hold for the one published consumer. That question goes to the joint discovery queue, and this draft does not resolve it.
3. **The role-version record does not include the shared file.**
   - failure_code: `ROLE_VERSION_TARGET_FILES_EXCLUDE_SHARED_INSTALLER`
   - failed_predicate: `SHARED_EDGE_INSTALLER_IS_A_RECORDED_TARGET_VERSION_FILE`
   - required_evidence_or_repair: two records are needed, and the SDK writes neither.
     - A successor version in StegVerse-Labs/StegDB `registry/organization-role/versions.json`, whose files are produced by `extend_role_version_files`.
     - A bounded extension on the canonical task record, carried by the canonical-work ingress transition at generation >= 320.
   - retry_entrypoint: StegDB `tools/evaluate_organization_role_conformance.py`, then Labs `organization_manifest_ingress.py::receive`
   - owning_existing_goal: `STEGDB-ORGANIZATION-ROLE-VERSION-PROPAGATION-002`
   - next_attempt: once the file to record is decided (an open question; see the Lane B #162 checkpoint)
