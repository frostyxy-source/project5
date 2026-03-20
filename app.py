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

# ── Colours ───────────────────────────────────────────────────────────────────
BG         = "#1A1A2E"
CARD_BG    = "#16213E"
ACCENT     = "#E94560"
TEAL       = "#0F6E8C"
GREEN      = "#2ECC71"
AMBER      = "#F0A500"
PURPLE     = "#9B59B6"
TEXT_LT    = "#F5F5F5"
TEXT_MUTED = "#94A3B8"
GRID_CLR   = "#2A2A4A"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(color=TEXT_LT, family="Arial"),
    xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
    yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR),
    margin=dict(l=40, r=20, t=45, b=40),
)

# ── Data loading ──────────────────────────────────────────────────────────────
DATA_DIR  = "/tmp/data"
FOLDER_ID = "1aJZulbtsffKJK54CkvY62eS2n7iIllwq"
EXPECTED  = ["articles_sample.csv", "customers_sample.csv", "transactions_sample_500k.csv"]

def load_data():
    pathlib.Path(DATA_DIR).mkdir(parents=True, exist_ok=True)

    if not all(os.path.exists(os.path.join(DATA_DIR, f)) for f in EXPECTED):
        print("Downloading data from Google Drive...")
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
    <div style="background:{CARD_BG};border-left:4px solid {colour};
                border-radius:6px;padding:14px 18px;margin-top:6px;margin-bottom:8px;">
      <div style="font-size:10px;color:{colour};font-weight:700;letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:6px;">
        {icon} AI Use Case {uc_num} — {uc_label}
      </div>
      <div style="font-size:12px;color:{TEXT_MUTED};line-height:1.65;">{body_html}</div>
    </div>
    """, sizing_mode="stretch_width")

def kpi_card(label, value, sub, colour=ACCENT):
    return pn.pane.HTML(f"""
    <div style="background:{CARD_BG};border-left:4px solid {colour};
                border-radius:8px;padding:16px 20px;">
      <div style="font-size:10px;color:{TEXT_MUTED};letter-spacing:1px;
                  text-transform:uppercase;margin-bottom:4px;">{label}</div>
      <div style="font-size:26px;font-weight:700;color:{TEXT_LT};margin-bottom:3px;">{value}</div>
      <div style="font-size:10px;color:{colour};font-style:italic;">{sub}</div>
    </div>
    """, sizing_mode="stretch_width")

def sec(label):
    return pn.pane.HTML(
        f"""<div style="color:{TEXT_MUTED};font-size:10px;font-weight:700;
        letter-spacing:2px;text-transform:uppercase;
        padding:10px 0 4px;border-bottom:1px solid {GRID_CLR};
        margin-bottom:2px;">{label}</div>""",
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
    fig.update_traces(line_color=ACCENT, line_width=2.5,
                      fill="tozeroy", fillcolor="rgba(233,69,96,0.08)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_products(*_):
    d = (filtered().groupby("product_type_name")["price"].sum()
         .nlargest(15).reset_index().sort_values("price"))
    fig = px.bar(d, x="price", y="product_type_name", orientation="h",
                 title="Where should the recommendation engine focus first?",
                 labels={"price": "Revenue (normalised)", "product_type_name": ""})
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(**PLOTLY_LAYOUT, height=360)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=360)

@pn.depends(date_range, channel_filter)
def c_channel(*_):
    d   = filtered().groupby("channel_label")["price"].sum().reset_index()
    fig = px.pie(d, names="channel_label", values="price",
                 title="Online dominates — where AI delivers the highest ROI",
                 color_discrete_sequence=[ACCENT, TEAL])
    fig.update_layout(**PLOTLY_LAYOUT, legend=dict(font=dict(color=TEXT_LT)))
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_garment(*_):
    d = (filtered().groupby("garment_group_name")["price"].sum()
         .nlargest(10).reset_index().sort_values("price"))
    fig = px.bar(d, x="price", y="garment_group_name", orientation="h",
                 title="High-revenue garment groups = highest return risk — AI targets these first",
                 labels={"price": "Revenue (normalised)", "garment_group_name": ""})
    fig.update_traces(marker_color=AMBER)
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=300)

@pn.depends(date_range, channel_filter)
def c_age(*_):
    ages = filtered()["age"].dropna()
    fig  = px.histogram(ages, x="age", nbins=10,
                        title="Your core customer is 25–45 — they expect personalisation as standard",
                        labels={"age": "Age group", "count": "Customers"})
    fig.update_traces(marker_color=PURPLE)
    fig.update_layout(**PLOTLY_LAYOUT)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=260)

@pn.depends(date_range, channel_filter)
def c_colours(*_):
    d   = (filtered().groupby("colour_group_name")["price"].sum()
           .nlargest(20).reset_index())
    fig = px.treemap(d, path=["colour_group_name"], values="price",
                     title="Colour demand is concentrated — AI prevents stockouts on core colours",
                     color="price",
                     color_continuous_scale=["#16213E", ACCENT])
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
        "One-time buyer":       ACCENT,
        "2–3 purchases":        AMBER,
        "4+ purchases (loyal)": GREEN,
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
                 color_continuous_scale=["#0F6E8C", "#F0A500", "#E94560"],
                 text=top["return_rate"].apply(lambda x: f"{x}% return rate"))
    fig.update_traces(textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False, height=380)
    return pn.pane.Plotly(fig, sizing_mode="stretch_width", height=380)

# ── Insight boxes ─────────────────────────────────────────────────────────────
i_revenue  = insight_box(2, "Product Recommendations",
    "Revenue dips in summer and spikes pre-winter. An AI recommendation engine automatically "
    "triggers personalised re-engagement emails during slow periods. "
    "<b style='color:#F5F5F5;'>Industry benchmark: personalised emails generate 3–5× higher "
    "click rates than generic newsletters.</b>", TEAL)

i_products = insight_box(2, "Product Recommendations",
    "Top 5 product types generate the majority of revenue. An AI model learns that a customer "
    "buying a dress is highly likely to want coordinating basics or shoes next. "
    "<b style='color:#F5F5F5;'>Recommending the right product increases average order value "
    "by 8–15% — with zero extra acquisition cost.</b>", TEAL)

i_channel  = insight_box(3, "Customer Support Automation",
    "The majority of revenue is online → the majority of support tickets also arrive digitally. "
    "The n8n automation workflow auto-classifies and drafts replies to the 3 most common query types. "
    "<b style='color:#F5F5F5;'>Automating 30–40% of inbound tickets frees 10–15 hours "
    "of agent time per week.</b>", PURPLE)

i_garment  = insight_box(1, "Return Rate Reduction",
    "Jersey basics, trousers and dresses are highest-revenue — and most returned. "
    "A return prediction model flags high-risk orders at checkout and shows a size guide. "
    "<b style='color:#F5F5F5;'>Estimated saving: 10–15pp reduction = €30K–€60K/year "
    "on a €5M revenue base.</b>", ACCENT)

i_age      = insight_box(2, "Product Recommendations",
    "The 25–45 demographic is the most digitally native segment. "
    "<b style='color:#F5F5F5;'>81% prefer brands that offer personalised experiences</b> — "
    "and they switch to competitors that do. AI recommendations give Balando the same capability "
    "as Zalando without Zalando's engineering budget.", TEAL)

i_colours  = insight_box(1, "Return Rate Reduction",
    "Black, grey, white and dark blue account for the majority of revenue — consistent across "
    "all European fashion markets. "
    "<b style='color:#F5F5F5;'>AI demand forecasting ensures Balando never stockouts on core "
    "colours while avoiding overstock</b> that ends in 30–50% markdown losses.", ACCENT)

i_repeat   = insight_box(2, "Product Recommendations",
    "The majority of customers buy once and never return. "
    "<b style='color:#F5F5F5;'>Acquiring a new customer costs 5–7× more than retaining one.</b> "
    "Moving just 10% of one-time buyers to a second purchase through a personalised email "
    "can increase annual revenue by 8–12% with near-zero incremental cost.", GREEN)

i_returns  = insight_box(1, "Return Rate Reduction",
    "<b style='color:#F5F5F5;'>Germany has the highest fashion return rate in Europe — "
    "up to 52% for dresses and skirts</b> (University of Bamberg / EHI 2024). "
    "An AI return prediction model scores every order at checkout. "
    "A 10pp reduction saves €30K–€60K/year in direct logistics costs alone.", ACCENT)

# ── Layout ────────────────────────────────────────────────────────────────────
header = pn.pane.HTML(f"""
<div style="position:relative;overflow:hidden;background:linear-gradient(135deg,{BG} 0%,#0d1117 100%);
            padding:32px 36px 28px;border-bottom:2px solid {ACCENT};">

  <!-- Fashion SVG background decorations -->
  <svg style="position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;opacity:0.07;"
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
      <div style="font-size:10px;color:{ACCENT};letter-spacing:3px;font-weight:700;">
        ✦ BALANDO GMBH — CONFIDENTIAL ✦
      </div>
    </div>

    <div style="font-size:28px;font-weight:800;color:{TEXT_LT};margin-bottom:6px;
                letter-spacing:-0.5px;line-height:1.2;">
      AI-Powered Proposal Plan
      <span style="color:{ACCENT};"> for Balando GmbH</span>
    </div>

    <div style="font-size:12px;color:{TEXT_MUTED};margin-bottom:20px;">
      Prepared for <b style="color:{TEXT_LT};">Chleo, CEO</b> &nbsp;·&nbsp;
      H&amp;M European Fashion Dataset · DACH Market Proxy &nbsp;·&nbsp;
      <b style="color:{ACCENT};">March 2026</b>
    </div>

    <!-- Executive Summary -->
    <div style="background:rgba(22,33,62,0.85);border:1px solid rgba(233,69,96,0.3);
                border-radius:10px;padding:18px 22px;backdrop-filter:blur(4px);
                max-width:900px;">
      <div style="font-size:10px;color:{ACCENT};font-weight:700;letter-spacing:2px;
                  text-transform:uppercase;margin-bottom:12px;">
        ⚡ Executive Summary — 3 Things You Need to Know
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">

        <div style="border-left:3px solid {ACCENT};padding-left:12px;">
          <div style="font-size:10px;color:{ACCENT};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">🔴 Biggest Problem</div>
          <div style="font-size:12px;color:{TEXT_LT};font-weight:600;margin-bottom:3px;">
            40–50% return rate
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            Germany's fashion return rate is the highest in Europe. On a €5M revenue base
            this costs Balando an estimated <b style="color:{TEXT_LT};">€100K–€200K/year</b>
            in direct logistics alone.
          </div>
        </div>

        <div style="border-left:3px solid {TEAL};padding-left:12px;">
          <div style="font-size:10px;color:{TEAL};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">🟢 Biggest Opportunity</div>
          <div style="font-size:12px;color:{TEXT_LT};font-weight:600;margin-bottom:3px;">
            Most customers never return
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            Over 60% of customers buy once and disappear. A personalised AI recommendation
            engine moving just <b style="color:{TEXT_LT};">10% to a second purchase</b>
            adds €150K–€400K in annual revenue — at zero acquisition cost.
          </div>
        </div>

        <div style="border-left:3px solid {AMBER};padding-left:12px;">
          <div style="font-size:10px;color:{AMBER};font-weight:700;text-transform:uppercase;
                      letter-spacing:1px;margin-bottom:4px;">⚡ Recommended First Step</div>
          <div style="font-size:12px;color:{TEXT_LT};font-weight:600;margin-bottom:3px;">
            Start with support automation
          </div>
          <div style="font-size:11px;color:{TEXT_MUTED};line-height:1.5;">
            The fastest win: automate 30–40% of inbound support emails with n8n + AI.
            <b style="color:{TEXT_LT};">Live in 4–6 weeks.</b> Every AI decision is
            fully logged and visible — solving your transparency concern from day one.
          </div>
        </div>

      </div>
    </div>

    <!-- WHY H&M note -->
    <div style="margin-top:12px;background:rgba(15,110,140,0.15);border-radius:6px;
                padding:8px 14px;border-left:3px solid {AMBER};max-width:900px;">
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
    <div style="background:linear-gradient(135deg,{ACCENT},#c0392b);border-radius:8px;
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

      <div style="background:rgba(233,69,96,0.1);border-radius:6px;padding:8px 10px;margin-bottom:6px;">
        <span style="color:{ACCENT};font-weight:700;">① Return Rate Reduction</span><br>
        <span style="font-size:10px;">Saves €20K–€60K/year</span>
      </div>

      <div style="background:rgba(15,110,140,0.1);border-radius:6px;padding:8px 10px;margin-bottom:6px;">
        <span style="color:{TEAL};font-weight:700;">② Product Recommendations</span><br>
        <span style="font-size:10px;">+€150K–€400K revenue</span>
      </div>

      <div style="background:rgba(155,89,182,0.1);border-radius:6px;padding:8px 10px;margin-bottom:14px;">
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
    width=240,
    styles={"background": CARD_BG, "padding": "18px"},
)

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
    pn.Spacer(height=20),
    styles={"background": BG, "padding": "16px"},
    sizing_mode="stretch_width",
)

dashboard = pn.template.FastListTemplate(
    title             ="Balando — AI Opportunity Dashboard",
    header_background = BG,
    accent_base_color = ACCENT,
    theme             ="dark",
    sidebar           =[sidebar],
    main              =[main],
)

dashboard.servable()
