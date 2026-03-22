"""
Balando — AI Opportunity Dashboard
====================================
Railway/Linux deployment entry point.

Run locally:
    panel serve app.py --show --port 5006

Deploy to Railway:
    Push to GitHub, Railway uses Procfile automatically.
"""

import os
import pathlib
import warnings

import gdown
import pandas as pd
import plotly.express as px
import panel as pn

warnings.filterwarnings("ignore")
pn.extension("plotly", sizing_mode="stretch_width")  # NO template= here

# ── Colours — Warm Cream / Luxury Fashion (Chloé / Bottega palette) ──────────
BG         = "#EDE8DF"   # warm cream background — slightly deeper
CARD_BG    = "#FFFFFF"   # pure white cards
ACCENT     = "#C9956A"   # warm terracotta / camel
TEAL       = "#6B8F71"   # soft sage green
GREEN      = "#7AAB82"   # muted sage
AMBER      = "#D4A853"   # muted gold
PURPLE     = "#A67B8A"   # dusty mauve / rose
TEXT_LT    = "#2C2C2C"   # near-black — primary text
TEXT_MUTED = "#8A7E72"   # warm grey — secondary text
GRID_CLR   = "#E8E0D5"   # cream border / grid lines

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="#FDFBF8",
    font=dict(color="#2C2C2C", family="Georgia, serif"),
    title_font=dict(color="#2C2C2C", family="Georgia, serif", size=14),
    xaxis=dict(gridcolor="#E8E0D5", zerolinecolor="#E8E0D5",
               tickfont=dict(color="#8A7E72"), linecolor="#E8E0D5"),
    yaxis=dict(gridcolor="#E8E0D5", zerolinecolor="#E8E0D5",
               tickfont=dict(color="#8A7E72"), linecolor="#E8E0D5"),
    margin=dict(l=40, r=20, t=45, b=40),
)

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_DIR    = "/tmp/data"
FOLDER_ID   = "1aJZulbtsffKJK54CkvY62eS2n7iIllwq"
EXPECTED    = ["articles_sample.csv", "customers_sample.csv", "transactions_sample_500k.csv"]
SCREENSHOTS = ["true.png", "false.png", "email.png",
               "balando-uc2-recommendations10call.png",
               "customerprofile.png", "recommendations.png",
               "balandolangsmithprompt.png"]

def load_data():
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    all_files = EXPECTED + SCREENSHOTS
    if not all(os.path.exists(os.path.join(DATA_DIR, f)) for f in all_files):
        print("Downloading data and assets from Google Drive...")
        gdown.download_folder(id=FOLDER_ID, output=DATA_DIR, quiet=False, use_cookies=False)

    print(f"Loading data from: {DATA_DIR}")

    articles = pd.read_csv(
        os.path.join(DATA_DIR, "articles_sample.csv"),
        usecols=["article_id", "prod_name", "product_type_name",
                 "garment_group_name", "colour_group_name", "index_group_name"],
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
    transactions["sales_channel_id"] = transactions["sales_channel_id"].astype(str)

    df = (
        transactions
        .merge(articles,  on="article_id",  how="left")
        .merge(customers, on="customer_id", how="left")
    )
    df["month"]         = df["t_dat"].dt.to_period("M").dt.to_timestamp()
    df["channel_label"] = df["sales_channel_id"].map(
        {"1": "In-store", "2": "Online"}
    ).fillna("Unknown")

    print(f"Loaded {len(df):,} rows | {df['t_dat'].min().date()} to {df['t_dat'].max().date()}")
    return df

df = load_data()

# ── Widgets ───────────────────────────────────────────────────────────────────
date_range = pn.widgets.DateRangeSlider(
    name="Date range",
    width=210,
    margin=(5, 0, 5, 0),
    start=df["t_dat"].min(),
    end=df["t_dat"].max(),
    value=(df["t_dat"].min(), df["t_dat"].max()),
)

channel_filter = pn.widgets.CheckBoxGroup(
    name="Sales channel",
    options=["Online", "In-store"],
    value=["Online", "In-store"],
)

def filtered():
    s, e = date_range.value
    ch   = channel_filter.value
    return df[
        (df["t_dat"] >= pd.Timestamp(s)) &
        (df["t_dat"] <= pd.Timestamp(e)) &
        (df["channel_label"].isin(ch))
    ]

# ── UI helpers ────────────────────────────────────────────────────────────────
def insight_box(uc_num, uc_label, body_html, colour=TEAL):
    icons = {"1": "🔮", "2": "🎯", "3": "💬"}
    icon  = icons.get(str(uc_num), "💡")
    return pn.pane.HTML(f"""
    <div style="background:#F5EFE6;border-left:4px solid {colour};
                border-radius:6px;padding:14px 18px;margin-top:6px;margin-bottom:8px;
                box-shadow:0 1px 6px rgba(0,0,0,0.05);">
      <div style="font-size:9px;color:{colour};font-weight:700;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:6px;font-family:Georgia,serif;">
        {icon} AI Use Case {uc_num} — {uc_label}
      </div>
      <div style="font-size:12px;color:{TEXT_MUTED};line-height:1.7;">{body_html}</div>
    </div>
    """, sizing_mode="stretch_width")

def kpi_card(label, value, sub, colour=ACCENT):
    return pn.pane.HTML(f"""
    <div style="background:{CARD_BG};border-left:4px solid {colour};
                border-radius:8px;padding:16px 20px;
                box-shadow:0 2px 12px rgba(0,0,0,0.06);">
      <div style="font-size:9px;color:{TEXT_MUTED};letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:6px;
                  font-family:Georgia,serif;">{label}</div>
      <div style="font-size:28px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;
                  font-family:Georgia,serif;">{value}</div>
      <div style="font-size:10px;color:{colour};font-style:italic;">{sub}</div>
    </div>
    """, sizing_mode="stretch_width")

def sec(label):
    return pn.pane.HTML(
        f"""<div style="color:{ACCENT};font-size:9px;font-weight:700;
        letter-spacing:3px;text-transform:uppercase;
        padding:14px 0 6px;border-bottom:2px solid {ACCENT};
        margin-bottom:4px;font-family:Georgia,serif;">{label}</div>""",
        sizing_mode="stretch_width",
    )

# ── KPI cards ─────────────────────────────────────────────────────────────────
@pn.depends(date_range, channel_filter)
def kpi_row(*_):
    d = filtered()
    if len(d) == 0:
        return pn.pane.HTML("<p style='color:white'>No data for selected filters.</p>")
    counts      = d.groupby("customer_id")["article_id"].count()
    repeat_rate = round((counts > 1).sum() / len(counts) * 100, 1)
    online_pct  = round(len(d[d["channel_label"] == "Online"]) / len(d) * 100, 1)
    return pn.Row(
        kpi_card("Total transactions",   f"{len(d):,}",                    "orders in period",              ACCENT),
        kpi_card("Unique customers",     f"{d['customer_id'].nunique():,}", "individual buyers",             TEAL),
        kpi_card("Repeat purchase rate", f"{repeat_rate}%",                "industry avg ~25% — AI target", AMBER),
        kpi_card("Online share",         f"{online_pct}%",                 "of revenue is digital",         GREEN),
        sizing_mode="stretch_width",
    )

# ── Charts ────────────────────────────────────────────────────────────────────
@pn.depends(date_range, channel_filter)
def c_revenue(*_):
    d   = filtered().groupby("month")["price"].sum().reset_index()
    fig = px.line(d, x="month", y="price",
                  title="When does revenue peak? — Plan AI campaigns around these windows",
                  labels={"month": "", "price": "Revenue (normalised)"})
    fig.update_traces(line_color="#C9956A", line_width=2.5,
                      fill="tozeroy", fillcolor="rgba(201,149,106,0.1)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_products(*_):
    d = (filtered().groupby("product_type_name")["price"].sum()
         .nlargest(15).reset_index().sort_values("price"))
    fig = px.bar(d, x="price", y="product_type_name", orientation="h",
                 title="Where should the recommendation engine focus first?",
                 labels={"price": "Revenue (normalised)", "product_type_name": ""})
    fig.update_traces(marker_color="#C9956A")
    fig.update_layout(**PLOTLY_LAYOUT, height=360)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=360)

@pn.depends(date_range, channel_filter)
def c_channel(*_):
    d   = filtered().groupby("channel_label")["price"].sum().reset_index()
    fig = px.pie(d, names="channel_label", values="price",
                 title="Online dominates — where AI delivers the highest ROI",
                 color_discrete_sequence=["#C9956A", "#6B8F71"])
    fig.update_layout(**PLOTLY_LAYOUT, legend=dict(font=dict(color="#2C2C2C")))
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_garment(*_):
    d = (filtered().groupby("garment_group_name")["price"].sum()
         .nlargest(10).reset_index().sort_values("price"))
    fig = px.bar(d, x="price", y="garment_group_name", orientation="h",
                 title="High-revenue garment groups = highest return risk — AI targets these first",
                 labels={"price": "Revenue (normalised)", "garment_group_name": ""})
    fig.update_traces(marker_color="#D4A853")
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=300)

@pn.depends(date_range, channel_filter)
def c_age(*_):
    ages = filtered()["age"].dropna()
    fig  = px.histogram(ages, x="age", nbins=10,
                        title="Your core customer is 25–45 — they expect personalisation as standard",
                        labels={"age": "Age group", "count": "Customers"})
    fig.update_traces(marker_color="#A67B8A")
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_colours(*_):
    d   = (filtered().groupby("colour_group_name")["price"].sum()
           .nlargest(20).reset_index())
    fig = px.treemap(d, path=["colour_group_name"], values="price",
                     title="Colour demand is concentrated — AI prevents stockouts on core colours",
                     color="price",
                     color_continuous_scale=["#F0E8DE", "#C9956A"])
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=300)

@pn.depends(date_range, channel_filter)
def c_repeat(*_):
    counts = (filtered().groupby("customer_id")["article_id"]
              .count().reset_index())
    counts.columns = ["customer_id", "purchases"]
    counts["segment"] = counts["purchases"].apply(
        lambda x: "One-time buyer" if x == 1
        else ("2–3 purchases" if x <= 3 else "4+ purchases (loyal)")
    )
    seg   = counts.groupby("segment").size().reset_index(name="customers")
    order = ["One-time buyer", "2–3 purchases", "4+ purchases (loyal)"]
    seg["segment"] = pd.Categorical(seg["segment"], categories=order, ordered=True)
    seg   = seg.sort_values("segment")
    total = seg["customers"].sum()
    seg["pct"] = (seg["customers"] / total * 100).round(1)
    colour_map = {
        "One-time buyer":       "#C9956A",
        "2–3 purchases":        "#D4A853",
        "4+ purchases (loyal)": "#6B8F71",
    }
    fig = px.bar(seg, x="segment", y="customers",
                 title="Most customers never come back — this is the #1 problem AI solves",
                 labels={"segment": "", "customers": "Customers"},
                 color="segment", color_discrete_map=colour_map,
                 text=seg["pct"].apply(lambda x: f"{x}%"))
    fig.update_traces(textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=280)

@pn.depends(date_range, channel_filter)
def c_returns(*_):
    d   = filtered()
    top = (d.groupby("product_type_name")["article_id"].count()
           .nlargest(12).reset_index())
    top.columns = ["product_type", "order_volume"]
    rates = {
        "Trousers": 47, "Dress": 52, "Blouse": 45, "Sweater": 38,
        "T-shirt":  35, "Skirt": 49, "Jacket": 41, "Shorts":  32,
        "Socks":    12, "Bra":   28, "Leggings": 36, "Vest top": 30,
    }
    top["return_rate"] = top["product_type"].map(
        lambda x: next((v for k, v in rates.items() if k.lower() in x.lower()), 33)
    )
    top["est_returns"] = (top["order_volume"] * top["return_rate"] / 100).astype(int)
    top = top.sort_values("est_returns", ascending=True)
    fig = px.bar(top, x="est_returns", y="product_type", orientation="h",
                 title="Most returned product types — Germany benchmarks (Bamberg / EHI 2024)",
                 labels={"est_returns": "Estimated returns", "product_type": ""},
                 color="return_rate",
                 color_continuous_scale=["#6B8F71", "#D4A853", "#C9956A"],
                 text=top["return_rate"].apply(lambda x: f"{x}% return rate"))
    fig.update_traces(textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=380)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=380)

# ── Insight boxes ─────────────────────────────────────────────────────────────
i_revenue  = insight_box(2, "Product Recommendations",
    "Revenue dips in summer and spikes pre-winter. An AI recommendation engine automatically "
    "triggers personalised re-engagement emails during slow periods. "
    "<b style='color:#2C2C2C;'>Industry benchmark: personalised emails generate 3–5× higher "
    "click rates than generic newsletters.</b>", TEAL)

i_products = insight_box(2, "Product Recommendations",
    "Top 5 product types generate the majority of revenue. An AI model learns that a customer "
    "buying a dress is highly likely to want coordinating basics or shoes next. "
    "<b style='color:#2C2C2C;'>Recommending the right product increases average order value "
    "by 8–15% — with zero extra acquisition cost.</b>", TEAL)

i_channel  = insight_box(3, "Customer Support Automation",
    "The majority of revenue is online → the majority of support tickets also arrive digitally. "
    "The n8n automation workflow auto-classifies and drafts replies to the 3 most common query types. "
    "<b style='color:#2C2C2C;'>Automating 30–40% of inbound tickets frees 10–15 hours "
    "of agent time per week.</b>", PURPLE)

i_garment  = insight_box(1, "Return Rate Reduction",
    "Jersey basics, trousers and dresses are highest-revenue — and most returned. "
    "A return prediction model flags high-risk orders at checkout and shows a size guide. "
    "<b style='color:#2C2C2C;'>Estimated saving: 10–15pp reduction = €30K–€60K/year "
    "on a €5M revenue base.</b>", ACCENT)

i_age      = insight_box(2, "Product Recommendations",
    "The 25–45 demographic is the most digitally native segment. "
    "<b style='color:#2C2C2C;'>81% prefer brands that offer personalised experiences</b> — "
    "and they switch to competitors that do. AI recommendations give Balando the same capability "
    "as Zalando without Zalando's engineering budget.", TEAL)

i_colours  = insight_box(1, "Return Rate Reduction",
    "Black, grey, white and dark blue account for the majority of revenue — consistent across "
    "all European fashion markets. "
    "<b style='color:#2C2C2C;'>AI demand forecasting ensures Balando never stockouts on core "
    "colours while avoiding overstock</b> that ends in 30–50% markdown losses.", ACCENT)

i_repeat   = insight_box(2, "Product Recommendations",
    "The majority of customers buy once and never return. "
    "<b style='color:#2C2C2C;'>Acquiring a new customer costs 5–7× more than retaining one.</b> "
    "Moving just 10% of one-time buyers to a second purchase through a personalised email "
    "can increase annual revenue by 8–12% with near-zero incremental cost.", GREEN)

i_returns  = insight_box(1, "Return Rate Reduction",
    "<b style='color:#2C2C2C;'>Germany has the highest fashion return rate in Europe — "
    "up to 52% for dresses and skirts</b> (University of Bamberg / EHI 2024). "
    "An AI return prediction model scores every order at checkout. "
    "A 10pp reduction saves €30K–€60K/year in direct logistics costs alone.", ACCENT)

# ── Layout ────────────────────────────────────────────────────────────────────
header = pn.pane.HTML(f"""
<div style="position:relative;overflow:hidden;
            background:linear-gradient(135deg,#EDE8DF 0%,#E5DDD0 100%);
            padding:36px 40px 32px;border-bottom:2px solid #E8E0D5;">

  <!-- Fashion SVG background decorations -->
  <svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:0.12;"
       xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" preserveAspectRatio="xMidYMid slice">

    <!-- Dress silhouette 1 -->
    <g transform="translate(60,10)" fill="{ACCENT}">
      <ellipse cx="40" cy="18" rx="14" ry="14"/>
      <path d="M26 32 Q20 50 10 120 L70 120 Q60 50 54 32 Z"/>
      <path d="M10 120 Q5 180 0 260 L80 260 Q75 180 70 120 Z"/>
    </g>

    <!-- Hanger -->
    <g transform="translate(200,20)" stroke="{TEAL}" stroke-width="3" fill="none">
      <path d="M60 0 Q60 20 30 35 Q0 50 0 70 L120 70 Q120 50 90 35 Q60 20 60 0"/>
      <line x1="55" y1="0" x2="65" y2="0"/>
      <path d="M58 0 Q60 -15 65 -10"/>
    </g>

    <!-- Dress silhouette 2 (right side) -->
    <g transform="translate(950,5)" fill="{TEAL}">
      <ellipse cx="40" cy="18" rx="14" ry="14"/>
      <path d="M26 32 Q18 55 5 130 L75 130 Q62 55 54 32 Z"/>
      <path d="M5 130 Q0 195 -5 270 L85 270 Q80 195 75 130 Z"/>
    </g>

    <!-- Shopping bag -->
    <g transform="translate(1080,30)" stroke="{AMBER}" stroke-width="3" fill="none">
      <rect x="0" y="30" width="80" height="90" rx="4"/>
      <path d="M15 30 Q15 0 40 0 Q65 0 65 30"/>
      <line x1="20" y1="55" x2="60" y2="55"/>
    </g>

    <!-- Tag / price label -->
    <g transform="translate(400,25)" stroke="{PURPLE}" stroke-width="2.5" fill="none">
      <path d="M0 0 L60 0 L75 20 L60 40 L0 40 Z"/>
      <circle cx="12" cy="20" r="5"/>
      <line x1="75" y1="20" x2="95" y2="5"/>
      <line x1="18" y1="15" x2="55" y2="15"/>
      <line x1="18" y1="25" x2="45" y2="25"/>
    </g>

    <!-- Scissors -->
    <g transform="translate(700,15)" stroke="{ACCENT}" stroke-width="2.5" fill="none">
      <circle cx="12" cy="12" r="10"/>
      <circle cx="38" cy="12" r="10"/>
      <line x1="19" y1="18" x2="70" y2="65"/>
      <line x1="31" y1="18" x2="70" y2="65"/>
    </g>

    <!-- Needle and thread -->
    <g transform="translate(830,40)" stroke="{GREEN}" stroke-width="2" fill="none">
      <line x1="0" y1="0" x2="40" y2="80"/>
      <ellipse cx="5" cy="5" rx="5" ry="8" transform="rotate(-60 5 5)"/>
      <path d="M40 80 Q55 60 50 40 Q45 20 60 10 Q75 0 70 20 Q65 40 80 50"/>
    </g>

    <!-- Stars / sparkles -->
    <g fill="{AMBER}" opacity="0.6">
      <polygon points="550,20 553,28 562,28 555,33 558,42 550,37 542,42 545,33 538,28 547,28" transform="scale(0.7)"/>
      <polygon points="150,200 152,206 158,206 153,209 155,215 150,212 145,215 147,209 142,206 148,206" transform="scale(0.5)"/>
      <polygon points="1150,150 1152,156 1158,156 1153,159 1155,165 1150,162 1145,165 1147,159 1142,156 1148,156" transform="scale(0.6)"/>
    </g>

    <!-- Decorative circles -->
    <circle cx="300" cy="250" r="80" stroke="{ACCENT}" stroke-width="1.5" fill="none" opacity="0.5"/>
    <circle cx="900" cy="280" r="60" stroke="{TEAL}" stroke-width="1.5" fill="none" opacity="0.5"/>
    <circle cx="600" cy="260" r="100" stroke="{PURPLE}" stroke-width="1" fill="none" opacity="0.3"/>
  </svg>

  <!-- Content -->
  <div style="position:relative;z-index:2;">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:6px;">
      <div style="font-size:9px;color:{ACCENT};letter-spacing:4px;font-weight:700;font-family:Georgia,serif;">
        ✦ BALANDO GMBH — CONFIDENTIAL ✦
      </div>
    </div>

    <div style="font-size:32px;font-weight:400;color:#2C2C2C;margin-bottom:6px;
                letter-spacing:-0.5px;line-height:1.2;font-family:Georgia,serif;">
      AI-Powered Proposal Plan
      <span style="color:{ACCENT};font-style:italic;"> for Balando GmbH</span>
    </div>

    <div style="font-size:12px;color:{TEXT_MUTED};margin-bottom:20px;">
      Prepared for <b style="color:#2C2C2C;">Chleo, CEO</b> &nbsp;·&nbsp;
      H&amp;M European Fashion Dataset · DACH Market Proxy &nbsp;·&nbsp;
      <b style="color:{ACCENT};">March 2026</b>
    </div>

    <!-- Executive Summary -->
    <div style="background:#FFFFFF;border:1px solid #E8E0D5;
                border-radius:10px;padding:20px 24px;
                box-shadow:0 2px 16px rgba(0,0,0,0.06);max-width:900px;">
      <div style="font-size:9px;color:{ACCENT};font-weight:700;letter-spacing:3px;
                  text-transform:uppercase;margin-bottom:14px;font-family:Georgia,serif;">
        ✦ Executive Summary — 3 Things You Need to Know
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">

        <div style="border-left:3px solid {ACCENT};padding-left:12px;">
          <div style="font-size:10px;color:{ACCENT};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">🔴 Biggest Problem</div>
          <div style="font-size:12px;color:#2C2C2C;font-weight:600;margin-bottom:3px;">
            40–50% return rate
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            Germany's fashion return rate is the highest in Europe. On a €5M revenue base
            this costs Balando an estimated <b style="color:#2C2C2C;font-weight:700;">€100K–€200K/year</b>
            in direct logistics alone.
          </div>
        </div>

        <div style="border-left:3px solid {TEAL};padding-left:12px;">
          <div style="font-size:10px;color:{TEAL};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">🟢 Biggest Opportunity</div>
          <div style="font-size:12px;color:#2C2C2C;font-weight:600;margin-bottom:3px;">
            Most customers never return
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            Over 60% of customers buy once and disappear. A personalised AI recommendation
            engine moving just <b style="color:#2C2C2C;font-weight:700;">10% to a second purchase</b>
            adds €150K–€400K in annual revenue — at zero acquisition cost.
          </div>
        </div>

        <div style="border-left:3px solid {AMBER};padding-left:12px;">
          <div style="font-size:10px;color:{AMBER};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">⚡ Recommended First Step</div>
          <div style="font-size:12px;color:#2C2C2C;font-weight:600;margin-bottom:3px;">
            Start with support automation
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            The fastest win: automate 30–40% of inbound support emails with n8n + AI.
            <b style="color:#2C2C2C;font-weight:700;">Live in 4–6 weeks.</b> Every AI decision is
            fully logged and visible — solving your transparency concern from day one.
          </div>
        </div>

      </div>
    </div>

    <!-- WHY H&M note -->
    <div style="margin-top:14px;background:#FDF8F0;border-radius:6px;
                padding:10px 16px;border-left:3px solid {AMBER};max-width:900px;">
      <span style="font-size:10px;color:{AMBER};font-weight:700;">WHY H&amp;M DATA?&nbsp;&nbsp;</span>
      <span style="font-size:10px;color:{TEXT_MUTED};">
        Closest publicly available proxy for a DACH fashion SME — same European market,
        same 25–45 customer profile, same pain points. Every pattern below exists in
        Balando's business today.
      </span>
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

sidebar = pn.Column(
    pn.pane.HTML(f"""
    <div style="background:linear-gradient(135deg,{ACCENT},#B5845A);border-radius:8px;
                padding:12px 14px;margin-bottom:14px;text-align:center;">
      <div style="font-size:10px;color:white;font-weight:700;letter-spacing:2px;">
        🎛️ EXPLORE THE DATA
      </div>
      <div style="font-size:9px;color:rgba(255,255,255,0.75);margin-top:3px;">
        Use filters below to drill into any time period or channel
      </div>
    </div>
    """),
    date_range,
    pn.layout.Divider(),
    channel_filter,
    pn.layout.Divider(),
    pn.pane.HTML(f"""
    <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.9;">
      <div style="color:{TEXT_LT};font-weight:600;margin-bottom:8px;font-size:12px;">
        3 AI Use Cases
      </div>

      <div style="background:rgba(201,149,106,0.1);border:1px solid rgba(201,149,106,0.3);border-radius:6px;padding:8px 10px;margin-bottom:6px;">
        <span style="color:{ACCENT};font-weight:700;">① Return Rate Reduction</span><br>
        <span style="font-size:10px;">Saves €20K–€60K/year</span>
      </div>

      <div style="background:rgba(107,143,113,0.1);border:1px solid rgba(107,143,113,0.3);border-radius:6px;padding:8px 10px;margin-bottom:6px;">
        <span style="color:{TEAL};font-weight:700;">② Product Recommendations</span><br>
        <span style="font-size:10px;">+€150K–€400K revenue</span>
      </div>

      <div style="background:rgba(166,123,138,0.1);border:1px solid rgba(166,123,138,0.3);border-radius:6px;padding:8px 10px;margin-bottom:14px;">
        <span style="color:{PURPLE};font-weight:700;">③ Support Automation</span><br>
        <span style="font-size:10px;">10–15 hrs saved/week</span>
      </div>

      <div style="color:{TEXT_LT};font-weight:600;margin-bottom:4px;">Dataset</div>
      H&M Kaggle — 500K rows<br>
      Sep 2018 → Sep 2020<br><br>
      <div style="color:{TEXT_LT};font-weight:600;margin-bottom:4px;">How to read</div>
      <span style="font-size:10px;">Each chart has a coloured insight box below it — connecting the data directly to Balando's AI opportunity.</span>
    </div>
    """),
    width=260,
    styles={"background": "#FFFFFF", "padding": "16px", "overflow": "hidden", "border-right": "1px solid #E8E0D5"},
)

# ── N8N Demo Section ──────────────────────────────────────────────────────────
# Screenshots loaded via _img_src() below

n8n_divider = pn.pane.HTML(f"""
<div style="margin:40px 0 0 0;">
  <div style="height:3px;background:linear-gradient(90deg,{ACCENT},{TEAL},{PURPLE});
              border-radius:2px;margin-bottom:28px;"></div>
  <div style="background:#3D2B1F;
              border:1px solid rgba(201,149,106,0.4);border-radius:12px;
              padding:28px 32px;margin-bottom:8px;">
    <div style="font-size:9px;color:{ACCENT};font-weight:700;letter-spacing:3px;
                text-transform:uppercase;margin-bottom:10px;">
      ⚡ LIVE IMPLEMENTATION DEMO — USE CASE 3
    </div>
    <div style="font-size:26px;font-weight:800;color:#F5EFE6;line-height:1.25;margin-bottom:10px;">
      Automated AI Return Risk Assistant
      <span style="color:{ACCENT};"> Proposal for Chleo &amp; Balando GmbH</span>
    </div>
    <div style="font-size:13px;color:#C8BAA8;max-width:820px;line-height:1.7;">
      The workflow below was built and tested live during this engagement using
      <b style="color:#F5EFE6;">n8n Cloud + GPT-4o</b>.
      It demonstrates exactly how Balando's return risk alerts would work in production —
      a real order triggers a real AI assessment and a branded email lands in the operations
      team's inbox within seconds. Every decision is logged and fully auditable.
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

n8n_flow = pn.pane.HTML(f"""
<div style="background:{CARD_BG};border-radius:10px;padding:22px 28px;margin-bottom:6px;">
  <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:2px;margin-bottom:16px;">
    THE WORKFLOW — 6 NODES, FULLY AUTOMATED
  </div>
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;">
    {''.join([f"""
    <div style="background:{bg};border:1px solid {border};border-radius:6px;
                padding:10px 14px;text-align:center;min-width:115px;">
      <div style="font-size:16px;margin-bottom:4px;">{icon}</div>
      <div style="font-size:10px;font-weight:700;color:{TEXT_LT};">{label}</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:2px;">{sub}</div>
    </div>
    <div style="font-size:18px;color:{TEXT_MUTED};padding:0 2px;">→</div>
    """ for icon, label, sub, bg, border in [
        ("🔗", "Webhook",     "POST trigger",    f"rgba(233,69,96,0.1)",  ACCENT),
        ("📋", "Edit Fields", "Mock order data", f"rgba(15,110,140,0.1)", TEAL),
        ("🤖", "GPT-4o",      "Score risk",      f"rgba(240,165,0,0.1)",  AMBER),
        ("⚙️", "Code Node",   "Parse JSON",      f"rgba(46,204,113,0.1)", GREEN),
        ("🔀", "IF Node",     "HIGH or LOW?",    f"rgba(155,89,182,0.1)", PURPLE),
    ]])}
    <div style="display:flex;flex-direction:column;gap:6px;">
      <div style="background:rgba(233,69,96,0.1);border:1px solid {ACCENT};
                  border-radius:6px;padding:8px 14px;text-align:center;min-width:115px;">
        <div style="font-size:14px;margin-bottom:2px;">📧</div>
        <div style="font-size:10px;font-weight:700;color:{ACCENT};">Gmail Alert</div>
        <div style="font-size:9px;color:{TEXT_MUTED};">HIGH risk → fires</div>
      </div>
      <div style="background:{CARD_BG};border:1px solid {GRID_CLR};
                  border-radius:6px;padding:8px 14px;text-align:center;min-width:115px;">
        <div style="font-size:14px;margin-bottom:2px;">🔇</div>
        <div style="font-size:10px;font-weight:700;color:{TEXT_MUTED};">No-op</div>
        <div style="font-size:9px;color:{TEXT_MUTED};">LOW risk → silent</div>
      </div>
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

n8n_screenshots_header = pn.pane.HTML(f"""
<div style="margin-top:8px;">
  <div style="font-size:9px;color:{ACCENT};font-weight:700;letter-spacing:2px;
              text-transform:uppercase;margin-bottom:8px;">
    📸 LIVE TEST RESULTS — CAPTURED DURING THIS ENGAGEMENT
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
    <div style="background:{CARD_BG};border-left:3px solid {GREEN};
                border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{GREEN};">✅ HIGH RISK — TRUE BRANCH</div>
      <div style="font-size:11px;color:{TEXT_MUTED};margin-top:3px;">
        Dress · Size M · First purchase · Germany → score 85/100 → email fires
      </div>
    </div>
    <div style="background:{CARD_BG};border-left:3px solid {TEAL};
                border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{TEAL};">🔇 LOW RISK — FALSE BRANCH</div>
      <div style="font-size:11px;color:{TEXT_MUTED};margin-top:3px;">
        Socks · Returning customer → low risk → no email, silent log
      </div>
    </div>
    <div style="background:{CARD_BG};border-left:3px solid {AMBER};
                border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{AMBER};">📧 CHLEO'S INBOX</div>
      <div style="font-size:11px;color:{TEXT_MUTED};margin-top:3px;">
        Branded alert · Risk score · Top reason · Recommended action
      </div>
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

# Screenshots rendered as pure HTML grid — no Panel layout overhead, no gap
GITHUB_BASE = "https://raw.githubusercontent.com/frostyxy-source/project5/main/assets"

def _img_src(filename):
    local = os.path.join(DATA_DIR, filename)
    if os.path.exists(local):
        import base64
        with open(local, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    return f"{GITHUB_BASE}/{filename}"

n8n_screenshots = pn.pane.HTML(
    lightbox_js +
    f'''<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:0;">
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_img_src("true.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_img_src("false.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_img_src("email.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
</div>''',
    sizing_mode="stretch_width",
)

n8n_cost = pn.pane.HTML(f"""
<div style="background:{CARD_BG};border-radius:10px;padding:22px 28px;margin-top:8px;">
  <div style="font-size:9px;color:{AMBER};font-weight:700;letter-spacing:2px;margin-bottom:14px;">
    💰 COST BREAKDOWN — GPT-4o PRICING (MARCH 2026)
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
    {''.join([f"""
    <div style="background:{BG};border-radius:6px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{col};">{val}</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:4px;text-transform:uppercase;
                  letter-spacing:1px;">{lbl}</div>
    </div>
    """ for val, col, lbl in [
        ("~$0.01",    AMBER,  "cost per alert email"),
        ("~$3–5",     GREEN,  "cost per 500 orders/day"),
        ("~$30–50",   TEAL,   "cost per month (5K orders)"),
        ("€20K–60K",  ACCENT, "estimated annual saving"),
    ]])}
  </div>
  <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.7;
              border-top:1px solid {GRID_CLR};padding-top:12px;">
    <b style="color:{TEXT_LT};">How the cost is calculated:</b>
    Each order sends ~400 tokens to GPT-4o (system prompt + order details) and receives
    ~100 tokens back (JSON risk score). At GPT-4o pricing of $2.50/1M input tokens and
    $10/1M output tokens, each call costs approximately
    <b style="color:{AMBER};">$0.001–0.002</b>.
    Even at 1,000 orders/day the monthly AI cost is under <b style="color:{AMBER};">$60</b> —
    against a logistics saving of <b style="color:{GREEN};">€1,500–5,000/month</b>.
    ROI is positive from day one.
  </div>
</div>
""", sizing_mode="stretch_width")

n8n_production = pn.pane.HTML(f"""
<div style="background:{CARD_BG};border-radius:10px;padding:22px 28px;margin-top:8px;">
  <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:2px;margin-bottom:14px;">
    🔌 FROM MOCK DATA TO BALANDO'S REAL WEBSHOP — 3 STEPS
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px;">
    {''.join([f"""
    <div style="background:{BG};border-radius:8px;padding:16px;border-top:3px solid {border};">
      <div style="font-size:22px;margin-bottom:8px;">{icon}</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:6px;">{title}</div>
      <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.65;">{body}</div>
    </div>
    """ for icon, title, body, border in [
        ("🛒", "Connect Shopify or Shopware",
         "Replace the 'Edit Fields' mock node with a Shopify trigger node. Every real order placed on Balando's store automatically fires the workflow. Takes ~15 minutes with an API key.",
         TEAL),
        ("🎯", "Enrich with Customer History",
         "Add a database lookup node between the trigger and GPT-4o. Pull the customer's return history and feed it into the prompt — GPT-4o now knows if this customer has returned before.",
         AMBER),
        ("⚡", "Close the Loop",
         "Add a Shopify node after the Gmail alert to tag the order as 'high-return-risk' in the backend automatically. The warehouse team sees the flag before picking and packing.",
         ACCENT),
    ]])}
  </div>
  <div style="background:rgba(15,110,140,0.1);border:1px solid {TEAL};
              border-radius:6px;padding:12px 16px;">
    <span style="font-size:10px;font-weight:700;color:{TEAL};">⏱ ESTIMATED PRODUCTION SETUP: </span>
    <span style="font-size:10px;color:{TEXT_LT};">
      2–3 days for a developer with Shopify API access. The n8n workflow built here
      is already 80% of the final product — the core AI logic requires zero changes.
    </span>
  </div>
</div>
""", sizing_mode="stretch_width")

n8n_future = pn.pane.HTML(f"""
<div style="background:linear-gradient(135deg,{CARD_BG} 0%,#0d1117 100%);
            border:1px solid rgba(233,69,96,0.2);border-radius:10px;
            padding:22px 28px;margin-top:8px;margin-bottom:20px;">
  <div style="font-size:9px;color:{ACCENT};font-weight:700;letter-spacing:2px;margin-bottom:6px;">
    🚀 WHAT ELSE WE CAN BUILD — IF BALANDO CHOOSES US
  </div>
  <div style="font-size:12px;color:{TEXT_MUTED};margin-bottom:16px;">
    The infrastructure built for this demo is reusable. Every additional use case plugs into
    the same n8n + GPT-4o stack — no new tools, no new vendors, no new learning curve.
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    {''.join([f"""
    <div style="background:{BG};border-radius:8px;padding:14px 16px;border-left:3px solid {border};">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
        <span style="font-size:16px;">{icon}</span>
        <span style="font-size:11px;font-weight:700;color:{TEXT_LT};">{title}</span>
        <span style="margin-left:auto;font-size:8px;font-weight:700;color:{border};
                     background:rgba(255,255,255,0.05);padding:2px 6px;border-radius:10px;">
          {tag}
        </span>
      </div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.6;">{body}</div>
    </div>
    """ for icon, title, body, border, tag in [
        ("🎯", "Personalised Email Recommendations",
         "Order confirmed → GPT-4o generates 3 personalised product picks → Klaviyo sends branded email. Same n8n stack. Target: +5–10pp repeat purchase rate.",
         TEAL, "USE CASE 2"),
        ("💬", "Customer Support Auto-Classifier",
         "Inbound email → GPT-4o classifies intent → drafts reply with live order data → sends automatically or routes to agent. Target: 30–40% tickets resolved with zero agent time.",
         PURPLE, "USE CASE 3"),
        ("📊", "Weekly AI Insight Digest for Chleo",
         "Every Monday: n8n pulls KPIs → GPT-4o writes a 5-bullet executive summary with anomalies flagged → lands in Chleo's inbox before 8am. Zero manual reporting.",
         AMBER, "BONUS"),
        ("⚠️", "Stockout &amp; Overstock Early Warning",
         "Daily inventory check: top SKU drops below threshold → GPT-4o drafts reorder recommendation → alert to buying team. Prevents lost sales and markdown waste.",
         GREEN, "BONUS"),
    ]])}
  </div>
  <div style="margin-top:16px;background:#3D2B1F;border:1px solid {ACCENT};
              border-radius:8px;padding:16px 20px;text-align:center;">
    <div style="font-size:13px;font-weight:700;color:#F5EFE6;margin-bottom:4px;">
      All four use cases. Same stack. Phased rollout. Full transparency.
    </div>
    <div style="font-size:11px;color:#C8BAA8;">
      Every AI decision logged in real time · Human override on every automated action ·
      No black boxes · No vendor lock-in · Built for a team of 50–250, not 5,000.
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")


# ── LangSmith Monitoring Section ─────────────────────────────────────────────
GH_RAW = "https://raw.githubusercontent.com/frostyxy-source/project5/main/assets"

def _ls_img(filename):
    local = os.path.join(DATA_DIR, filename)
    if os.path.exists(local):
        import base64
        with open(local, "rb") as f2:
            b64 = base64.b64encode(f2.read()).decode()
        return f"data:image/png;base64,{b64}"
    return f"{GH_RAW}/{filename}"

ls_divider = pn.pane.HTML(f"""
<div style="margin:40px 0 0 0;">
  <div style="height:3px;background:linear-gradient(90deg,{TEAL},{GREEN},{AMBER});
              border-radius:2px;margin-bottom:28px;"></div>
  <div style="background:#1E3028;
              border:1px solid rgba(107,143,113,0.4);border-radius:12px;
              padding:28px 32px;margin-bottom:8px;">
    <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:3px;
                text-transform:uppercase;margin-bottom:10px;">
      MONITORING DEMO — USE CASE 2
    </div>
    <div style="font-size:26px;font-weight:800;color:#F0F5F1;line-height:1.25;margin-bottom:10px;">
      LangSmith Monitoring —
      <span style="color:{TEAL};"> The Answer to the Black Box Problem</span>
    </div>
    <div style="font-size:13px;color:#B8CCBE;max-width:820px;line-height:1.7;">
      Chleo asked: <b style="color:#F0F5F1;">"AI is a black box — I cannot see what it is doing."</b>
      This is the direct answer. Every GPT-4o recommendation call is fully logged in LangSmith —
      the exact customer profile sent in, the exact recommendations returned, token usage, latency,
      and cost per call. Nothing is hidden. Every decision is auditable, timestamped and searchable.
      Built using <b style="color:#F0F5F1;">LangChain + GPT-4o + real H&amp;M customer data</b>
      as a proxy for Balando's own customer base.
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

ls_captures = pn.pane.HTML(f"""
<div style="background:{CARD_BG};border-radius:10px;padding:22px 28px;margin-bottom:8px;">
  <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:2px;margin-bottom:14px;">
    WHAT LANGSMITH CAPTURES PER AI CALL — AUTOMATICALLY
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;">
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {TEAL};">
      <div style="font-size:18px;margin-bottom:6px;">📥</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Full Input</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Exact customer profile sent to GPT-4o — age, purchase history, colours, price range.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {GREEN};">
      <div style="font-size:18px;margin-bottom:6px;">📤</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Full Output</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">3 recommendations returned — product, colour, price range and personalised reason.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {AMBER};">
      <div style="font-size:18px;margin-bottom:6px;">⚡</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Latency and Tokens</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Response time in ms, input tokens (541), output tokens (278), total (819) per call.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {ACCENT};">
      <div style="font-size:18px;margin-bottom:6px;">💰</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Cost Per Call</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Exact USD cost logged per run. 10 calls cost ~$0.02 total. No surprise bills.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {PURPLE};">
      <div style="font-size:18px;margin-bottom:6px;">🏷️</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Metadata Tags</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Every run tagged: customer_age, top_category, use_case, club_member for filtering.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {TEAL};">
      <div style="font-size:18px;margin-bottom:6px;">🔎</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Searchable</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Filter by tag, date, model or outcome. Find any decision ever made instantly.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {GREEN};">
      <div style="font-size:18px;margin-bottom:6px;">✅</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Pass/Fail Status</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Each run shows green (success) or red (error). Failed calls flagged for review immediately.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:14px;border-top:3px solid {AMBER};">
      <div style="font-size:18px;margin-bottom:6px;">📊</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:4px;">Dataset Linked</div>
      <div style="font-size:10px;color:{TEXT_MUTED};line-height:1.55;">Every run linked to balando-recommendation-dataset — input vs output at a glance.</div>
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

ls_screenshots_header = pn.pane.HTML(f"""
<div style="margin-top:4px;">
  <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:2px;
              text-transform:uppercase;margin-bottom:8px;">
    LIVE LANGSMITH SCREENSHOTS — CAPTURED DURING THIS ENGAGEMENT
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:8px;">
    <div style="background:{CARD_BG};border-left:3px solid {TEAL};border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{TEAL};">📊 10 Traced Runs</div>
      <div style="font-size:10px;color:{TEXT_MUTED};margin-top:3px;">All 10 GPT-4o calls with status and latency</div>
    </div>
    <div style="background:{CARD_BG};border-left:3px solid {GREEN};border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{GREEN};">👤 Customer Input</div>
      <div style="font-size:10px;color:{TEXT_MUTED};margin-top:3px;">Exact profile sent — age, history, colours</div>
    </div>
    <div style="background:{CARD_BG};border-left:3px solid {AMBER};border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{AMBER};">🎯 Recommendations Output</div>
      <div style="font-size:10px;color:{TEXT_MUTED};margin-top:3px;">3 personalised picks with confidence score</div>
    </div>
    <div style="background:{CARD_BG};border-left:3px solid {PURPLE};border-radius:6px;padding:10px 14px;">
      <div style="font-size:10px;font-weight:700;color:{PURPLE};">📝 Full Prompt Visible</div>
      <div style="font-size:10px;color:{TEXT_MUTED};margin-top:3px;">System + user message fully inspectable</div>
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

ls_screenshots = pn.pane.HTML(
    f'''<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:8px;">
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_ls_img("balando-uc2-recommendations10call.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_ls_img("customerprofile.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_ls_img("recommendations.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
  <div style="background:#EAF4FB;border:2px solid #B8D9EE;border-radius:10px;
              padding:10px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
    <img src="{_ls_img("balandolangsmithprompt.png")}" class="lb-thumb"
         onclick="openLB(this.src)"
         style="width:100%;border-radius:6px;display:block;" />
  </div>
</div>''',
    sizing_mode="stretch_width",
)

ls_cost = pn.pane.HTML(f"""
<div style="background:{CARD_BG};border-radius:10px;padding:22px 28px;margin-top:4px;">
  <div style="font-size:9px;color:{AMBER};font-weight:700;letter-spacing:2px;margin-bottom:14px;">
    COST BREAKDOWN — LANGSMITH + GPT-4o RECOMMENDATION ENGINE
  </div>
  <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
    <div style="background:{BG};border-radius:6px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{AMBER};">~$0.002</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:4px;text-transform:uppercase;letter-spacing:1px;">cost per recommendation call</div>
    </div>
    <div style="background:{BG};border-radius:6px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{GREEN};">~$0.02</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:4px;text-transform:uppercase;letter-spacing:1px;">cost for 10 customer profiles</div>
    </div>
    <div style="background:{BG};border-radius:6px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{TEAL};">~$6-10</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:4px;text-transform:uppercase;letter-spacing:1px;">cost per month (5K customers)</div>
    </div>
    <div style="background:{BG};border-radius:6px;padding:14px;text-align:center;">
      <div style="font-size:20px;font-weight:800;color:{ACCENT};">+150-400K EUR</div>
      <div style="font-size:9px;color:{TEXT_MUTED};margin-top:4px;text-transform:uppercase;letter-spacing:1px;">estimated annual revenue uplift</div>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;
              border-top:1px solid {GRID_CLR};padding-top:14px;">
    <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.7;">
      <b style="color:{TEXT_LT};">How the cost is calculated:</b>
      Each call sends ~541 input tokens and receives ~278 output tokens.
      At GPT-4o pricing of $2.50/1M input and $10/1M output tokens,
      each call costs <b style="color:{AMBER};">~$0.002</b>.
      For 5,000 active customers receiving monthly recommendations the monthly AI cost is
      <b style="color:{AMBER};">~$10</b> — against a revenue uplift of
      <b style="color:{GREEN};">150K-400K EUR/year</b>.
    </div>
    <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.7;">
      <b style="color:{TEXT_LT};">LangSmith monitoring cost:</b>
      Free tier includes <b style="color:{GREEN};">5,000 traces/month</b> at zero cost.
      For Balando's scale the free tier covers full monitoring with no additional cost.
      Paid tier starts at $39/month for unlimited traces if scale requires it.
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

ls_production = pn.pane.HTML(f"""
<div style="background:linear-gradient(135deg,{CARD_BG} 0%,#0d1117 100%);
            border:1px solid rgba(15,110,140,0.2);border-radius:10px;
            padding:22px 28px;margin-top:8px;margin-bottom:20px;">
  <div style="font-size:9px;color:{TEAL};font-weight:700;letter-spacing:2px;margin-bottom:14px;">
    HOW THIS CONNECTS TO BALANDO'S REAL DATA — 3 STEPS
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px;">
    <div style="background:{BG};border-radius:8px;padding:16px;border-top:3px solid {TEAL};">
      <div style="font-size:22px;margin-bottom:8px;">🛒</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:6px;">Replace H&amp;M Proxy with Balando Data</div>
      <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.65;">dataset_creation.py reads from H&M Kaggle as a proxy. In production point it at Balando's Shopify order export. Same script, same LangSmith setup, real customer data.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:16px;border-top:3px solid {GREEN};">
      <div style="font-size:22px;margin-bottom:8px;">⚙️</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:6px;">Automate via n8n</div>
      <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.65;">Connect to the n8n workflow already built. After an order is placed, n8n calls the recommendation engine, GPT-4o generates picks, LangSmith logs the call, Klaviyo sends the email.</div>
    </div>
    <div style="background:{BG};border-radius:8px;padding:16px;border-top:3px solid {AMBER};">
      <div style="font-size:22px;margin-bottom:8px;">📊</div>
      <div style="font-size:11px;font-weight:700;color:{TEXT_LT};margin-bottom:6px;">Monitor in Real Time</div>
      <div style="font-size:10.5px;color:{TEXT_MUTED};line-height:1.65;">Every recommendation logged in LangSmith. Chleo can log in at any time and see exactly what the AI recommended, to whom, why, and at what cost. No black boxes — ever.</div>
    </div>
  </div>
  <div style="background:#1E3028;border:1px solid {TEAL};
              border-radius:8px;padding:14px 18px;text-align:center;">
    <div style="font-size:12px;font-weight:700;color:#F0F5F1;margin-bottom:4px;">
      H&amp;M dataset used as proxy · Same DACH market · Same demographics · Same pain points
    </div>
    <div style="font-size:10px;color:#B8CCBE;">
      31M transactions · European fashion · Age 20-65 · Every pattern in this demo exists in Balando's business today
    </div>
  </div>
</div>
""", sizing_mode="stretch_width")

# ── Main layout ───────────────────────────────────────────────────────────────
main = pn.Column(
    header,
    pn.Spacer(height=10),
    sec("KEY METRICS — WHERE THE OPPORTUNITY IS"),
    kpi_row,
    pn.Spacer(height=8),
    sec("SALES PATTERN — WHEN TO ACTIVATE AI"),
    c_revenue, i_revenue,
    pn.Spacer(height=6),
    sec("WHAT CUSTOMERS RETURN — THE COST AI DIRECTLY REDUCES"),
    c_returns, i_returns,
    pn.Spacer(height=6),
    sec("PRODUCT & CHANNEL — WHERE AI RECOMMENDS FIRST"),
    pn.Row(
        pn.Column(c_products, i_products, sizing_mode="stretch_width"),
        pn.Column(c_channel,  i_channel,  sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    ),
    pn.Spacer(height=6),
    sec("GARMENT RISK & CUSTOMER PROFILE"),
    pn.Row(
        pn.Column(c_garment, i_garment, sizing_mode="stretch_width"),
        pn.Column(c_age,     i_age,     sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    ),
    pn.Spacer(height=6),
    sec("COLOUR INTELLIGENCE & LOYALTY — THE BIGGEST WINS"),
    pn.Row(
        pn.Column(c_colours, i_colours, sizing_mode="stretch_width"),
        pn.Column(c_repeat,  i_repeat,  sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    ),
    # ── N8N Demo Section ──────────────────────────────────────────────────────
    n8n_divider,
    n8n_flow,
    n8n_screenshots_header,
    n8n_screenshots,
    n8n_cost,
    n8n_production,
    n8n_future,
    # ── LangSmith Section ────────────────────────────────────────────────────
    ls_divider,
    ls_captures,
    ls_screenshots_header,
    ls_screenshots,
    ls_cost,
    ls_production,
    styles={"background": "#EDE8DF", "padding": "16px"},
    sizing_mode="stretch_width",
)

dashboard = pn.template.FastListTemplate(
    title             ="Balando — AI Opportunity Dashboard",
    header_background = "#FFFFFF",
    accent_base_color = "#C9956A",
    theme             ="default",
    sidebar           =[sidebar],
    main              =[main],
)

dashboard.servable()
