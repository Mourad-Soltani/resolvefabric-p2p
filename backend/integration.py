"""
Author: Mourad.Soltani
System-of-Record Integration Layer - ERP Connectors (SAP, NetSuite)
Mockable in tests but real-shaped in prod
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
import time
import random
from .config import config

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@dataclass
class ERPResponse:
    success: bool
    data: Dict
    error: Optional[str] = None
    latency_ms: float = 0
    source: str = ""
    signature: str = "Mourad.Soltani"

class ERPConnector(ABC):
    AUTHOR = "Mourad.Soltani"
    SIGNATURE = "Mourad.Soltani"

    @abstractmethod
    def get_po(self, po_number: str) -> ERPResponse:
        pass

    @abstractmethod
    def get_vendor(self, vendor_id: str) -> ERPResponse:
        pass

    @abstractmethod
    def get_gr(self, po_number: str) -> ERPResponse:
        pass

    @abstractmethod
    def post_resolution(self, resolution: Dict) -> ERPResponse:
        pass

class SAPConnector(ERPConnector):
    """
    SAP S/4HANA connector - mock implementation with real shape
    In prod, would use OData / RFC
    """
    def __init__(self, mock_enabled: bool = True):
        self.mock_enabled = mock_enabled
        self.source = "SAP_S4HANA"
        self._po_cache = {
            "PO-1001": {"po_number": "PO-1001", "amount": 50000, "currency": "USD", "status": "OPEN", "vendor_id": "VEND-001", "vendor_name": "Acme Corp"},
            "PO-1002": {"po_number": "PO-1002", "amount": 120000, "currency": "USD", "status": "OPEN", "vendor_id": "VEND-002", "vendor_name": "Globex Inc"},
            "PO-1003": {"po_number": "PO-1003", "amount": 75000, "currency": "USD", "status": "CLOSED", "vendor_id": "VEND-003", "vendor_name": "Initech LLC"},
        }
        self._vendor_cache = {
            "VEND-001": {"vendor_id": "VEND-001", "vendor_name": "Acme Corp", "status": "ACTIVE", "payment_terms": "NET30", "currency": "USD"},
            "VEND-002": {"vendor_id": "VEND-002", "vendor_name": "Globex Inc", "status": "ACTIVE", "payment_terms": "NET45", "currency": "USD"},
            "VEND-003": {"vendor_id": "VEND-003", "vendor_name": "Initech LLC", "status": "BLOCKED", "payment_terms": "NET30", "currency": "USD"},
        }

    def get_po(self, po_number: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            time.sleep(0.02)  # simulate latency
            data = self._po_cache.get(po_number)
            if data:
                return ERPResponse(success=True, data=data, latency_ms=(time.time()-start)*1000, source=self.source)
            else:
                return ERPResponse(success=False, data={}, error=f"PO {po_number} not found in SAP", latency_ms=(time.time()-start)*1000, source=self.source)
        # Real implementation would call SAP OData here
        return ERPResponse(success=False, data={}, error="SAP real connector not configured", source=self.source)

    def get_vendor(self, vendor_id: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            time.sleep(0.015)
            data = self._vendor_cache.get(vendor_id)
            if data:
                return ERPResponse(success=True, data=data, latency_ms=(time.time()-start)*1000, source=self.source)
            else:
                return ERPResponse(success=False, data={}, error=f"Vendor {vendor_id} not found", latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="SAP real connector not configured", source=self.source)

    def get_gr(self, po_number: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            # Simulate GR logic
            if po_number == "PO-1001":
                return ERPResponse(success=True, data={"po_number": po_number, "gr_received": True, "gr_quantity": 100, "gr_date": "2026-09-10"}, latency_ms=(time.time()-start)*1000, source=self.source)
            else:
                return ERPResponse(success=True, data={"po_number": po_number, "gr_received": False, "gr_quantity": 0}, latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="SAP real connector not configured", source=self.source)

    def post_resolution(self, resolution: Dict) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            time.sleep(0.01)
            return ERPResponse(success=True, data={"posted": True, "resolution_id": f"SAP-RES-{resolution.get('po_number')}", "resolution": resolution}, latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="SAP real connector not configured", source=self.source)

class NetSuiteConnector(ERPConnector):
    def __init__(self, mock_enabled: bool = True):
        self.mock_enabled = mock_enabled
        self.source = "NETSUITE"
        self._po_cache = {
            "NS-PO-5001": {"po_number": "NS-PO-5001", "amount": 45000, "currency": "USD", "status": "OPEN", "vendor_id": "NS-V-001", "vendor_name": "Umbrella Corp"},
        }

    def get_po(self, po_number: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            time.sleep(0.02)
            data = self._po_cache.get(po_number)
            if data:
                return ERPResponse(success=True, data=data, latency_ms=(time.time()-start)*1000, source=self.source)
            return ERPResponse(success=False, data={}, error=f"PO {po_number} not found in NetSuite", latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="NetSuite real connector not configured", source=self.source)

    def get_vendor(self, vendor_id: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            return ERPResponse(success=True, data={"vendor_id": vendor_id, "vendor_name": f"Vendor {vendor_id}", "status": "ACTIVE"}, latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="NetSuite real connector not configured", source=self.source)

    def get_gr(self, po_number: str) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            return ERPResponse(success=True, data={"po_number": po_number, "gr_received": True, "gr_quantity": 50}, latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="NetSuite real connector not configured", source=self.source)

    def post_resolution(self, resolution: Dict) -> ERPResponse:
        start = time.time()
        if self.mock_enabled:
            return ERPResponse(success=True, data={"posted": True, "resolution_id": f"NS-RES-{resolution.get('po_number')}"}, latency_ms=(time.time()-start)*1000, source=self.source)
        return ERPResponse(success=False, data={}, error="NetSuite real connector not configured", source=self.source)

class ERPIntegrationHub:
    """
    Hub that routes to appropriate ERP and provides unified interface
    Author: Mourad.Soltani
    """
    AUTHOR = "Mourad.Soltani"
    SIGNATURE = "Mourad.Soltani"

    def __init__(self):
        self.sap = SAPConnector(mock_enabled=config.SAP_MOCK_ENABLED)
        self.netsuite = NetSuiteConnector(mock_enabled=config.NETSUITE_MOCK_ENABLED)
        self.signature = "Mourad.Soltani"

    def _route(self, po_number: str) -> ERPConnector:
        if po_number.startswith("NS-"):
            return self.netsuite
        return self.sap

    def fetch_full_context(self, po_number: str, vendor_id: str) -> Dict:
        connector = self._route(po_number)
        po_resp = connector.get_po(po_number)
        vendor_resp = connector.get_vendor(vendor_id)
        gr_resp = connector.get_gr(po_number)

        return {
            "po": po_resp.data if po_resp.success else {},
            "po_error": po_resp.error if not po_resp.success else None,
            "vendor": vendor_resp.data if vendor_resp.success else {},
            "vendor_error": vendor_resp.error if not vendor_resp.success else None,
            "gr": gr_resp.data if gr_resp.success else {},
            "gr_error": gr_resp.error if not gr_resp.success else None,
            "source": connector.source,
            "signature": "Mourad.Soltani"
        }

    def get_status(self) -> Dict:
        return {
            "sap": {"enabled": True, "mock": config.SAP_MOCK_ENABLED, "source": "SAP_S4HANA"},
            "netsuite": {"enabled": True, "mock": config.NETSUITE_MOCK_ENABLED, "source": "NETSUITE"},
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani"
        }
