import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.export_deepwiki_review import extract_jsonrpc, response_text, export, compare_page_coverage


def result(text):
    return {"result": {"content": [{"type": "text", "text": text}]}}


class DeepWikiReviewExportTests(unittest.TestCase):
    def test_plain_and_sse_responses(self):
        body = result("Documentation content")
        self.assertEqual(extract_jsonrpc(json.dumps(body).encode(), "application/json"), body)
        sse = ("event: message\ndata: " + json.dumps(body) + "\n\n").encode()
        self.assertEqual(extract_jsonrpc(sse, "text/event-stream"), body)

    def test_error_and_empty_fail_closed(self):
        with self.assertRaises(ValueError):
            extract_jsonrpc(b'{"jsonrpc":"2.0","error":{"code":-1}}', "application/json")
        with self.assertRaises(ValueError):
            extract_jsonrpc(b'{"result":{"isError":true}}', "application/json")

    def test_only_review_files_and_no_publication(self):
        items = [
            result("Available pages for StegVerse-org/StegVerse-SDK:\n- 1 Overview\n  - 1.1 Manifest Pipeline"),
            result("# Page: Overview\n# Overview\nDetailed documentation.\n# Page: Manifest Pipeline\n# Manifest Pipeline\nMore documentation."),
        ]
        with tempfile.TemporaryDirectory() as folder:
            with patch("scripts.export_deepwiki_review.rpc_call", side_effect=items):
                manifest = export(Path(folder))
            self.assertEqual(manifest["authority_effect"], "NONE_REVIEW_ONLY")
            self.assertFalse(manifest["publication_allowed"])
            self.assertEqual(len(manifest["files"]), 4)\n            self.assertEqual(manifest["captured_page_count"], 2)
            self.assertEqual(len(list(Path(folder).iterdir())), 5)
            self.assertIn("UNREVIEWED", manifest["content_status"])


if __name__ == "__main__":
    unittest.main()
