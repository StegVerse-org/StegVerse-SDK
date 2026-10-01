"""The dangerous substitute is the one that works.

A principal of the wrong class that is available, well-formed and productive
will file its result under a condition it does not satisfy. These tests hold
the executor and assert it is never called.
"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "stegverse" / "principal_class_conformance.py"


def _load_conformance():
    """Load by file path, as the gate's own workflow does.

    Importing ``stegverse.principal_class_conformance`` would execute the
    package ``__init__``, which pulls in the whole SDK and its runtime
    dependencies. A control that gates a run's starting condition must be able
    to run when those are absent.
    """
    spec = importlib.util.spec_from_file_location(
        "_principal_class_conformance", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_conformance = _load_conformance()

AUTHORITY_BOUNDARY = _conformance.AUTHORITY_BOUNDARY
CLASS_ESTABLISHED = _conformance.CLASS_ESTABLISHED
CLASS_UNAVAILABLE = _conformance.CLASS_UNAVAILABLE
CONFORMS = _conformance.CONFORMS
DECLARATION_ALTERED = _conformance.DECLARATION_ALTERED
EXECUTION_WITHHELD = _conformance.EXECUTION_WITHHELD
PREREQUISITE_NOT_ESTABLISHED = _conformance.PREREQUISITE_NOT_ESTABLISHED
REFUSED = _conformance.REFUSED
RECEIPT_SCHEMA = _conformance.RECEIPT_SCHEMA
SUBSTITUTE_REFUSED = _conformance.SUBSTITUTE_REFUSED
UNDECLARED_CLASS_OFFERED = _conformance.UNDECLARED_CLASS_OFFERED
PrincipalClassRefused = _conformance.PrincipalClassRefused
declare_required_principal_class = _conformance.declare_required_principal_class
execute_under_principal_class_conformance = (
    _conformance.execute_under_principal_class_conformance)
resolve_principal_class = _conformance.resolve_principal_class

GOAL = "SDK-PRINCIPAL-CLASS-CONFORMANCE-001"
REQUIRED = "DECLARED_RESIDENT_PRINCIPAL"
ALTERNATE = "EVENT_EPHEMERAL_WORKER"
PREREQS = ("DECLARED_ENDPOINT_ESTABLISHED", "RUNTIME_IDENTITY_BOUND")


def declaration(**overrides):
    base = dict(
        declaration_id="REQUIRED-PRINCIPAL-CLASS-001",
        required_class=REQUIRED,
        prerequisites=PREREQS,
        recognized_classes=(REQUIRED, ALTERNATE),
    )
    base.update(overrides)
    return declare_required_principal_class(**base)


def predicates(result):
    return [item["failed_predicate"] for item in result["refusals"]]


class DeclarationTest(unittest.TestCase):
    def test_the_declaration_is_frozen_and_forbids_substitution(self):
        declared = declaration()
        self.assertTrue(declared["declaration_is_frozen"])
        self.assertFalse(declared["substitution_permitted"])
        self.assertTrue(declared["declaration_sha256"].startswith("sha256:"))

    def test_the_required_class_is_always_recognized(self):
        declared = declaration(recognized_classes=(ALTERNATE,))
        self.assertIn(REQUIRED, declared["recognized_principal_classes"])

    def test_a_declaration_without_a_required_class_is_refused(self):
        with self.assertRaises(PrincipalClassRefused):
            declaration(required_class="  ")


class ConformanceTest(unittest.TestCase):
    def test_the_declared_class_with_its_prerequisites_conforms(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": PREREQS},
        ], owning_existing_goal=GOAL)
        self.assertEqual(result["state"], CONFORMS)
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertTrue(result["required_principal_class_established"])
        self.assertEqual(result["refusals"], [])
        self.assertNotIn("receipt_sha256", result)

    def test_a_reachable_alternate_is_reported_but_does_not_fail_conformance(self):
        """A substitution route that exists is worth recording before it is taken."""
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": PREREQS},
            {"principal_class": ALTERNATE, "available": True},
        ], owning_existing_goal=GOAL)
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertEqual(result["reachable_alternate_classes"], [ALTERNATE])
        self.assertEqual(result["refused_substitute_classes"], [])


class RefusalTest(unittest.TestCase):
    def test_required_class_down_with_an_alternate_up_refuses_both_by_name(self):
        """The acceptance criterion: a receipt naming the prerequisite and the substitute."""
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": False},
            {"principal_class": ALTERNATE, "available": True,
             "runtime_ref": "worker-under-lease"},
        ], owning_existing_goal=GOAL)
        self.assertEqual(result["state"], REFUSED)
        self.assertEqual(result["disposition"], "FAIL_CLOSED")
        self.assertEqual(sorted(set(predicates(result))),
                         sorted({CLASS_UNAVAILABLE, SUBSTITUTE_REFUSED}))
        self.assertEqual(result["missing_prerequisites"], sorted(PREREQS))
        self.assertEqual(result["refused_substitute_classes"], [ALTERNATE])
        self.assertEqual(result["receipt_schema"], RECEIPT_SCHEMA)
        self.assertTrue(result["receipt_sha256"].startswith("sha256:"))
        refused = next(r for r in result["refusals"]
                       if r["failed_predicate"] == SUBSTITUTE_REFUSED)
        self.assertEqual(refused["refused_runtime_ref"], "worker-under-lease")
        self.assertEqual(refused["in_place_of_required_class"], REQUIRED)

    def test_the_required_class_not_offered_at_all_is_distinguished(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": ALTERNATE, "available": True},
        ], owning_existing_goal=GOAL)
        unavailable = next(r for r in result["refusals"]
                           if r["failed_predicate"] == CLASS_UNAVAILABLE)
        self.assertFalse(unavailable["required_class_offered"])

    def test_the_required_class_present_with_a_missing_prerequisite_is_not_that_class(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": [PREREQS[0]]},
        ], owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [PREREQUISITE_NOT_ESTABLISHED])
        entry = result["refusals"][0]
        self.assertEqual(entry["missing_prerequisites"], [PREREQS[1]])
        self.assertEqual(entry["established_prerequisites"], [PREREQS[0]])

    def test_no_substitute_is_invented_when_none_is_available(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": False},
            {"principal_class": ALTERNATE, "available": False},
        ], owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [CLASS_UNAVAILABLE])
        self.assertEqual(result["refused_substitute_classes"], [])
        self.assertEqual(result["reachable_alternate_classes"], [])

    def test_an_unrecognized_class_is_reported_not_inferred_into_the_set(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": PREREQS},
            {"principal_class": "NEVER_DECLARED", "available": False},
        ], owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [UNDECLARED_CLASS_OFFERED])
        self.assertEqual(result["refusals"][0]["offered_principal_class"],
                         "NEVER_DECLARED")

    def test_a_duplicate_candidate_class_is_refused(self):
        with self.assertRaises(PrincipalClassRefused):
            resolve_principal_class(declaration(), [
                {"principal_class": REQUIRED, "available": True},
                {"principal_class": REQUIRED, "available": False},
            ], owning_existing_goal=GOAL)


class RefusalIsNotJudgementTest(unittest.TestCase):
    def test_refusing_a_substitute_does_not_invalidate_it(self):
        """An alternate may be a legitimate principal for its own declaration."""
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": False},
            {"principal_class": ALTERNATE, "available": True},
        ], owning_existing_goal=GOAL)
        refused = next(r for r in result["refusals"]
                       if r["failed_predicate"] == SUBSTITUTE_REFUSED)
        self.assertTrue(refused["substitute_may_run_under_its_own_declaration"])
        self.assertFalse(refused["substitute_result_may_materialize_into_this_lane"])
        self.assertFalse(AUTHORITY_BOUNDARY["refusal_invalidates_the_substitute_itself"])


class AlteredDeclarationTest(unittest.TestCase):
    def test_an_altered_declaration_fails_before_any_resolution(self):
        altered = dict(declaration())
        altered["required_prerequisites"] = []
        result = resolve_principal_class(altered, [
            {"principal_class": REQUIRED, "available": True},
        ], owning_existing_goal=GOAL)
        self.assertEqual(predicates(result), [DECLARATION_ALTERED])
        self.assertFalse(result["declaration_intact"])
        self.assertFalse(result["required_principal_class_established"])


class ExecutionOrderingTest(unittest.TestCase):
    def test_a_refused_class_never_reaches_the_executor(self):
        calls = []
        result = execute_under_principal_class_conformance(declaration(), [
            {"principal_class": REQUIRED, "available": False},
            {"principal_class": ALTERNATE, "available": True},
        ], owning_existing_goal=GOAL, principal_executor=calls.append)
        self.assertEqual(calls, [])
        self.assertFalse(result["principal_executed"])
        self.assertEqual(result["execution_state"], EXECUTION_WITHHELD)

    def test_a_conforming_class_executes_once(self):
        calls = []

        def executor(resolution):
            calls.append(resolution)
            return "PRINCIPAL-EXECUTION-REF-1"

        result = execute_under_principal_class_conformance(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": PREREQS},
        ], owning_existing_goal=GOAL, principal_executor=executor)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["disposition"], "ALLOW")
        self.assertTrue(result["principal_executed"])
        self.assertEqual(result["execution_reference"], "PRINCIPAL-EXECUTION-REF-1")

    def test_no_executor_is_refused_rather_than_skipped(self):
        with self.assertRaises(PrincipalClassRefused):
            execute_under_principal_class_conformance(
                declaration(), [], owning_existing_goal=GOAL, principal_executor=None)


class DispositionContractTest(unittest.TestCase):
    def test_every_refusal_names_its_repair_and_owner(self):
        """ECOSYSTEM_STATE_TRANSITION_DISPOSITION_INVARIANT: no bare blocker."""
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": False},
            {"principal_class": ALTERNATE, "available": True},
            {"principal_class": "NEVER_DECLARED", "available": True},
        ], owning_existing_goal=GOAL)
        self.assertTrue(result["refusals"])
        for entry in result["refusals"]:
            with self.subTest(failed_predicate=entry["failed_predicate"]):
                for field in ("failed_predicate", "required_evidence_or_repair",
                              "retry_entrypoint", "owning_existing_goal", "disposition"):
                    self.assertTrue(entry.get(field), field)
                self.assertEqual(entry["owning_existing_goal"], GOAL)

    def test_an_owning_goal_is_required(self):
        with self.assertRaises(PrincipalClassRefused):
            resolve_principal_class(declaration(), [], owning_existing_goal="")

    def test_resolution_claims_nothing(self):
        result = resolve_principal_class(declaration(), [
            {"principal_class": REQUIRED, "available": True,
             "established_prerequisites": PREREQS},
        ], owning_existing_goal=GOAL)
        self.assertEqual(result["authority_boundary"], AUTHORITY_BOUNDARY)
        self.assertEqual(result["authority_effect"], "NONE_CLASS_RESOLUTION_ONLY")
        for claim, value in AUTHORITY_BOUNDARY.items():
            with self.subTest(claim=claim):
                self.assertFalse(value)


class StdlibOnlyTest(unittest.TestCase):
    def test_it_runs_with_sdk_runtime_dependencies_absent(self):
        """The gate installs nothing, so a package import here would go red on requests."""
        script = textwrap.dedent(f"""
            import importlib.util
            try:
                import requests
            except ImportError:
                pass
            else:
                raise SystemExit("requests should have been unavailable")
            spec = importlib.util.spec_from_file_location("m", {str(MODULE_PATH)!r})
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            declared = module.declare_required_principal_class(
                declaration_id="D-1", required_class="C", prerequisites=["P"],
                recognized_classes=["C"])
            refused = module.resolve_principal_class(
                declared, [{{"principal_class": "C", "available": False}}],
                owning_existing_goal="G-1")
            assert refused["disposition"] == "FAIL_CLOSED", refused
            allowed = module.resolve_principal_class(
                declared,
                [{{"principal_class": "C", "available": True,
                   "established_prerequisites": ["P"]}}],
                owning_existing_goal="G-1")
            assert allowed["disposition"] == "ALLOW", allowed
            print("STDLIB_ONLY_OK")
        """)
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "requests.py").write_text(
                'raise ImportError("deliberately unavailable")\n', encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-c", script], capture_output=True, text=True,
                env={"PYTHONPATH": tmp, "PATH": "/usr/bin:/bin"}, cwd=str(ROOT))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("STDLIB_ONLY_OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
