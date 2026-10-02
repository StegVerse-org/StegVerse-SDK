"""Source-only discovery/CLI parity. These tests never invoke a live receiver."""
from contextlib import redirect_stdout
from io import StringIO
import json
from unittest.mock import patch
import unittest

from stegverse import cli, evaluator_console, manifest_builder
from stegverse.machine_contract import sdk_machine_contract, SUBMISSION_TERMINAL_STEPS
from stegverse.console_manifest_commands import COMMANDS


class MachineContractTests(unittest.TestCase):
    def test_declarations_are_live_not_copied(self):
        with patch.dict(manifest_builder.PROCESSOR_ROUTES, {"future": "uninstalled"}):
            c = sdk_machine_contract()
        self.assertEqual(c["processors"]["future"]["route_id"], "uninstalled")
        self.assertFalse(c["processors"]["future"]["installed"])
        self.assertIn("processor_request", c["builder"]["required_parameters"])

    def test_console_and_machine_projection_are_identical(self):
        for entry in (cli.main, evaluator_console.main):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(entry(["machine-contract"]), 0)
            self.assertEqual(json.loads(output.getvalue()), sdk_machine_contract())
        help_text = cli.build_parser().format_help()
        for name in COMMANDS:
            self.assertIn(name, help_text)

    def test_existing_cli_commands_reach_their_real_parsers(self):
        for entry in (cli.main, evaluator_console.main):
            for args in (["manifest", "build", "--help"], ["external-run", "--help"], ["run-manifest", "--help"]):
                with redirect_stdout(StringIO()), self.assertRaises(SystemExit) as caught:
                    entry(args)
                self.assertEqual(caught.exception.code, 0)

    def test_external_boundary_and_evidence_do_not_promote_runtime(self):
        c = sdk_machine_contract()
        for profile in c["machine_readable_instructions"].values():
            self.assertEqual(profile["steps"][-2:], list(SUBMISSION_TERMINAL_STEPS))
            self.assertFalse(any("INTERLOCK" in step or "INTR" in step for step in profile["steps"]))
            self.assertEqual(profile["interlock_intr"], "INTERNAL_POST_SUBMISSION")
        self.assertFalse(c["local_handoff_proves_receiver_observation"])
        self.assertFalse(c["submission_proves_downstream_completion"])

    def test_projection_does_not_mutate_declarations(self):
        c = sdk_machine_contract()
        c["return_depths"].clear()
        self.assertTrue(sdk_machine_contract()["return_depths"])
