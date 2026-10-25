python - <<'PY' | tee /tmp/served-surface-assertion.json
import importlib.util, json
spec = importlib.util.spec_from_file_location(
    "served_surface_assertion", "stegverse/served_surface_assertion.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

digest = lambda seed: "sha256:" + (seed * 64)[:64]
declaration = module.declare_frozen_surface(
    [{"resource_id": "DECLARED_A", "content_sha256": digest("1")},
     {"resource_id": "DECLARED_B", "content_sha256": digest("2")}],
    declaration_id="CI-FROZEN-SURFACE-001",
    excluded_provenance=["CI-PRIOR-ATTEMPT-LANE"])

emitted = []
report = module.emit_under_served_surface_assertion(
    declaration,
    [{"resource_id": "DECLARED_A", "content_sha256": digest("1")},
     {"resource_id": "DECLARED_B", "content_sha256": digest("2")},
     {"resource_id": "INJECTED", "content_sha256": digest("9")}],
    owning_existing_goal="SDK-SERVED-SURFACE-ASSERTION-001",
    evidence_emitter=emitted.append)

assert emitted == [], "evidence was emitted under a divergent surface"
assert report["disposition"] == "FAIL_CLOSED", report
assert report["evidence_emitted"] is False, report
assert report["evidence_state"] == module.EVIDENCE_WITHHELD, report
assert [d["failed_predicate"] for d in report["divergences"]] == [
    module.EXTRA_SERVED], report
assert report["authority_effect"] == "NONE_SURFACE_COMPARISON_ONLY"

conforming = module.emit_under_served_surface_assertion(
    declaration,
    [{"resource_id": "DECLARED_A", "content_sha256": digest("1")},
     {"resource_id": "DECLARED_B", "content_sha256": digest("2")}],
    owning_existing_goal="SDK-SERVED-SURFACE-ASSERTION-001",
    evidence_emitter=lambda assertion: "CI-EVIDENCE-REF")
assert conforming["disposition"] == "ALLOW", conforming
assert conforming["evidence_emitted"] is True, conforming

print(json.dumps({"injected": report, "conforming": conforming},
                 indent=2, sort_keys=True))
PY
