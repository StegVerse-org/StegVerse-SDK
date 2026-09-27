import unittest
from unittest.mock import patch

from scripts.observe_sdk_public_wiki import fetch


class FakeResponse:
    def __init__(self, body: bytes, final_url: str, status: int = 200, content_type: str = "text/html"):
        self._body = body
        self._final_url = final_url
        self.status = status
        self.headers = {"Content-Type": content_type}

    def read(self):
        return self._body

    def geturl(self):
        return self._final_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class PublicWikiOriginBindingTests(unittest.TestCase):
    def test_sdk_case_accepts_sdk_origin(self):
        case = {
            "id": "SDK",
            "url": "https://sdk.stegverse.org/source.json",
            "expected_origin": "https://sdk.stegverse.org",
            "markers": ["needle"],
        }
        with patch("urllib.request.urlopen", return_value=FakeResponse(b"needle", case["url"])):
            result = fetch(case)
        self.assertTrue(result["origin_match"])
        self.assertTrue(result["passed"])

    def test_site_link_accepts_site_origin(self):
        case = {
            "id": "SITE",
            "url": "https://stegverse.org/wikis.html",
            "expected_origin": "https://stegverse.org",
            "markers": ["StegVerse SDK Developer Wiki", "https://sdk.stegverse.org/"],
        }
        body = b"StegVerse SDK Developer Wiki https://sdk.stegverse.org/"
        with patch("urllib.request.urlopen", return_value=FakeResponse(body, case["url"])):
            result = fetch(case)
        self.assertTrue(result["origin_match"])
        self.assertTrue(result["passed"])

    def test_cross_origin_redirect_fails_closed(self):
        case = {
            "id": "SDK",
            "url": "https://sdk.stegverse.org/source.json",
            "expected_origin": "https://sdk.stegverse.org",
            "markers": ["needle"],
        }
        with patch("urllib.request.urlopen", return_value=FakeResponse(b"needle", "https://example.com/source.json")):
            result = fetch(case)
        self.assertFalse(result["origin_match"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
