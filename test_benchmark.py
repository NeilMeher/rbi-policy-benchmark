import unittest
from datetime import date
from urllib.parse import urlsplit

import benchmark as b


class BenchmarkTests(unittest.TestCase):
    def test_manifest(self):
        rows = b.read_data()
        dates = [date.fromisoformat(row["date"]) for row in rows]
        self.assertEqual(dates, sorted(set(dates)))
        for row in rows:
            self.assertEqual(row["change_bps"], row["rate_bps"] - row["previous_bps"])
            self.assertEqual(urlsplit(row["source"]).scheme, "https")
            self.assertIn("rbi.org.in", urlsplit(row["source"]).hostname)
            self.assertLess(row["evidence"], len(row["digest"]))

    def test_ambiguous_rate_abstains(self):
        row = dict(digest=["The repo rate went from 6% to 5%."], previous_bps=600)
        self.assertEqual(b.predict(row, b.rule)["action"], "unknown")

    def test_pilot(self):
        result = b.evaluate(b.read_data(), pilot=True)
        self.assertEqual((result["train"], result["test"]), (7, 3))
