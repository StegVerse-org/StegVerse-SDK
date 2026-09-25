"""Nonpublishing source-link candidate tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.resolve_deepwiki_review_citations import audit, resolve_label

SHA = '0' * 40


class TestDeepWikiCitationCandidates(unittest.TestCase):
    def test_partition_and_nonpublication(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'demo.py').write_text('a\nb\n', encoding='utf-8')
            raw = '# Page: A\n[demo.py:1-2]() [demo.py:3]() [missing.py:1]() [demo.py]() [demo.py:fn]()'
            result, report = audit(raw, root, SHA)
            self.assertEqual(report['input_empty_targets'], 5)
            self.assertEqual(report['candidate_source_links'], 2)
            self.assertEqual(report['remaining_empty_targets'], 3)
            self.assertEqual(report['entries'][0]['page'], 'A')
            self.assertIn('#L1-L2', result)
            self.assertFalse(report['publication_allowed'])

    def test_invalid_path_and_revision(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(
                resolve_label('/demo.py:1', Path(tmp), SHA)[1],
                'UNSAFE_OR_AMBIGUOUS_PATH',
            )
            with self.assertRaises(ValueError):
                audit('x', Path(tmp), 'main')

    def test_malformed_remains_visible(self):
        with TemporaryDirectory() as tmp:
            _, report = audit('one [ok.py]() and malformed source]()',
                              Path(tmp), SHA)
            self.assertEqual(report['input_empty_targets'], 2)
            self.assertEqual(report['non_simple_occurrences'], 1)
            self.assertEqual(report['remaining_empty_targets'], 2)
            self.assertFalse(report['publication_allowed'])


if __name__ == '__main__':
    unittest.main()
