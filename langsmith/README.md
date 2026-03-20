# LangSmith Monitoring — Balando GmbH
## Use Case 2: Personalised Product Recommendations

This folder contains the LangSmith monitoring setup for Balando's AI recommendation engine.
It demonstrates full AI transparency and observability — directly addressing Chleo's concern
about AI being a "black box."

---

## What It Does

1. **`dataset_creation.py`** — Extracts 10 real customer profiles from the H&M Kaggle dataset
   and creates a LangSmith dataset called `balando-recommendation-dataset`

2. **`monitoring_setup.py`** — Runs each profile through GPT-4o with full LangSmith tracing.
   Every recommendation call is logged with inputs, outputs, latency, token cost, and metadata.

3. **`monitoring_results/summary.md`** — Auto-generated report of all 10 runs

---

## Setup

```bash
# 1. Install dependencies
pip install langchain langchain-openai langsmith gdown pandas python-dotenv

# 2. Create your .env file
cp .env.example .env
# Fill in OPENAI_API_KEY and LANGCHAIN_API_KEY

# 3. Run dataset creation first
python dataset_creation.py

# 4. Run monitoring
python monitoring_setup.py
```

---

## What You See in LangSmith

After running `monitoring_setup.py`, open [smith.langchain.com](https://smith.langchain.com) and navigate to project **`balando-uc2-recommendations`**.

You will see 10 traced runs. For each run LangSmith shows:

| Field | What it contains |
|-------|-----------------|
| Input | Full customer profile (age, purchase history, colours, price range) |
| Output | 3 personalised recommendations with reasoning |
| Latency | Response time in milliseconds |
| Tokens | Input + output token count |
| Cost | Estimated USD cost per call |
| Metadata | Customer age, top category, club member status |
| Tags | `balando`, `uc2`, `recommendations` |

---

## Why This Matters for Chleo

Chleo's main fear is that AI is a black box — she can't see what it's doing or why.

LangSmith solves this directly:
- Every recommendation is logged with the exact customer data that produced it
- Every decision is timestamped and auditable
- Token costs are visible — no surprise bills
- The dataset shows the expected vs actual output format
- Filtering by tag (`uc2`) shows only recommendation calls

This is not a demo of monitoring. This is actual monitoring of actual AI calls,
using real H&M customer data as a proxy for Balando's real customers.

---

## Data Source

Customer profiles are extracted from the **H&M Personalized Fashion Recommendations**
dataset (Kaggle), the same dataset powering the Balando Railway dashboard.
This is the closest publicly available proxy for a DACH fashion SME customer base.

- Dataset: `transactions_sample_500k.csv`, `customers_sample.csv`, `articles_sample.csv`
- Source: Google Drive (same folder as dashboard data — auto-downloaded via gdown)
- Customers selected: age 20–65, 3–8 purchases, valid demographic data

---

*Balando GmbH AI Consulting — March 2026*
