"""
Author: Mourad.Soltani
Health endpoint tests - 4 tests
"""
__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "data" in data
    assert data["data"]["status"] in ["healthy", "degraded"]
    assert data["signature"] == "Mourad.Soltani"
    assert data["data"]["signature"] == "Mourad.Soltani"
    assert data["data"]["author"] == "Mourad.Soltani"

def test_health_has_required_fields(client):
    resp = client.get("/health")
    j = resp.get_json()
    d = j["data"]
    assert "project" in d
    assert "version" in d
    assert "ai_layer_configured" in d
    assert "integrations_configured" in d
    assert d["project"] == "resolvefabric-p2p"

def test_root_returns_json_or_html(client):
    resp = client.get("/")
    # Could be HTML or JSON, but should be 200
    assert resp.status_code == 200

def test_404_returns_json_with_signature(client):
    resp = client.get("/api/v1/nonexistent")
    assert resp.status_code == 404
    j = resp.get_json()
    assert "error" in j
    assert j["signature"] == "Mourad.Soltani"
    assert "author" in j
