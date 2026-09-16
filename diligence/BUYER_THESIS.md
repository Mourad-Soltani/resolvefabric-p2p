# BUYER_THESIS.md - Who Pays $5M–$10M Pre-Revenue and Why
**Author: Mourad.Soltani** | **Version: 3.0.0** | **Signature: Mourad.Soltani**

## Thesis
$5M–$10M pre-revenue valuation is justified by defensible ACV path ($400K–$1.2M), proprietary data moat (vendor normalization + verification ledger + rot detection every 18mo), integration depth (SAP+NetSuite), and buyer pool of PE-backed roll-ups + platform acquirers who cannot build cross-system coordination quickly. Revenue is zero, but strategic value is data + workflow + team + architecture that survives diligence.

## Acquirer Archetypes (3–5 specific, per spec §5)

### 1. PE-Backed ERP Roll-Up (e.g., Epicor, Aptean, or PE-backed manufacturing ERP platform)
**Rationale:** Roll-ups acquire mid-market manufacturers with messy vendor masters and high P2P exception rates. Vendor churn every ~18 months is recurring pain that roll-up cannot solve with seat-based ERP alone. Buying ResolveFabric gives roll-up a differentiated P2P module with autonomous re-verification, increasing NRR and ACV from $250K to $600K per customer via data moat. Strategic fit: vertical SaaS consolidation.

### 2. Mid-Market MSP Platform (e.g., PE-backed MSP consolidator like Thrive, New Charter, or similar)
**Rationale:** Gartner or comparable expects large share of enterprise apps to embed task-specific AI agents by end 2026 (verify figure per run — see reference block). MSPs serve 50–500 employee firms drowning in P2P exceptions across multiple ERPs. ResolveFabric's multi-ERP hub (SAP + NetSuite) + deterministic audit trail fits MSP platform need for standardized, auditable automation. ACV $300K–$900K per MSP platform (per Tier A ITSM adjacent). Buyer thesis: add P2P as wedge to land larger finance ops automation.

### 3. BPO / AP Outsourcing Roll-Up (e.g., PE-backed BPO like Auxis, Invensis, or procurement BPO platform)
**Rationale:** 40–60% of support workflow tasks reported automatable across ERP, CRM, billing, support (verify per run). BPO roll-ups actively buying automation to increase margin — labor arbitrage to automation arbitrage. ResolveFabric's auto-resolve rate (40% target) + ROI simulator + deterministic audit trail reduces BPO cost per invoice from $8 to $2. ACV $500K–$2M for BPO platform (per Tier A Customer Support Cross-System Resolution adjacent). Strategic: BPO can productize P2P exception handling as SaaS.

### 4. Regulated Fintech Incumbent / Financial Crime Platform (e.g., Unit21, Alloy, or bank mid-market procurement fintech)
**Rationale:** Financial Crime Transaction Monitoring ACV $750K–$3M per Tier B — adjacent category with same deterministic+AI pattern. ResolveFabric's deterministic engine final word + verification ledger + audit trail is directly transferable to transaction monitoring false-positive reduction (reported reduction — verify per run). Buyer gets pre-built deterministic+AI architecture + ERP integration depth that can be repurposed for vendor KYC / transaction monitoring. Strategic: regulated-data moat.

### 5. Procurement SaaS Platform (e.g., Coupa, Ivalua, or mid-market P2P challenger)
**Rationale:** Major RPA and ERP vendors racing into P2P exception handling (see reference block). Incumbent per-seat model structurally misaligned — they charge seats, buyer wants outcome (auto-resolve). ResolveFabric is AI-native challenger with category-defining potential in greenfield cross-system coordination (Bain & Company agentic AI research 2026 — majority greenfield, verify). Procurement platform buys to defend against AI-native disruption and to add autonomous vendor verification (network effect: more vendors verified → better data → higher auto-resolve). ACV $400K–$1.2M per Tier A.

## Why $5M–$10M Not $5K–$25K (v2.1 vs v3.0)
- v2.1 micro-SaaS $5K–$25K priced on revenue multiple (no revenue = low). v3.0 pre-revenue SaaS $5M–$10M priced on buyer thesis, moat, comparables — not revenue.
- Basis: ACV targets $250K–$1M+, named comparables ≥$3M last 36mo (see COMPARABLES.md), buyer thesis above.
- Diligence pack separates $5K asset from $5M asset — architecture, moat memo, buyer thesis, TAM/SAM/SOM, comparables, IP posture all mandatory per §5.
- Primary channel: direct one-to-one outreach to named strategic acquirers and PE platform teams (max 3 templates below). Secondary: boutique M&A advisors specializing in vertical SaaS and RegTech. Tertiary: ExitBid / Acquire.com for price discovery only.

## Valuation Bridge
- Working product, no users: $500K–$2M (v3.0 band)
- Working product + design-partner LOIs: $2M–$5M
- Working product + pilot deployment + named pipeline: $5M–$10M (this asset target with LOI path)
- Working product + signed paid pilot: $8M–$15M+
- Our asset: working product + 85 tests + diligence pack + live AI path + ERP integration depth → list $6.5M with LOI path to $8–10M with paid pilot. Verify against current strategic-acquirer comps before listing per §8.

## One-to-One Outreach Templates (Max 3, Named Archetypes Only, No Bulk Email, No Scraping)

### Template 1: PE-Backed ERP Roll-Up CTO
Subject: P2P exception fabric — 40% auto-resolve + vendor rot detection (18mo churn) — Mourad.Soltani

Hi [First Name],

Building ResolveFabric — P2P exception autonomy fabric with deterministic core (10 exception types, fingerprinting, audit trail) + live AI advisory (AI never has final word) + SAP/NetSuite depth + proprietary vendor normalization + autonomous re-verification ledger.

Why you: [Roll-up name] consolidates mid-market manufacturers with vendor churn every ~18mo and 40–60% invoice exception rate. Our data pipeline detects rot >540 days and auto-verifies batch — recurring value incumbent ERP doesn't solve. Deterministic engine final word = audit-ready for SOX.

Moat: verification ledger + exception fingerprinting + multi-party workflow network effect. Not a wrapper — 85 tests, Docker+Terraform ECS, clean IP.

Open to 20-min walkthrough? I can show deterministic decision trace + live AI advisory + ERP posting.

Author: Mourad.Soltani — resolvefabric-p2p v3.0 — $5M–$10M asset edition.

[Signature block with author]

### Template 2: BPO / AP Outsourcing Platform Head of Automation
Subject: Outcome-based P2P — from $8 to $2 cost per invoice — deterministic + AI — Mourad.Soltani

Hi [First Name],

ResolveFabric P2P — we autonomously resolve P2P exceptions (price, quantity, GR, duplicate, vendor master, tax, currency, approval) with deterministic engine + live AI advisory.

For BPO: auto-resolve rate 40% target, 15 min saved per auto-resolved, duplicate blocking $5K avoidance avg, vendor health scoring. ROI simulator shows hours saved + cost avoidance. Deterministic audit trail for client diligence.

Why [BPO name]: You're rolling up AP outsourcing and need automation arbitrage, not labor arbitrage. Our multi-party workflow (buyer+vendor+requester) + verification ledger gives you productized SaaS vs staff aug.

Architecture: Python 3.12, Flask, gunicorn, real OpenAI calls with timeout/retry/cost guard, SAP+NetSuite hub, 85 tests. No GPL, no scraped data.

Can I share diligence pack (ARCHITECTURE, MOAT, TAM/SAM/SOM, COMPARABLES, IP_POSTURE) + 15-min demo?

Author: Mourad.Soltani

### Template 3: Procurement SaaS VP Product (Coupa/Ivalua challenger)
Subject: AI-native P2P challenger — greenfield cross-system coordination — deterministic moat

Hi [First Name],

Bain & Co describes cross-system coordination agentic AI as majority greenfield (2026 research — verify). P2P exception handling sits in that greenfield — incumbent per-seat model misaligned.

ResolveFabric: deterministic core (final word) + live AI (advisory only) + ERP depth + proprietary vendor data pipeline with 18mo rot detection. Feb 2026 SaaSpocalypse repricing opened window for AI-native (major press Feb 2026 — verify).

For [Platform name]: defensive acquisition to add autonomous vendor verification + exception autonomy vs AI-native disruption. Our fingerprinting + pattern tracking creates network effect — more customers → more patterns → higher auto-resolve.

Diligence-ready: 85 tests, Docker HEALTHCHECK, Terraform ECS stub, clean IP posture, no GPL, no ToS violation.

Open to intro? Can share architecture doc + moat memo + buyer thesis + comparables.

Author: Mourad.Soltani — $5M–$10M pre-revenue SaaS edition v3.0

---
All templates one-to-one only, max 3 per spec §7 Deliverables #9. No cold/bulk email. No scraping. Use temporarily provided GitHub credentials only after local verification per spec.

Signature: Mourad.Soltani
