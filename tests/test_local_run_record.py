"""SDK-internal local run record: stdlib, non-authoritative, caller-located (SDK-MR-A-VALIDATION-CUSTODY-001)."""
from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from stegverse import sovereign_validation_runtime as runtime
from stegverse.local_run_record import LocalRunRecordError, LocalRunRecordStore

ROOT = Path(__file__).resolve().parents[1]
STDLIB_ONLY = {"__future__", "hashlib", "json", "os", "sqlite3", "contextlib", "pathlib", "typing"}


def _assert_non_authoritative(case: unittest.TestCase, row: dict) -> None:
    case.assertEqual(row["authority_effect"], "NONE")
    case.assertIs(row["completes_transition"], False)
    case.assertIs(row["gates_transition"], False)
    text = json.dumps({k: v for k, v in row.items() if k not in {"event", "evidence_package"}})
    case.assertNotIn('"ALLOW"', text)
    case.assertNotIn('"RECORDED"', text)


class LocalRunRecordStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "run-record.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_no_default_location(self):
        for location in (None, "", "   "):
            with self.assertRaises(LocalRunRecordError):
                LocalRunRecordStore(location)  # type: ignore[arg-type]
        with self.assertRaises(runtime.SovereignValidationError):
            runtime.local_run_store(None)

    def test_writes_only_at_the_caller_supplied_location(self):
        LocalRunRecordStore(self.path)
        self.assertEqual([p.name for p in Path(self._tmp.name).iterdir()], ["run-record.db"])

    def test_route_events_chain_and_read_back(self):
        store = LocalRunRecordStore(self.path)
        first = store.record_route_event({"route_manifest_id": "RM-1", "stop": "a"})
        second = store.record_route_event({"route_manifest_id": "RM-1", "stop": "b"})
        self.assertIsNone(first["previous_event_sha256"])
        self.assertEqual(second["previous_event_sha256"], first["event_sha256"])
        events = store.route_events("RM-1")
        self.assertEqual([e["route_receipt_id"] for e in events], [first["route_receipt_id"], second["route_receipt_id"]])
        for row in events:
            _assert_non_authoritative(self, row)

    def test_register_is_append_only_and_keeps_reader_fields(self):
        store = LocalRunRecordStore(self.path)
        package = {"manifest_receipt_id": "mr-1", "manifest": {"metadata": {}}}
        retained = store.register(package)
        self.assertEqual(store.register(package)["record_sha256"], retained["record_sha256"])
        with self.assertRaises(LocalRunRecordError):
            store.register({**package, "changed": True})
        record = store.evidence_package("MR-1")
        self.assertEqual(record["manifest_receipt_id"], "MR-1")
        self.assertEqual(record["evidence_package"], package)
        self.assertEqual(record["master_record_sha256"], record["record_sha256"])
        _assert_non_authoritative(self, record)

    def test_operation_events_and_reconstruction_never_complete(self):
        store = LocalRunRecordStore(self.path)
        store.record_route_event({"route_manifest_id": "RM-2"})
        store.register({"manifest_receipt_id": "MR-2", "ecosystem_route_link": {"route_manifest_id": "RM-2"},
                        "execution_observation": {"evaluation": {"disposition": "ALLOW"}}})
        event = store.record_operation_event({"source_manifest_receipt_id": "MR-2", "operation_id": "OP-1",
                                              "sequence": 0, "event_type": "REQUESTED"})
        self.assertTrue(event["event_receipt_id"].startswith("LOE-"))
        _assert_non_authoritative(self, event)
        artifact = store.reconstruct("MR-2")
        self.assertIs(artifact["consequence_reexecuted"], False)
        self.assertIs(artifact["original_record_mutated"], False)
        self.assertIs(artifact["local_route_chain_intact"], True)
        self.assertEqual(artifact["original_disposition"], "ALLOW")  # the run's governance disposition, as evidence
        self.assertIs(artifact["completes_transition"], False)
        self.assertEqual(artifact["authority_effect"], "NONE")

    def test_module_is_stdlib_only_and_names_no_ledger(self):
        source = (ROOT / "stegverse" / "local_run_record.py").read_text(encoding="utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertLessEqual(imported, STDLIB_ONLY)
        self.assertNotIn("Ledger", source.replace("not a ledger", ""))


class MasterRecordsPackageRemovedTests(unittest.TestCase):
    def test_runtime_does_not_import_the_master_records_package(self):
        for rel in ("stegverse/sovereign_validation_runtime.py", "stegverse/governance_fallback.py"):
            source = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("services.manifest_receipt_custody", source, rel)
            self.assertNotIn("build_master_records_submission", source, rel)

    def test_governed_test_extra_no_longer_pins_master_records(self):
        self.assertNotIn("stegverse-master-records", (ROOT / "pyproject.toml").read_text(encoding="utf-8"))


# --- Sovereign lane run through the local run record, with stand-in canonical components ---

class _Model:
    def __init__(self, body):
        self.body = dict(body)
        self.candidate = SimpleNamespace(action=body["candidate"]["action"])

    @classmethod
    def model_validate(cls, body):
        return cls(body)

    def model_dump(self, **_kwargs):
        return dict(self.body)


class _Carrier:
    def __init__(self, manifest, sink):
        self.manifest, self.sink = manifest, sink

    def run(self, payload, handlers):
        active = {"route_manifest_id": self.manifest["route_manifest_id"], "transaction_id": "TX-1",
                  "receipt_chain_head": None}
        self.sink({"stop": "ingress"})
        handlers["stegcore"](active, payload)
        last = self.sink({"stop": "return"})
        return {"route_manifest_id": active["route_manifest_id"], "transaction_id": "TX-1",
                "receipt_chain_head": last["event"]["event_sha256"]}


class _Registry:
    def register(self, result):
        self.result = result
        return SimpleNamespace(manifest_receipt_id="MR-" + "A" * 64, transaction_id=result.transaction_id)

    def evidence_package(self, _rid):
        return {"manifest": {"metadata": self.result.metadata},
                "execution_observation": self.result.execution_observation}


def _run_tx(request, executor, **kwargs):
    return SimpleNamespace(transaction_id=kwargs["transaction_id"], chain_verified=True, metadata=kwargs["metadata"],
                           execution_observation={"evaluation": {"disposition": "ALLOW"}, "result": executor()})


def _fake_components():
    return (_Carrier, lambda **_k: {"route_manifest_id": "RM-FAKE"}, lambda: "route", _Registry, _Model,
            lambda request: SimpleNamespace(disposition="ALLOW"), object, _run_tx)


def _fake_prov(request, host_identity, _governance_request):
    resolved = {"route_id": runtime.CANONICAL_PRODUCTION_ROUTE_ID, "route_declaration_hash": "sha256:route",
                "state_graph_adapter_binding": "stegverse.manifest_state_transition_adapters.derive_governance_state_graph"}
    return {"route_id": resolved["route_id"], "state_binding_hash": "sha256:state",
            "execution_host_identity": host_identity}, resolved


class SovereignLaneLocalRunRecordTests(unittest.TestCase):
    def test_run_replay_reconstruct_use_the_sdk_local_run_record(self):
        request = json.loads((ROOT / "inspection" / "examples" / "governed-test-request.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(runtime, "_components", _fake_components), \
                patch.object(runtime, "_prov", _fake_prov):
            db = Path(tmp) / "lane.db"
            result = runtime.run_sovereign_validation(request, custody_db=db)
            rid = result["manifest_receipt_id"]
            local = result["local_run_store"]
            self.assertEqual(local["status"], "LOCAL_EVIDENCE_ONLY")
            self.assertEqual(local["authority_effect"], "NONE")
            self.assertIs(local["completes_transition"], False)
            self.assertIs(result["sovereign_completion"], False)
            self.assertEqual(result["organization_ledger_completion"]["disposition"], "FAIL_CLOSED")
            self.assertEqual(result["route_transition_count"], 2)
            self.assertTrue(all(r.startswith("LRR-") for r in result["route_receipt_ids"]))

            replay = runtime.replay_sovereign(rid, custody_db=db)
            self.assertIs(replay["deterministic_disposition_match"], True)
            self.assertEqual(replay["operation_transition_custody_status"], "RECORDED")
            reconstruction = runtime.reconstruct_sovereign(rid, custody_db=db)
            self.assertEqual(reconstruction["manifest_receipt_id"], rid)
            self.assertIs(reconstruction["consequence_reexecuted"], False)
            self.assertIs(reconstruction["local_route_chain_intact"], True)
            self.assertEqual(len(LocalRunRecordStore(db).route_events(result["route_manifest_id"])), 2)

    def test_cli_requires_a_caller_supplied_location(self):
        with self.assertRaises(SystemExit):
            runtime.main(["replay", "MR-X"])


if __name__ == "__main__":
    unittest.main()
