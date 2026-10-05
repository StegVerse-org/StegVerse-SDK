"""Non-authorizing discovery projected from current SDK declarations."""
from copy import deepcopy
import inspect
import json

from .manifest_builder import (
    build_manifest, PROCESSOR_ROUTES, GOVERNANCE_PROFILE_ROUTES,
    RETURN_DEPTHS, DIAGNOSTIC_RETURN_DEPTHS,
)
from .manifest_contract import validate_ingress_manifest
from .route_resolution import PUBLISHED_ROUTES

SUBMISSION_TERMINAL_STEPS = [
    "SUBMIT_CANONICAL_MANIFEST", "RETAIN_SUBMISSION_RESULT_AND_EVIDENCE",
]
MANIFEST_COMMANDS = {
    "manifest": "build and validate canonical manifests",
    "run-manifest": "dispatch the manifest-declared installed route",
    "external-run": "prepare the external-framework canonical manifest handoff",
    "machine-contract": "print SDK machine discovery as JSON",
}


def _declaration(function):
    parameters = inspect.signature(function).parameters
    return {
        "api": function.__module__ + "." + function.__name__,
        "required_parameters": [name for name, p in parameters.items()
                                if p.default is inspect.Parameter.empty
                                and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)],
    }


def sdk_machine_contract():
    from .external_framework_runner import prepare_external_framework_manifest
    profiles = {}
    for name, preparation, api in (
        ("LLM_MACHINE_CONTINUATION", "VALIDATE_CANONICAL_MANIFEST_WITH_SDK",
         "llm_adapter.governed_manifest_ingress.process_manifest"),
        ("EXTERNAL_FRAMEWORK_MANIFEST_CONTINUATION", "BUILD_AND_VALIDATE_CANONICAL_MANIFEST_WITH_SDK",
         "stegverse.external_framework_runner.manifest_external_framework_submission"),
    ):
        profiles[name] = {
            "steps": ["GET_NODE_ADVERTISEMENT_AND_HEALTH",
                      "ESTABLISH_OR_VERIFY_CANONICAL_NODE_STANDING",
                      preparation, *SUBMISSION_TERMINAL_STEPS],
            "standing_required": True,
            "standing_modes": ["ESTABLISH_GENESIS", "VERIFY_EXISTING"],
            "standing_owner": "CANONICAL_RECEIVING_NODE_BOUNDARY",
            "standing_is_established_by_this_contract": False,
            "submission_api": api,
            "receiving_owner": api.rsplit(".", 1)[0],
            "processing_selector": "manifest.processing.capability + manifest.processing.route_id",
            "interlock_intr": "INTERNAL_POST_SUBMISSION",
            "external_interlock_intr": "DEFERRED_TO_SUCCESSOR_AFTER_TESTS_5_AND_6",
        }
    profiles["EXTERNAL_FRAMEWORK_MANIFEST_CONTINUATION"].update({
        "sdk_builder_api": _declaration(build_manifest)["api"],
        "sdk_builder_cli": "stegverse manifest build",
        "sdk_framework_api": "stegverse.external_framework_runner.manifest_external_framework_submission",
        "sdk_framework_cli": "stegverse external-run",
        "framework_helper_is_submission_preparation_only": True,
        "native_sdk_requires_llm_adapter": False,
    })
    return {
        "schema": "stegverse.sdk.machine-contract.v1",
        "contract_id": "SDK_MACHINE_CONTRACT",
        "owner": "StegVerse-org/StegVerse-SDK",
        "authority_effect": "NONE_INSTRUCTIONS_ONLY",
        "evidence_class": "SOURCE_DECLARATION_PROJECTION",
        "builder": _declaration(build_manifest),
        "validator": _declaration(validate_ingress_manifest),
        "framework_builder": _declaration(prepare_external_framework_manifest),
        "cli": {name: "stegverse " + name for name in MANIFEST_COMMANDS},
        "processors": deepcopy(PROCESSOR_ROUTES),
        "published_routes": deepcopy(PUBLISHED_ROUTES),
        "governance_execution_profiles": deepcopy(GOVERNANCE_PROFILE_ROUTES),
        "return_depths": deepcopy(RETURN_DEPTHS),
        "diagnostic_return_depths": deepcopy(DIAGNOSTIC_RETURN_DEPTHS),
        "machine_readable_instructions": profiles,
        "framework_handoff_evidence_class": "SDK_LOCAL_MANIFEST_HANDOFF",
        "local_handoff_proves_receiver_observation": False,
        "enclosed_validation_is_canonical": False,
        "submission_proves_downstream_completion": False,
        "retention": ["exact_manifest", "raw_submission_result_or_error",
                      "sha256", "source_and_receiver_evidence_references"],
    }


def main(argv=None):
    import argparse
    argparse.ArgumentParser(prog="stegverse machine-contract").parse_args(argv)
    print(json.dumps(sdk_machine_contract(), indent=2, sort_keys=True))
    return 0
