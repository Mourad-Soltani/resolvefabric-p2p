"""
Author: Mourad.Soltani
Workers tests
"""
import pytest
from backend.data_pipeline import VendorNormalizationPipeline
from backend.integration import ERPIntegrationHub
from backend.workers.async_task import AsyncTaskRunner

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

def test_reverification_no_pipeline():
    runner = AsyncTaskRunner(data_pipeline=None)
    result = runner.autonomous_reverification()
    assert result["success"] is False

def test_reverification_with_old_vendors():
    pipe = VendorNormalizationPipeline()
    pipe.ingest_vendor({"vendor_id": "OLD1", "vendor_name": "Old1", "last_verified": "2020-01-01T00:00:00"})
    pipe.ingest_vendor({"vendor_id": "OLD2", "vendor_name": "Old2", "last_verified": "2020-01-01T00:00:00"})
    runner = AsyncTaskRunner(data_pipeline=pipe)
    result = runner.autonomous_reverification()
    assert result["rotten_detected"] == 2
    assert result["verified"] == 2
    assert result["signature"] == "Mourad.Soltani"

def test_polling_gr():
    hub = ERPIntegrationHub()
    runner = AsyncTaskRunner(data_pipeline=None, integration_hub=hub)
    result = runner.polling_gr_status(["PO-1001", "PO-1002"])
    assert "results" in result
    assert result["signature"] == "Mourad.Soltani"
    assert len(result["results"]) == 2

def test_task_log():
    runner = AsyncTaskRunner(data_pipeline=VendorNormalizationPipeline())
    runner.autonomous_reverification()
    log = runner.get_task_log()
    assert len(log) == 1
    assert log[0]["task"] == "autonomous_reverification"
