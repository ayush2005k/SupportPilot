# Dataset Overview

## File
* **File Path**: `data/raw/twcs.csv`
* **File Size**: 492.58 MB (516,508,641 bytes)
* **Processing Method**: 2-pass streaming chunk processing via standard library CSV reader (zero in-memory table bloat).
* **Audit Duration**: 68.3 seconds.

## Schema
Actual columns present in `twcs.csv`:
1. `tweet_id`: Unique integer string identifier for the tweet.
2. `author_id`: Alphanumeric handle for support brands (e.g. `AppleSupport`, `AmazonHelp`) or anonymized numeric ID for customers (e.g. `115712`).
3. `inbound`: Boolean string (`'True'` or `'False'`).
4. `created_at`: Raw RFC 2822 timestamp (e.g. `Tue Oct 31 22:10:47 +0000 2017`).
5. `text`: Customer inquiry or brand response text (including `@mentions` and URLs).
6. `response_tweet_id`: Comma-separated list of tweet IDs that responded to this tweet (empty for terminal replies).
7. `in_response_to_tweet_id`: ID of the prior tweet to which this tweet directly replies (empty for thread-initiating tweets).

## Tweet Counts
* **Total Tweets**: 2,811,774
* **Inbound (Customer) Tweets**: 1,537,843 (54.69%)
* **Outbound (Brand/Company) Tweets**: 1,273,931 (45.31%)

## Authors
* **Total Unique Authors**: 702,777
* **Unique Inbound Authors (Customers)**: 702,669
* **Unique Outbound Authors (Support Brands)**: 108

## Inbound vs. Outbound Representation
* `inbound == 'True'`: Customer message sent towards a brand or general mention.
* `inbound == 'False'`: Official response authored by a company support handle.

## Missing Data Statistics
| Column Name | Total Rows | Missing Rows | Missing % | Data Type / Role |
| :--- | :--- | :--- | :--- | :--- |
| `tweet_id` | 2,811,774 | 0 | 0.00% | Integer ID (Primary Key) |
| `author_id` | 2,811,774 | 0 | 0.00% | Alphanumeric Handle / User ID |
| `inbound` | 2,811,774 | 0 | 0.00% | Boolean String |
| `created_at` | 2,811,774 | 0 | 0.00% | Timestamp String |
| `text` | 2,811,774 | 0 | 0.00% | Text Body |
| `response_tweet_id` | 2,811,774 | 1,040,629 | 37.01% | Relational Pointer (Nullable on terminal leaves) |
| `in_response_to_tweet_id` | 2,811,774 | 794,335 | 28.25% | Relational Pointer (Nullable on thread roots) |

*Note: The missing values in `response_tweet_id` (37.01%) represent conversational leaf tweets that received no further reply. The missing values in `in_response_to_tweet_id` (28.25%) represent conversation starter/root tweets.*

## Conversation Relationships
Conversations are threaded using two reciprocal relational pointers:
* `in_response_to_tweet_id`: Points backwards to the immediate predecessor tweet.
* `response_tweet_id`: Points forwards to the subsequent response(s).
* **Direct Usable Pairs**: A support interaction pair is formed when a brand outbound tweet (`inbound == False`) has an `in_response_to_tweet_id` referencing an existing inbound customer tweet (`inbound == True`). Across the entire dataset, **99.5%** of outbound brand tweets are direct responses to a previous tweet.

---

# Candidate Brands

The top 25 customer support brands ranked by outbound volume and verified customer interactions:

| Rank | Brand | Outbound Tweets | Outbound Replies | Reply % | Inbound Mentions | Answered Inquiries | Usable Interaction Pairs |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **AmazonHelp** | 169,840 | 169,287 | 99.7% | 135,160 | 154,976 | **168,814** |
| 2 | **AppleSupport** | 106,860 | 106,719 | 99.9% | 97,896 | 106,623 | **106,646** |
| 3 | **Uber_Support** | 56,270 | 56,261 | 100.0% | 46,624 | 55,182 | **56,160** |
| 4 | **SpotifyCares** | 43,265 | 43,243 | 100.0% | 31,353 | 41,585 | **43,092** |
| 5 | **Delta** | 42,253 | 42,197 | 99.9% | 44,836 | 36,134 | **42,114** |
| 6 | **Tesco** | 38,573 | 38,501 | 99.8% | 33,964 | 25,282 | **38,468** |
| 7 | **AmericanAir** | 36,764 | 36,598 | 99.5% | 49,516 | 36,457 | **36,531** |
| 8 | **TMobileHelp** | 34,317 | 34,287 | 99.9% | 21,964 | 33,837 | **34,215** |
| 9 | **comcastcares** | 33,031 | 33,007 | 99.9% | 23,278 | 30,369 | **32,921** |
| 10 | **British_Airways** | 29,361 | 29,315 | 99.8% | 30,856 | 24,084 | **29,290** |
| 11 | **SouthwestAir** | 28,977 | 28,889 | 99.7% | 35,106 | 28,285 | **28,828** |
| 12 | **VirginTrains** | 27,817 | 27,522 | 98.9% | 37,396 | 26,272 | **27,416** |
| 13 | **Ask_Spectrum** | 25,860 | 25,807 | 99.8% | 23,676 | 24,976 | **25,617** |
| 14 | **XboxSupport** | 24,557 | 24,341 | 99.1% | 28,124 | 20,213 | **23,235** |
| 15 | **sprintcare** | 22,381 | 22,335 | 99.8% | 13,746 | 20,026 | **22,209** |
| 16 | **hulu_support** | 21,872 | 21,783 | 99.6% | 18,615 | 21,468 | **21,681** |
| 17 | **sainsburys** | 19,466 | 19,417 | 99.8% | 22,862 | 17,717 | **19,399** |
| 18 | **GWRHelp** | 19,364 | 19,294 | 99.6% | 27,021 | 18,506 | **19,237** |
| 19 | **AskPlayStation** | 19,098 | 18,694 | 97.9% | 22,263 | 18,650 | **18,675** |
| 20 | **ChipotleTweets** | 18,749 | 18,612 | 99.3% | 21,815 | 18,565 | **18,599** |
| 21 | **VerizonSupport** | 17,966 | 17,851 | 99.4% | 17,929 | 17,534 | **17,805** |
| 22 | **UPSHelp** | 17,817 | 17,772 | 99.8% | 14,653 | 17,601 | **17,762** |
| 23 | **ATVIAssist** | 17,650 | 17,531 | 99.3% | 24,741 | 16,879 | **17,514** |
| 24 | **O2** | 16,212 | 16,091 | 99.2% | 19,435 | 15,952 | **16,069** |
| 25 | **Safaricom_Care** | 16,077 | 15,471 | 96.2% | 17,274 | 13,881 | **15,441** |

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

1. **Sufficient Usable Support Conversations**: The brand must have tens of thousands of clean, verifiable customer inquiry $\rightarrow$ brand response pairs to construct a rich historical retrieval index.
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
