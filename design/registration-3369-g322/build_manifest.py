#!/usr/bin/env python3
"""Build the DRAFT NEW_IDENTITY request manifest for the #3369 candidate.

Scope digest is computed by the repo's own scripts/goal_scope_seal.py canon/digest.
Nothing here is an approval, COSV, claim, fence or receipt.
"""
import hashlib, json, sys
from pathlib import Path

REPO = Path(sys.argv[1])
OUT = Path(sys.argv[2])
GEN = int(sys.argv[3])
VARIANT = sys.argv[4] if len(sys.argv) > 4 else "primary"

TASK = "PROTOCOL-V1-MINIMUM-PACKET-CONFORMANCE-001"
DRAFT = "DRAFT_PENDING_OWNER_APPROVAL"


def canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


GOAL = (
    "Protocol v1.0 minimum packet conformance (StegVerse-Labs/.github#3369, parent #3368): "
    "hold one intra-organization packet on the existing SDK:ManifestIngress binding to a "
    "deterministic, exact-head conformance profile across the existing ingress path "
    "(resident-runtime/sdk_manifest_crossing.py, org-boundary/runtime/process_boundary.py, "
    "resident-runtime/organization_manifest_ingress.py) and the Organization Ledger readback "
    "(org-kernel/organization-ledger), where every non-ALLOW outcome returns the six-field "
    "fail-closed shape (failure_code, failed_predicate, required_evidence_or_repair, "
    "retry_entrypoint, owning_existing_goal, next_attempt) and no effect is committed. "
    "Positive ALLOW is fixture evidence only; no runtime ALLOW, ledger append, claim, fence or "
    "admission is asserted. " + DRAFT + "."
)

if VARIANT == "primary":
    # Honest vocabulary: reuses the component names existing owners already use for the
    # same surfaces, so the evaluator sees the real overlap instead of a renamed one.
    COMPONENTS = [
        "sdk-manifest-ingress",            # CANONICAL-WORK-END-TO-END-CYCLE-CLOSURE-001 (omitted CHECKED_OUT shard)
        "sdk-manifest-crossing",
        "process-boundary",
        "allow-deny-fail-closed",          # SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 (CHECKED_OUT)
        "organization-ledger-readback",    # CANONICAL-WORK-EXACT-INVOCATION-EVIDENCE-RECONCILIATION-001 (omitted CHECKED_OUT shard)
        "protocol-v1-conformance-fixtures",
    ]
    ADJACENT = [
        "SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001",
        "ORGANIZATION-BATCH-CUSTODY-REPLAY-001",
        "STEGVERSE-CANONICAL-WORK-COORDINATION-001",
    ]
else:
    # Name-distinct variant: identical scope, components named so no existing string matches,
    # and no declared adjacency. Exists only to show what the evaluator does with naming.
    COMPONENTS = [
        "protocol-v1-packet-ingress-conformance",
        "protocol-v1-packet-crossing-conformance",
        "protocol-v1-packet-boundary-conformance",
        "protocol-v1-six-field-refusal-shape",
        "protocol-v1-ledger-readback-conformance",
        "protocol-v1-conformance-fixtures",
    ]
    ADJACENT = []

TARGETS = {
    "organizations": ["StegVerse-Labs", "StegVerse-org"],
    "repositories": ["StegVerse-Labs/.github", "StegVerse-org/StegVerse-SDK"],
    "components": COMPONENTS,
}

PREDICATES = [
    "PROTOCOL_V1_POSITIVE_PACKET_FIXTURE_ALLOW_WITH_NO_LEDGER_APPEND",
    "PROTOCOL_V1_SEVEN_REFUSALS_OBSERVED_CODE_EQUALS_DECLARED_FAILURE_CODE",
    "PROTOCOL_V1_REPLAY_REDELIVERY_IS_ONE_TRANSITION_ONE_RECEIPT_PER_LEVEL",
    "PROTOCOL_V1_EVERY_NON_ALLOW_CARRIES_SIX_FIELDS",
    "PROTOCOL_V1_EXACT_HEAD_CI_RUN_RETAINED",
    "PROTOCOL_V1_ORGANIZATION_LEDGER_READBACK_INDEPENDENTLY_OBSERVED_OR_SIX_FIELD_NOT_ATTEMPTED",
]

RECORD = {
    "schema": "stegverse.canonical-task-record/v1",
    "task_id": TASK,
    "correlation_id": TASK,
    "root_correlation_id": TASK,
    "parent_task_id": None,
    "goal": GOAL,
    "coordination_state": "PROPOSED",
    "source_refs": [
        "StegVerse-Labs/.github#3369",
        "StegVerse-Labs/.github#3368",
        "docs/PROTOCOL_V1_CONFORMANCE_SHARE_PACKET.md",
        "docs/PROTOCOL_V1_MINIMUM_PACKET_MIRROR_HANDOFF.md",
        "docs/TASK_REGISTRATION_GUIDE.md",
        "resident-runtime/sdk_manifest_crossing.py",
        "org-boundary/runtime/process_boundary.py",
        "resident-runtime/organization_manifest_ingress.py",
        "org-kernel/organization-ledger/fixtures/protocol-v1-conformance/README.md",
        "org-kernel/organization-ledger/fixtures/protocol-v1-conformance/packet.json",
        "org-kernel/organization-ledger/fixtures/protocol-v1-conformance/cases/",
        "tests/test_protocol_v1_conformance_fixtures.py",
        "org-runtime/interlock-intr.json",
        "StegVerse-org/StegVerse-SDK#566",
    ],
    "targets": TARGETS,
    "dependencies": [
        {
            "dependency_id": "DEP-P1-OWNER-COLLISION-RULING",
            "kind": "HUMAN_ACTION",
            "state": "UNRESOLVED",
            "ref": "Registry owner scoped collision ruling over SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001, ORGANIZATION-BATCH-CUSTODY-REPLAY-001 and the omitted CHECKED_OUT shards CANONICAL-WORK-END-TO-END-CYCLE-CLOSURE-001 / CANONICAL-WORK-EXACT-INVOCATION-EVIDENCE-RECONCILIATION-001 (" + DRAFT + ")",
        },
        {
            "dependency_id": "DEP-P1-SDK-INGRESS-BINDING",
            "kind": "TASK",
            "state": "UNRESOLVED",
            "ref": "SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 (SDK:ManifestIngress binding, org-runtime/interlock-intr.json; SDK#566)",
        },
        {
            "dependency_id": "DEP-P1-LEDGER-REPLAY-REFUSAL",
            "kind": "TASK",
            "state": "UNRESOLVED",
            "ref": "ORGANIZATION-BATCH-CUSTODY-REPLAY-001 (replay refusal spec_gap recorded by cases/n2-replay.json)",
        },
    ],
    "blockers": [],
    "systemic_incident_ref": None,
    "adjacent_task_refs": ADJACENT,
    "existing_evidence_refs": [
        "org-kernel/organization-ledger/fixtures/protocol-v1-conformance/ (FIXTURE_ONLY_NOT_RUNTIME_RECEIPT)",
        "tests/test_protocol_v1_conformance_fixtures.py",
        "tests/test_registry_collision_claimed_integration_guard.py::Issue3369RealRegistrationTests",
    ],
    "expected_evidence_predicates": PREDICATES,
    "worker_claim": {"authority": "WORKERCOORDINATOR", "claim_ref": None, "fence_ref": None, "projection_only": True},
    "completion": {"claimed": False, "validated": False, "reconciliation_ref": None},
    "allowed_next_transitions": ["INGRESS_ADMITTED", "DEFERRED", "SUPERSEDED"],
    "handoff_projection_refs": ["docs/PROTOCOL_V1_MINIMUM_PACKET_MIRROR_HANDOFF.md"],
    "authority_model": {
        "task_registry_mints_execution_authority": False,
        "source_state_proves_execution": False,
        "worker_claim_authority": "WORKERCOORDINATOR",
        "master_records_reality_authority": False,
        "interlock_intr_required_for_governed_ingress_egress": True,
    },
}

FINISH = {
    # One addressable test file (scripts/adjacency_ruling.py ADDRESSABLE:
    # '<org>/<repo>:<path/to/test.py>[::<Class>::<test>]'); the whole module is the finish test.
    "acceptance_test": "StegVerse-Labs/.github:tests/test_protocol_v1_conformance_fixtures.py",
    # The conjunction the test decides; each expected_evidence_predicates entry maps to a node id below.
    "predicate": "PROTOCOL_V1_MINIMUM_PACKET_CONFORMANCE_PROFILE_HELD_AT_EXACT_HEAD",
    "verifier_entrypoint": (
        "python -m unittest tests.test_protocol_v1_conformance_fixtures at the exact head (12 tests; "
        ".stegverse/test-sets.json set id tests/test_protocol_v1_conformance_fixtures.py). Node ids -> predicate: "
        "PositiveCaseTest::test_positive_is_not_refused_and_echoes_the_bounded_effect_with_no_ledger_append -> "
        "PROTOCOL_V1_POSITIVE_PACKET_FIXTURE_ALLOW_WITH_NO_LEDGER_APPEND; "
        "NegativeCaseTest::test_each_negative_refusal_code_and_temp_ledger_no_append and "
        "NegativeCaseTest::test_stale_head_refusal_code_is_the_standing_contracts_own -> "
        "PROTOCOL_V1_SEVEN_REFUSALS_OBSERVED_CODE_EQUALS_DECLARED_FAILURE_CODE; "
        "ReplayCaseTest::test_redelivery_under_another_packet_id_is_the_same_transition_with_no_second_append -> "
        "PROTOCOL_V1_REPLAY_REDELIVERY_IS_ONE_TRANSITION_ONE_RECEIPT_PER_LEVEL; "
        "FixtureShapeTest::test_every_negative_declares_six_fields_and_a_non_allow_disposition and "
        "FixtureShapeTest::test_replay_declares_idempotent_redelivery_and_a_six_field_spec_gap -> "
        "PROTOCOL_V1_EVERY_NON_ALLOW_CARRIES_SIX_FIELDS; "
        "FixtureShapeTest::test_manifest_digest_is_exact_byte_identity plus the retained CI run of that set at the "
        "exact head -> PROTOCOL_V1_EXACT_HEAD_CI_RUN_RETAINED; "
        "python -m pytest tests/test_organization_ledger_same_store_readback.py::"
        "test_ingress_readback_reads_the_declared_git_store (organization_manifest_ingress._organization_receipt_read_back "
        "against the declared git store) -> "
        "PROTOCOL_V1_ORGANIZATION_LEDGER_READBACK_INDEPENDENTLY_OBSERVED_OR_SIX_FIELD_NOT_ATTEMPTED. "
        "ExpectationMutationRegressionTest (2) guards the fixture expectations themselves."
    ),
    "lowest_supported_mode": "E0",
}
SCOPE = {
    "goal": GOAL,
    "targets": TARGETS,
    "expected_evidence_predicates": PREDICATES,
    "finish_point": FINISH,
}

req = {
    "schema": "stegverse.canonical-task-registration-request/v1",
    "request_id": "protocol-v1-minimum-packet-conformance-001" + ("" if VARIANT == "primary" else "-" + VARIANT),
    "task_id": TASK,
    "observed_registry_generation": GEN,
    "registration_mode": "NEW_IDENTITY",
    "issue": "StegVerse-Labs/.github#3369",
    "allocation_request_ref": None,
    "collision_analysis": [
        DRAFT + ": this manifest proposes; the Registry owner has not approved it, and no COSV, claim, fence or receipt exists.",
        "Candidate PROTOCOL-V1-MINIMUM-PACKET-CONFORMANCE-001 is STOP_NOT_REGISTERED at generation " + str(GEN) + " (scripts/evaluate_task_registry_collision_checkin.py; tests/test_registry_collision_claimed_integration_guard.py::Issue3369RealRegistrationTests).",
        "SDK-MANIFEST-ECOSYSTEM-TRANSITION-DISPOSITION-001 (ACTIVE/CHECKED_OUT): real scope overlap. Row targets both candidate repositories and component allow-deny-fail-closed (data/canonical-task-registry.json:20552-20560); bounded extension I12 names resident-runtime/organization_manifest_ingress.py (registry:20653; shard:161); six of the eight committed #3369 refusal fixtures name it owning_existing_goal.",
        "ORGANIZATION-BATCH-CUSTODY-REPLAY-001 (ACTIVE/HANDOFF_READY, not owner-held): real scope overlap on ledger readback only. Row declares no targets (no components), so the evaluator cannot see it; current_truth names organization_manifest_ingress.py::_organization_receipt_read_back (registry:10810); cases/n2-replay.json names it owner of the replay refusal gap.",
        "STEGVERSE-CANONICAL-WORK-COORDINATION-001 (PROPOSED): name adjacency only. Its components (registry:88-115) do not include any candidate component; it is not ACTIVE-ish so it is never a collision candidate; its own STOP_COLLISION comes from its CHECKED_OUT children by lineage.",
        "Omitted CHECKED_OUT shards (collision guards, not registered): CANONICAL-WORK-END-TO-END-CYCLE-CLOSURE-001 holds sdk-manifest-ingress, organization-transition-ledger, workercoordinator-claim-fence, universal-interlock-intr over both candidate repositories and source_ref org-runtime/interlock-intr.json (shard:28-40); CANONICAL-WORK-EXACT-INVOCATION-EVIDENCE-RECONCILIATION-001 holds organization-ledger-readback (shard:23-31). Both are lineage children of STEGVERSE-CANONICAL-WORK-COORDINATION-001.",
        "GITHUB-UNIVERSAL-GOVERNANCE-PRODUCT-001: not registered (NO_SHARD_NO_ROW, tests/fixtures/canonical_task_registration/i1-goal-manifests/MANIFEST.json); no overlap to evaluate.",
        "EC9-WHEN-AI-SERVICES-FAIL-PUBLICATION-001 (PROPOSED, registered at generation 322 by StegVerse-Labs/.github#3373): targets Executive_Rhetoric_Ledger, Site and SV-LLM/Ecosystem_Chat with paper-publication components; no repository or component overlap with the candidate; PROPOSED is never a collision candidate.",
        "CANONICAL-NODE-INGRESS-CONTRACT-001 (named owner by cases/n4-stale-head.json) is not registered.",
    ],
    "record": RECORD,
    "sealed_scope": {
        "schema": "stegverse.goal-scope-seal/v1",
        "scope": SCOPE,
        "scope_digest": "sha256:" + hashlib.sha256(canon(SCOPE)).hexdigest(),
        "supersedes_scope_digest": None,
    },
    "vector": {
        "exact_metrics": {
            "symbol_order": "LRUIVGOCMTBEAP",
            "lifecycle": "UNCLAIMED",
            "archive_ready": False,
            "unassigned_work": 1,
            "chat_owned_implementation": 0,
            "chat_owned_validation": 0,
            "chat_owned_integration": 0,
            "chat_owned_observation": 0,
            "chat_owned_credentials": 0,
            "canonical_owner_installed": False,
            "thread_required": True,
            "blocker_count": 0,
            "evidence_complete": False,
            "activated": False,
            "propagated": False,
        },
        "metric_evidence": {
            "lifecycle": "PROPOSED; no WorkerCoordinator claim; " + DRAFT,
            "unassigned_work": "owner collision ruling, exact-head CI run and independent ledger readback pending",
            "canonical_owner_installed": "false until the Registry owner approves this request or binds the work to an existing owner",
            "blocker_count": "no blocker recorded; dependencies UNRESOLVED",
        },
        "evidence_refs": [
            "StegVerse-Labs/.github#3369",
            "org-kernel/organization-ledger/fixtures/protocol-v1-conformance/README.md",
            "tests/test_protocol_v1_conformance_fixtures.py",
        ],
        "observed_at": "2026-10-28T00:00:00Z",
    },
    "authority_effect": "NONE_REGISTRATION_ONLY",
}

OUT.write_text(json.dumps(req, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(OUT, req["sealed_scope"]["scope_digest"])
