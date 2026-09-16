"""
Author: Mourad.Soltani
Integration layer tests - 6-8 tests
"""
import pytest
from backend.integration import SAPConnector, NetSuiteConnector, ERPIntegrationHub

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

def test_sap_get_po_success():
    sap = SAPConnector(mock_enabled=True)
    resp = sap.get_po("PO-1001")
    assert resp.success is True
    assert resp.data["po_number"] == "PO-1001"
    assert resp.source == "SAP_S4HANA"
    assert resp.signature == "Mourad.Soltani"

def test_sap_get_po_not_found():
    sap = SAPConnector(mock_enabled=True)
    resp = sap.get_po("PO-9999")
    assert resp.success is False
    assert "not found" in resp.error.lower()

def test_sap_get_vendor():
    sap = SAPConnector(mock_enabled=True)
    resp = sap.get_vendor("VEND-001")
    assert resp.success is True
    assert resp.data["vendor_id"] == "VEND-001"

def test_sap_get_gr():
    sap = SAPConnector(mock_enabled=True)
    resp = sap.get_gr("PO-1001")
    assert resp.success is True
    assert "gr_received" in resp.data

def test_sap_post_resolution():
    sap = SAPConnector(mock_enabled=True)
    resp = sap.post_resolution({"po_number": "PO-1001", "action": "AUTO_RESOLVE"})
    assert resp.success is True
    assert resp.data["posted"] is True

def test_netsuite_routing():
    hub = ERPIntegrationHub()
    # NS prefix should route to NetSuite
    ctx = hub.fetch_full_context("NS-PO-5001", "NS-V-001")
    assert ctx["source"] == "NETSUITE"
    assert ctx["signature"] == "Mourad.Soltani"

def test_sap_routing():
    hub = ERPIntegrationHub()
    ctx = hub.fetch_full_context("PO-1001", "VEND-001")
    assert ctx["source"] == "SAP_S4HANA"

def test_integration_status():
    hub = ERPIntegrationHub()
    status = hub.get_status()
    assert "sap" in status
    assert "netsuite" in status
    assert status["signature"] == "Mourad.Soltani"
    assert status["sap"]["enabled"] is True
