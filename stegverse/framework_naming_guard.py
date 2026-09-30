"""Artifacts are named by capability, never by the framework or person they came from.

An evaluator's identity belongs in manifest data - `source_framework` is a
required field of the ingress manifest - not in a module name, a schema
identifier, a fixture path or a workflow file. A demo named after the first
framework that exercised it reads as that framework's demo, and the next
evaluator has to reverse-engineer a neutral shape from someone else's name.

This module reports where that rule is broken. It draws one distinction the
rule depends on:

* a schema identifier the SDK **owns** (`stegverse.*`) must be capability-named;
* a scheme the SDK merely **recognizes** because a counterpart emits it
  (`mir.leaf.v3`, `elan.relational-state.v1`) is that counterpart's format, and
  naming it is recognizing data, exactly as `source_framework: ELAN` is.

Detection is by exact path/identifier segment, never substring: `MIRROR_HANDOFF`
tokenizes to `mirror`, which is not `mir`, so the eighty-five mirror-handoff
documents are not swept up by a search for MIR.

Artifacts that predate the organization receipt chains are provenance. They are
declared in a committed baseline with the reason they are retained, and they
pass. Anything framework-named and *not* declared fails, so the set can only
shrink. A baseline entry whose artifact no longer exists also fails, so the
baseline cannot rot into a list of things nobody checks.

Non-authorizing. Source naming only: it renames nothing, installs nothing,
admits nothing and observes no runtime.
"""
from __future__ import annotations

import json
import re
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "stegverse.sdk.framework-naming-guard-evaluation/v1"
BASELINE_SCHEMA = "stegverse.sdk.framework-named-historical-baseline/v1"

INVARIANT = "ARTIFACTS_ARE_NAMED_BY_CAPABILITY_NOT_BY_ORIGINATING_FRAMEWORK"

# Counterpart frameworks and people whose names must not name an artifact.
FRAMEWORK_TOKENS: frozenset[str] = frozenset({
    "mir", "elan", "hgai", "flint", "richard", "stcm", "chf",
})

# Schemes a counterpart owns and emits. The SDK recognizes these as values; it
# does not own them and must not be judged for carrying them.
RECOGNIZED_EXTERNAL_SCHEMES: frozenset[str] = frozenset({
    "mir.leaf.v3",
    "mir.checkpoint-tip.v0.3",
    "elan.relational-state.v1",
    "elan.intr.bridge.v1",
    "elan.evaluator-preregistration.v1",
})

# Dispositions a baseline entry may declare.
HISTORICAL = "HISTORICAL_PRE_ORG_RECEIPT"
PENDING_RENAME = "PENDING_CAPABILITY_RENAME"
DISPOSITIONS = (HISTORICAL, PENDING_RENAME)

# Verdicts.
CAPABILITY_NAMED = "CAPABILITY_NAMED"
UNDECLARED = "UNDECLARED_FRAMEWORK_NAMED_ARTIFACT"
STALE_BASELINE = "STALE_HISTORICAL_BASELINE_ENTRY"

AUTHORITY_BOUNDARY = {
    "guard_renames_anything": False,
    "baseline_entry_grants_permanence": False,
    "historical_disposition_excuses_new_artifacts": False,
    "recognizing_external_scheme_is_naming_violation": False,
    "guard_observes_runtime": False,
}

_SEGMENT = re.compile(r"[^A-Za-z0-9]+")
# A quoted identifier the SDK owns: starts with the stegverse namespace.
_OWNED_ID = re.compile(r"[\"'](stegverse[A-Za-z0-9._/-]*)[\"']")
# A quoted string may be a source path rather than a schema identifier. Paths
# are reported by the path scan; counting them again as identifiers would
# double-declare the same artifact.
_SOURCE_SUFFIXES = (
    ".py", ".json", ".md", ".yml", ".yaml", ".mjs", ".ts", ".js", ".txt", ".mdx",
)


class FrameworkNamingGuardError(ValueError):
    """Raised when a baseline declaration is structurally invalid."""


def segments(value: str) -> set[str]:
    """Lowercased alphanumeric segments of a path or identifier.

    Segment equality is what keeps `MIRROR` from matching `MIR`.
    """
    return {part.lower() for part in _SEGMENT.split(value) if part}


def framework_tokens_in(value: str) -> list[str]:
    return sorted(segments(value) & FRAMEWORK_TOKENS)


def framework_named_paths(paths: Iterable[str]) -> list[str]:
    return sorted(p for p in paths if framework_tokens_in(p))


def owned_schema_ids(text: str) -> list[str]:
    """SDK-owned identifiers in `text` that carry a framework token."""
    found: set[str] = set()
    for identifier in _OWNED_ID.findall(text):
        if identifier in RECOGNIZED_EXTERNAL_SCHEMES:
            continue
        if identifier.endswith(_SOURCE_SUFFIXES):
            continue
        if framework_tokens_in(identifier):
            found.add(identifier)
    return sorted(found)


def validate_baseline(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise FrameworkNamingGuardError("baseline must be an object")
    baseline = dict(value)
    if baseline.get("schema") != BASELINE_SCHEMA:
        raise FrameworkNamingGuardError("unsupported baseline schema")
    entries = baseline.get("entries")
    if not isinstance(entries, list):
        raise FrameworkNamingGuardError("baseline entries must be an array")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise FrameworkNamingGuardError("each baseline entry must be an object")
        artifact = str(entry.get("artifact") or "").strip()
        if not artifact:
            raise FrameworkNamingGuardError("baseline entry requires artifact")
        if artifact in seen:
            raise FrameworkNamingGuardError(f"duplicate baseline entry: {artifact}")
        seen.add(artifact)
        disposition = str(entry.get("disposition") or "").strip()
        if disposition not in DISPOSITIONS:
            raise FrameworkNamingGuardError(
                f"{artifact}: disposition must be one of {', '.join(DISPOSITIONS)}"
            )
        reason = str(entry.get("reason") or "").strip()
        if not reason:
            raise FrameworkNamingGuardError(f"{artifact}: reason is required")
        # A rename that is pending must say what it is renaming to, or it is a
        # standing intention with no edge that would satisfy it.
        capability_name = str(entry.get("capability_name") or "").strip()
        if disposition == PENDING_RENAME and not capability_name:
            raise FrameworkNamingGuardError(
                f"{artifact}: {PENDING_RENAME} requires capability_name"
            )
        if capability_name and framework_tokens_in(capability_name):
            raise FrameworkNamingGuardError(
                f"{artifact}: capability_name still carries a framework token"
            )
        normalized.append({
            "artifact": artifact,
            "disposition": disposition,
            "reason": reason,
            **({"capability_name": capability_name} if capability_name else {}),
        })
    baseline["entries"] = normalized
    return baseline


def evaluate_framework_naming(
    *,
    paths: Sequence[str],
    owned_identifiers: Sequence[str] = (),
    baseline: Any,
) -> dict[str, Any]:
    """Compare the framework-named artifact set against its declared baseline."""
    declared = validate_baseline(baseline)
    declared_map = {e["artifact"]: e for e in declared["entries"]}

    observed = framework_named_paths(paths) + sorted(set(owned_identifiers))
    observed_set = set(observed)

    undeclared = sorted(a for a in observed_set if a not in declared_map)
    stale = sorted(a for a in declared_map if a not in observed_set)

    by_disposition: dict[str, list[str]] = {d: [] for d in DISPOSITIONS}
    for artifact in observed:
        entry = declared_map.get(artifact)
        if entry:
            by_disposition[entry["disposition"]].append(artifact)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "invariant": INVARIANT,
        "observed_count": len(observed_set),
        "declared_count": len(declared_map),
        "historical": by_disposition[HISTORICAL],
        "pending_capability_rename": by_disposition[PENDING_RENAME],
        "undeclared": undeclared,
        "stale_baseline_entries": stale,
        "recognized_external_schemes": sorted(RECOGNIZED_EXTERNAL_SCHEMES),
        "authority_boundary": dict(AUTHORITY_BOUNDARY),
        "authority_effect": "NONE_SOURCE_NAMING_ONLY",
    }

    if undeclared:
        result["verdict"] = UNDECLARED
        result["conforming"] = False
        result["required_repair"] = (
            "Name the artifact by its capability. If it predates the organization "
            "receipt chains and is retained as provenance, declare it in the "
            "baseline with its reason."
        )
    elif stale:
        result["verdict"] = STALE_BASELINE
        result["conforming"] = False
        result["required_repair"] = (
            "Remove the baseline entries whose artifacts no longer exist, so the "
            "baseline records what is actually present."
        )
    else:
        result["verdict"] = CAPABILITY_NAMED
        result["conforming"] = True
        result["required_repair"] = None
    return result


def load_baseline(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return validate_baseline(json.load(handle))
