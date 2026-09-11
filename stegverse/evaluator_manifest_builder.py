"""Evaluator-safe composition over the canonical SDK Manifest Builder.

This module does not implement governance or resolve final security posture. It
keeps source-native observations, evaluator preregistration, governance evidence,
and posture request inputs in distinct manifest locations before handing the
result to the normal processor-generic ingress contract.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .manifest_builder import build_manifest
from .manifest_contract import validate_ingress_manifest
from .security_posture_request import (
    EXTENSION_KEY as SECURITY_POSTURE_REQUEST_EXTENSION,
    validate_security_posture_request,
)

EVALUATION_DECLARATION_EXTENSION = "evaluation_declaration"


def build_evaluator_governance_manifest(
    *,
    data: Any,
    source_framework: str,
    source_output_id: str,
    governance_request: Mapping[str, Any],
    evaluation_declaration: Mapping[str, Any] | None = None,
    security_posture_request: Mapping[str, Any] | None = None,
    return_depth: str = "result+evidence",
    data_class: str | None = None,
    source_instance: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Build one evaluator-safe governance ingress manifest.

    The governance request remains processor-specific evidence. The evaluator
    declaration remains preregistration metadata. The security posture request is
    request context only; Interlock/InTr resolves automatic/effective posture.
    """
    manifest = build_manifest(
        data=data,
        source_framework=source_framework,
        source_output_id=source_output_id,
        processor_request=governance_request,
        process="governance",
        return_depth=return_depth,
        data_class=data_class,
        source_instance=source_instance,
        created_at=created_at,
    )

    if evaluation_declaration is not None:
        if not isinstance(evaluation_declaration, Mapping):
            raise ValueError("evaluation_declaration must be an object when supplied")
        manifest["extensions"][EVALUATION_DECLARATION_EXTENSION] = deepcopy(
            dict(evaluation_declaration)
        )

    if security_posture_request is not None:
        request = validate_security_posture_request(security_posture_request)
        request_data_class = request.get("data_class")
        if data_class is not None and request_data_class is not None and request_data_class != data_class:
            raise ValueError("security_posture_request.data_class must match manifest data_class when both are supplied")
        manifest["extensions"][SECURITY_POSTURE_REQUEST_EXTENSION] = request

    # Re-run the processor-generic contract after evaluator/posture metadata is
    # attached. Neither extension changes payload/candidate hashes or authority.
    validate_ingress_manifest(manifest)
    return manifest


__all__ = [
    "EVALUATION_DECLARATION_EXTENSION",
    "build_evaluator_governance_manifest",
]
