"""
Author: Mourad.Soltani
HTTP endpoint tests - 8-10 tests
"""
import json

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

def test_analyze_happy_path(client, sample_payload):
    resp = client.post("/api/v1/exceptions/analyze", json=sample_payload)
    assert resp.status_code == 200
    j = resp.get_json()
    assert "data" in j
    assert j["signature"] == "Mourad.Soltani"
    data = j["data"]
    assert "exceptions" in data
    assert "decision" in data
    assert "ai_advisory" in data
    assert data["signature"] == "Mourad.Soltani"
    assert data["decision"]["signature"] == "Mourad.Soltani"

def test_analyze_price_mismatch(client):
    payload = {
        "po_number": "PO-1001",
        "po_amount": 50000,
        "invoice_number": "INV-9001",
        "invoice_amount": 60000,
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Corp",
        "po_status": "OPEN",
        "currency_po": "USD",
        "currency_invoice": "USD"
    }
    resp = client.post("/api/v1/exceptions/analyze", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    exc_types = [e["exception_type"] for e in data["exceptions"]]
    assert "PRICE_MISMATCH" in exc_types

def test_analyze_missing_field_400(client):
    payload = {"po_number": "PO-1"}  # missing required
    resp = client.post("/api/v1/exceptions/analyze", json=payload)
    assert resp.status_code == 400
    j = resp.get_json()
    assert "error" in j
    assert j["signature"] == "Mourad.Soltani"

def test_analyze_bad_type_400(client):
    payload = {
        "po_number": "PO-1001",
        "po_amount": "not-a-number",
        "invoice_number": "INV-1",
        "invoice_amount": 50000,
        "vendor_id": "VEND-001",
        "vendor_name": "Acme"
    }
    resp = client.post("/api/v1/exceptions/analyze", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["signature"] == "Mourad.Soltani"

def test_analyze_invalid_json_400(client):
    resp = client.post("/api/v1/exceptions/analyze", data="not json", content_type="application/json")
    assert resp.status_code == 400
    assert resp.get_json()["signature"] == "Mourad.Soltani"

def test_resolve_endpoint(client):
    payload = {
        "po_number": "PO-1001",
        "invoice_number": "INV-9001",
        "action": "AUTO_RESOLVE"
    }
    resp = client.post("/api/v1/exceptions/resolve", json=payload)
    assert resp.status_code in [200, 502]  # 502 if ERP mock fails, but mock should succeed
    j = resp.get_json()
    assert j["signature"] == "Mourad.Soltani"

def test_vendor_verify(client):
    payload = {"vendor_id": "VEND-001", "vendor_name": "Acme Corp"}
    resp = client.post("/api/v1/vendors/verify", json=payload)
    assert resp.status_code == 200
    j = resp.get_json()
    assert j["signature"] == "Mourad.Soltani"
    assert "data" in j

def test_vendor_health_not_found(client):
    resp = client.get("/api/v1/vendors/health/NONEXISTENT")
    assert resp.status_code == 404
    assert resp.get_json()["signature"] == "Mourad.Soltani"

def test_integrations_status(client):
    resp = client.get("/api/v1/integrations/status")
    assert resp.status_code == 200
    j = resp.get_json()
    assert j["signature"] == "Mourad.Soltani"
    assert "sap" in j["data"]

def test_roi_endpoint(client):
    payload = {
        "documents": [
            {
                "po_number": "PO-1001",
                "po_amount": 50000,
                "invoice_number": "INV-9001",
                "invoice_amount": 50000,
                "vendor_id": "VEND-001",
                "vendor_name": "Acme Corp"
            },
            {
                "po_number": "PO-1001",
                "po_amount": 50000,
                "invoice_number": "INV-9002",
                "invoice_amount": 60000,
                "vendor_id": "VEND-001",
                "vendor_name": "Acme Corp"
            }
        ]
    }
    resp = client.post("/api/v1/roi", json=payload)
    assert resp.status_code == 200
    j = resp.get_json()
    assert j["signature"] == "Mourad.Soltani"
    assert "total_processed" in j["data"]

def test_oversize_body_413(client):
    # Create payload >5MB
    big_str = "x" * (6 * 1024 * 1024)
    payload = {
        "po_number": "PO-1001",
        "po_amount": 50000,
        "invoice_number": "INV-1",
        "invoice_amount": 50000,
        "vendor_id": "VEND-001",
        "vendor_name": "Acme",
        "extra": big_str
    }
    resp = client.post("/api/v1/exceptions/analyze", json=payload)
    # Flask should return 413
    assert resp.status_code == 413
    j = resp.get_json()
    assert j["signature"] == "Mourad.Soltani"
