from __future__ import annotations
import hashlib
import unittest

from scripts.build_private_state_economy_publication_manifest import (
    SOURCE_SHA256, SOURCE_GIT_BLOB_SHA, TASK_ID, COSV, build
)


SOURCE = b"# exact approved-source fixture cannot satisfy production identity"


class BuildPrivateStateEconomyPublicationManifestTests(unittest.TestCase):
    def test_wrong_source_refuses_before_manifest(self):
        with self.assertRaisesRegex(ValueError, "approved_source_sha256_mismatch"):
            build(SOURCE)

    def test_canonical_identity_constants_are_exact(self):
        self.assertEqual(TASK_ID, "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001")
        self.assertEqual(COSV, "10100000102000")
        self.assertEqual(SOURCE_SHA256, "3329a0c47161eb4613c32bbc5e0a393116f395cb8fa78368ed21fed8775c3dca")
        self.assertEqual(SOURCE_GIT_BLOB_SHA, "5c03d8ef1d79c65bb2338268c156d00295caa48a")


if __name__ == "__main__":
    unittest.main()
