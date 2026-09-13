#!/usr/bin/env python3
"""SupportPilot - Brand Extraction Module for AmazonHelp.

This module extracts, cleans, and pairs customer messages with official AmazonHelp
responses from the raw Customer Support on Twitter dataset (data/raw/twcs.csv).
It processes data in streaming chunks without loading the entire 5.1 GB dataset
into memory, applies rigorous data cleaning, and outputs:
1. data/sample/amazonhelp_conversations.csv (primary project sample dataset)
2. reports/amazonhelp_sample.csv (human-readable inspection subset of 100 cases)
3. reports/brand_selection.md (brand rationale, extraction statistics, data quality)
"""

import argparse
import csv
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

# CJK Ideographs, Hiragana, Katakana, Hangul, and Arabic scripts
NON_LATIN_PATTERN = re.compile(
    r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF\u0600-\u06FF]"
)

# Core English stopwords and common support tokens to ensure language fidelity
ENGLISH_INDICATIVE_WORDS = {
    "the", "to", "you", "your", "please", "we", "is", "our", "for", "have",
    "with", "us", "order", "help", "dm", "link", "reach", "here", "item",
    "delivery", "account", "amazon", "prime", "package", "delay", "refund",
    "track", "tracking", "received", "card", "card", "service", "support",
    "can", "my", "me", "i", "not", "it", "on", "at", "be", "this", "from"
}


def is_english_text(text: str) -> bool:
    """Heuristic check to ensure customer and brand messages are primarily English."""
    if NON_LATIN_PATTERN.search(text):
        return False
    # Check word intersection
    tokens = set(re.findall(r"[a-z]+", text.lower()))
    if not tokens:
        return False
    return bool(tokens.intersection(ENGLISH_INDICATIVE_WORDS))


def extract_amazon_conversations(
    raw_dataset_path: Path,
    sample_output_path: Path,
    inspection_output_path: Path,
    report_output_path: Path,
    sample_size: int = 20000,
    inspection_size: int = 100,
    random_seed: int = 42,
) -> dict:
    """Stream twcs.csv to extract and clean AmazonHelp customer-brand interaction pairs."""
    if not raw_dataset_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {raw_dataset_path}")

    start_time = time.time()
    print(f"[*] Starting extraction for AmazonHelp from: {raw_dataset_path}")

    # Pass 1: Collect AmazonHelp outbound replies and index their target parent tweet IDs
    print("[*] Pass 1: Indexing AmazonHelp outbound responses...")
    total_outbound_amazon = 0
    outbound_without_parent = 0
    outbound_non_english = 0
    outbound_empty_text = 0

    # parent_tweet_id -> list of brand response dicts
    brand_replies_by_parent = {}

    with open(raw_dataset_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            author = row.get("author_id", "").strip()
            inbound_val = row.get("inbound", "").strip().lower()

            if author == "AmazonHelp" and inbound_val == "false":
                total_outbound_amazon += 1
                brand_text = row.get("text", "").strip()
                brand_tweet_id = row.get("tweet_id", "").strip()
                parent_id = row.get("in_response_to_tweet_id", "").strip()
                created_at = row.get("created_at", "").strip()

                if not brand_text:
                    outbound_empty_text += 1
                    continue

                if not parent_id:
                    outbound_without_parent += 1
                    continue

                if not is_english_text(brand_text):
                    outbound_non_english += 1
                    continue

                try:
                    parent_int = int(parent_id)
                except ValueError:
                    continue

                if parent_int not in brand_replies_by_parent:
                    brand_replies_by_parent[parent_int] = {
                        "brand_tweet_id": brand_tweet_id,
                        "brand_response": brand_text,
                        "brand_created_at": created_at,
                    }

    pass1_time = time.time() - start_time
    target_parent_ids = set(brand_replies_by_parent.keys())
    print(
        f"[*] Pass 1 complete in {pass1_time:.1f}s. Indexed {len(target_parent_ids):,} "
        f"unique parent targets from {total_outbound_amazon:,} AmazonHelp tweets."
    )

    # Pass 2: Stream raw dataset to match parent customer tweets
    print("[*] Pass 2: Streaming dataset to extract customer messages...")
    pass2_start = time.time()

    matched_pairs = []
    customer_empty_text = 0
    customer_non_english = 0
    customer_not_inbound = 0
    seen_customer_ids = set()

    with open(raw_dataset_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tweet_id_str = row.get("tweet_id", "").strip()
            if not tweet_id_str:
                continue

            try:
                tweet_id_int = int(tweet_id_str)
            except ValueError:
                continue

            if tweet_id_int in target_parent_ids:
                inbound_val = row.get("inbound", "").strip().lower()
                if inbound_val != "true":
                    customer_not_inbound += 1
                    continue

                if tweet_id_int in seen_customer_ids:
                    continue
                seen_customer_ids.add(tweet_id_int)

                customer_text = row.get("text", "").strip()
                if not customer_text:
                    customer_empty_text += 1
                    continue

                if not is_english_text(customer_text):
                    customer_non_english += 1
                    continue

                brand_data = brand_replies_by_parent[tweet_id_int]
                customer_created_at = row.get("created_at", "").strip()
                in_resp_to = row.get("in_response_to_tweet_id", "").strip()

                # Conversation ID: root tweet ID if thread initiated here, or traceable thread parent
                conv_id = f"conv_{in_resp_to}" if in_resp_to else f"conv_{tweet_id_str}"
                source_ids = f"{tweet_id_str};{brand_data['brand_tweet_id']}"

                matched_pairs.append({
                    "conversation_id": conv_id,
                    "customer_tweet_id": tweet_id_str,
                    "brand_tweet_id": brand_data["brand_tweet_id"],
                    "customer_message": customer_text,
                    "brand_response": brand_data["brand_response"],
                    "created_at": customer_created_at or brand_data["brand_created_at"],
                    "source_tweet_ids": source_ids,
                })

    pass2_time = time.time() - pass2_start
    total_time = time.time() - start_time
    total_matched = len(matched_pairs)

    print(
        f"[*] Pass 2 complete in {pass2_time:.1f}s. Extracted {total_matched:,} "
        f"clean customer -> AmazonHelp interaction pairs."
    )

    # Deterministic sampling to maintain a high-quality, reproducible sample
    rng = random.Random(random_seed)
    if sample_size and sample_size < total_matched:
        # Sort chronologically / by ID first for stability before shuffling with seed
        matched_pairs.sort(key=lambda x: int(x["customer_tweet_id"]))
        sample_indices = sorted(rng.sample(range(total_matched), sample_size))
        retained_records = [matched_pairs[i] for i in sample_indices]
    else:
        retained_records = matched_pairs

    # Extract human-readable inspection sample (50-100 examples)
    inspection_records = retained_records[: min(inspection_size, len(retained_records))]

    # Save primary sample dataset: data/sample/amazonhelp_conversations.csv
    sample_output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "conversation_id",
        "customer_tweet_id",
        "brand_tweet_id",
        "customer_message",
        "brand_response",
        "created_at",
        "source_tweet_ids",
    ]

    with open(sample_output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(retained_records)
    print(f"[+] Saved primary processed dataset ({len(retained_records):,} pairs) to: {sample_output_path}")

    # Save inspection sample: reports/amazonhelp_sample.csv
    inspection_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(inspection_output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inspection_records)
    print(f"[+] Saved inspection sample ({len(inspection_records):,} pairs) to: {inspection_output_path}")

    # Calculate discard statistics
    discard_not_found = len(target_parent_ids) - len(seen_customer_ids)
    total_discarded = (
        outbound_without_parent
        + outbound_non_english
        + outbound_empty_text
        + customer_empty_text
        + customer_non_english
        + customer_not_inbound
        + discard_not_found
    )

    # Generate reports/brand_selection.md
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    report_content = f"""# Selected Brand

**AmazonHelp**

---

# Why AmazonHelp

AmazonHelp was selected based on the empirical findings of the Phase 2 large-scale dataset audit:

1. **Highest Support Volume**: AmazonHelp is the largest customer support entity in the dataset with **169,840 outbound tweets** and **135,160 inbound customer mentions**.
2. **Superior Linkage Fidelity**: **99.67%** of AmazonHelp's outbound tweets possess a valid `in_response_to_tweet_id`, yielding **168,814 verified direct customer-response linkages**.
3. **Domain Problem Diversity**: Inquiries span package tracking, shipping delays, damaged goods, refund inquiries, subscription billing (Prime), and digital streaming issues (Prime Video, Kindle, Fire TV). This rich problem variety is essential for constructing a non-trivial intent taxonomy.
4. **Actionable Historical Responses**: AmazonHelp's historical replies feature concrete diagnostic instructions, policy references, secure escalation links (DM / customer support URLs), and clear resolution steps, making them ideal for retrieval-grounded generation.
5. **Clear Escalation Scenarios**: Clear operational demarcation between low-risk inquiries that can be automated (tracking instructions, return policies) and high-risk inquiries requiring human escalation (refund authorizations, missing deliveries, fraudulent account charges).

---

# Extraction Results

The raw dataset was streamed in two passes without loading the monolithic 5.1 GB CSV into memory.

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Total AmazonHelp Outbound Tweets** | {total_outbound_amazon:,} | Total rows where `author_id == 'AmazonHelp'` and `inbound == 'False'` |
| **Outbound Replies Indexed (Pass 1)** | {len(target_parent_ids):,} | Unique parent customer tweet IDs referenced by AmazonHelp |
| **Total Clean Interaction Pairs Extracted** | {total_matched:,} | Valid, verified customer inquiry $\\rightarrow$ AmazonHelp response pairs |
| **Sample Dataset Records Retained** | {len(retained_records):,} | Saved to `data/sample/amazonhelp_conversations.csv` for downstream pipeline |
| **Inspection Sample Records** | {len(inspection_records):,} | Saved to `reports/amazonhelp_sample.csv` for human review |
| **Total Records Filtered / Discarded** | {total_discarded:,} | Total non-support, foreign, or broken records filtered |

### Reasons for Discarding Records
* **Non-English / Multilingual Replies ({outbound_non_english + customer_non_english:,})**: Amazon operates global Twitter handles; non-Latin (Japanese/CJK) and non-English European inquiries were filtered to preserve linguistic integrity for the English evaluation harness.
* **Unreferenced Parent Tweets ({discard_not_found:,})**: Brand replies referencing parent tweet IDs that did not exist in the raw dataset (due to Twitter privacy/deletion).
* **Missing Inbound Customer Flag ({customer_not_inbound:,})**: Outbound brand tweets referencing other brand accounts rather than customer inquiries.
* **Empty Text ({outbound_empty_text + customer_empty_text:,})**: Malformed rows or media-only tweets lacking text bodies.
* **Root Outbound Broadcasts ({outbound_without_parent:,})**: Brand announcements lacking an `in_response_to_tweet_id`.

---

# Data Quality

1. **Missing Responses**: All retained records are strictly 1-to-1 customer inquiry $\\rightarrow$ brand response pairs. No customer inquiries with missing brand responses are included in the sample.
2. **Duplicate Handling**: Deduplication was enforced on unique customer tweet IDs (`customer_tweet_id`). Where multiple follow-up tweets occurred, the primary initial support response was retained.
3. **Broken Relationships**: Verified that every `customer_tweet_id` exists in `twcs.csv` and is flagged as an inbound customer message.
4. **Short-Message Handling**: Short customer messages (e.g. *"Where is my stuff?"*, *"Order late"*) were **deliberately preserved** rather than pruned, ensuring the golden evaluation set can accurately evaluate model robustness on ambiguous or context-sparse inputs.

---

### Verification
* Processed Dataset: `data/sample/amazonhelp_conversations.csv` ({len(retained_records):,} rows)
* Inspection Sample: `reports/amazonhelp_sample.csv` ({len(inspection_records):,} rows)
* Raw Dataset Integrity: `data/raw/twcs.csv` remains unmodified.
"""

    with open(report_output_path, mode="w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"[+] Saved brand selection and extraction report to: {report_output_path}")

    stats = {
        "total_outbound_amazon": total_outbound_amazon,
        "indexed_parent_targets": len(target_parent_ids),
        "total_clean_matched": total_matched,
        "retained_sample": len(retained_records),
        "inspection_sample": len(inspection_records),
        "total_discarded": total_discarded,
        "discard_reasons": {
            "outbound_without_parent": outbound_without_parent,
            "outbound_non_english": outbound_non_english,
            "outbound_empty_text": outbound_empty_text,
            "customer_empty_text": customer_empty_text,
            "customer_non_english": customer_non_english,
            "customer_not_inbound": customer_not_inbound,
            "discard_not_found": discard_not_found,
        },
        "first_samples": retained_records[:3],
        "duration_seconds": total_time,
    }
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="SupportPilot - Extract AmazonHelp Support Interactions"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/raw/twcs.csv"),
        help="Path to raw twcs.csv dataset",
    )
    parser.add_argument(
        "--sample-output",
        type=Path,
        default=Path("data/sample/amazonhelp_conversations.csv"),
        help="Output path for processed AmazonHelp sample dataset",
    )
    parser.add_argument(
        "--inspection-output",
        type=Path,
        default=Path("reports/amazonhelp_sample.csv"),
        help="Output path for human-readable inspection sample",
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path("reports/brand_selection.md"),
        help="Output path for brand selection markdown report",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=20000,
        help="Target number of records to retain in sample dataset",
    )
    parser.add_argument(
        "--inspection-size",
        type=int,
        default=100,
        help="Target number of records for inspection sample",
    )
    args = parser.parse_args()

    stats = extract_amazon_conversations(
        raw_dataset_path=args.dataset,
        sample_output_path=args.sample_output,
        inspection_output_path=args.inspection_output,
        report_output_path=args.report_output,
        sample_size=args.sample_size,
        inspection_size=args.inspection_size,
    )

    print()
    print("========================================")
    print("SUPPORTPILOT BRAND EXTRACTION: AmazonHelp")
    print("========================================")
    print(f"Total Outbound AmazonHelp Tweets: {stats['total_outbound_amazon']:,}")
    print(f"Indexed Parent Customer Targets:  {stats['indexed_parent_targets']:,}")
    print(f"Total Clean Matched Pairs:        {stats['total_clean_matched']:,}")
    print(f"Retained Sample Records:          {stats['retained_sample']:,}")
    print(f"Inspection Sample Records:        {stats['inspection_sample']:,}")
    print(f"Total Filtered / Discarded:       {stats['total_discarded']:,}")
    print(f"Execution Time:                   {stats['duration_seconds']:.1f}s")
    print()
    print("Sample Interactions:")
    for idx, s in enumerate(stats["first_samples"], start=1):
        print(f"--- Sample {idx} (Cust ID: {s['customer_tweet_id']} -> Brand ID: {s['brand_tweet_id']}) ---")
        print(f"Customer: {s['customer_message']}")
        print(f"Brand:    {s['brand_response']}")
        print(f"Created:  {s['created_at']}")
    print("========================================")


if __name__ == "__main__":
    main()
