#!/usr/bin/env python3
"""Folded groups keep their original push / pull_request path filters (python tools/tasks/selection_selftest.py).

A group whose original filter does not match the event's changed files records NOT_SELECTED
(a run, never a skipped job); a group whose filter matches runs its steps.
"""
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run_catalog", ROOT / "tools/tasks/run_catalog.py")
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)
CATALOG = json.loads((ROOT / "tools/tasks/task_catalog.json").read_text(encoding="utf-8"))
GROUPS = {g["id"]: g for g in CATALOG["groups"]}


def cell(event, files, gid):
    return [c for c in rc.matrix(event, files)["include"] if c["group"] == gid][0]["selected"]


class GlobTests(unittest.TestCase):
    def test_star_stops_at_slash_and_double_star_does_not(self):
        self.assertTrue(rc.glob_regex("data/*.json").match("data/a.json"))
        self.assertFalse(rc.glob_regex("data/*.json").match("data/x/a.json"))
        self.assertTrue(rc.glob_regex("data/**").match("data/x/y/a.json"))
        self.assertTrue(rc.glob_regex("**/a.json").match("a.json"))

    def test_later_negation_removes_an_earlier_match(self):
        self.assertFalse(rc.path_matches(["docs/**", "!docs/skip.md"], "docs/skip.md"))

    def test_paths_ignore_runs_unless_every_file_is_ignored(self):
        filt = {"paths_ignore": ["docs/**"]}
        self.assertFalse(rc.filter_selects(filt, ["docs/a.md"]))
        self.assertTrue(rc.filter_selects(filt, ["docs/a.md", "src/a.py"]))

    def test_unknown_changed_files_select_everything(self):
        self.assertTrue(rc.filter_selects({"paths": ["only/this"]}, None))


class GroupSelectionTests(unittest.TestCase):
    def test_unrelated_change_selects_only_groups_whose_filter_matches_it(self):
        unrelated = "zz-unrelated-selection-probe/none.txt"
        for gid, group in GROUPS.items():
            for event, filt in (group.get("path_filters") or {}).items():
                if "pull_request" not in group["events"] and event == "pull_request":
                    continue
                if "paths" in filt:
                    expected = any(rc.path_matches(filt["paths"], f) for f in [unrelated])
                else:
                    expected = not any(rc.glob_regex(pat).match(unrelated) for pat in filt["paths_ignore"])
                self.assertEqual(cell(event, [unrelated], gid), "true" if expected else "false", (gid, event))
                self.assertEqual(cell(event, None, gid), "true", (gid, event))

    def test_groups_without_a_pull_request_filter_always_run_on_pull_requests(self):
        for gid, group in GROUPS.items():
            filters = group.get("path_filters") or {}
            if "pull_request" in group["events"] and "pull_request" not in filters:
                self.assertEqual(cell("pull_request", ["README.md"], gid), "true", gid)

    def test_every_filtered_group_is_selected_by_each_of_its_own_literal_paths(self):
        for gid, group in GROUPS.items():
            for event, filt in (group.get("path_filters") or {}).items():
                for pattern in filt.get("paths", []):
                    if pattern.startswith("!") or any(ch in pattern for ch in "*?+["):
                        continue
                    self.assertEqual(cell(event, [pattern], gid), "true", (gid, event, pattern))

    def test_filters_match_the_folded_originals(self):
        # stdlib only: a folded original has a paths / paths-ignore filter under `on:` exactly when its group
        # carries path_filters for that event (the values are copied from the original's own `on:` block).
        for gid, group in GROUPS.items():
            wf = Path((group.get("source") or {}).get("workflow", "")).name
            original = ROOT / "tools/tasks/folded" / wf
            if not wf or not original.is_file():
                continue
            text = original.read_text(encoding="utf-8")
            on_block = re.split(r"^jobs:", text, maxsplit=1, flags=re.M)[0]
            for event in group["events"]:
                m = re.search(r"^  %s:\s*\n((?:    .*\n|\s*\n)*)" % event, on_block, re.M)
                has = bool(m and re.search(r"^    (paths|paths-ignore):", m.group(1), re.M))
                self.assertEqual(has, event in (group.get("path_filters") or {}), (gid, event))


DISPATCHER = (ROOT / ".github/workflows/validation-dispatcher.yml").read_text(encoding="utf-8")
CARRIED = CATALOG.get("carried_job_selection") or {}


def job_block(job):
    m = re.search(r"^  %s:\n((?:(?:    |\s*\n).*\n?)*)" % re.escape(job), DISPATCHER, re.M)
    return m.group(1) if m else ""


class CarriedJobTests(unittest.TestCase):
    """Carried dispatcher jobs are selected by their original filters without a job-level `if` (that would
    be a SKIPPED job): the job always runs, records SELECTED / NOT_SELECTED, and its other steps are gated."""

    def test_plan_emits_the_selection(self):
        self.assertIn("carried: ${{ steps.carried.outputs.carried }}", DISPATCHER)
        self.assertIn("run_catalog.py carried --event", DISPATCHER)

    def test_no_job_level_if_and_every_other_step_is_gated(self):
        self.assertTrue(CARRIED)
        for job in CARRIED:
            block = job_block(job)
            self.assertTrue(block, job)
            self.assertIn("    needs: plan\n", block, job)
            self.assertIsNone(re.search(r"^    if:", block, re.M), job)
            gate = "fromJSON(needs.plan.outputs.carried)['%s']" % job
            steps = re.split(r"^      - ", block, flags=re.M)[1:]
            self.assertEqual(sum(1 for st in steps if "Record the original-path selection" in st), 1, job)
            for st in steps:
                if "Record the original-path selection" in st:
                    self.assertNotRegex(st, r"(?m)^        if:", job)
                else:
                    self.assertIn(gate, st, (job, st.splitlines()[0]))

    def test_selection_follows_the_original_events_and_paths(self):
        for job, spec in CARRIED.items():
            self.assertTrue((ROOT / spec["workflow"]).is_file(), job)
            text = (ROOT / spec["workflow"]).read_text(encoding="utf-8")
            on_block = re.split(r"^jobs:", text, maxsplit=1, flags=re.M)[0]
            for event in ("pull_request", "push"):
                present = bool(re.search(r"^  %s:" % event, on_block, re.M))
                self.assertEqual(present, event in spec["events"], (job, event))
                if event not in spec["events"]:
                    self.assertFalse(rc.carried(event, ["README.md"])[job], (job, event))
                    continue
                m = re.search(r"^  %s:\s*\n((?:    .*\n|\s*\n)*)" % event, on_block, re.M)
                has = bool(m and re.search(r"^    (paths|paths-ignore):", m.group(1), re.M))
                self.assertEqual(has, event in spec["path_filters"], (job, event))
                if event in spec["path_filters"]:
                    self.assertFalse(rc.carried(event, ["zz-unrelated-selection-probe/none.txt"])[job], (job, event))
                    self.assertTrue(rc.carried(event, None)[job], (job, event))
                    for pattern in spec["path_filters"][event].get("paths", []):
                        if not pattern.startswith("!") and not any(ch in pattern for ch in "*?+["):
                            self.assertTrue(rc.carried(event, [pattern])[job], (job, event, pattern))
                else:
                    self.assertTrue(rc.carried(event, ["README.md"])[job], (job, event))


if __name__ == "__main__":
    unittest.main()
