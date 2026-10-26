"""Deterministic tests for safety-critical scaffold behaviour."""
import tempfile
import unittest
from pathlib import Path

from venture_lab.db import Store
from venture_lab.engine import parse_proposal


class ProposalTests(unittest.TestCase):
    def test_valid_proposal(self):
        result = parse_proposal(
            '{"title":"Improve evidence labels","rationale":"Separate claims from evidence",'
            '"change_type":"prompt","validation_plan":"Run ten fixed cases"}'
        )
        self.assertEqual(result["title"], "Improve evidence labels")

    def test_rejects_missing_field(self):
        with self.assertRaises(ValueError):
            parse_proposal('{"title":"x","rationale":"y"}')

    def test_rejects_obvious_safety_bypass(self):
        with self.assertRaises(ValueError):
            parse_proposal(
                '{"title":"Disable safety checks","rationale":"x","change_type":"prompt",'
                '"validation_plan":"y"}'
            )

    def test_store_records_run_and_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / "test.sqlite3")
            run_id = store.create_run("test goal")
            proposal_id = store.add_proposal(run_id, {
                "title": "Test", "rationale": "Reason", "change_type": "prompt",
                "validation_plan": "Run tests",
            })
            store.finish_run(run_id, "completed", "done")
            self.assertEqual(len(store.runs()), 1)
            self.assertEqual(store.proposals()[0]["id"], proposal_id)


if __name__ == "__main__":
    unittest.main()
