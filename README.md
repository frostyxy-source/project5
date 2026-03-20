# Balando GmbH — AI Opportunity Dashboard
### BI Dashboard Mini Project · Module 5 · Ironhack Data Analytics Bootcamp

**Sector:** Fashion E-Commerce  
**Company Size:** SME (50–250 employees)  
**Client:** Chleo, CEO — Balando GmbH, Frankfurt  
**Live Dashboard:** [balando.up.railway.app/app](https://balando.up.railway.app/app)

---

## Project Summary

Balando GmbH is a DACH-region fashion e-commerce SME facing three structural problems:
Germany has the highest fashion return rate in Europe (40–50%), most customers never
make a second purchase (~25% repeat rate), and customer support is overwhelmed by
repetitive queries. This project proposes three AI use cases to address these problems,
backed by data analysis, a live automation demo, and a fully monitored AI system.

---

## Repository Structure

```
project5/
├── app.py                          # Main dashboard — Panel + Plotly, deployed on Railway
├── requirements.txt                # Python dependencies
├── Procfile                        # Railway deployment config
├── README.md                       # This file
│
├── assets/                         # Screenshots used in the dashboard
│   ├── true.png                    # n8n HIGH risk branch screenshot
│   ├── false.png                   # n8n LOW risk branch screenshot
│   ├── email.png                   # Return risk alert email screenshot
│   ├── balando-uc2-recommendations10call.png  # LangSmith 10 runs overview
│   ├── customerprofile.png         # LangSmith customer input screenshot
│   ├── recommendations.png         # LangSmith recommendations output screenshot
│   └── balandolangsmithprompt.png  # LangSmith full prompt screenshot
│
├── research/
│   ├── sector_research.md          # DACH fashion e-commerce market analysis
│   ├── opportunities_risks.md      # AI opportunity and risk mapping
│   └── use_cases.md                # Three AI use case proposals
│
├── langsmith/
│   ├── dataset_creation.py         # Creates LangSmith dataset from H&M data
│   ├── monitoring_setup.py         # Runs 10 GPT-4o calls with full tracing
│   ├── monitoring_results/
│   │   ├── summary.md              # Auto-generated monitoring report
│   │   └── results.json            # Full JSON output of all 10 runs
│   └── README.md                   # LangSmith setup guide
│
├── n8n/
│   ├── workflow.json               # n8n workflow export (return risk alert)
│   └── workflow_documentation.md   # Workflow explanation and setup guide
│
└── cost_estimation/
    ├── cost_analysis.md            # Full cost breakdown per use case
    └── timeline_estimate.md        # Implementation timeline
```

---

## The Three AI Use Cases

### Use Case 1 — Return Risk Prediction *(n8n demo built)*
**Problem:** Germany has the highest fashion return rate in Europe — up to 50% for dresses.  
**Solution:** An n8n workflow scores every incoming order for return risk using GPT-4o.
High-risk orders trigger an alert email to the operations team before the parcel ships.  
**ROI:** €20K–€60K/year in logistics savings at Balando's scale.  
**Demo:** Live n8n workflow — Webhook → GPT-4o → IF node → Gmail alert.

### Use Case 2 — Personalised Product Recommendations *(LangSmith demo built)*
**Problem:** ~75% of customers buy once and never return. Acquisition cost is 5–7× retention cost.  
**Solution:** GPT-4o analyses each customer's purchase history and generates 3 personalised
product recommendations, delivered via post-purchase email.  
**ROI:** +€150K–€400K annual revenue at +5–10pp repeat purchase rate.  
**Demo:** 10 real H&M customer profiles run through GPT-4o, fully traced in LangSmith.

### Use Case 3 — Customer Support Automation *(proposed)*
**Problem:** Support is dominated by repetitive queries — order status, returns, sizing.  
**Solution:** n8n classifies inbound emails and auto-drafts replies using order data.  
**ROI:** 30–40% of tickets auto-resolved, 10–15 agent hours saved per week.

---

## Technical Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| Dashboard | Panel + Plotly | Interactive BI dashboard |
| Deployment | Railway | Cloud hosting |
| Data | H&M Kaggle Dataset (500K rows) | DACH fashion proxy |
| Automation | n8n Cloud | Return risk alert workflow |
| AI Model | GPT-4o (OpenAI) | Risk scoring + recommendations |
| Monitoring | LangSmith | AI transparency and observability |
| Language | Python 3.11 | Data processing and scripting |

---

## Dataset

**Primary:** H&M Personalized Fashion Recommendations (Kaggle)  
**Source:** [kaggle.com/competitions/h-and-m-personalized-fashion-recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)  
**Size:** 500K transactions (sampled), 105K articles, 1.3M customers  
**Relevance:** European fashion market, same 25–45 customer profile, same DACH pain points  
**Files used:** `transactions_sample_500k.csv`, `articles_sample.csv`, `customers_sample.csv`  
**Storage:** Google Drive (auto-downloaded via gdown on Railway startup)

---

## Live Demo

**Dashboard:** [balando.up.railway.app/app](https://balando.up.railway.app/app)

The dashboard contains:
- KPI cards (transactions, customers, repeat purchase rate, online share)
- 8 interactive charts with AI insight boxes
- n8n return risk demo section with live test screenshots
- LangSmith monitoring section with cost breakdown and production roadmap

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/frostyxy-source/project5.git
cd project5

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run dashboard locally
panel serve app.py --show --port 5006
```

**For LangSmith scripts:**
```bash
cd langsmith
cp .env.example .env
# Fill in OPENAI_API_KEY and LANGCHAIN_API_KEY
pip install langchain langchain-openai langsmith gdown pandas python-dotenv
python dataset_creation.py
python monitoring_setup.py
```

---

## Environment Variables

```
OPENAI_API_KEY=sk-...          # OpenAI API key (for n8n and LangSmith scripts)
LANGCHAIN_API_KEY=ls__...      # LangSmith API key
```

Never commit `.env` to GitHub. Use `.env.example` as the template.

---

## Key Findings from the Data

- **40–50% return rate** in German fashion e-commerce — highest in Europe
- **75%+ of customers** are one-time buyers — the biggest revenue leak
- **Top returned categories:** Dresses (52%), Skirts (49%), Trousers (47%)
- **Core customer:** Age 25–45, online-first, mobile-dominant
- **Top colours:** Black, dark blue, white — concentrate stock here
- **Revenue peaks:** Pre-winter (Oct–Nov) and pre-summer (Apr–May) — AI campaign windows

---

## Regulatory Context

- **GDPR:** All customer data pseudonymised. DPIA required before production deployment.
- **EU AI Act (2026):** Use cases fall under "limited risk" — transparency labelling required.
- **EU Consumer Rights Directive:** 14-day return right is legally mandated — AI manages it smarter, not away.

---

## Sources

- BEVH: German E-Commerce Statistics 2024
- Landmark Global: Top 10 Essential Facts About German E-Commerce 2025
- University of Bamberg: European Return-o-Meter
- McKinsey & Company: State of AI in Retail 2024
- Stanford HAI: AI Index Report 2025
- EU AI Act (Official Journal of the EU, 2024)
- H&M Personalized Fashion Recommendations — Kaggle

---

