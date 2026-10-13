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
