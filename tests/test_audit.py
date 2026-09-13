import csv
import tempfile
import unittest
from pathlib import Path

from src.analysis.audit_dataset import format_bytes, run_audit


class TestDatasetAudit(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a small synthetic twcs.csv matching the exact real schema
        self.csv_path = self.temp_path / "twcs_sample.csv"
        rows = [
            # tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
            # 1: Brand reply to 2
            ["1", "AppleSupport", "False", "Tue Oct 31 22:10:47 +0000 2017", "@1001 We can help with your iPhone battery.", "2", "2"],
            # 2: Customer query to AppleSupport
            ["2", "1001", "True", "Tue Oct 31 22:00:00 +0000 2017", "@AppleSupport my battery dies quickly", "1", ""],
            # 3: Brand reply to 4
            ["3", "AmazonHelp", "False", "Tue Oct 31 22:15:00 +0000 2017", "@1002 Please provide order ID", "", "4"],
            # 4: Customer query to AmazonHelp
            ["4", "1002", "True", "Tue Oct 31 22:12:00 +0000 2017", "@AmazonHelp where is my package", "3", ""],
            # 5: Customer query without reply
            ["5", "1003", "True", "Tue Oct 31 22:20:00 +0000 2017", "@AppleSupport screen is cracked", "", ""],
            # 6: Brand root broadcast (no in_response_to)
            ["6", "AppleSupport", "False", "Tue Oct 31 22:25:00 +0000 2017", "New iOS update available now.", "", ""],
        ]

        with open(self.csv_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "tweet_id",
                "author_id",
                "inbound",
                "created_at",
                "text",
                "response_tweet_id",
                "in_response_to_tweet_id",
            ])
            writer.writerows(rows)

        self.candidates_csv = self.temp_path / "brand_candidates.csv"
        self.audit_md = self.temp_path / "dataset_audit.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_format_bytes(self):
        self.assertEqual(format_bytes(500), "500.00 B")
        self.assertEqual(format_bytes(2048), "2.00 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 5), "5.00 MB")

    def test_run_audit_metrics(self):
        summary = run_audit(
            dataset_path=self.csv_path,
            candidates_csv_path=self.candidates_csv,
            audit_md_path=self.audit_md,
            top_n=5,
        )

        self.assertEqual(summary["total_tweets"], 6)
        self.assertEqual(summary["inbound_tweets"], 3)
        self.assertEqual(summary["outbound_tweets"], 3)
        self.assertEqual(summary["unique_authors"], 5)  # AppleSupport, AmazonHelp, 1001, 1002, 1003
        self.assertEqual(summary["unique_outbound_authors"], 2)  # AppleSupport, AmazonHelp
        self.assertEqual(summary["unique_inbound_authors"], 3)

        # Verify candidate CSV was generated
        self.assertTrue(self.candidates_csv.exists())
        with open(self.candidates_csv, mode="r", encoding="utf-8") as f:
            candidates = list(csv.DictReader(f))
            self.assertEqual(len(candidates), 2)
            brand_map = {c["brand"]: c for c in candidates}
            self.assertIn("AppleSupport", brand_map)
            self.assertIn("AmazonHelp", brand_map)
            # AppleSupport has 2 outbound, 1 reply to customer (tweet 1 -> 2), 1 broadcast (tweet 6)
            self.assertEqual(int(brand_map["AppleSupport"]["outbound_tweets"]), 2)
            self.assertEqual(int(brand_map["AppleSupport"]["usable_interactions"]), 1)
            # AmazonHelp has 1 outbound, 1 reply to customer (tweet 3 -> 4)
            self.assertEqual(int(brand_map["AmazonHelp"]["outbound_tweets"]), 1)
            self.assertEqual(int(brand_map["AmazonHelp"]["usable_interactions"]), 1)

        # Verify markdown was generated with ending requirement
        self.assertTrue(self.audit_md.exists())
        md_text = self.audit_md.read_text(encoding="utf-8")
        self.assertIn("# Dataset Overview", md_text)
        self.assertIn("# Candidate Brands", md_text)
        self.assertIn("# Brand Selection Criteria", md_text)
        self.assertIn("Candidate brands identified. Final brand selection requires human review.", md_text)


if __name__ == "__main__":
    unittest.main()
