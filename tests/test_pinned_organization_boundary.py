"""T2 offline installed organization boundary identity regression."""
import hashlib
from importlib import resources

from stegverse.manifest_execution import _canonical_organization_boundary


def test_installed_boundary_is_pinned_and_never_fetches():
    raw = resources.files("stegverse").joinpath("pinned_sources", "interlock-intr.json").read_bytes()
    blob = b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
    assert hashlib.sha1(blob).hexdigest() == "a1f61d82a38a817a1dd2749505d8802dd09a22f8"

    def forbidden_fetch(*args, **kwargs):
        raise AssertionError("runtime network fetch prohibited")

    boundary = _canonical_organization_boundary(fetcher=forbidden_fetch)
    assert boundary["schema"] == "stegverse.organization-interlock-intr-boundary/v1"
    assert boundary["organization"] == "StegVerse-Labs"


def test_tampered_installed_boundary_fails_closed(monkeypatch):
    import pytest
    from pathlib import Path

    class FakePackage:
        def joinpath(self, *parts):
            class FakeResource:
                def read_bytes(self):
                    return b'{"schema":"stegverse.organization-interlock-intr-boundary/v1","organization":"attacker"}'
            return FakeResource()

    monkeypatch.setattr("stegverse.manifest_execution.resources.files", lambda name: FakePackage())
    with pytest.raises(ValueError, match="CANONICAL_ORGANIZATION_BOUNDARY_PIN_MISMATCH"):
        _canonical_organization_boundary()


def test_missing_installed_boundary_fails_closed(monkeypatch):
    import pytest

    class FakePackage:
        def joinpath(self, *parts):
            class FakeResource:
                def read_bytes(self):
                    raise FileNotFoundError("pinned source absent")
            return FakeResource()

    monkeypatch.setattr("stegverse.manifest_execution.resources.files", lambda name: FakePackage())
    with pytest.raises(ValueError, match="CANONICAL_ORGANIZATION_BOUNDARY_INSTALLED_SOURCE_REQUIRED"):
        _canonical_organization_boundary()
