import csv
import tempfile
import unittest
from pathlib import Path

from src.data.extract_brand import extract_amazon_conversations, is_english_text


class TestBrandExtraction(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a small synthetic twcs.csv
        self.csv_path = self.temp_path / "twcs_sample.csv"
        rows = [
            # tweet_id, author_id, inbound, created_at, text, response_tweet_id, in_response_to_tweet_id
            # 1: AmazonHelp reply to customer 2
            ["1", "AmazonHelp", "False", "Tue Oct 31 22:10:47 +0000 2017", "@1001 We would like to help with your order. Please DM us.", "", "2"],
            # 2: Customer 1001 inquiry to AmazonHelp
            ["2", "1001", "True", "Tue Oct 31 22:00:00 +0000 2017", "@AmazonHelp where is my package? It is late.", "1", ""],
            # 3: AppleSupport reply to customer 4 (should NOT be extracted)
            ["3", "AppleSupport", "False", "Tue Oct 31 22:15:00 +0000 2017", "@1002 Please update iOS.", "", "4"],
            # 4: Customer 1002 inquiry to AppleSupport (should NOT be extracted)
            ["4", "1002", "True", "Tue Oct 31 22:12:00 +0000 2017", "@AppleSupport my iPhone is frozen.", "3", ""],
            # 5: AmazonHelp Japanese reply (should be filtered out by language check)
            ["5", "AmazonHelp", "False", "Tue Oct 31 22:20:00 +0000 2017", "@1003 こんにちは、アマゾン公式です。", "", "6"],
            # 6: Customer Japanese query
            ["6", "1003", "True", "Tue Oct 31 22:18:00 +0000 2017", "@AmazonHelp 届かない", "5", ""],
            # 7: AmazonHelp reply to non-existent tweet ID 999 (broken relationship)
            ["7", "AmazonHelp", "False", "Tue Oct 31 22:25:00 +0000 2017", "@1004 Please send tracking number.", "", "999"],
            # 8: Short English customer message to AmazonHelp
            ["8", "AmazonHelp", "False", "Tue Oct 31 22:30:00 +0000 2017", "@1005 Can you confirm your order number?", "", "9"],
            ["9", "1005", "True", "Tue Oct 31 22:28:00 +0000 2017", "@AmazonHelp Order late", "8", ""],
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

        self.sample_csv = self.temp_path / "amazonhelp_conversations.csv"
        self.inspection_csv = self.temp_path / "amazonhelp_sample.csv"
        self.report_md = self.temp_path / "brand_selection.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_is_english_text(self):
        self.assertTrue(is_english_text("@AmazonHelp where is my package? It is late."))
        self.assertTrue(is_english_text("@AmazonHelp Order late"))
        self.assertFalse(is_english_text("@AmazonHelp こんにちは、アマゾン公式です。"))
        self.assertFalse(is_english_text(""))

    def test_extract_amazon_conversations(self):
        stats = extract_amazon_conversations(
            raw_dataset_path=self.csv_path,
            sample_output_path=self.sample_csv,
            inspection_output_path=self.inspection_csv,
            report_output_path=self.report_md,
            sample_size=10,
            inspection_size=5,
        )

        self.assertTrue(self.sample_csv.exists())
        self.assertTrue(self.inspection_csv.exists())
        self.assertTrue(self.report_md.exists())

        # Check extracted records
        with open(self.sample_csv, mode="r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))

        # Expected: exactly 2 valid pairs:
        # Pair 1: Customer 2 -> Brand 1
        # Pair 2: Customer 9 -> Brand 8 (short message preserved)
        self.assertEqual(len(records), 2)

        # Verify expected fields
        expected_fields = {
            "conversation_id",
            "customer_tweet_id",
            "brand_tweet_id",
            "customer_message",
            "brand_response",
            "created_at",
            "source_tweet_ids",
        }
        self.assertEqual(set(records[0].keys()), expected_fields)

        # Check that customer messages and brand responses are present
        cust_ids = {r["customer_tweet_id"] for r in records}
        self.assertIn("2", cust_ids)
        self.assertIn("9", cust_ids)
        # AppleSupport customer 4 must NOT be present
        self.assertNotIn("4", cust_ids)

        # Check markdown report contents
        report_text = self.report_md.read_text(encoding="utf-8")
        self.assertIn("# Selected Brand", report_text)
        self.assertIn("AmazonHelp", report_text)
        self.assertIn("# Why AmazonHelp", report_text)
        self.assertIn("# Extraction Results", report_text)
        self.assertIn("# Data Quality", report_text)


if __name__ == "__main__":
    unittest.main()
