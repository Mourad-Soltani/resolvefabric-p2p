"""
Author: Mourad.Soltani
AI layer tests - 8-10 tests
"""
import pytest
from unittest.mock import patch, MagicMock
from backend.ai_layer import ResolveFabricAI, AICallError, AICostGuardError

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@pytest.fixture
def ai():
    return ResolveFabricAI(api_key="test-key")

def test_is_configured_false_when_no_key():
    ai = ResolveFabricAI(api_key="")
    assert ai.is_configured() is False

def test_is_configured_true_when_key():
    ai = ResolveFabricAI(api_key="sk-test")
    assert ai.is_configured() is True

def test_mock_response_structure(ai):
    doc = {"po_number": "PO-1001", "po_amount": 50000, "invoice_number": "INV-9001", "invoice_amount": 52000}
    exc = [{"exception_type": "PRICE_MISMATCH"}]
    resp = ai._mock_response(doc, exc)
    assert "root_cause" in resp
    assert "vendor_email_draft" in resp
    assert "internal_next_steps" in resp
    assert "risk_level" in resp
    assert "confidence" in resp
    assert "summary" in resp
    assert resp["signature"] == "Mourad.Soltani"
    assert resp["advisory_only"] is True
    assert resp["deterministic_engine_final"] is True

def test_mock_duplicate_high_risk(ai):
    doc = {"po_number": "PO-1", "invoice_number": "INV-DUP"}
    exc = [{"exception_type": "DUPLICATE_INVOICE"}]
    resp = ai._mock_response(doc, exc)
    assert resp["risk_level"] == "HIGH"
    assert "duplicate" in resp["root_cause"].lower()

def test_mock_price_medium_risk(ai):
    doc = {"po_number": "PO-1"}
    exc = [{"exception_type": "PRICE_MISMATCH"}]
    resp = ai._mock_response(doc, exc)
    assert resp["risk_level"] == "MEDIUM"
    assert "price" in resp["root_cause"].lower() or "variance" in resp["root_cause"].lower()

def test_analyze_uses_mock_when_no_key():
    ai_no_key = ResolveFabricAI(api_key="")
    doc = {"po_number": "PO-1001", "po_amount": 50000, "invoice_number": "INV-9001", "invoice_amount": 50000}
    exc = [{"exception_type": "NO_EXCEPTION"}]
    resp = ai_no_key.analyze_exception(doc, exc, use_mock=False)  # should fallback to mock because not configured
    assert resp["mock"] is True
    assert resp["signature"] == "Mourad.Soltani"

def test_analyze_with_mock_flag(ai):
    doc = {"po_number": "PO-1001"}
    exc = [{"exception_type": "MISSING_GR"}]
    resp = ai.analyze_exception(doc, exc, use_mock=True)
    assert resp["mock"] is True
    assert "summary" in resp

def test_cost_guard_blocks_expensive():
    ai = ResolveFabricAI(api_key="test")
    ai.cost_guard_cents = 0  # set guard to 0 to force block
    # Create huge doc to exceed guard
    big_doc = {"po_number": "PO-1", "data": "x"*10000}
    exc = [{"exception_type": "PRICE_MISMATCH"}]
    with pytest.raises(AICostGuardError):
        ai.analyze_exception(big_doc, exc, use_mock=False)

def test_real_api_call_mocked_success(ai):
    doc = {"po_number": "PO-1001", "po_amount": 50000, "invoice_number": "INV-9001", "invoice_amount": 52000}
    exc = [{"exception_type": "PRICE_MISMATCH"}]
    
    mock_resp_data = {
        "choices": [{"message": {"content": '{"root_cause": "Test cause", "vendor_email_draft": "Test email", "internal_next_steps": ["step1"], "risk_level": "MEDIUM", "confidence": 0.9, "summary": "Test summary"}'}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 50}
    }
    
    with patch.object(ai.session, 'post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_resp_data
        mock_post.return_value.raise_for_status = MagicMock()
        
        resp = ai.analyze_exception(doc, exc, use_mock=False)
        assert resp["root_cause"] == "Test cause"
        assert resp["model_used"] == ai.model
        assert resp["signature"] == "Mourad.Soltani"
        assert "latency_ms" in resp

def test_real_api_timeout_fallback(ai):
    doc = {"po_number": "PO-1001"}
    exc = [{"exception_type": "PRICE_MISMATCH"}]
    
    import requests
    with patch.object(ai.session, 'post', side_effect=requests.exceptions.Timeout):
        resp = ai.analyze_exception(doc, exc, use_mock=False)
        # Should fallback to mock
        assert resp["mock"] is True
        assert resp["fallback_reason"] == "timeout"

def test_stats_tracking(ai):
    stats_before = ai.get_stats()
    assert stats_before["call_count"] == 0
    doc = {"po_number": "PO-1"}
    exc = []
    ai.analyze_exception(doc, exc, use_mock=True)
    stats_after = ai.get_stats()
    assert stats_after["call_count"] == 1
    assert stats_after["signature"] == "Mourad.Soltani"
