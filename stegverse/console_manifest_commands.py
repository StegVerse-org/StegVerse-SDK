"""Shared dispatch declarations for existing manifest console surfaces."""
from importlib import import_module

COMMANDS = {
    "manifest": ("stegverse.manifest_builder", "build and validate a canonical manifest"),
    "run-manifest": ("stegverse.manifest_execution", "dispatch through the manifest-selected SDK owner"),
    "external-run": ("stegverse.external_framework_runner", "prepare framework submission; enclosed execution is opt-in"),
    "machine-contract": ("stegverse.machine_contract", "print SDK_MACHINE_CONTRACT from installed declarations"),
}
ALIASES = {"manifest-builder": "manifest", "manifest-run": "run-manifest", "framework-run": "external-run"}


def dispatch(argv):
    name = ALIASES.get(argv[0], argv[0]) if argv else None
    if name not in COMMANDS:
        return None
    if name == "external-run":
        from .evaluator_console import _install_versioned_governance_wrapper
        _install_versioned_governance_wrapper()
    return import_module(COMMANDS[name][0]).main(argv[1:])
