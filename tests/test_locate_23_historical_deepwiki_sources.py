"""Check non-authorizing exact-current source locator and provenance fences."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.locate_23_historical_deepwiki_sources import inspect_current


class Current23LocatorTests(unittest.TestCase):
    def fixture(self):
        rows=[]
        for i in range(27):
            rows.append({
                "index":i,
                "label":"sample.py:1",
                "exact_historical_literal":"SOURCE_LITERAL",
                "current_source_narrow_fact_also_observed":i>=23,
                "historical_excerpt_sha256":"a"*64,
                "predecessor_disposition":"DENY:PREVIOUS_NARROW_FACT_EXACT_SOURCE_REVALIDATION_REQUIRED",
            })
        return {"original_raw_sha256":"b"*64,
                "historic_review_source":"c"*40,
                "source_reconciliations":rows}

    def test_locator_preserves_23_historic_predecessors(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            (root/"sample.py").write_text("SOURCE_LITERAL\n",encoding="utf-8")
            packet=self.fixture()
            with patch("scripts.locate_23_historical_deepwiki_sources.FROZEN_CAPTURE","b"*64),patch(
                "scripts.locate_23_historical_deepwiki_sources.REVIEWED_HISTORIC","c"*40
            ):
                result=inspect_current(packet,root,"d"*40)
                self.assertEqual(result["historical_only_rechecked"],23)
                self.assertEqual(result["exact_current_literal_located"],23)
                self.assertEqual(result["full_generated_claims_approved"],0)
                self.assertTrue(all(not x["execution_observed"] for x in result["findings"]))
                (root/"sample.py").unlink()
                missing=inspect_current(packet,root,"d"*40)
                self.assertEqual(missing["current_literal_missing_or_source_unavailable"],23)
                with self.assertRaisesRegex(ValueError,"CAPTURE_HASH_CHANGED"):
                    inspect_current({**packet,"original_raw_sha256":"0"*64},root,"d"*40)


if __name__=="__main__":
    unittest.main()
