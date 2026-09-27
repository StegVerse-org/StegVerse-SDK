from stegverse.capability_inventory import installed_capability_inventory, qualify_requirements

def test_inventory_is_derived_from_current_published_routes_and_non_authorizing():
    rows = installed_capability_inventory()
    assert len(rows) >= 6
    assert {row["capability_id"] for row in rows} >= {
        "governance",
        "ecosystem_diagnostic",
        "purpose_bound_worker",
        "atomic_task_worker",
        "native_source_math",
    }
    assert all(row["execution_authorized"] is False for row in rows)
    assert all(row["route_substitution_permitted"] is False for row in rows)

def test_supported_requirement():
    out = qualify_requirements(
        {"payload": "x"},
        [{"requirement_id": "r1", "capability_id": "native_source_math"}],
    )
    assert out["results"][0]["disposition"] == "SUPPORTED"
    assert out["results"][0]["failed_predicate"] is None

def test_missing_input_is_explicit():
    out = qualify_requirements(
        {},
        [{"requirement_id": "r2", "capability_id": "native_source_math", "required_inputs": ["payload"]}],
    )
    row = out["results"][0]
    assert row["disposition"] == "MISSING_INPUT"
    assert row["failed_predicate"] == "REQUIRED_INPUT_PRESENT"

def test_unsupported_capability_is_explicit():
    out = qualify_requirements({}, [{"requirement_id": "r3", "capability_id": "not_installed"}])
    row = out["results"][0]
    assert row["disposition"] == "UNSUPPORTED"
    assert row["failed_predicate"] == "CAPABILITY_INSTALLED"

def test_version_incompatible_is_explicit():
    out = qualify_requirements(
        {},
        [{"requirement_id": "r4", "capability_id": "native_source_math", "version_compatible": False}],
    )
    row = out["results"][0]
    assert row["disposition"] == "VERSION_INCOMPATIBLE"
    assert row["failed_predicate"] == "REQUESTED_VERSION_COMPATIBLE"

def test_runtime_evidence_requirement_is_probe_required_not_source_success():
    out = qualify_requirements(
        {},
        [{
            "requirement_id": "r5",
            "capability_id": "native_source_math",
            "authentic_runtime_evidence_required": True,
        }],
    )
    row = out["results"][0]
    assert row["disposition"] == "PROBE_REQUIRED"
    assert row["failed_predicate"] == "AUTHENTIC_RUNTIME_EVIDENCE_OBSERVED"

def test_exact_route_is_never_substituted():
    out = qualify_requirements(
        {},
        [{
            "requirement_id": "r6",
            "capability_id": "governance",
            "route_id": "stegverse.route.not-installed.v1",
        }],
    )
    row = out["results"][0]
    assert row["disposition"] == "UNSUPPORTED"
    assert row["failed_predicate"] == "EXACT_ROUTE_INSTALLED"
    assert out["route_substitution_permitted"] is False

def test_manifest_digest_changes_when_original_manifest_changes():
    a = qualify_requirements({"payload": "a"}, [])
    b = qualify_requirements({"payload": "b"}, [])
    assert a["manifest_sha256"] != b["manifest_sha256"]
