# SupportPilot 

> **AI Customer Support Decision & Grounded Response System**  
> *Hiver SDE Intern Take-Home Project*

---

## 1. Project Overview

SupportPilot is an evidence-first, reproducible AI customer support copilot engineered for a selected brand from Kaggle's [Customer Support on Twitter (`twcs.csv`)](https://www.kaggle.com/datasets/thoughtvector/customer-support-on-twitter). 

Rather than acting as an ungrounded or hallucinating chatbot, SupportPilot executes a structured decision and response pipeline:
1. **Classify Intent**: Maps incoming customer messages into a curated, brand-specific intent taxonomy.
2. **Retrieve Historical Evidence**: Uses local vector retrieval (embeddings + FAISS) to find top historically resolved customer-brand interactions.
3. **Draft Grounded Reply**: Generates a concise response strictly anchored in historical resolutions without fabricating policies, refund numbers, or unsupported promises.
4. **Determine Escalation**: Evaluates explicit, measurable signals (intent risk, model confidence, retrieval similarity, sensitive keywords) to output `AUTO_HANDLE` or `ESCALATE` with a transparent reason.

---

## 2. Repository Structure

```
SupportPilot/
├── data/
│   ├── raw/
│   │   └── README.md                       # Instructions for acquiring raw twcs.csv
│   ├── sample/                             # Small processed brand dataset (Git-tracked)
│   └── golden/                             # Manually reviewed golden evaluation set (Git-tracked)
├── src/
│   ├── analysis/                           # Dataset audit and candidate brand profiling
│   ├── data/                               # Brand extraction and conversation pair building
│   ├── classification/                     # Intent classifiers (baselines & AI classifier)
│   ├── retrieval/                          # Vector indexing and historical case retrieval
│   ├── generation/                         # Grounded prompt construction & reply generator
│   ├── escalation/                         # Explicit policy logic (AUTO_HANDLE vs ESCALATE)
│   └── evaluation/                         # Evaluation harness, metrics, LLM-as-a-judge
├── reports/
│   └── results/                            # Benchmark tables, failure analysis, audit reports
├── tests/                                  # Pytest automated test suite
├── requirements.txt                        # Project dependencies
├── .env.example                            # Environment variable template
├── .gitignore                              # Strict rules ignoring 5GB raw CSV, env, faiss, logs
└── README.md
```

---

## 3. Setup & Installation

### Prerequisites
* Python 3.10+ (tested on Python 3.11)
* Git

### Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   cd SupportPilot
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to supply your GEMINI_API_KEY
   ```

---

## 4. Dataset Acquisition
The full ~5.1 GB dataset (`twcs.csv`) is intentionally excluded from Git.  
See [`data/raw/README.md`](data/raw/README.md) for instructions on downloading and placing it at `data/raw/twcs.csv`.

---

## 5. Development Phases
The project is built in small, verified, independently runnable phases:
* **Phase 1**: Project Foundation & directory setup *(Current)*
* **Phase 2**: Memory-efficient dataset audit & brand candidate ranking
* **Phase 3**: Brand selection & profile analysis
* **Phase 4**: Extract selected brand conversations
* **Phase 5**: Build customer → brand interaction pairs
* **Phase 6**: Discover & document intent taxonomy
* **Phase 7**: Build manually reviewed golden evaluation set (150–250 samples)
* **Phase 8**: Baseline classifiers (Majority Class & TF-IDF + Logistic Regression)
* **Phase 9**: AI intent classifier
* **Phase 10**: Historical semantic retrieval with local vector index
* **Phase 11**: Grounded reply generation
* **Phase 12**: Explainable escalation policy
* **Phase 13**: End-to-end runnable CLI pipeline
* **Phase 14**: LLM-as-a-judge evaluation
* **Phase 15**: Human vs. LLM judge agreement validation
* **Phase 16**: Reproducible evaluation harness (<15 min reproduction)
* **Phase 17**: Top 5 failure mode analysis
* **Phase 18**: "What is misleading about my headline number?"
* **Phase 19**: Final project report
* **Phase 20**: Engineering decision log
* **Phase 21**: Finalized documentation
