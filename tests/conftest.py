"""
Author: Mourad.Soltani
Pytest fixtures
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from backend.app import app as flask_app
from backend.core_engine import P2PCoreEngine, P2PDocument, LineItem
from backend.ai_layer import ResolveFabricAI
from backend.integration import ERPIntegrationHub, SAPConnector, NetSuiteConnector
from backend.data_pipeline import VendorNormalizationPipeline

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def core_engine():
    return P2PCoreEngine()

@pytest.fixture
def ai_layer():
    return ResolveFabricAI(api_key="test-key-mock")

@pytest.fixture
def integration_hub():
    return ERPIntegrationHub()

@pytest.fixture
def data_pipeline():
    pipe = VendorNormalizationPipeline()
    pipe.ingest_vendor({"vendor_id": "VEND-TEST", "vendor_name": "Test Corp", "tax_id": "11-1111111", "status": "ACTIVE"})
    return pipe

@pytest.fixture
def sample_doc():
    return P2PDocument(
        po_number="PO-1001",
        po_amount=50000,
        invoice_number="INV-9001",
        invoice_amount=50000,
        vendor_id="VEND-001",
        vendor_name="Acme Corp",
        po_status="OPEN",
        gr_received=True,
        approval_limit=100000
    )

@pytest.fixture
def sample_payload():
    return {
        "po_number": "PO-1001",
        "po_amount": 50000,
        "invoice_number": "INV-9001",
        "invoice_amount": 50000,
        "vendor_id": "VEND-001",
        "vendor_name": "Acme Corp",
        "po_status": "OPEN",
        "currency_po": "USD",
        "currency_invoice": "USD",
        "approval_limit": 100000,
        "gr_received": True,
        "is_duplicate_check": False
    }
