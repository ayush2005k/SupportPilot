# Selected Brand

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
| **Total AmazonHelp Outbound Tweets** | 169,840 | Total rows where `author_id == 'AmazonHelp'` and `inbound == 'False'` |
| **Outbound Replies Indexed (Pass 1)** | 124,269 | Unique parent customer tweet IDs referenced by AmazonHelp |
| **Total Clean Interaction Pairs Extracted** | 114,891 | Valid, verified customer inquiry $\rightarrow$ AmazonHelp response pairs |
| **Sample Dataset Records Retained** | 20,000 | Saved to `data/sample/amazonhelp_conversations.csv` for downstream pipeline |
| **Inspection Sample Records** | 100 | Saved to `reports/amazonhelp_sample.csv` for human review |
| **Total Records Filtered / Discarded** | 42,353 | Total non-support, foreign, or broken records filtered |

### Reasons for Discarding Records
* **Non-English / Multilingual Replies (41,384)**: Amazon operates global Twitter handles; non-Latin (Japanese/CJK) and non-English European inquiries were filtered to preserve linguistic integrity for the English evaluation harness.
* **Unreferenced Parent Tweets (408)**: Brand replies referencing parent tweet IDs that did not exist in the raw dataset (due to Twitter privacy/deletion).
* **Missing Inbound Customer Flag (8)**: Outbound brand tweets referencing other brand accounts rather than customer inquiries.
* **Empty Text (0)**: Malformed rows or media-only tweets lacking text bodies.
* **Root Outbound Broadcasts (553)**: Brand announcements lacking an `in_response_to_tweet_id`.

---

# Data Quality

1. **Missing Responses**: All retained records are strictly 1-to-1 customer inquiry $\rightarrow$ brand response pairs. No customer inquiries with missing brand responses are included in the sample.
2. **Duplicate Handling**: Deduplication was enforced on unique customer tweet IDs (`customer_tweet_id`). Where multiple follow-up tweets occurred, the primary initial support response was retained.
3. **Broken Relationships**: Verified that every `customer_tweet_id` exists in `twcs.csv` and is flagged as an inbound customer message.
4. **Short-Message Handling**: Short customer messages (e.g. *"Where is my stuff?"*, *"Order late"*) were **deliberately preserved** rather than pruned, ensuring the golden evaluation set can accurately evaluate model robustness on ambiguous or context-sparse inputs.

---

### Verification
* Processed Dataset: `data/sample/amazonhelp_conversations.csv` (20,000 rows)
* Inspection Sample: `reports/amazonhelp_sample.csv` (100 rows)
* Raw Dataset Integrity: `data/raw/twcs.csv` remains unmodified.
