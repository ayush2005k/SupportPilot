import csv
import tempfile
import unittest
from pathlib import Path

from src.analysis.discover_intents import (
    INTENT_DEFINITIONS,
    classify_message,
    discover_and_document_intents,
)


class TestIntentDiscovery(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create synthetic conversation dataset covering distinct intents
        self.sample_csv = self.temp_path / "sample_conversations.csv"
        rows = [
            # 1: Delivery Delay
            ["conv_1", "1", "101", "Where is my package? It was supposed to arrive yesterday.", "We are checking your tracking.", "Tue Oct 31", "1;101"],
            # 2: False Delivery / Missing Package
            ["conv_2", "2", "102", "It says delivered but I never received anything at my door.", "Please check with neighbors while we look into this.", "Tue Oct 31", "2;102"],
            # 3: Damaged item
            ["conv_3", "3", "103", "The item arrived completely shattered and broken.", "Please visit the online return center for a replacement.", "Tue Oct 31", "3;103"],
            # 4: Refund
            ["conv_4", "4", "104", "I returned the shoes two weeks ago and haven't received my refund.", "Refunds take 3-5 business days to post to your bank.", "Tue Oct 31", "4;104"],
            # 5: Account access
            ["conv_5", "5", "105", "My account has been placed on hold and I cannot sign in.", "Please respond to the email from our account specialist.", "Tue Oct 31", "5;105"],
            # 6: Cancellation
            ["conv_6", "6", "106", "I ordered by mistake, please cancel my order now.", "You can cancel from Your Orders before it ships.", "Tue Oct 31", "6;106"],
            # 7: Prime subscription
            ["conv_7", "7", "107", "Please cancel my prime membership auto renew and refund me.", "You can end Prime in membership settings.", "Tue Oct 31", "7;107"],
            # 8: Payment issue
            ["conv_8", "8", "108", "There is an unknown unauthorized charge on my credit card.", "Please reach us via phone or chat to verify this.", "Tue Oct 31", "8;108"],
            # 9: Digital / device
            ["conv_9", "9", "109", "My Firestick has an error code and prime video won't stream.", "Try clearing the cache and restarting your Fire TV.", "Tue Oct 31", "9;109"],
            # 10: Service complaint
            ["conv_10", "10", "110", "Your delivery driver threw my package in the mud. Disgraceful service!", "We are very sorry. Please share details so we can report this.", "Tue Oct 31", "10;110"],
        ]

        with open(self.sample_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "conversation_id",
                "customer_tweet_id",
                "brand_tweet_id",
                "customer_message",
                "brand_response",
                "created_at",
                "source_tweet_ids",
            ])
            writer.writerows(rows)

        self.candidates_csv = self.temp_path / "intent_candidates.csv"
        self.examples_csv = self.temp_path / "intent_examples.csv"
        self.taxonomy_md = self.temp_path / "intent_taxonomy.md"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_taxonomy_intent_count(self):
        # We target 8-12 intents; exactly 11 defined
        self.assertEqual(len(INTENT_DEFINITIONS), 11)

    def test_classify_core_messages(self):
        self.assertEqual(
            classify_message("Where is my package? It is late."),
            "delivery_status_and_delay",
        )
        self.assertEqual(
            classify_message("Tracking says delivered but I never received it"),
            "missing_package_false_delivery",
        )
        self.assertEqual(
            classify_message("The screen is shattered and broken"),
            "damaged_defective_or_wrong_item",
        )
        self.assertEqual(
            classify_message("Where is my refund for the returned book?"),
            "refund_inquiry",
        )
        self.assertEqual(
            classify_message("My account is on hold and I can't sign in"),
            "account_access_and_security",
        )

    def test_discover_and_document_intents(self):
        results = discover_and_document_intents(
            sample_csv_path=self.sample_csv,
            candidates_csv_path=self.candidates_csv,
            examples_csv_path=self.examples_csv,
            taxonomy_md_path=self.taxonomy_md,
        )

        self.assertEqual(results["total_records"], 10)
        self.assertTrue(self.candidates_csv.exists())
        self.assertTrue(self.examples_csv.exists())
        self.assertTrue(self.taxonomy_md.exists())

        # Check taxonomy markdown content
        md_text = self.taxonomy_md.read_text(encoding="utf-8")
        self.assertIn("# AmazonHelp Intent Taxonomy", md_text)
        self.assertIn("## 1. Intent Distribution Analysis", md_text)
        self.assertIn("## 2. Intent Specifications", md_text)
        self.assertIn("## 3. Final Recommendation & Design Rationale", md_text)
        self.assertIn("delivery_status_and_delay", md_text)
        self.assertIn("missing_package_false_delivery", md_text)


if __name__ == "__main__":
    unittest.main()
