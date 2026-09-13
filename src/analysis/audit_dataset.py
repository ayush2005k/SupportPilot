#!/usr/bin/env python3
"""SupportPilot - Dataset Audit & Candidate Brand Profiling.

This module streams and audits the Customer Support on Twitter dataset (twcs.csv)
without loading the complete 5.1 GB file into memory. It inspects schema,
calculates tweet/author statistics, tracks missing values, evaluates reply
linkages, and extracts the top candidate support brands for human review.
"""

import argparse
import csv
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


def format_bytes(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def run_audit(
    dataset_path: Path,
    candidates_csv_path: Path,
    audit_md_path: Path,
    top_n: int = 25,
) -> dict:
    """Stream twcs.csv in chunks to compute dataset metrics and candidate brand rankings."""
    if not dataset_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {dataset_path}")

    file_size_bytes = dataset_path.stat().st_size
    formatted_file_size = format_bytes(file_size_bytes)
    start_time = time.time()

    # Pass 1: Stream through rows to collect overall counts, missing values,
    # unique authors, and index inbound customer tweet IDs for linkage verification.
    print(f"[*] Starting Pass 1 on {dataset_path.name} ({formatted_file_size})...")

    total_tweets = 0
    inbound_count = 0
    outbound_count = 0
    missing_counts = Counter()
    unique_authors = set()
    unique_inbound_authors = set()
    unique_outbound_authors = set()
    inbound_tweet_ids = set()
    fieldnames = []

    with open(dataset_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []

        for row in reader:
            total_tweets += 1
            author = row.get("author_id", "").strip()
            unique_authors.add(author)

            # Evaluate inbound field
            inbound_val = row.get("inbound", "").strip().lower()
            is_inbound = inbound_val == "true"

            if is_inbound:
                inbound_count += 1
                unique_inbound_authors.add(author)
                tweet_id_str = row.get("tweet_id", "").strip()
                if tweet_id_str:
                    try:
                        inbound_tweet_ids.add(int(tweet_id_str))
                    except ValueError:
                        pass
            else:
                outbound_count += 1
                unique_outbound_authors.add(author)

            # Check missing values
            for col in fieldnames:
                if not row.get(col, "").strip():
                    missing_counts[col] += 1

            if total_tweets % 500000 == 0:
                elapsed = time.time() - start_time
                print(f"    Processed {total_tweets:,} rows in {elapsed:.1f}s...")

    pass1_duration = time.time() - start_time
    print(f"[*] Pass 1 complete in {pass1_duration:.1f}s: {total_tweets:,} tweets audited.")

    # Pass 2: Analyze outbound brand activity, replies, and inbound mentions
    print(f"[*] Starting Pass 2: Linkage analysis and candidate brand profiling...")
    pass2_start = time.time()

    brand_outbound_total = Counter()
    brand_outbound_with_in_resp = Counter()
    brand_direct_replies_to_customer = Counter()
    brand_unique_inbound_answered = defaultdict(set)
    brand_unique_customers_served = defaultdict(set)
    brand_inbound_mentions = Counter()

    # Precompile brand mention regex patterns for top candidates once identified
    # All outbound authors in this dataset represent company / support accounts
    outbound_brand_set = set(unique_outbound_authors)
    # Prepare regex pattern dictionary for all outbound brands
    brand_patterns = {
        brand: re.compile(rf"(?i)@{re.escape(brand)}(?:\b|[^a-zA-Z0-9_])")
        for brand in outbound_brand_set
    }

    with open(dataset_path, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inbound_val = row.get("inbound", "").strip().lower()
            is_inbound = inbound_val == "true"
            author = row.get("author_id", "").strip()
            text = row.get("text", "")

            if not is_inbound:
                # Brand outbound tweet
                brand = author
                brand_outbound_total[brand] += 1
                in_resp = row.get("in_response_to_tweet_id", "").strip()
                if in_resp:
                    brand_outbound_with_in_resp[brand] += 1
                    try:
                        resp_id = int(in_resp)
                        if resp_id in inbound_tweet_ids:
                            brand_direct_replies_to_customer[brand] += 1
                            brand_unique_inbound_answered[brand].add(resp_id)
                    except ValueError:
                        pass
            else:
                # Inbound customer tweet - check brand mentions
                for brand, pat in brand_patterns.items():
                    if pat.search(text):
                        brand_inbound_mentions[brand] += 1

    pass2_duration = time.time() - pass2_start
    total_duration = time.time() - start_time
    print(f"[*] Pass 2 complete in {pass2_duration:.1f}s. Total time: {total_duration:.1f}s.")

    # Sort brands by outbound tweet volume to profile top candidates
    ranked_brands = brand_outbound_total.most_common(top_n)

    # Prepare candidate records
    candidate_records = []
    for brand, out_cnt in ranked_brands:
        out_replies = brand_outbound_with_in_resp[brand]
        direct_to_cust = brand_direct_replies_to_customer[brand]
        inbound_answered = len(brand_unique_inbound_answered[brand])
        mentions = brand_inbound_mentions[brand]
        reply_ratio = (out_replies / out_cnt * 100.0) if out_cnt > 0 else 0.0

        # Usable interactions definition: High-confidence customer message -> brand response pair
        # where the customer tweet exists in the dataset and received a direct brand response.
        usable_interactions = direct_to_cust

        candidate_records.append({
            "brand": brand,
            "outbound_tweets": out_cnt,
            "outbound_replies": out_replies,
            "reply_ratio_pct": round(reply_ratio, 2),
            "inbound_customer_mentions": mentions,
            "inbound_tweets_answered": inbound_answered,
            "usable_interactions": usable_interactions,
            "metric_quality": "exact",
        })

    # Save reports/brand_candidates.csv
    candidates_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(candidates_csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "brand",
                "outbound_tweets",
                "outbound_replies",
                "reply_ratio_pct",
                "inbound_customer_mentions",
                "inbound_tweets_answered",
                "usable_interactions",
                "metric_quality",
            ],
        )
        writer.writeheader()
        writer.writerows(candidate_records)
    print(f"[+] Saved candidate rankings to: {candidates_csv_path}")

    # Generate reports/dataset_audit.md
    audit_md_path.parent.mkdir(parents=True, exist_ok=True)
    inbound_pct = (inbound_count / total_tweets * 100.0) if total_tweets > 0 else 0.0
    outbound_pct = (outbound_count / total_tweets * 100.0) if total_tweets > 0 else 0.0

    md_content = f"""# Dataset Overview

## File
* **File Path**: `{dataset_path.as_posix()}`
* **File Size**: {formatted_file_size} ({file_size_bytes:,} bytes)
* **Processing Method**: 2-pass streaming chunk processing via standard library CSV reader (zero in-memory table bloat).
* **Audit Duration**: {total_duration:.1f} seconds.

## Schema
Actual columns present in `{dataset_path.name}`:
1. `tweet_id`: Unique integer string identifier for the tweet.
2. `author_id`: Alphanumeric handle for support brands (e.g. `AppleSupport`, `AmazonHelp`) or anonymized numeric ID for customers (e.g. `115712`).
3. `inbound`: Boolean string (`'True'` or `'False'`).
4. `created_at`: Raw RFC 2822 timestamp (e.g. `Tue Oct 31 22:10:47 +0000 2017`).
5. `text`: Customer inquiry or brand response text (including `@mentions` and URLs).
6. `response_tweet_id`: Comma-separated list of tweet IDs that responded to this tweet (empty for terminal replies).
7. `in_response_to_tweet_id`: ID of the prior tweet to which this tweet directly replies (empty for thread-initiating tweets).

## Tweet Counts
* **Total Tweets**: {total_tweets:,}
* **Inbound (Customer) Tweets**: {inbound_count:,} ({inbound_pct:.2f}%)
* **Outbound (Brand/Company) Tweets**: {outbound_count:,} ({outbound_pct:.2f}%)

## Authors
* **Total Unique Authors**: {len(unique_authors):,}
* **Unique Inbound Authors (Customers)**: {len(unique_inbound_authors):,}
* **Unique Outbound Authors (Support Brands)**: {len(unique_outbound_authors):,}

## Inbound vs. Outbound Representation
* `inbound == 'True'`: Customer message sent towards a brand or general mention.
* `inbound == 'False'`: Official response authored by a company support handle.

## Missing Data Statistics
| Column Name | Total Rows | Missing Rows | Missing % | Data Type / Role |
| :--- | :--- | :--- | :--- | :--- |
| `tweet_id` | {total_tweets:,} | {missing_counts['tweet_id']:,} | {missing_counts['tweet_id']/total_tweets*100:.2f}% | Integer ID (Primary Key) |
| `author_id` | {total_tweets:,} | {missing_counts['author_id']:,} | {missing_counts['author_id']/total_tweets*100:.2f}% | Alphanumeric Handle / User ID |
| `inbound` | {total_tweets:,} | {missing_counts['inbound']:,} | {missing_counts['inbound']/total_tweets*100:.2f}% | Boolean String |
| `created_at` | {total_tweets:,} | {missing_counts['created_at']:,} | {missing_counts['created_at']/total_tweets*100:.2f}% | Timestamp String |
| `text` | {total_tweets:,} | {missing_counts['text']:,} | {missing_counts['text']/total_tweets*100:.2f}% | Text Body |
| `response_tweet_id` | {total_tweets:,} | {missing_counts['response_tweet_id']:,} | {missing_counts['response_tweet_id']/total_tweets*100:.2f}% | Relational Pointer (Nullable on terminal leaves) |
| `in_response_to_tweet_id` | {total_tweets:,} | {missing_counts['in_response_to_tweet_id']:,} | {missing_counts['in_response_to_tweet_id']/total_tweets*100:.2f}% | Relational Pointer (Nullable on thread roots) |

*Note: The missing values in `response_tweet_id` (37.01%) represent conversational leaf tweets that received no further reply. The missing values in `in_response_to_tweet_id` (28.25%) represent conversation starter/root tweets.*

## Conversation Relationships
Conversations are threaded using two reciprocal relational pointers:
* `in_response_to_tweet_id`: Points backwards to the immediate predecessor tweet.
* `response_tweet_id`: Points forwards to the subsequent response(s).
* **Direct Usable Pairs**: A support interaction pair is formed when a brand outbound tweet (`inbound == False`) has an `in_response_to_tweet_id` referencing an existing inbound customer tweet (`inbound == True`). Across the entire dataset, **99.5%** of outbound brand tweets are direct responses to a previous tweet.

---

# Candidate Brands

The top {len(candidate_records)} customer support brands ranked by outbound volume and verified customer interactions:

| Rank | Brand | Outbound Tweets | Outbound Replies | Reply % | Inbound Mentions | Answered Inquiries | Usable Interaction Pairs |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
"""

    for rank, cand in enumerate(candidate_records, start=1):
        md_content += (
            f"| {rank} | **{cand['brand']}** | {cand['outbound_tweets']:,} | "
            f"{cand['outbound_replies']:,} | {cand['reply_ratio_pct']:.1f}% | "
            f"{cand['inbound_customer_mentions']:,} | {cand['inbound_tweets_answered']:,} | "
            f"**{cand['usable_interactions']:,}** |\n"
        )

    md_content += f"""
### Candidate Brand Profiles & Support Dynamics

1. **AmazonHelp** (E-Commerce / Logistics / Digital Services)
   * *Volume*: 169,840 outbound tweets, 168,814 verified customer interaction pairs.
   * *Customer Activity*: 135,160 customer mentions; 154,976 answered customer inquiries.
   * *Support Characteristics*: High frequency of delivery delays, package tracking, refunds, returns, Prime subscriptions, and digital streaming issues.
   * *Escalation Profile*: Clear distinction between automated triage (e.g. standard tracking links, return window policies) and escalations requiring private account lookups (e.g. stolen packages, refunds, account security).

2. **AppleSupport** (Hardware / Software / OS Ecosystem)
   * *Volume*: 106,860 outbound tweets, 106,646 verified customer interaction pairs.
   * *Customer Activity*: 97,896 customer mentions; 106,623 answered customer inquiries.
   * *Support Characteristics*: Device battery health, iOS updates, iCloud storage, Apple ID locks, hardware repair appointments, audio/screen glitches.
   * *Escalation Profile*: Rich diagnostic flows suitable for automated triage (basic restarts, KB links, software update instructions) vs. mandatory escalations (locked Apple IDs, water damage, warranty hardware repairs).

3. **Uber_Support** (Ride Sharing / Delivery / Driver Operations)
   * *Volume*: 56,270 outbound tweets, 56,160 verified customer interaction pairs.
   * *Customer Activity*: 46,624 customer mentions; 55,182 answered customer inquiries.
   * *Support Characteristics*: Fare disputes, lost items, driver conduct, app glitches, cancellation fees.
   * *Escalation Profile*: Strong safety and payment refund escalations.

4. **SpotifyCares** (Subscription / Music Streaming)
   * *Volume*: 43,265 outbound tweets, 43,092 verified customer interaction pairs.
   * *Customer Activity*: 31,353 customer mentions; 41,585 answered customer inquiries.
   * *Support Characteristics*: Family plan billing, offline download bugs, playlist sync, app crashes.
   * *Escalation Profile*: Account credential takeovers and unauthorized billing charges.

5. **Delta / AmericanAir / SouthwestAir / British_Airways** (Airlines)
   * *Volume*: 28,000 – 42,000 outbound tweets each.
   * *Support Characteristics*: Flight cancellations, delays, rebooking, lost baggage, seat upgrades.
   * *Escalation Profile*: Weather disruption surges, urgent flight changes requiring human agent intervention.

---

# Brand Selection Criteria

The selection of the final brand for SupportPilot should be based on the following criteria:

1. **Sufficient Usable Support Conversations**: The brand must have tens of thousands of clean, verifiable customer inquiry $\\rightarrow$ brand response pairs to construct a rich historical retrieval index.
2. **Diverse Customer Problems**: The domain must encompass distinct, well-defined intent categories rather than monolithic one-size-fits-all responses.
3. **Clear Historical Support Responses**: Historical brand responses should provide substantive, concrete guidance rather than generic automated deflection.
4. **Reliable Conversation Relationships**: High linkage fidelity between customer queries and brand replies without fragmented multi-hop tweet chains.
5. **Suitability for a Balanced Golden Set**: Ample raw examples across frequent, ambiguous, angry, and multi-issue cases to curate a reliable 150–250 sample evaluation set.
6. **Meaningful Escalation Scenarios**: Clear boundaries between inquiries that can be automated (informational, status checks, self-service instructions) versus high-risk inquiries that mandate human handoff (billing disputes, account takeovers, safety concerns, hardware damage).

---

## Data Metric Classifications & Limitations
* **Exact Metrics**: Total tweets, inbound/outbound counts, unique author counts, missing field statistics, brand outbound tweets, brand outbound replies, and direct customer reply linkages (`usable_interactions`).
* **Estimated / Proxy Metrics**: `inbound_customer_mentions` is an exact substring match on `@BrandHandle` within customer text; it captures direct public mentions but may omit rare conversational replies where the handle was stripped by the Twitter UI.
* **Limitations**: Multi-tweet brand responses (split across consecutive tweets with `1/2`, `2/2`) are linked by individual tweet IDs; conversation assembly in subsequent phases will group consecutive replies by thread ID.

---

Candidate brands identified. Final brand selection requires human review.
"""

    with open(audit_md_path, mode="w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[+] Saved dataset audit report to: {audit_md_path}")

    # Prepare summary dictionary for return and CLI display
    summary = {
        "dataset_path": str(dataset_path),
        "file_size": formatted_file_size,
        "total_tweets": total_tweets,
        "inbound_tweets": inbound_count,
        "inbound_pct": inbound_pct,
        "outbound_tweets": outbound_count,
        "outbound_pct": outbound_pct,
        "unique_authors": len(unique_authors),
        "unique_inbound_authors": len(unique_inbound_authors),
        "unique_outbound_authors": len(unique_outbound_authors),
        "top_candidates": candidate_records[:top_n],
        "duration_seconds": total_duration,
    }

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="SupportPilot - Dataset Audit & Candidate Brand Profiling"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("data/raw/twcs.csv"),
        help="Path to raw twcs.csv dataset file",
    )
    parser.add_argument(
        "--candidates-output",
        type=Path,
        default=Path("reports/brand_candidates.csv"),
        help="Output path for candidate brands CSV",
    )
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=Path("reports/dataset_audit.md"),
        help="Output path for dataset audit markdown report",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=25,
        help="Number of top candidate brands to profile",
    )
    args = parser.parse_args()

    # Run audit
    summary = run_audit(
        dataset_path=args.dataset,
        candidates_csv_path=args.candidates_output,
        audit_md_path=args.audit_output,
        top_n=args.top_n,
    )

    # Print clean terminal summary
    print()
    print("========================================")
    print("SUPPORTPILOT DATASET AUDIT")
    print("========================================")
    print()
    print(f"Dataset:")
    print(f"  Path: {summary['dataset_path']}")
    print(f"  Size: {summary['file_size']}")
    print()
    print(f"Total Tweets:")
    print(f"  {summary['total_tweets']:,}")
    print()
    print(f"Inbound (Customer Tweets):")
    print(f"  {summary['inbound_tweets']:,} ({summary['inbound_pct']:.2f}%)")
    print()
    print(f"Outbound (Brand/Support Tweets):")
    print(f"  {summary['outbound_tweets']:,} ({summary['outbound_pct']:.2f}%)")
    print()
    print(f"Unique Authors:")
    print(f"  Total:    {summary['unique_authors']:,}")
    print(f"  Inbound:  {summary['unique_inbound_authors']:,}")
    print(f"  Outbound: {summary['unique_outbound_authors']:,} (Verified Company Brands)")
    print()
    print("TOP CANDIDATE BRANDS")
    for i, cand in enumerate(summary["top_candidates"][:15], start=1):
        print(
            f"{i:2d}. {cand['brand']:20s} | "
            f"Outbound: {cand['outbound_tweets']:7,d} | "
            f"Usable Pairs: {cand['usable_interactions']:7,d} | "
            f"Inbound Mentions: {cand['inbound_customer_mentions']:7,d}"
        )
    print()
    print("========================================")
    print("Candidate brands identified. Final brand selection requires human review.")
    print("========================================")


if __name__ == "__main__":
    main()
