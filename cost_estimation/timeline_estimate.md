# Implementation Timeline — Balando GmbH AI Rollout
**Prepared by:** AI Consultant  
**Date:** March 2026  
**Client:** Chleo, CEO — Balando GmbH, Frankfurt

---

## Guiding Principles

- **Phased rollout:** One use case at a time. Each phase is independently valuable.
- **Start simple:** Begin with the lowest-complexity, fastest-to-value use case.
- **Build on success:** Each phase creates infrastructure the next phase reuses.
- **No big bang:** Balando never needs to commit to all three phases upfront.

---

## Phase 1 — Customer Support Automation (Month 1–2)

**Use Case 3 · Effort: Low · Time to value: 4–6 weeks**

| Week | Activity | Owner |
|------|----------|-------|
| Week 1 | Data audit — review existing support ticket categories and volumes | Internal |
| Week 1 | n8n Cloud account setup, OpenAI API key, Gmail integration | Developer |
| Week 2 | Build classification workflow (intent detection + draft reply) | Developer |
| Week 2 | Write response templates for top 3 query types | Internal team |
| Week 3 | Internal testing with 50 historical emails | Developer + team |
| Week 4 | Soft launch — AI drafts, human approves every reply | Operations team |
| Week 5–6 | Monitor CSAT scores, tune prompts, increase auto-send threshold | Developer |
| Week 6 | Full launch — auto-send for high-confidence classifications | Operations team |

**Key dependencies:** Access to existing support inbox, 50+ historical ticket examples  
**Go/no-go decision point:** End of Week 3 — if accuracy < 80% delay launch by 1 week

---

## Phase 2 — Personalised Recommendations (Month 2–4)

**Use Case 2 · Effort: Medium · Time to value: 6–8 weeks**

| Week | Activity | Owner |
|------|----------|-------|
| Week 1 | Export 6 months of Shopify order history to CSV | Internal |
| Week 1 | Set up LangSmith project, configure monitoring | Developer |
| Week 2 | Build LangChain recommendation engine (based on existing demo) | Developer |
| Week 3 | Connect to Klaviyo or existing email platform | Developer |
| Week 3 | Design 3 email templates (post-purchase recommendation flow) | Designer |
| Week 4 | A/B test setup — 50% get AI recommendations, 50% get standard email | Developer |
| Week 5–6 | Monitor click-through rates, open rates, repeat purchase conversions | Internal |
| Week 7–8 | Optimise based on results, expand to full customer base | Developer |

**Key dependencies:** Shopify order export access, Klaviyo account, email templates  
**Go/no-go decision point:** End of Week 6 — if CTR < 5% review recommendation logic

---

## Phase 3 — Return Risk Prediction (Month 4–6)

**Use Case 1 · Effort: Medium · Time to value: 6–8 weeks**

| Week | Activity | Owner |
|------|----------|-------|
| Week 1 | Shopify webhook setup — connect order trigger to n8n | Developer |
| Week 1 | Pull 6+ months of return data to validate risk model | Internal |
| Week 2 | Configure GPT-4o risk scoring prompt with real product data | Developer |
| Week 2 | Build IF node routing + operations team alert email | Developer |
| Week 3 | Parallel run — flag high-risk orders without acting | Operations team |
| Week 4 | Compare AI flags vs actual returns — validate accuracy | Developer + internal |
| Week 5 | Activate size guide prompts at checkout for flagged orders | Developer |
| Week 6 | Activate warehouse flagging for high-risk orders | Operations team |
| Week 7–8 | Monitor return rate reduction, tune risk threshold | Developer |

**Key dependencies:** Shopify API access, 6+ months of return history data, checkout integration  
**Go/no-go decision point:** End of Week 4 — if model precision < 65% adjust prompt

---

## Full Rollout Timeline (Visual)

```
Month 1    Month 2    Month 3    Month 4    Month 5    Month 6
|----------|----------|----------|----------|----------|----------|

[== PHASE 1: Support Automation ==]
           [======== PHASE 2: Recommendations ========]
                                  [======== PHASE 3: Return Risk ========]
```

---

## Milestones & Decision Gates

| Milestone | Target Date | Success Criteria |
|-----------|------------|-----------------|
| Phase 1 soft launch | End of Month 1 | AI drafts ready, team comfortable |
| Phase 1 full launch | End of Month 2 | 30%+ tickets auto-resolved |
| Phase 2 A/B test start | Month 2 Week 3 | Email platform connected |
| Phase 2 full rollout | End of Month 4 | CTR >8%, repeat purchase rate up |
| Phase 3 parallel run | Month 4 Week 3 | Webhook connected, alerts firing |
| Phase 3 full launch | End of Month 6 | Return rate down 10pp+ |

---

## Resource Requirements

| Phase | Developer Days | Internal Days | Total Cost Estimate |
|-------|--------------|--------------|---------------------|
| Phase 1 | 4–5 days | 3 days | €3,700–5,300 |
| Phase 2 | 6–8 days | 4 days | €5,500–8,000 |
| Phase 3 | 5–6 days | 3 days | €4,500–6,500 |
| **Total** | **15–19 days** | **10 days** | **€13,700–19,800** |

Developer rate: €600–800/day (Frankfurt freelancer)  
Internal staff time: €250/day

---

## What Can Go Wrong & How We Handle It

| Risk | Likely impact | Response |
|------|--------------|---------|
| Data quality issues | +1–2 weeks per phase | Data audit in Week 1 of each phase |
| Shopify API complexity | +1 week Phase 3 | Budget 1 contingency day |
| Staff adoption slow | +2 weeks soft launch | Include team in testing from Week 3 |
| GDPR review required | +2–4 weeks any phase | Start legal review in Month 1 alongside Phase 1 |
| Model accuracy below threshold | +1–2 weeks | Prompt tuning sprint, not a rebuild |

---

## Total Project Completion

**All three use cases live:** End of Month 6  
**First measurable ROI:** End of Month 2 (support automation savings)  
**Full ROI visible:** Month 8–12 (return rate reduction + recommendations compound)

---

*Timeline assumes no major technical blockers. Adjust based on Balando's existing  
infrastructure complexity and internal team availability.*  

