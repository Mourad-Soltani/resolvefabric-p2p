# ResolveFabric P2P — Exception Autonomy Platform
**Author: Mourad.Soltani** | **Version: 3.0.0** | **Status: Working Vertical Slice (Pre-Revenue)**

> Purchase-to-Pay Exception Handling — Deterministic Core + Live AI Advisory + ERP Integration Depth

**Repository:** https://github.com/Mourad-Soltani/resolvefabric-p2p

## Current Status (as of 2026-09-16)
- **Stage:** Working vertical slice / prototype. Zero revenue, zero customers, zero LOIs or paid pilots.
- **Code:** Production-shaped Python/Flask backend + pure JS frontend, ~85 tests, Docker + Terraform stubs.
- **Live AI path:** Structured for real OpenAI-compatible calls (timeout/retry/cost guard); falls back to mock when no API key.
- **ERP connectors:** Real-shaped (SAP S/4HANA + NetSuite) but mocked in tests and default runtime.
- **Realistic market positioning:** Pre-revenue code + diligence asset. Not a $5M–$10M acquisition candidate in its current state. Suitable as a starting point for a founder, small team, or strategic prototype evaluation.

Every source header, JSON response, and diligence document is signed **Mourad.Soltani**. Verify via `/health` → `signature`.

## Problem
Enterprise P2P (Purchase-to-Pay) teams routinely face high exception rates on invoices (price/quantity mismatches, missing goods receipts, duplicates, vendor master issues, tax/currency problems, approval breaches). Manual triage across ERP, vendor master, and internal stakeholders is expensive. Vendor master data decays as vendors churn (roughly every 18 months in many mid-market environments). Seat-based RPA and traditional AP tools often leave multi-party exception coordination unsolved.

## Solution
ResolveFabric is a multi-component P2P exception autonomy fabric:

1. **Deterministic Core Engine** (`backend/core_engine.py`)  
   10 exception types, severity scoring, fingerprinting, auditable decision tree. No LLM in the critical path.

2. **Live AI Advisory Layer** (`backend/ai_layer.py`)  
   Real HTTP calls to an OpenAI-compatible endpoint with timeout, retry, and cost guard. AI suggests; the deterministic engine has the final word.

3. **ERP Integration Hub** (`backend/integration.py`)  
   SAP S/4HANA + NetSuite connectors (real-shaped, mockable in tests). Latency tracking and error handling.

4. **Data Pipeline** (`backend/data_pipeline.py`)  
   Vendor normalization, verification scoring, immutable ledger, exception pattern tracking, and data-rot detection.

5. **Autonomous Workers** (`backend/workers/async_task.py`)  
   Batch re-verification and goods-receipt polling stubs.

**Frontend:** Pure HTML/CSS/JS using DOM APIs only (no `innerHTML` on user input). Payload size guards in place.

## Quick Start
```bash
# Install
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for tests

# Run
python run.py
# or
gunicorn -b 0.0.0.0:8080 backend.app:app

# Health check
curl http://localhost:8080/health

# Tests
pytest -v
```

Docker:
```bash
docker build -t resolvefabric-p2p .
docker-compose -f deploy/docker-compose.yml up --build
```

Set `OPENAI_API_KEY` (or compatible endpoint vars) for the live AI path.

## Architecture Highlights
- Deterministic engine always has the final decision; AI output is advisory only.
- Exception fingerprinting and pattern tracking for potential network effects.
- Vendor master normalization + verification ledger + rot detection (18-month horizon).
- Clean separation of concerns across engine, AI layer, integrations, and data pipeline.
- MIT license, no GPL dependencies, no scraped data claims.

See `diligence/ARCHITECTURE.md` and `diligence/MOAT.md` for deeper notes.

## Test Inventory (approx. 85 tests)
| Area                    | Coverage                          | Status |
|-------------------------|-----------------------------------|--------|
| Health / signature      | Endpoint, envelope, signature     | ✅     |
| Core engine             | Happy path + boundaries           | ✅     |
| AI layer                | Call structure, guards, fallback  | ✅     |
| Integration             | SAP/NetSuite shaped mocks         | ✅     |
| Data pipeline           | Normalization, ledger, rot        | ✅     |
| Workers                 | Async task stubs                  | ✅     |
| HTTP / API              | Status codes, payload limits      | ✅     |
| Frontend safety         | No innerHTML on user input        | ✅     |

## Diligence Pack
Located in `diligence/`:

- `ARCHITECTURE.md` — components, data flow, failure modes
- `MOAT.md` — defensibility arguments
- `BUYER_THESIS.md` — potential acquirer archetypes
- `TAM_SAM_SOM.md` — market sizing notes (many figures flagged for verification)
- `COMPARABLES.md` — acquisition references (explicitly require independent verification)
- `IP_POSTURE.md` — license and IP notes

These documents were written as an “asset edition” package. Several market and comparable claims carry explicit “verify before use” caveats. Treat them as starting points, not audited facts.

## Tech Stack
- Python 3.12, Flask 3.0.3, gunicorn, requests
- Pure JavaScript frontend (no framework)
- Docker + docker-compose
- Terraform ECS/Fargate stub
- pytest suite

## Honest Positioning
This repository contains a clean, well-structured vertical slice of a P2P exception-handling system with thoughtful architecture choices (deterministic core + advisory AI, vendor data pipeline, ERP-shaped integrations).  

It is **not**:
- A production-deployed product with customers
- A revenue-generating business
- A validated $5M–$10M strategic asset in its current form

Realistic next steps for anyone evaluating or extending it:
1. Wire real ERP credentials and run end-to-end flows.
2. Add design-partner LOIs or a paid pilot.
3. Harden the data pipeline against production vendor master volumes.
4. Measure actual auto-resolve rates and cost savings on real invoice streams.

Until those exist, the asset is best valued as high-quality prototype code + documentation rather than a mature acquisition target.

## License
MIT License — Copyright (c) 2026 Mourad.Soltani

---

Mourad.Soltani · ResolveFabric P2P v3.0 · Pre-revenue working vertical slice · 2026
