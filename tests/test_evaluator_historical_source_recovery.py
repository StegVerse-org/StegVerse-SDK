"""Exact historic source restoration; no claim of live admitted runtime."""
from __future__ import annotations
import hashlib,json,tempfile,unittest
from pathlib import Path
from stegverse import evaluator_historical_source_recovery as R

def request():
    return {
        "task_id":R.REQUEST_TASK,
        "state":"REQUESTED",
        "manifest_ref":R.MANIFEST_REL.as_posix(),
        "historical_source_artifact_id":R.ARTIFACT_ID,
        "historical_manifest_sha256":R.ORIGINAL_MANIFEST_SHA256,
    }

class HistoricalSourceRecoveryTests(unittest.TestCase):
    def test_exact_original_manifest_and_transition_reconstructed(self):
        manifest=R.rebuild_original_manifest()
        self.assertEqual(hashlib.sha256(R._exact_bytes(manifest)).hexdigest(),R.ORIGINAL_MANIFEST_SHA256)
        self.assertEqual(manifest["extensions"]["security_posture_request"]["authority_effect"],"NONE_REQUEST_INPUT_ONLY")

    def test_stages_only_for_existing_task_request_and_never_grants_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt=R.materialize_historical_source(runtime_root=Path(tmp),request=request())
            self.assertEqual(receipt["state"],"HISTORICAL_SOURCE_STAGED_NOT_RUNTIME_PROVEN")
            self.assertFalse(receipt["governed_execution_observed"])
            self.assertFalse(receipt["master_records_closure_observed"])
            self.assertFalse(receipt["tvc_authorization_verified"])
            self.assertEqual(hashlib.sha256((Path(tmp)/R.MANIFEST_REL).read_bytes()).hexdigest(),R.ORIGINAL_MANIFEST_SHA256)
            self.assertEqual(json.loads((Path(tmp)/R.SOURCE_RECEIPT_REL).read_text()),receipt)
            self.assertEqual(R.materialize_historical_source(runtime_root=Path(tmp),request=request()),receipt)

    def test_rejects_mismatched_request_without_writing_a_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            value=request(); value["historical_manifest_sha256"]="0"*64
            with self.assertRaisesRegex(ValueError,"historical_evaluator_source_request_binding_invalid"):
                R.materialize_historical_source(runtime_root=Path(tmp),request=value)
            self.assertFalse((Path(tmp)/R.MANIFEST_REL).exists())

    def test_rejects_conflicting_existing_manifest_without_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/R.MANIFEST_REL
            path.parent.mkdir(parents=True)
            path.write_text('{"forged":true}')
            with self.assertRaisesRegex(ValueError,"evaluator_manifest_existing_bytes_mismatch"):
                R.materialize_historical_source(runtime_root=Path(tmp),request=request())
            self.assertEqual(path.read_text(),'{"forged":true}')

    def test_no_runtime_root_is_created_as_a_side_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            absent=Path(tmp)/"not-an-admitted-root"
            with self.assertRaises((FileNotFoundError,ValueError)):
                R.materialize_historical_source(runtime_root=absent,request=request())
            self.assertFalse(absent.exists())

if __name__=="__main__":unittest.main()
