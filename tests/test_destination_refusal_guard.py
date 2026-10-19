"""Every outbound request in stegverse/ turns a non-answer into a six-field record (SDK#484 V-P7).

Each site makes one bounded request. When the destination does not answer, the result is a
DURABLE_QUEUE_OR_EVENT_EPHEMERAL_MATERIALIZATION record with the six fields, either returned or
carried as ``.disposition`` on the raised error or its cause, and never a wait or a retry loop.
SITES lists every urlopen call; a new one fails here until it is listed and covered.
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request

import stegverse._stdlib_http as http
import stegverse.comparison_transport as transport
import stegverse.github_repository_fetcher as fetcher
import stegverse.portable_packages as portable
import stegverse.production_release_set as release_set
import stegverse.release_index as release_index
from stegverse.destination_refusal import SIX_FIELDS, disposition_of

ROOT = Path(__file__).resolve().parents[1]
SITES = {
    "stegverse/_stdlib_http.py": 1,
    "stegverse/release_index.py": 1,
    "stegverse/production_release_set.py": 1,
    "stegverse/portable_packages.py": 1,
    "stegverse/github_repository_fetcher.py": 1,
}


def _unreachable(*_args, **_kwargs):
    raise URLError("destination unreachable (simulated)")


def _assert_six(record):
    assert record is not None and record["disposition"] == "FAIL_CLOSED", record
    assert all(record[field] for field in SIX_FIELDS), record


class _Patched:
    def __init__(self, module, name="urlopen"):
        self.module, self.name = module, name

    def __enter__(self):
        self.saved = getattr(self.module, self.name)
        setattr(self.module, self.name, _unreachable)

    def __exit__(self, *exc):
        setattr(self.module, self.name, self.saved)


def test_every_urlopen_site_is_listed():
    found = {}
    for path in sorted((ROOT / "stegverse").rglob("*.py")):
        count = len(re.findall(r"\burlopen\(", path.read_text(encoding="utf-8")))
        if count:
            found[path.relative_to(ROOT).as_posix()] = count
    assert found == SITES


def test_stdlib_http_transport_failure_carries_six_fields():
    with _Patched(http.urlrequest):
        try:
            http.get("https://destination.invalid/x", timeout=1)
        except http.HttpTransportError as exc:
            _assert_six(disposition_of(exc))
        else:
            raise AssertionError("no refusal")


def test_wrapping_errors_expose_the_record_through_their_cause():
    # comparison_transport, comparison_orchestrator and production_validation_runtime re-raise
    # HttpTransportError as their own error "from exc"; disposition_of reads it through the chain.
    try:
        try:
            raise http.HttpTransportError("HTTP 503", destination="https://destination.invalid/compare",
                                          failure_code="DESTINATION_ANSWERED_WITH_ERROR_STATUS")
        except http.HttpTransportError as cause:
            raise transport.ComparisonTransportError("comparison transport failed") from cause
    except transport.ComparisonTransportError as exc:
        record = disposition_of(exc)
    _assert_six(record)
    assert record["failure_code"] == "DESTINATION_ANSWERED_WITH_ERROR_STATUS"


def test_release_index_returns_six_fields_when_unavailable():
    with _Patched(release_index):
        result = release_index.fetch_versions(timeout=1)
    assert result["state"] == "UNAVAILABLE_NON_AUTHORIZING"
    _assert_six(result)


def test_production_release_catalog_rows_carry_six_fields_when_unavailable():
    with _Patched(release_set):
        catalog = release_set.public_release_catalog(timeout=1)
    rows = catalog["components"]
    assert rows and all(row["state"] == "UNAVAILABLE_NON_AUTHORIZING" for row in rows)
    for row in rows:
        _assert_six(row)


def test_github_fetcher_carries_six_fields_when_unreachable():
    with _Patched(fetcher):
        try:
            fetcher._default_http_executor(Request("https://api.github.com/repos/x/y/contents/z"), 1)
        except fetcher.GitHubRepositoryFetcherError as exc:
            _assert_six(disposition_of(exc))
        else:
            raise AssertionError("no refusal")


def test_portable_download_carries_six_fields_when_unreachable(tmp_path):
    artifact = {"release_url": "https://destination.invalid/pkg.zip", "archive_sha256": "0" * 64}
    saved = portable.inspect_package
    portable.inspect_package = lambda _cls: {"artifacts": {fmt: artifact for fmt in portable.ARCHIVE_FORMATS}}
    try:
        with _Patched(portable):
            try:
                portable.download_package("ANY", tmp_path / "pkg.zip", "zip")
            except portable.PortablePackageError as exc:
                _assert_six(disposition_of(exc))
            else:
                raise AssertionError("no refusal")
    finally:
        portable.inspect_package = saved
