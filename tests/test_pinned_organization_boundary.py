"""T2 offline installed organization boundary identity regression."""
import hashlib
from importlib import resources
from unittest import mock

from stegverse.manifest_execution import _canonical_organization_boundary


def test_installed_boundary_is_pinned_and_never_fetches():
    raw = resources.files("stegverse").joinpath("pinned_sources", "interlock-intr.json").read_bytes()
    blob = b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
    assert hashlib.sha1(blob).hexdigest() == "609707d5ecd3e09f5b97cd98a2e665a59659fce8"

    def forbidden_fetch(*args, **kwargs):
        raise AssertionError("runtime network fetch prohibited")

    boundary = _canonical_organization_boundary(fetcher=forbidden_fetch)
    assert boundary["schema"] == "stegverse.organization-interlock-intr-boundary/v1"
    assert boundary["organization"] == "StegVerse-Labs"


class _FakePackage:
    """Stand-in for importlib.resources.files("stegverse") returning fixed bytes or an error."""

    def __init__(self, payload=None, error=None):
        self.payload, self.error = payload, error

    def joinpath(self, *parts):
        outer = self

        class _FakeResource:
            def read_bytes(self):
                if outer.error is not None:
                    raise outer.error
                return outer.payload

        return _FakeResource()


def _refusal(package):
    """Run the loader against a fake package and return the ValueError it must raise."""
    with mock.patch("stegverse.manifest_execution.resources.files", lambda name: package):
        try:
            _canonical_organization_boundary()
        except ValueError as exc:
            return str(exc)
    raise AssertionError("tampered or missing boundary was accepted")


def test_tampered_installed_boundary_fails_closed():
    payload = b'{"schema":"stegverse.organization-interlock-intr-boundary/v1","organization":"attacker"}'
    assert "CANONICAL_ORGANIZATION_BOUNDARY_PIN_MISMATCH" in _refusal(_FakePackage(payload=payload))


def test_missing_installed_boundary_fails_closed():
    error = FileNotFoundError("pinned source absent")
    assert "CANONICAL_ORGANIZATION_BOUNDARY_INSTALLED_SOURCE_REQUIRED" in _refusal(_FakePackage(error=error))
