# Balando GmbH — LangSmith Monitoring Results
## Use Case 2: Personalised Product Recommendations

**Generated:** 2026-03-20 12:29
**Project:** `balando-uc2-recommendations` on LangSmith
**Dataset:** `balando-recommendation-dataset`
**Model:** GPT-4o

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total runs | 10 |
| Successful | 10 / 10 |
| Average latency | 5549ms |
| HIGH personalisation score | 10 / 10 runs |
| Average confidence | 85/100 |
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

### Run 01 — Customer Age 63

- **Status:** ✅ SUCCESS
- **Latency:** 5285ms
- **Personalisation Score:** HIGH
- **Confidence:** 80/100
- **Summary:** The recommendations focus on dresses and tops in your preferred colours and price range, aligning with your purchase history and style preferences.

**Recommendations:**

1. **Casual Summer Dress** (Dresses, Light Beige, €2–€5)
   > Given your previous purchase of a dress and preference for Light Beige, this casual summer dress is a perfect addition to your wardrobe.

2. **Knit Sweater** (Tops & Blouses, Greenish Khaki, €2–€5)
   > Since you have bought sweaters before and like Greenish Khaki, this knit sweater matches your style and keeps you cozy.

3. **Basic T-Shirt** (Tops & Blouses, Light Beige, €2–€5)
   > A basic T-shirt in Light Beige will seamlessly fit into your wardrobe, aligning with your colour preference and casual style.

---

### Run 02 — Customer Age 33

- **Status:** ✅ SUCCESS
- **Latency:** 6038ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on enhancing your accessories and swimwear collection with items that reflect your preferred colours and spending habits.

**Recommendations:**

1. **Silver Hoop Earrings** (Accessories, Silver, €1–€2)
   > Based on your previous purchase of earrings and preference for silver, these Silver Hoop Earrings are a perfect match.

2. **Light Pink Knotted Bikini Top** (Ladieswear, Light Pink, €1–€2)
   > Considering your last purchase was a bikini top and your fondness for light pink, this Light Pink Knotted Bikini Top aligns with your style.

3. **Black Lace Underwear Bottom** (Ladieswear, Black, €1–€2)
   > Given your purchase history of underwear bottoms and preference for black, this Black Lace Underwear Bottom would complement your collection.

---

### Run 03 — Customer Age 21

- **Status:** ✅ SUCCESS
- **Latency:** 4085ms
- **Personalisation Score:** HIGH
- **Confidence:** 90/100
- **Summary:** The recommendation strategy focuses on casual ladieswear in preferred colours within the customer's budget, enhancing their existing wardrobe.

**Recommendations:**

1. **Basic Cotton T-shirt** (Tops & Blouses, Dark Orange, €1–€2)
   > Since you have previously purchased a T-shirt and favour the colour Dark Orange, this Basic Cotton T-shirt aligns well with your preferences and spending habits.

2. **Grey Casual Tank Top** (Tops & Blouses, Grey, €1–€2)
   > Given your interest in casual wear and your preference for the colour Grey, the Grey Casual Tank Top is a great match for your style and budget.

3. **Orange Comfort Bikini Bottom** (Swimwear, Dark Orange, €1–€2)
   > Considering your previous purchase of a bikini top and your favourite colour being Dark Orange, the Orange Comfort Bikini Bottom would complete your swimwear set while staying within your typical price range.

---

### Run 04 — Customer Age 48

- **Status:** ✅ SUCCESS
- **Latency:** 5532ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on your favourite colours and categories, with products that match your purchasing habits and typical price range.

**Recommendations:**

1. **Luna Light Blue T-shirt** (Tops & Blouses, Light Blue, €2–€3)
   > Since you have previously purchased a t-shirt and light blue is one of your favourite colours, the Luna Light Blue T-shirt aligns well with both your style preferences and past purchases.

2. **Sienna Light Pink Scarf** (Accessories, Light Pink, €2–€3)
   > As a fan of light pink and having bought a scarf before, the Sienna Light Pink Scarf would be a perfect accessory to complement your collection.

3. **Georgia Dark Blue Midi Skirt** (Trousers & Skirts, Dark Blue, €2–€3)
   > Considering your preference for dark blue and your past purchase of trousers, the Georgia Dark Blue Midi Skirt could be a versatile addition to your wardrobe.

---

### Run 05 — Customer Age 21

- **Status:** ✅ SUCCESS
- **Latency:** 5543ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on affordable and stylish items in your favourite colours, aligning with your purchasing habits and spending preferences.

**Recommendations:**

1. **Basic Cotton T-Shirt** (Tops & Blouses, Black, €2–€3)
   > Since you enjoy versatile pieces and have purchased a blouse, this black basic cotton t-shirt fits well within your average spending range and matches your favourite colour.

2. **Casual Summer Dress** (Dresses, Light Pink, €2–€3)
   > Given your previous purchase of a dress and preference for light pink, this casual summer dress is a charming addition that aligns with your style and budget.

3. **Classic Knit Scarf** (Accessories, Dark Blue, €2–€3)
   > Since you appreciate dark blue and have shown interest in ladieswear, this classic knit scarf offers a stylish and practical accessory within your preferred price range.

---

### Run 06 — Customer Age 28

- **Status:** ✅ SUCCESS
- **Latency:** 5283ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on tops and skirts in your favorite colors and align with your typical spending range, enhancing your existing wardrobe preferences.

**Recommendations:**

1. **Basic White T-Shirt** (Tops & Blouses, White, €0.50–€1.00)
   > Given your recent purchase of a t-shirt, your preference for white, and your typical spending range, this basic white t-shirt will perfectly fit your style and budget.

2. **Black Mini Skirt** (Trousers & Skirts, Black, €0.50–€1.00)
   > Since you previously purchased a skirt and black is one of your favourite colours, this black mini skirt aligns with both your style preferences and spending habits.

3. **Light Orange Vest Top** (Tops & Blouses, Light Orange, €0.50–€1.00)
   > Considering your interest in vest tops and your liking for light orange, this vest top would be a great addition to your wardrobe, fitting well within your budget.

---

### Run 07 — Customer Age 56

- **Status:** ✅ SUCCESS
- **Latency:** 5134ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** Recommendations focus on trousers and accessories in your preferred colors and price range, reflecting your past purchase patterns and favorite hues.

**Recommendations:**

1. **Blue Cotton Casual Trousers** (Trousers & Skirts, Blue, €2–€3)
   > Given your preference for trousers and the color blue, these casual trousers perfectly align with your style and budget.

2. **Light Orange Summer Scarf** (Accessories, Light Orange, €2–€3)
   > To complement your love for light orange, this summer scarf combines style with affordability, fitting into your price range.

3. **Greenish Khaki Relaxed Fit Shorts** (Trousers & Skirts, Greenish Khaki, €2–€3)
   > Since your last purchase was shorts and you favor greenish khaki, these relaxed fit shorts would be a great addition to your wardrobe.

---

### Run 08 — Customer Age 31

- **Status:** ✅ SUCCESS
- **Latency:** 6189ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on the customer's preferred colours and spending habits, targeting their interest in practical and affordable fashion items.

**Recommendations:**

1. **Casual Black Midi Skirt** (Trousers & Skirts, Black, €3-€5)
   > Given your preference for black items and your previous purchase of trousers, this black midi skirt fits well within your style and budget.

2. **Basic Blue T-Shirt** (Tops & Blouses, Blue, €3-€5)
   > You have shown an interest in blue, and this simple blue t-shirt matches your colour preference and typical spending range.

3. **Black Knit Leggings** (Trousers & Skirts, Black, €3-€5)
   > Considering your previous purchase of leggings and your preference for black, these knit leggings would be a comfortable and stylish addition to your wardrobe.

---

### Run 09 — Customer Age 31

- **Status:** ✅ SUCCESS
- **Latency:** 6293ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** Recommendations focus on dark colour preferences, past purchases of casual wear, and maintaining the low average spending range.

**Recommendations:**

1. **Classic Black Turtleneck Knitwear** (Tops & Blouses, Black, €3–€5)
   > As you enjoy dark shades and have previously purchased a jacket, a black turtleneck knitwear will complement your wardrobe, especially in the cooler months.

2. **Dark Grey Casual Shorts** (Trousers & Skirts, Dark Grey, €3–€5)
   > Given your previous purchase of shorts and preference for darker colours, these dark grey casual shorts align well with your style and existing collection.

3. **Dark Blue Lightweight Scarf** (Accessories, Dark Blue, €3–€5)
   > To add variety and cater to your love for dark blue, a lightweight scarf can be a versatile accessory for your wardrobe without exceeding your typical spending range.

---

### Run 10 — Customer Age 22

- **Status:** ✅ SUCCESS
- **Latency:** 6112ms
- **Personalisation Score:** HIGH
- **Confidence:** 85/100
- **Summary:** The recommendations focus on casual, affordable items in your favourite colours, aligning with your recent purchases and spending patterns.

**Recommendations:**

1. **Divided Basic T-Shirt** (Tops & Blouses, Black, €2–€5)
   > Given your preference for black and your interest in casual wear, this basic T-shirt complements your existing wardrobe and fits your spending habits.

2. **Light Blue Denim Shorts** (Trousers & Skirts, Light Blue, €2–€5)
   > Since you recently bought shorts and enjoy light blue, these denim shorts are a great match for your style and budget.

3. **Divided Sleeveless Top** (Tops & Blouses, Black, €2–€5)
   > With your affinity for black and casual styles, this sleeveless top will enhance your collection in an affordable way.

---

## How to View in LangSmith

1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Open project: **`balando-uc2-recommendations`**
3. You will see 10 traced runs
4. Click any run to inspect:
   - The exact customer profile sent to GPT-4o
   - The exact recommendations returned
   - Token usage and cost breakdown
   - Latency timeline
5. Use the dataset **`balando-recommendation-dataset`** tab to compare inputs vs outputs

---

*Generated by Balando GmbH AI Consulting — March 2026*
