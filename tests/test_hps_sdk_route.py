from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_hps_sdk_route import DECISION_ALLOW, DECISION_DENY, DECISION_FAIL_CLOSED, decide  # noqa: E402

EXAMPLES = ROOT / "examples"


def load_example(name: str) -> dict:
    with (EXAMPLES / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


class HpsSdkRouteTests(unittest.TestCase):
    def test_allowed_route(self) -> None:
        result = decide(load_example("hps_sdk_route_allowed.json"))
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.decision, DECISION_ALLOW)

    def test_expired_route_denies(self) -> None:
        result = decide(load_example("hps_sdk_route_expired.json"))
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.decision, DECISION_DENY)

    def test_unknown_or_broken_route_fails_closed(self) -> None:
        result = decide(load_example("hps_sdk_route_fail_closed.json"))
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.decision, DECISION_FAIL_CLOSED)


if __name__ == "__main__":
    unittest.main()
