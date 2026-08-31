import unittest
from unittest.mock import patch

from stegverse.viewer_bound_operations import reconstruct_for_viewer, replay_for_viewer


class _FakeCustody:
    events = []

    def __init__(self, _path):
        pass

    def record_operation_event(self, event):
        self.__class__.events.append(dict(event))
        return {"event_receipt_id": "OP-EVENT-RECEIPT-001"}


def _fake_components():
    return (None, None, None, _FakeCustody, None, None, None, None, None, None)


class ViewerBoundOperationTests(unittest.TestCase):
    def setUp(self):
        _FakeCustody.events = []

    @patch("stegverse.viewer_bound_operations._components", side_effect=_fake_components)
    @patch("stegverse.viewer_bound_operations.replay_sovereign")
    def test_replay_appends_viewer_binding_event(self, replay, _components):
        replay.return_value = {
            "manifest_receipt_id": "MR-" + "A" * 64,
            "operation_id": "OP-REPLAY-ABC",
            "operation_receipt_ids": ["R0", "R1", "R2", "R3"],
            "consequence_reexecuted": False,
            "original_record_mutated": False,
        }
        result = replay_for_viewer(
            "MR-" + "A" * 64,
            viewer_node_id="node:viewer:001",
            custody_db=":memory:",
        )
        self.assertEqual("stegverse.viewer-bound-replay.v1", result["schema"])
        self.assertTrue(result["viewer_binding"]["viewer_operation_id"].startswith("VR-"))
        self.assertEqual("RECORDED", result["viewer_binding"]["binding_transition_custody_status"])
        self.assertEqual(1, len(_FakeCustody.events))
        event = _FakeCustody.events[0]
        self.assertEqual(4, event["sequence"])
        self.assertEqual("VIEWER_BOUND", event["event_type"])
        self.assertFalse(event["authority_granted"])
        self.assertEqual("node:viewer:001", event["details"]["viewer_binding"]["viewer_node_id"])
        self.assertFalse(event["details"]["source_run_mutated"])

    @patch("stegverse.viewer_bound_operations._components", side_effect=_fake_components)
    @patch("stegverse.viewer_bound_operations.reconstruct_sovereign")
    def test_reconstruction_appends_viewer_binding_event(self, reconstruct, _components):
        reconstruct.return_value = {
            "manifest_receipt_id": "MR-" + "B" * 64,
            "operation_id": "OP-RECONSTRUCT-ABC",
            "operation_receipt_ids": ["R0", "R1", "R2", "R3"],
        }
        result = reconstruct_for_viewer(
            "MR-" + "B" * 64,
            viewer_node_id="node:viewer:002",
            custody_db=":memory:",
        )
        self.assertEqual("stegverse.viewer-bound-reconstruction.v1", result["schema"])
        self.assertTrue(result["viewer_binding"]["viewer_operation_id"].startswith("VC-"))
        event = _FakeCustody.events[0]
        self.assertEqual("RECONSTRUCT", event["operation"])
        self.assertEqual("node:viewer:002", event["details"]["viewer_binding"]["viewer_node_id"])
        self.assertFalse(result["original_record_mutated"])
        self.assertFalse(result["consequence_reexecuted"])


if __name__ == "__main__":
    unittest.main()
