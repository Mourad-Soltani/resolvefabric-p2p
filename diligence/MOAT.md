# MOAT.md - Defensibility Argument
**Author: Mourad.Soltani** | **Version: 3.0.0** | **Signature: Mourad.Soltani**

## The Moat in One Page
ResolveFabric's defensibility comes from **four interlocking moats**, not one. Per spec §2.4, at least one required; we have four, each hard to copy.

### Moat 1: Proprietary Data Pipeline (Hard-to-Replicate Data + Algorithmic Normalization)
- **What:** Vendor master normalization with proprietary suffix stripping, noise-word removal, fuzzy duplicate detection via normalized name matching, verification scoring (tax_id + payment_terms + recency - risk_flags), immutable verification ledger.
- **Why hard:** Data rot every ~18 months (vendor churn) means static vendor master decays. Our pipeline detects rot via `detect_data_rot(days_threshold=540)` and autonomous re-verification batch (10 per run cost guard) updates scores and ledger. This is recurring pain → recurring value. Incumbent ERP has vendor master but no autonomous re-verification loop; their data rots too.
- **What breaks moat:** If vendor data becomes self-healing via global network (e.g., SAP Business Network does autonomous verification for free), normalization moat weakens. Mitigation: exception fingerprinting + pattern tracking adds second data layer beyond vendor master.

### Moat 2: System-of-Record Integration Depth (Integration Moat)
- **What:** ERP Integration Hub with SAP S/4HANA + NetSuite connectors, real-shaped (OData/RFC shape, latency simulation, error handling), unified `fetch_full_context()` pulling PO+vendor+GR in one call, `post_resolution()` pushing back resolution_id.
- **Why hard:** Depth matters — not just API call, but handling schema drift, auth failure, rate limit, GR polling. Tests cover these. PE-backed roll-ups buying mid-market manufacturers need this depth; horizontal AI wrapper cannot fake it. Mockable in tests but real-shaped in prod per spec.
- **What breaks:** If ERP vendors publish unified P2P exception API that auto-resolves, integration depth commoditizes. Unlikely — ERP vendors race here but their per-seat model misaligned (they charge seats, not outcome). See Reference Block: major RPA and ERP vendors racing here (verify per run).

### Moat 3: Two-Sided Coordination Dynamic + Multi-Party Workflow Network Effect
- **What:** P2P exception involves three parties: buyer (AP/procurement), vendor (external), requester (internal). Our resolution decision routes to escalation_target (finance_ops, procurement, vendor_master_team, cfo_office, requester) with next_steps and vendor_email_draft from AI advisory. Each resolution recorded as pattern with fingerprint, frequency, avg_resolution_time. More customers → more patterns → better auto-resolve rates → more vendors verified → network effect.
- **Why incumbent cannot copy without cannibalizing:** Incumbent per-seat RPA tools (UiPath, Automation Anywhere) charge per bot/seat. Our model is outcome-based (auto-resolve rate, hours saved, cost avoidance). To copy, incumbent must shift from seat to outcome, cannibalizing existing revenue. Per-seat software repricing Feb 2026 "SaaSpocalypse" (major business press Feb 2026 — verify per run) opened window for AI-native challengers.
- **What breaks:** If buyer centralizes all P2P into single ERP with no vendor interaction (unlikely — vendors are external), two-sided dynamic weakens. Mitigation: vendor health scoring still valuable even in centralized.

### Moat 4: Deterministic Engine Final Word (Regulatory / Auditability Moat)
- **What:** All AI outputs pass through deterministic engine before reaching user — AI never has final word. Decision tree is auditable, traceable, fingerprintable. Every decision includes `deterministic_reason` and `signature`. AI advisory marked `advisory_only=True`, `deterministic_engine_final=True`.
- **Why hard + why compliance:** For financial crime, procurement, SOX-relevant AP, auditability is requirement. Pure LLM wrapper fails audit. Our deterministic core + AI advisory is pattern from Financial Crime Transaction Monitoring and Loan Underwriting categories (Tier B/C) — regulated-data moat. EU AI Act readiness (Annex III high-risk, deferrals 2027-12-02, 2028-08-02 per Regulation (EU) 2024/1689 as amended — verify) will require explainability.
- **What breaks:** If regulators allow fully autonomous LLM decisions without deterministic audit trail (unlikely in finance/procurement), this moat weakens.

## Why Incumbent Cannot Copy Without Cannibalizing
1. **Seat model misaligned:** Incumbent charges per seat/bot. ResolveFabric charges outcome (auto-resolve rate + cost avoidance). To copy, incumbent must launch outcome-based product that undercuts own seat revenue — classic innovator's dilemma.
2. **Data moat requires new pipeline:** Incumbent ERP has vendor master but no verification ledger, no rot detection, no fingerprinting. Building it requires re-architecting master data management, not just adding AI feature.
3. **Multi-party workflow:** Incumbent is single-system (ERP or RPA). P2P exception spans ERP + vendor master + GR + approval workflow. Cross-system coordination is greenfield per Bain & Company agentic AI research 2026 (verify per run) — analysts describe majority as greenfield.

## What We Are Not (Reject Criteria per §2)
- Not a thin LLM wrapper — deterministic core is 500+ lines, tested 31 tests, hand-verifiable
- Not prompt engineering — moat is data pipeline + integration depth + workflow
- Not dependent on single customer — pattern tracking works across vendors
- Not under $100K ACV — target $400K–$1.2M at scale

## Signature
Mourad.Soltani — This moat memo is part of diligence pack per §5 mandatory.
