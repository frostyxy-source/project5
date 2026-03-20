"""
Balando GmbH — LangSmith Dataset Creation
==========================================
Use Case 2: Personalised Product Recommendations

This script:
1. Downloads the H&M dataset from Google Drive (same source as the dashboard)
2. Extracts 10 real customer profiles from the transaction data
3. Creates a LangSmith dataset called 'balando-recommendation-dataset'
4. Each example = one real customer profile + expected output format

Run once before monitoring_setup.py.

Usage:
    pip install langchain langchain-openai langsmith gdown pandas python-dotenv
    python dataset_creation.py
"""

import os
import pathlib
import pandas as pd
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
LANGSMITH_API_KEY = os.getenv("LANGCHAIN_API_KEY")
DATASET_NAME      = "balando-recommendation-dataset"
FOLDER_ID         = "1aJZulbtsffKJK54CkvY62eS2n7iIllwq"
DATA_DIR          = "./tmp_data"
EXPECTED          = [
    "articles_sample.csv",
    "customers_sample.csv",
    "transactions_sample_500k.csv",
]

# ── Download data ─────────────────────────────────────────────────────────────
def download_data():
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    if not all(os.path.exists(os.path.join(DATA_DIR, f)) for f in EXPECTED):
        print("📥 Downloading H&M dataset from Google Drive...")
        import gdown
        gdown.download_folder(
            id=FOLDER_ID, output=DATA_DIR, quiet=False, use_cookies=False
        )
    else:
        print("✅ Data already downloaded — skipping")

# ── Build customer profiles from real H&M data ────────────────────────────────
def build_customer_profiles(n=10):
    print("🔍 Loading H&M data...")

    articles = pd.read_csv(
        os.path.join(DATA_DIR, "articles_sample.csv"),
        usecols=["article_id", "prod_name", "product_type_name",
                 "colour_group_name", "index_group_name"],
        dtype=str,
    )

    customers = pd.read_csv(
        os.path.join(DATA_DIR, "customers_sample.csv"),
        usecols=["customer_id", "age", "club_member_status", "fashion_news_frequency"],
        dtype={"customer_id": str},
    )
    customers["age"] = pd.to_numeric(customers["age"], errors="coerce")

    transactions = pd.read_csv(
        os.path.join(DATA_DIR, "transactions_sample_500k.csv"),
        usecols=["t_dat", "customer_id", "article_id", "price", "sales_channel_id"],
        dtype={"customer_id": str, "article_id": str},
        parse_dates=["t_dat"],
    )
    transactions["price"] = pd.to_numeric(transactions["price"], errors="coerce")

    # Merge
    df = (
        transactions
        .merge(articles,  on="article_id",  how="left")
        .merge(customers, on="customer_id", how="left")
    )

    # Pick customers with 3-8 purchases (enough history, not overwhelming)
    purchase_counts = df.groupby("customer_id")["article_id"].count()
    qualified = purchase_counts[(purchase_counts >= 3) & (purchase_counts <= 8)].index

    df_qualified = df[df["customer_id"].isin(qualified)]

    # Sample n unique customers with valid age
    sample_customers = (
        df_qualified.dropna(subset=["age"])
        .groupby("customer_id")
        .filter(lambda x: len(x) >= 3)
        ["customer_id"]
        .drop_duplicates()
        .sample(n=n, random_state=42)
    )

    profiles = []
    for cid in sample_customers:
        cdata   = df[df["customer_id"] == cid]
        cinfo   = customers[customers["customer_id"] == cid].iloc[0]
        age     = int(cinfo["age"]) if pd.notna(cinfo["age"]) else "Unknown"
        member  = cinfo["club_member_status"] if pd.notna(cinfo["club_member_status"]) else "Unknown"
        news    = cinfo["fashion_news_frequency"] if pd.notna(cinfo["fashion_news_frequency"]) else "Unknown"

        # Purchase history
        purchases      = cdata["product_type_name"].dropna().value_counts().head(5).to_dict()
        top_colours    = cdata["colour_group_name"].dropna().value_counts().head(3).index.tolist()
        top_categories = cdata["index_group_name"].dropna().value_counts().head(2).index.tolist()
        avg_price      = round(cdata["price"].mean() * 100, 2)  # H&M prices are normalised
        last_product   = cdata.sort_values("t_dat").iloc[-1]["prod_name"] \
                         if not cdata.empty else "Unknown"
        total_spend    = round(cdata["price"].sum() * 100, 2)

        profile = {
            "customer_id":       cid[:8] + "...",  # anonymised
            "age":               age,
            "club_member":       member,
            "news_frequency":    news,
            "purchase_history":  purchases,
            "top_colours":       top_colours,
            "top_categories":    top_categories,
            "avg_price_eur":     avg_price,
            "last_item_bought":  last_product,
            "total_spend_eur":   total_spend,
            "total_purchases":   len(cdata),
        }
        profiles.append(profile)
        print(f"  → Built profile: age={age}, purchases={len(cdata)}, "
              f"avg_price=€{avg_price}")

    return profiles

# ── Create LangSmith dataset ──────────────────────────────────────────────────
def create_langsmith_dataset(profiles):
    print(f"\n🚀 Connecting to LangSmith...")
    client = Client(api_key=LANGSMITH_API_KEY)

    # Delete existing dataset if it exists (clean slate)
    existing = [d for d in client.list_datasets() if d.name == DATASET_NAME]
    if existing:
        print(f"  ↺ Dataset '{DATASET_NAME}' already exists — deleting for fresh run")
        client.delete_dataset(dataset_id=existing[0].id)

    # Create fresh dataset
    dataset = client.create_dataset(
        dataset_name=DATASET_NAME,
        description=(
            "Balando GmbH — Use Case 2: Personalised Product Recommendations. "
            "10 real customer profiles extracted from H&M European fashion dataset "
            "(Kaggle). Each profile contains purchase history, colour preferences, "
            "price range, and demographics. Used to demonstrate AI recommendation "
            "transparency via LangSmith monitoring."
        ),
    )
    print(f"  ✅ Dataset created: {dataset.name} (id: {dataset.id})")

    # Add examples
    examples = []
    for i, profile in enumerate(profiles):
        example_input = {
            "customer_profile": profile,
            "task": (
                "Based on this customer's purchase history and preferences, "
                "recommend exactly 3 products from Balando's fashion catalogue. "
                "For each recommendation explain why it fits this specific customer."
            ),
            "context": (
                "Balando GmbH is a DACH-region fashion e-commerce SME. "
                "Target demographic: 25-45, Germany/Austria/Switzerland. "
                "Product categories: dresses, tops, trousers, outerwear, accessories."
            ),
        }
        example_output = {
            "expected_format": {
                "recommendations": [
                    {
                        "product_name": "string",
                        "category":     "string",
                        "price_range":  "string",
                        "reason":       "why this fits this specific customer"
                    }
                ] * 3,
                "personalisation_score": "HIGH / MEDIUM / LOW",
                "confidence":            "0-100",
            }
        }
        examples.append((example_input, example_output))
        print(f"  + Example {i+1:02d}: customer age={profile['age']}, "
              f"top category={list(profile['purchase_history'].keys())[0] if profile['purchase_history'] else 'N/A'}")

    # Bulk create
    client.create_examples(
        inputs  =[e[0] for e in examples],
        outputs =[e[1] for e in examples],
        dataset_id=dataset.id,
    )

    print(f"\n✅ Dataset '{DATASET_NAME}' created with {len(examples)} examples")
    print(f"🔗 View at: https://smith.langchain.com/")
    return dataset

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  Balando GmbH — LangSmith Dataset Creation")
    print("  Use Case 2: Personalised Product Recommendations")
    print("=" * 60)

    if not LANGSMITH_API_KEY:
        raise ValueError("❌ LANGCHAIN_API_KEY not found in .env file")

    download_data()
    profiles = build_customer_profiles(n=10)
    dataset  = create_langsmith_dataset(profiles)

    print("\n🎉 Done! Next step: run monitoring_setup.py")
    print("   This will send all 10 profiles through GPT-4o")
    print("   and trace every call in LangSmith.")
