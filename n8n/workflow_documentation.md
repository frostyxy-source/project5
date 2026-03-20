# n8n Workflow Documentation — Return Risk Alert
**Project:** Balando GmbH AI Consulting  
**Use Case:** UC1 — Automated Return Risk Prediction  
**Tool:** n8n Cloud  
**Date:** March 2026

---

## What This Workflow Does

When a customer places an order on Balando's webshop, this workflow:

1. Receives the order data via webhook
2. Scores the order for return risk using GPT-4o
3. If risk is HIGH → sends a branded alert email to the operations team
4. If risk is LOW → logs silently and does nothing

The entire flow runs in under 10 seconds. The operations team receives the alert
before the order is picked and packed, allowing them to take action proactively.

---

## Workflow Architecture

```
[Webhook] → [Edit Fields] → [OpenAI: Message a Model] → [Code: Parse JSON] → [IF: HIGH?]
                                                                                    ↓ TRUE
                                                                              [Gmail: Send Alert]
                                                                                    ↓ FALSE
                                                                              [No Operation]
```

---

## Node-by-Node Explanation

### Node 1 — Webhook (Trigger)
- **Type:** Webhook
- **Method:** POST
- **Path:** `return-risk`
- **Purpose:** Entry point. In production this is replaced by a Shopify order webhook.
  For the demo it accepts a manual POST request.

### Node 2 — Edit Fields (Mock Order Data)
- **Type:** Set / Edit Fields
- **Purpose:** Simulates a Shopify order payload with all required fields.
- **In production:** Replace with the Shopify trigger node — the rest of the workflow
  is identical.
- **Fields set:**

| Field | Value (demo) | Production source |
|-------|-------------|------------------|
| order_id | ORD-4821 | Shopify order.id |
| customer_name | Sophie Müller | Shopify customer.name |
| customer_email | sophie@example.de | Shopify customer.email |
| product_type | Dress | Shopify line_items[0].title |
| size | M | Shopify line_items[0].variant.title |
| price_eur | 89.90 | Shopify line_items[0].price |
| is_first_purchase | true | Derived from order count |
| sales_channel | Online | Shopify sales_channel |
| customer_country | Germany | Shopify shipping_address.country |

### Node 3 — OpenAI: Message a Model
- **Type:** OpenAI
- **Resource:** Text
- **Operation:** Message a Model
- **Model:** gpt-4o
- **System prompt:** See below
- **Purpose:** GPT-4o reads the order details and outputs a JSON risk assessment

**System Prompt:**
```
You are a return risk assistant for Balando GmbH, a German fashion e-commerce company.
Germany has the highest fashion return rate in Europe (up to 50% for dresses).
Score return likelihood and respond ONLY with valid JSON, no markdown, no code fences.
You MUST choose recommended_action from EXACTLY one of these four options, word for word:
- "Trigger size guide at checkout + include fit card in parcel"
- "Send pre-shipment confirmation email with styling tips"
- "Flag to warehouse: hold duplicate sizes pending confirmation"
- "Activate post-delivery SMS satisfaction nudge"
Respond only with this JSON structure:
{"risk_level": "HIGH" or "LOW", "risk_score": 0-100,
"top_reason": "one sentence", "recommended_action": "exact option from the list above"}
```

### Node 4 — Code (Parse JSON)
- **Type:** Code (JavaScript)
- **Purpose:** GPT-4o returns text — this node converts it to structured data
  that the IF node can read.

```javascript
const raw = $input.item.json.output[0].content[0].text;
const cleaned = raw.replace(/```json|```/g, "").trim();
const parsed = JSON.parse(cleaned);

return {
  json: {
    ...parsed,
    order_id:       $('Edit Fields').item.json.order_id,
    customer_name:  $('Edit Fields').item.json.customer_name,
    customer_email: $('Edit Fields').item.json.customer_email,
    product_type:   $('Edit Fields').item.json.product_type,
    price_eur:      $('Edit Fields').item.json.price_eur,
  }
};
```

### Node 5 — IF (Route by Risk)
- **Type:** IF
- **Condition:** `{{ $json.risk_level }}` equals `HIGH`
- **True output:** → Gmail alert node
- **False output:** → No Operation node
- **Purpose:** This is the decision gate. The AI routing is visible and auditable —
  every HIGH risk order triggers a transparent, logged alert.

### Node 6 — Gmail (Send Alert)
- **Type:** Gmail
- **Operation:** Send a message
- **To:** Operations team email
- **Subject:** `⚠️ High Return Risk — Order {{ $json.order_id }} ({{ $json.product_type }})`
- **Body:** HTML email with order details, risk score, reason and recommended action

### Node 7 — No Operation (Low Risk)
- **Type:** No Operation
- **Purpose:** Closes the FALSE branch cleanly. Low-risk orders are silently logged
  in n8n's execution history for audit purposes.

---

## Demo Test Cases

### High Risk Order (triggers email alert)
```json
{
  "product_type": "Dress",
  "size": "M",
  "price_eur": 89.90,
  "is_first_purchase": true,
  "sales_channel": "Online",
  "customer_country": "Germany"
}
```
Expected: risk_score ~80–90, recommended_action = size guide

### Low Risk Order (silent log)
```json
{
  "product_type": "Socks",
  "size": "One Size",
  "price_eur": 12.00,
  "is_first_purchase": false,
  "sales_channel": "Online",
  "customer_country": "Germany"
}
```
Expected: risk_score ~10–20, routes to No Operation

---

## How to Import the Workflow

1. Open [n8n Cloud](https://cloud.n8n.io)
2. Create a new workflow
3. Click the `...` menu → **Import from file**
4. Select `workflow.json` from this folder
5. Add your OpenAI credential (Settings → Credentials → New → OpenAI)
6. Add your Gmail credential (click the Gmail node → Sign in with Google)
7. Activate the workflow using the toggle in the top right

---

## From Demo to Production

| Demo setup | Production setup |
|-----------|-----------------|
| Edit Fields node (hardcoded mock data) | Shopify webhook trigger (real orders) |
| Manual POST to webhook test URL | Automatic trigger on every new order |
| Gmail personal account | Balando operations team inbox |
| Single alert email | + Shopify order tag "high-return-risk" |

Estimated production setup time: **2–3 days** with Shopify API access.

---

## Monitoring & Transparency

Every workflow execution is logged in n8n's Executions tab:
- Timestamp of every run
- Input data received
- GPT-4o output (risk score, reason, action)
- Email sent confirmation
- Any errors flagged

This provides Chleo with full visibility into every automated decision — directly
addressing the concern that AI is a "black box."
