# ARCHITECTURE.md - ResolveFabric P2P
**Author: Mourad.Soltani** | **Version: 3.0.0** | **Signature: Mourad.Soltani**

## Component Diagram (ASCII)
```
[ERP: SAP/NetSuite] --(OData/RFC, mocked real-shaped)--> [Integration Hub]
                                                              |
[Frontend: HTML/CSS/JS] --(JSON, DOM APIs only)--> [Flask app.py /health, /api/v1/*]
                                                    |         |         |
                                                    v         v         v
                                             [Core Engine] [AI Layer] [Data Pipeline]
                                             deterministic  live API   proprietary
                                             10 exc types   OpenAI     normalization
                                             fingerprint    timeout    verification ledger
                                             decision tree  retry      rot detection
                                             final word     cost guard pattern tracking
                                                    |         |
                                                    v         v
                                             [Resolution Decision] --> [ERP Post]
                                                    |
                                                    v
                                             [Workers: autonomous re-verification, GR polling]
```

## Data Flow
1. **Ingest:** User submits PO/Invoice JSON via frontend → `app.py` validates at HTTP boundary (type checks, 400 not 500)
2. **Context Enrichment:** `integration_hub.fetch_full_context()` pulls PO, vendor, GR from ERP (SAP mock with latency simulation)
3. **Vendor Normalization:** `data_pipeline.ingest_vendor()` normalizes name (proprietary suffix stripping), computes verification score, checks duplicate via normalized name, appends immutable ledger entry
4. **Exception Detection:** `core_engine.detect_exceptions()` runs 10 deterministic rules in priority order: duplicate → PO status → currency → GR → price → quantity → tax → vendor master → approval → delivery tolerance. Each exception gets fingerprint (SHA256 of PO+Invoice+Vendor+Type)
5. **AI Advisory (non-binding):** `ai_layer.analyze_exception()` builds system+user prompt, calls hosted model via `requests.Session` with Retry, timeout 12s, max_tokens 800, cost guard 10c. On timeout/429/401 falls back to deterministic mock. Response parsed as JSON, enriched with signature, latency, tokens, `advisory_only=True`, `deterministic_engine_final=True`
6. **Deterministic Decision:** `core_engine.decide_resolution()` takes exceptions + optional AI advisory. Critical rules (duplicate, critical approval breach) always block/escalate, AI cannot override. Medium/low rules evaluate auto-resolvable bands (price diff ≤$100 & ≤5% → auto-resolve with adjustment). Multi-exception → manual review. Decision includes `deterministic_reason`, `next_steps`, `signature`
7. **Pattern Recording:** `data_pipeline.record_exception_pattern()` increments frequency, running avg resolution time, feeds moat
8. **ERP Posting:** `resolve` endpoint posts resolution via connector, returns resolution_id
9. **Autonomous Jobs:** `workers/async_task.py` runs daily batch re-verification (detects rot >540 days, verifies 10 per run cost guard) and GR polling

## Failure Modes
| Failure | Handling | Why |
|---------|----------|-----|
| Bad JSON payload | 400 with signature envelope, never 500 | Input hardening per §4.2 |
| Type mismatch (po_amount string) | 400 | Validate at boundary |
| Oversize body (>5MB) | 413 with signature | Request cap ≥1MB |
| AI timeout | Fallback to mock, log, continue — never fail request | Cost guard + resilience |
| AI 401 invalid key | Raise AICallError, fallback to mock, surface fallback_reason | Fail loudly only if AI_REQUIRED=true at boot |
| AI 429 rate limit | Retry via urllib3 Retry (backoff 0.5, 2 retries), then fallback | Retry per spec |
| ERP PO not found | Return error in context, but continue exception detection | Graceful degradation |
| Vendor not in registry | ingest on verify endpoint, else health returns 404 JSON with signature | Clean error handling |
| Missing frontend/index.html | Warn at boot, continue (health returns frontend_exists false) | Startup sanity check per spec |
| Missing AI key with AI_REQUIRED=true | Fail boot sys.exit(1) | Per spec §4.2 |

## Why Each Choice Made
- **Flask 3.0.3 + gunicorn:** Enterprise-credible, minimal deps, clean IP posture, no GPL contamination. Alternatives (FastAPI) heavier, same outcome.
- **Python 3.12:** Required by spec, deterministic engine benefits from typing.
- **Pure HTML/CSS/JS frontend, no frameworks:** Reduces IP risk, no innerHTML XSS vector, DOM APIs only per spec §4.2. Tradeoff: more manual JS, but acceptable for enterprise internal tool.
- **Requests Session with Retry:** Simple, production-grade, avoids heavy SDK. Cost guard prevents runaway bills.
- **SQLite default for DATABASE_URL:** Zero-ops for pre-revenue asset, Postgres optional via compose. Keeps build multi-session friendly.
- **In-memory vendor registry + ledger:** For v1, proprietary pipeline is algorithmic (normalization, scoring, fingerprinting), not DB-heavy. Postgres can replace dicts in v2 without changing interfaces — moat is logic, not storage.
- **Deterministic engine separate from AI layer:** This is the moat statement — AI never has final word. Incumbent per-seat RPA vendors cannot copy without cannibalizing seat model (see MOAT.md).
- **Docker HEALTHCHECK polling /health:** Required by spec, enterprise deployment artifact.
- **Terraform ECS/Fargate stub:** Real enough that buyer's engineer nods, not full prod IaC (would be scope creep). Shows path to scale.
- **5MB request cap:** ≥1MB per spec, enterprise payloads large (line items, attachments stub).

## Deployment
- Local: `python run.py` or `gunicorn backend.app:app`
- Docker: `docker build -t resolvefabric-p2p .` → `docker run -p 8080:8080`
- Compose: `docker-compose -f deploy/docker-compose.yml up`
- Cloud: Terraform stub deploys to ECS Fargate with ECR, CloudWatch logs, secrets manager for OPENAI_API_KEY

## Signature
Mourad.Soltani — Every JSON response includes signature field per spec.
