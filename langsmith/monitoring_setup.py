"""
Balando GmbH — LangSmith Monitoring Setup
==========================================
Use Case 2: Personalised Product Recommendations

This script:
1. Loads the 'balando-recommendation-dataset' from LangSmith
2. Runs each customer profile through GPT-4o using LangChain
3. Every call is fully traced in LangSmith — inputs, outputs, latency, tokens, cost
4. Generates a local monitoring_results/summary.md report

This is the anti-black-box demo for Chleo:
Every AI recommendation decision is logged, auditable, and explainable.

Run AFTER dataset_creation.py.

Usage:
    python monitoring_setup.py
"""

import os
import json
import time
import pathlib
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import Client
from langsmith.wrappers import wrap_openai

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGCHAIN_API_KEY")
DATASET_NAME      = "balando-recommendation-dataset"
PROJECT_NAME      = "balando-uc2-recommendations"
RESULTS_DIR       = "./monitoring_results"

# Tell LangSmith to trace everything
os.environ["LANGCHAIN_TRACING_V2"]  = "true"
os.environ["LANGCHAIN_API_KEY"]     = LANGSMITH_API_KEY or ""
os.environ["LANGCHAIN_PROJECT"]     = PROJECT_NAME
os.environ["LANGCHAIN_ENDPOINT"]    = "https://api.smith.langchain.com"

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a personalised product recommendation engine for Balando GmbH,
a fashion e-commerce company in the DACH region (Germany, Austria, Switzerland).

Your job is to analyse a customer's purchase history and preferences, then recommend
exactly 3 products they are likely to buy next from Balando's catalogue.

Balando's product catalogue covers:
- Dresses (casual, formal, summer, evening)
- Tops & Blouses (shirts, blouses, t-shirts, knitwear)
- Trousers & Skirts (jeans, trousers, midi skirts, mini skirts)
- Outerwear (jackets, coats, blazers)
- Accessories (scarves, bags, belts)

Rules:
- Recommendations must be specific (include product name, category, colour, price range)
- Each recommendation must include a clear, personalised reason referencing the customer's data
- Prioritise the customer's most-purchased categories and favourite colours
- Respect their typical price range
- Respond ONLY with valid JSON, no markdown, no code fences

JSON format:
{
  "recommendations": [
    {
      "product_name": "specific product name",
      "category": "category name",
      "colour": "colour",
      "price_range": "€XX–€XX",
      "reason": "personalised reason referencing their history"
    },
    {
      "product_name": "specific product name",
      "category": "category name",
      "colour": "colour",
      "price_range": "€XX–€XX",
      "reason": "personalised reason referencing their history"
    },
    {
      "product_name": "specific product name",
      "category": "category name",
      "colour": "colour",
      "price_range": "€XX–€XX",
      "reason": "personalised reason referencing their history"
    }
  ],
  "personalisation_score": "HIGH or MEDIUM or LOW",
  "confidence": 0-100,
  "summary": "one sentence explaining the overall recommendation strategy for this customer"
}"""

# ── Run recommendations ───────────────────────────────────────────────────────
def build_user_message(profile: dict) -> str:
    history_str = ", ".join(
        [f"{cat} (x{cnt})" for cat, cnt in profile["purchase_history"].items()]
    ) if profile["purchase_history"] else "No history available"

    colours_str    = ", ".join(profile["top_colours"])    if profile["top_colours"]    else "Not specified"
    categories_str = ", ".join(profile["top_categories"]) if profile["top_categories"] else "Not specified"

    return f"""Customer Profile:
- Age: {profile['age']}
- Club member: {profile['club_member']}
- Fashion news frequency: {profile['news_frequency']}
- Purchase history: {history_str}
- Favourite colours: {colours_str}
- Top categories: {categories_str}
- Average spend per item: €{profile['avg_price_eur']}
- Last item bought: {profile['last_item_bought']}
- Total purchases: {profile['total_purchases']}
- Total lifetime spend: €{profile['total_spend_eur']}

Generate 3 personalised product recommendations for this Balando customer."""

def run_recommendation(llm: ChatOpenAI, profile: dict, run_number: int) -> dict:
    print(f"\n  🤖 Run {run_number:02d} — Customer age={profile['age']}, "
          f"purchases={profile['total_purchases']}")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=build_user_message(profile)),
    ]

    start = time.time()
    response = llm.invoke(
        messages,
        config={
            "run_name": f"balando-recommendation-{run_number:02d}",
            "tags":     ["balando", "uc2", "recommendations", f"age-{profile['age']}"],
            "metadata": {
                "customer_age":       profile["age"],
                "total_purchases":    profile["total_purchases"],
                "avg_price_eur":      profile["avg_price_eur"],
                "top_category":       list(profile["purchase_history"].keys())[0]
                                      if profile["purchase_history"] else "unknown",
                "club_member":        profile["club_member"],
                "use_case":           "UC2 - Product Recommendations",
                "project":            "Balando GmbH AI Consulting",
            },
        },
    )
    latency_ms = round((time.time() - start) * 1000)

    # Parse response
    raw = response.content.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw)
        status = "✅ SUCCESS"
    except json.JSONDecodeError:
        parsed = {"raw_response": raw, "parse_error": True}
        status = "⚠️  PARSE WARNING"

    result = {
        "run_number":           run_number,
        "customer_age":         profile["age"],
        "customer_purchases":   profile["total_purchases"],
        "avg_price_eur":        profile["avg_price_eur"],
        "latency_ms":           latency_ms,
        "status":               status,
        "recommendations":      parsed.get("recommendations", []),
        "personalisation_score":parsed.get("personalisation_score", "N/A"),
        "confidence":           parsed.get("confidence", "N/A"),
        "summary":              parsed.get("summary", "N/A"),
        "raw_response":         response.content,
    }

    # Print preview
    score = parsed.get("personalisation_score", "N/A")
    conf  = parsed.get("confidence", "N/A")
    print(f"     {status} | latency={latency_ms}ms | "
          f"personalisation={score} | confidence={conf}")
    if parsed.get("recommendations"):
        for i, rec in enumerate(parsed["recommendations"][:3], 1):
            print(f"     Rec {i}: {rec.get('product_name','?')} "
                  f"({rec.get('colour','?')}, {rec.get('price_range','?')})")

    return result

# ── Save results ──────────────────────────────────────────────────────────────
def save_results(results: list):
    pathlib.Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

    # JSON dump
    json_path = os.path.join(RESULTS_DIR, "results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Markdown summary
    now        = datetime.now().strftime("%Y-%m-%d %H:%M")
    successful = [r for r in results if "SUCCESS" in r["status"]]
    avg_lat    = round(sum(r["latency_ms"] for r in results) / len(results))
    high_pers  = sum(1 for r in results
                     if r.get("personalisation_score") == "HIGH")
    avg_conf   = round(sum(r["confidence"] for r in results
                           if isinstance(r.get("confidence"), (int, float)))
                       / max(len(results), 1))

    md = f"""# Balando GmbH — LangSmith Monitoring Results
## Use Case 2: Personalised Product Recommendations

**Generated:** {now}
**Project:** `{PROJECT_NAME}` on LangSmith
**Dataset:** `{DATASET_NAME}`
**Model:** GPT-4o

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total runs | {len(results)} |
| Successful | {len(successful)} / {len(results)} |
| Average latency | {avg_lat}ms |
| HIGH personalisation score | {high_pers} / {len(results)} runs |
| Average confidence | {avg_conf}/100 |
| Estimated cost per run | ~$0.002–0.004 |
| Estimated cost for all 10 | ~$0.02–0.04 |

---

## What LangSmith Captures Per Run

Every single recommendation call is logged in LangSmith with:
- ✅ Full input (customer profile sent to GPT-4o)
- ✅ Full output (3 recommendations + reasoning)
- ✅ Latency in milliseconds
- ✅ Token usage (input + output tokens)
- ✅ Estimated cost in USD
- ✅ Custom metadata (customer age, purchase count, top category)
- ✅ Tags for filtering (balando, uc2, recommendations)

This is the direct answer to Chleo's concern about AI being a black box.
Every decision the AI makes is logged, timestamped, and auditable.

---

## Individual Run Results

"""
    for r in results:
        md += f"### Run {r['run_number']:02d} — Customer Age {r['customer_age']}\n\n"
        md += f"- **Status:** {r['status']}\n"
        md += f"- **Latency:** {r['latency_ms']}ms\n"
        md += f"- **Personalisation Score:** {r['personalisation_score']}\n"
        md += f"- **Confidence:** {r['confidence']}/100\n"
        md += f"- **Summary:** {r['summary']}\n\n"

        if r.get("recommendations"):
            md += "**Recommendations:**\n\n"
            for i, rec in enumerate(r["recommendations"], 1):
                md += (f"{i}. **{rec.get('product_name','?')}** "
                       f"({rec.get('category','?')}, {rec.get('colour','?')}, "
                       f"{rec.get('price_range','?')})\n"
                       f"   > {rec.get('reason','?')}\n\n")
        md += "---\n\n"

    md += f"""## How to View in LangSmith

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Open project: **`{PROJECT_NAME}`**
3. You will see {len(results)} traced runs
4. Click any run to inspect:
   - The exact customer profile sent to GPT-4o
   - The exact recommendations returned
   - Token usage and cost breakdown
   - Latency timeline
5. Use the dataset **`{DATASET_NAME}`** tab to compare inputs vs outputs

---

*Generated by Balando GmbH AI Consulting — March 2026*
"""

    md_path = os.path.join(RESULTS_DIR, "summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"\n  📄 Results saved to {json_path}")
    print(f"  📄 Summary saved to {md_path}")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Balando GmbH — LangSmith Monitoring Setup")
    print("  Use Case 2: Personalised Product Recommendations")
    print("=" * 60)

    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY not found in .env file")
    if not LANGSMITH_API_KEY:
        raise ValueError("❌ LANGCHAIN_API_KEY not found in .env file")

    # Load dataset from LangSmith
    print(f"\n📂 Loading dataset '{DATASET_NAME}' from LangSmith...")
    client  = Client(api_key=LANGSMITH_API_KEY)
    datasets = [d for d in client.list_datasets() if d.name == DATASET_NAME]
    if not datasets:
        raise ValueError(
            f"❌ Dataset '{DATASET_NAME}' not found. "
            "Run dataset_creation.py first."
        )

    examples = list(client.list_examples(dataset_id=datasets[0].id))
    print(f"  ✅ Found {len(examples)} examples")

    # Init LangChain LLM — LangSmith traces automatically via env vars
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY,
    )

    print(f"\n🔍 Running {len(examples)} recommendation calls...")
    print(f"   All calls traced in LangSmith project: '{PROJECT_NAME}'")
    print("-" * 60)

    results = []
    for i, example in enumerate(examples, 1):
        profile = example.inputs.get("customer_profile", {})
        result  = run_recommendation(llm, profile, i)
        results.append(result)
        time.sleep(0.5)  # Be polite to the API

    # Summary
    successful = [r for r in results if "SUCCESS" in r["status"]]
    avg_lat    = round(sum(r["latency_ms"] for r in results) / len(results))

    print("\n" + "=" * 60)
    print(f"  ✅ Completed: {len(successful)}/{len(results)} successful")
    print(f"  ⚡ Average latency: {avg_lat}ms")
    print(f"  💰 Estimated total cost: ~${len(results) * 0.003:.3f}")
    print("=" * 60)

    save_results(results)

    print(f"\n🔗 View all traces at: https://smith.langchain.com")
    print(f"   Project: '{PROJECT_NAME}'")
    print(f"   Dataset: '{DATASET_NAME}'")
    print("\n🎉 LangSmith monitoring setup complete!")
    print("   Screenshot your LangSmith dashboard to include in your submission.")
