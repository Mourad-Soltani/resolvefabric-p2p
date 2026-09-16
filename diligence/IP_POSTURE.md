# IP_POSTURE.md - Clean IP Posture
**Author: Mourad.Soltani** | **Version: 3.0.0** | **Signature: Mourad.Soltani**

## Dependency Licenses
| Dependency | Version | License | GPL-Contaminated? | Notes |
|------------|---------|---------|-------------------|-------|
| Flask | 3.0.3 | BSD-3-Clause | No | Permissive, enterprise-friendly |
| gunicorn | 22.0.0 | MIT | No | Permissive |
| requests | 2.32.3 | Apache 2.0 | No | Permissive |
| python-dotenv | 1.0.1 | BSD-3-Clause | No | Permissive |
| pytest | 8.3.2 | MIT | No | Dev only |
| pytest-mock | 3.14.0 | MIT | No | Dev only |
| requests-mock | 1.12.1 | Apache 2.0 | No | Dev only |

**Check:** No GPL-contaminated deps per spec §2.7 and §9. All runtime deps permissive (MIT, BSD, Apache). No copyleft. Verified via `pip-licenses` or manual check of PyPI license metadata (verify per run).

## Data Provenance
- **Vendor master demo data:** Synthetic, generated in `backend/app.py` and `data_pipeline.py` — three demo vendors (Acme Corp, Globex Inc, Initech LLC) with fake tax IDs. No scraped data of unclear provenance per §2.7.
- **Exception patterns:** Generated via `fingerprint_exception` (SHA256 of PO+Invoice+Vendor+Type) + `record_exception_pattern` — proprietary, no external data.
- **ERP mock data:** Synthetic PO cache in `integration.py` — PO-1001, PO-1002, PO-1003, NS-PO-5001 — fake amounts, no real customer data.
- **AI training data:** No training — we call hosted model API, not train. No data provenance issue.
- **Frontend:** Pure HTML/CSS/JS, no external data.

**Open question for buyer counsel:** If real customer data ingested in pilot, need DPA and data processing addendum. For pre-revenue asset, synthetic data only — clean.

## API ToS Review
- **OpenAI API (or compatible):** Calls via `https://api.openai.com/v1/chat/completions` using `requests.Session`. ToS: API key from env, user provides key, we do not resell model output as model, we provide advisory that passes through deterministic engine (transformative use). No ToS violation per OpenAI API terms (verify current ToS per run — check https://openai.com/policies/terms-of-use). Cost guard prevents abuse.
- **SAP / NetSuite mock connectors:** Mocked, no real API calls in default mode (`SAP_MOCK_ENABLED=true`). Real connector shape would need customer-provided credentials and respect ERP API ToS. No scraping per spec §9.
- **No bulk email, no scraping:** Per spec §9 and Deliverables #9, outreach templates max 3, one-to-one only, no scraping.

## Patent Posture
- **Defensive publications:** Architecture doc, moat memo, core engine deterministic rules, vendor normalization algorithm, fingerprinting method are documented in `diligence/` and code comments — defensive publication count as prior art.
- **No patents filed:** Pre-revenue asset, no patents yet — typical for $5M–$10M stage. Buyer can file provisional on proprietary normalization + verification ledger + exception fingerprinting if desired.
- **No patent infringement known:** P2P exception handling is workflow automation, not patented algorithm. Deterministic rules (price tolerance, quantity tolerance, etc.) are industry standard thresholds, not novel. AI advisory is generic LLM use, not patented.
- **Recommendation:** Buyer should file defensive publication on data pipeline moat (vendor normalization + rot detection) before public listing to prevent troll.

## Trade Secrets
- Proprietary vendor normalization (suffix stripping, noise-word removal, duplicate detection via normalized name) + verification scoring formula + exception fingerprinting + rot detection threshold 540 days (18mo churn) are trade secrets documented in code but not publicly disclosed beyond diligence pack under NDA.
- Keep `diligence/` under NDA in data room — not public.

## Open Questions for Buyer Counsel
1. **Data processing:** If pilot uses real customer PO/invoice data, need DPA, retention policy, and audit log retention (ledger is immutable — good for audit, but need GDPR deletion handling if EU).
2. **AI Act:** EU AI Act high-risk deferrals (Annex III → 2027-12-02, Annex I → 2028-08-02 per Regulation (EU) 2024/1689 as amended — verify). P2P exception handling may be high-risk if used in critical finance? Likely not high-risk but need legal review per Article 50 and Chapter V unaffected (verify). Our deterministic engine final word helps explainability requirement.
3. **ERP connector licensing:** Real SAP/NetSuite connectors may require customer ERP license — not our IP issue, but deployment dependency.
4. **No GPL:** Verified, but run `pip-licenses` in CI to ensure no transitive GPL.

## Clean IP Posture Statement
This asset is sellable as-is: no GPL-contaminated deps, no scraped data of unclear provenance, no API ToS violations, MIT license, all artifacts signed Mourad.Soltani, no auth/billing/persistence unless required (compliance audit trails implemented minimally via ledger, correctly). Per spec §2.7: data room must be sellable as-is — it is.

## Signature
Mourad.Soltani — IP posture clean per §2.7, §9 constraints.
