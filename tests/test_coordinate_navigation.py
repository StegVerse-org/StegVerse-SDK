from stegverse.coordinate_navigation import CoordinateNavigationError, consume_navigation_envelope


def _registry():
    return {
        "registry_version": "1.0.0",
        "coordinates": [{
            "coordinate_id": "ecosystem://runtime/micro-node-governance",
            "version": "1.0.0",
            "contract_ref": "examples/coordinates/runtime.micro-node-governance.json",
            "content_sha256": "a" * 64,
        }],
        "edges": [{
            "source": "ecosystem://runtime/micro-node-governance",
            "destination": "ecosystem://records/master-records",
            "authority_transfer": "NONE",
            "receipt_required": True,
        }],
    }


def _envelope():
    return {
        "envelope_version": "1.0.0",
        "navigation_id": "navigation-001",
        "actor": "user:local",
        "source_coordinate": "ecosystem://runtime/micro-node-governance",
        "destination_coordinate": "ecosystem://records/master-records",
        "context_refs": ["receipt:example"],
        "authority_transfer": "NONE",
        "standing_transfer": "NONE",
        "delegation_transfer": "NONE",
        "data_transfer": "DECLARED_REFS_ONLY",
        "receipt_required": True,
        "commit_time_revalidation_required": True,
        "return_path": "ecosystem://runtime/micro-node-governance",
    }


def test_navigation_consumer_is_deterministic_and_non_authorizing():
    first = consume_navigation_envelope(_envelope(), _registry())
    second = consume_navigation_envelope(_envelope(), _registry())
    assert first == second
    assert len(first["consumer_sha256"]) == 64
    assert first["sdk_boundary"]["sdk_consumption_is_navigation_authority"] is False
    assert first["authority_transfer"] == "NONE"


def test_undeclared_destination_fails_closed():
    envelope = _envelope()
    envelope["destination_coordinate"] = "ecosystem://undeclared"
    try:
        consume_navigation_envelope(envelope, _registry())
    except CoordinateNavigationError as exc:
        assert "declared registry edge" in str(exc)
    else:
        raise AssertionError("undeclared navigation must fail closed")


def test_authority_transfer_fails_closed():
    envelope = _envelope()
    envelope["authority_transfer"] = "FULL"
    try:
        consume_navigation_envelope(envelope, _registry())
    except CoordinateNavigationError as exc:
        assert "cannot transfer authority" in str(exc)
    else:
        raise AssertionError("authority transfer must fail closed")
