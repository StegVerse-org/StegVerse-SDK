from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

from stegverse.mir_leaf_v3 import MirLeafV3Error, reproduce_fixture

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "mir_leaf_v3_conformance_fixture_v1.json"
NEUTRAL = ROOT / "tools" / "mir_leaf_v3_neutral_reproducer.mjs"


class MirLeafV3ConformanceTests(unittest.TestCase):
    def load_fixture(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_stegverse_reproduces_frozen_vectors(self):
        result = reproduce_fixture(self.load_fixture())
        self.assertEqual(
            result["merkle_root"],
            "sha256:bd0eb01fccc1d88942f2fb465d27f212afb98f5b0aee47faf370ea0bf21a5a94",
        )
        self.assertEqual(
            result["checkpoint_tip"],
            "sha256:683eac81cfd934700c7ebe8eb4da668f2d44ae95c0cfe74d6d157993324f2ad8",
        )
        self.assertEqual(result["witnesses"], [])
        self.assertEqual(result["proof_status"], "UNAVAILABLE")

    def test_neutral_javascript_reproducer_matches(self):
        completed = subprocess.run(
            ["node", str(NEUTRAL), str(FIXTURE)],
            check=True,
            capture_output=True,
            text=True,
        )
        neutral = json.loads(completed.stdout)
        stegverse = reproduce_fixture(self.load_fixture())
        self.assertEqual(neutral["leaf_hashes"], stegverse["leaf_hashes"])
        self.assertEqual(neutral["merkle_root"], stegverse["merkle_root"])
        self.assertEqual(neutral["checkpoint_tip"], stegverse["checkpoint_tip"])

    def test_event_byte_mutation_fails_closed(self):
        fixture = self.load_fixture()
        fixture["events"][0]["canonical_event_core_base64"] = "QQ=="
        with self.assertRaisesRegex(MirLeafV3Error, "leaf mismatch"):
            reproduce_fixture(fixture)

    def test_salt_mutation_fails_closed(self):
        fixture = self.load_fixture()
        fixture["events"][1]["salt_base64"] = "AAAAAAAAAAAAAAAAAAAAAA=="
        with self.assertRaisesRegex(MirLeafV3Error, "leaf mismatch"):
            reproduce_fixture(fixture)

    def test_order_mutation_fails_closed(self):
        fixture = self.load_fixture()
        fixture["events"][0], fixture["events"][1] = fixture["events"][1], fixture["events"][0]
        with self.assertRaisesRegex(MirLeafV3Error, "event indexes"):
            reproduce_fixture(fixture)

    def test_root_substitution_fails_closed(self):
        fixture = self.load_fixture()
        fixture["checkpoint"]["expected_merkle_root"] = "sha256:" + "00" * 32
        with self.assertRaisesRegex(MirLeafV3Error, "merkle root mismatch"):
            reproduce_fixture(fixture)

    def test_tip_substitution_fails_closed(self):
        fixture = self.load_fixture()
        fixture["checkpoint"]["expected_tip"] = "sha256:" + "00" * 32
        with self.assertRaisesRegex(MirLeafV3Error, "checkpoint tip mismatch"):
            reproduce_fixture(fixture)

    def test_witness_claim_before_12_6_fails_closed(self):
        fixture = self.load_fixture()
        fixture["witnesses"] = [{"witnessId": "not-shipped"}]
        with self.assertRaisesRegex(MirLeafV3Error, "witnesses must remain empty"):
            reproduce_fixture(fixture)

    def test_false_proof_completion_fails_closed(self):
        fixture = self.load_fixture()
        fixture["proof_status"] = "PROVIDED"
        with self.assertRaisesRegex(MirLeafV3Error, "proof_status"):
            reproduce_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
