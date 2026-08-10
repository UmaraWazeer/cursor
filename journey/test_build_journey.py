#!/usr/bin/env python3
"""Checks that the losslessness guarantees actually fail the build when broken.

Run with:
    python3 journey/test_build_journey.py
"""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

import yaml

from build_journey import Journey, check, render_csv, render_l0, render_l1, render_l2, render_miro_dsl

EXAMPLE = Path(__file__).parent / "journey.example.yaml"


def load() -> dict:
    return yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))


class ExampleIsValid(unittest.TestCase):
    def test_example_passes_every_check(self):
        report = check(Journey(load()))
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_declared_counts_match_the_data(self):
        journey = Journey(load())
        self.assertEqual(journey.object_count(), journey.expected["objects"])
        self.assertEqual(journey.connector_count(), journey.expected["connectors"])

    def test_every_layer_renders(self):
        journey = Journey(load())
        for render in (render_l0, render_l1, render_l2, render_miro_dsl):
            self.assertTrue(render(journey).strip(), f"{render.__name__} produced nothing")

    def test_register_carries_every_annotation_verbatim(self):
        journey = Journey(load())
        register = render_l2(journey)
        for note in journey.annotations:
            self.assertIn(note["text"].strip(), register, f"{note['id']} missing from register")


class LossIsRejected(unittest.TestCase):
    """Each case removes or corrupts something that must not be lost silently."""

    def assert_rejected(self, mutate) -> str:
        data = copy.deepcopy(load())
        mutate(data)
        report = check(Journey(data))
        self.assertTrue(report.errors, "expected at least one error")
        return " ".join(report.errors)

    def test_dropped_object_is_caught_by_count(self):
        self.assertIn("Object count mismatch", self.assert_rejected(lambda d: d["annotations"].pop()))

    def test_dropped_connector_is_caught_by_count(self):
        self.assertIn(
            "Connector count mismatch",
            self.assert_rejected(lambda d: d["cross_links"].clear()),
        )

    def test_unplaced_object_needs_a_reason(self):
        self.assertIn(
            "unanchored_reason",
            self.assert_rejected(lambda d: d["annotations"][-1].pop("unanchored_reason")),
        )

    def test_annotation_must_have_verbatim_text(self):
        self.assertIn(
            "verbatim wording is required",
            self.assert_rejected(lambda d: d["annotations"][0].__setitem__("text", "   ")),
        )

    def test_type_must_be_in_the_vocabulary(self):
        self.assertIn(
            "expected one of",
            self.assert_rejected(lambda d: d["annotations"][0].__setitem__("type", "sticky")),
        )

    def test_annotation_cannot_point_at_a_missing_step(self):
        self.assertIn(
            "undeclared step",
            self.assert_rejected(lambda d: d["annotations"][0].__setitem__("step", "S99")),
        )

    def test_step_cannot_point_at_a_missing_phase(self):
        self.assertIn(
            "undeclared phase",
            self.assert_rejected(lambda d: d["steps"][0].__setitem__("phase", "P99")),
        )

    def test_step_cannot_point_at_a_missing_lane(self):
        self.assertIn(
            "undeclared lane",
            self.assert_rejected(lambda d: d["steps"][0].__setitem__("lanes", ["L99"])),
        )

    def test_branch_must_leave_from_a_real_step(self):
        self.assertIn(
            "leaves from undeclared step",
            self.assert_rejected(lambda d: d["branches"][0].__setitem__("from_step", "S42")),
        )

    def test_duplicate_ids_are_rejected(self):
        self.assertIn(
            "Duplicate step id",
            self.assert_rejected(lambda d: d["steps"][1].__setitem__("id", "S1")),
        )


class SyntheticSpine(unittest.TestCase):
    """A synthetic spine consolidates cards, so only annotations reconcile."""

    def base(self) -> dict:
        return {
            "title": "t",
            "synthetic_spine": True,
            "expected_counts": {"objects": 2},
            "phases": [{"id": "P1", "name": "P1"}],
            "lanes": [{"id": "L1", "name": "L1"}],
            "steps": [
                {"id": "S1", "phase": "P1", "name": "one", "lanes": ["L1"]},
                {"id": "S2", "phase": "P1", "name": "two", "lanes": ["L1"]},
            ],
            "annotations": [
                {"id": "N1", "step": "S1", "type": "info", "text": "a"},
                {"id": "N2", "step": "S2", "type": "info", "text": "b"},
            ],
        }

    def test_steps_do_not_count_toward_board_objects(self):
        report = check(Journey(self.base()))
        self.assertEqual(report.errors, [])

    def test_annotation_miscount_is_still_caught(self):
        data = self.base()
        data["annotations"].pop()
        report = check(Journey(data))
        self.assertTrue(any("Object count mismatch" in e for e in report.errors))

    def test_connector_mismatch_is_advisory_not_fatal(self):
        data = self.base()
        data["expected_counts"]["connectors"] = 999
        report = check(Journey(data))
        self.assertEqual(report.errors, [])
        self.assertTrue(any("advisory" in w for w in report.warnings))


class MissingCountsWarn(unittest.TestCase):
    def test_absent_expected_counts_warns_rather_than_passing_silently(self):
        data = copy.deepcopy(load())
        data.pop("expected_counts")
        report = check(Journey(data))
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 2)


class CsvRegister(unittest.TestCase):
    def test_csv_has_one_row_per_annotation(self):
        import csv
        import tempfile

        journey = Journey(load())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "register.csv"
            render_csv(journey, path)
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), len(journey.annotations))


if __name__ == "__main__":
    unittest.main(verbosity=2)
