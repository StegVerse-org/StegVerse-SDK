"""Non-authorizing machine projection of existing SDK declarations.

Discovery is source evidence, not node standing, submission or runtime proof.
"""
from __future__ import annotations

from copy import deepcopy
import inspect
import json

from .manifest_builder import build_manifest, PROCESSOR_ROUTES, RETURN_DEPTHS, available_processors
from .manifest_contract import validate_ingress_manifest
from .route_resolution import PUBLISHED_ROUTES
from .governance_navigation import INGRESS_PROFILE

SUBMISSION_TERMINAL_STEPS = (
    "SUBMIT_CANONICAL_MANIFEST", "RETAIN_SUBMISSION_RESULT_AND_EVIDENCE",
)


def sdk_machine_contract() -> dict:
    from .console_manifest_commands import COMMANDS
    from .external_framework_runner import prepare_external_framework_manifest
    def declaration(function):
        parameters = inspect.signature(function).parameters
        return {
            "api": function.__module__ + "." + function.__name__,
            "required_parameters": [name for name, p in parameters.items()
                                    if p.default is inspect.Parameter.empty
                                    and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)],
        }
    profiles = {}
    for name, preparation in (
        ("LLM_MACHINE_CONTINUATION", "VALIDATE_CANONICAL_MANIFEST_WITH_SDK"),
        ("EXTERNAL_FRAMEWORK_MANIFEST_CONTINUATION", "BUILD_AND_VALIDATE_CANONICAL_MANIFEST_WITH_SDK"),
    ):
        profiles[name] = {
            "standing_required": True,
            "standing_modes": ["ESTABLISH_GENESIS", "VERIFY_EXISTING"],
            "steps": ["GET_NODE_ADVERTISEMENT_AND_HEALTH",
                      "ESTABLISH_OR_VERIFY_CANONICAL_NODE_STANDING",
                      preparation, *SUBMISSION_TERMINAL_STEPS],
            "standing_owner": "CANONICAL_RECEIVING_NODE_BOUNDARY",
            "standing_is_established_by_this_contract": False,
            "receiving_owner": "llm_adapter.governed_manifest_ingress",
            "submission_api": "llm_adapter.governed_manifest_ingress.process_manifest",
            "direct_bypass_without_standing": "FAIL_CLOSED",
            "receiving_surface_state": "SOURCE_CALLABLE_REQUIRES_EXISTING_AUTHENTIC_ENDPOINT_BINDING",
            "missing_binding_disposition": "FAIL_CLOSED",
            "processing_selector": "manifest.processing.capability + manifest.processing.route_id",
            "interlock_intr": "INTERNAL_POST_SUBMISSION",
            "external_interlock_intr": "DEFERRED_TO_SUCCESSOR_AFTER_TESTS_5_AND_6",
        }
    from .external_framework_runner import manifest_external_framework_submission
    profiles["EXTERNAL_FRAMEWORK_MANIFEST_CONTINUATION"].update({
        "sdk_builder_api": declaration(build_manifest)["api"],
        "sdk_builder_cli": "stegverse manifest build",
        "sdk_framework_api": declaration(manifest_external_framework_submission)["api"],
        "sdk_framework_cli": "stegverse external-run",
        "enclosed_validation_flag": "--execute-enclosed",
        "enclosed_validation_is_canonical": False,
        "framework_helper_is_submission_preparation_only": True,
    })
    return {
        "schema": "stegverse.sdk.machine-contract.v1",
        "contract_id": "SDK_MACHINE_CONTRACT",
        "owner": "StegVerse-org/StegVerse-SDK",
        "authority_effect": "NONE_INSTRUCTIONS_ONLY",
        "evidence_class": "SOURCE_DECLARATION_PROJECTION",
        "manifest_profile": INGRESS_PROFILE,
        "builder": declaration(build_manifest),
        "validator": declaration(validate_ingress_manifest),
        "framework_builder": declaration(prepare_external_framework_manifest),
        "cli": {name: "stegverse " + name for name in COMMANDS},
        "processors": {name: {"route_id": route,
                               "installed": name in available_processors(),
                               "declaration": deepcopy(PUBLISHED_ROUTES.get(route))}
                       for name, route in sorted(PROCESSOR_ROUTES.items())},
        "return_depths": deepcopy(RETURN_DEPTHS),
        "machine_readable_instructions": profiles,
        "framework_handoff_evidence_class": "SDK_LOCAL_MANIFEST_HANDOFF",
        "local_handoff_proves_receiver_observation": False,
        "enclosed_validation_is_canonical": False,
        "submission_proves_downstream_completion": False,
        "retention": ["exact_manifest", "raw_submission_result_or_error",
                      "sha256", "source_and_receiver_evidence_references"],
    }


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="stegverse machine-contract")
    parser.parse_args(argv)
    print(json.dumps(sdk_machine_contract(), indent=2, sort_keys=True))
    return 0
