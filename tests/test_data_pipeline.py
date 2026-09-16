"""
Author: Mourad.Soltani
Data pipeline tests - part of moat verification
"""
import pytest
from backend.data_pipeline import VendorNormalizationPipeline

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@pytest.fixture
def pipeline():
    return VendorNormalizationPipeline()

def test_normalize_vendor_name_basic(pipeline):
    assert pipeline.normalize_vendor_name("Acme Corp") == "ACME"
    assert pipeline.normalize_vendor_name("Acme Inc.") == "ACME"
    assert pipeline.normalize_vendor_name("The Acme Company") == "ACME"

def test_normalize_empty(pipeline):
    assert pipeline.normalize_vendor_name("") == ""
    assert pipeline.normalize_vendor_name(None) == ""

def test_ingest_vendor(pipeline):
    rec = pipeline.ingest_vendor({"vendor_id": "VEND-001", "vendor_name": "Acme Corp", "tax_id": "12-345", "status": "ACTIVE"})
    assert rec.vendor_id == "VEND-001"
    assert rec.normalized_name == "ACME"
    assert rec.verification_score > 0.5
    assert rec.signature == "Mourad.Soltani"

def test_ingest_duplicate_detection(pipeline):
    pipeline.ingest_vendor({"vendor_id": "VEND-001", "vendor_name": "Acme Corp"})
    pipeline.ingest_vendor({"vendor_id": "VEND-002", "vendor_name": "Acme Corp Inc."})
    # Second should be detected as duplicate via ledger
    assert len(pipeline.verification_ledger) == 2
    second_entry = pipeline.verification_ledger[1]
    assert second_entry["duplicate_of"] == "VEND-001"

def test_verification_score_with_tax_id(pipeline):
    rec1 = pipeline.ingest_vendor({"vendor_id": "V1", "vendor_name": "Test", "tax_id": "123", "payment_terms": "NET30", "last_verified": "2026-09-01T00:00:00"})
    rec2 = pipeline.ingest_vendor({"vendor_id": "V2", "vendor_name": "Test2", "status": "BLOCKED"})
    assert rec1.verification_score > rec2.verification_score

def test_verify_vendor(pipeline):
    pipeline.ingest_vendor({"vendor_id": "VEND-001", "vendor_name": "Acme"})
    result = pipeline.verify_vendor("VEND-001", "MANUAL")
    assert result["success"] is True
    assert result["verification_score"] > 0
    assert result["signature"] == "Mourad.Soltani"

def test_verify_nonexistent(pipeline):
    result = pipeline.verify_vendor("NONEXISTENT")
    assert result["success"] is False

def test_fingerprint_deterministic(pipeline):
    fp1 = pipeline.fingerprint_exception("PO-1", "INV-1", "PRICE_MISMATCH", "VEND-1")
    fp2 = pipeline.fingerprint_exception("PO-1", "INV-1", "PRICE_MISMATCH", "VEND-1")
    assert fp1 == fp2
    assert len(fp1) == 12

def test_exception_pattern_tracking(pipeline):
    fp = pipeline.fingerprint_exception("PO-1", "INV-1", "PRICE_MISMATCH", "VEND-1")
    pipeline.record_exception_pattern(fp, "PRICE_MISMATCH", "VEND-1", True, 1.5)
    pipeline.record_exception_pattern(fp, "PRICE_MISMATCH", "VEND-1", True, 2.5)
    assert pipeline.exception_patterns[fp].frequency == 2
    assert pipeline.exception_patterns[fp].avg_resolution_time_hours == 2.0

def test_vendor_health(pipeline):
    pipeline.ingest_vendor({"vendor_id": "VEND-001", "vendor_name": "Acme"})
    fp = pipeline.fingerprint_exception("PO-1", "INV-1", "PRICE_MISMATCH", "VEND-1")
    pipeline.record_exception_pattern(fp, "PRICE_MISMATCH", "VEND-001", True, 1.0)
    health = pipeline.get_vendor_health("VEND-001")
    assert health["found"] is True
    assert health["total_exceptions"] == 1
    assert health["signature"] == "Mourad.Soltani"

def test_data_rot_detection(pipeline):
    # Old vendor
    pipeline.ingest_vendor({"vendor_id": "OLD", "vendor_name": "Old Corp", "last_verified": "2020-01-01T00:00:00"})
    pipeline.ingest_vendor({"vendor_id": "NEW", "vendor_name": "New Corp", "last_verified": "2026-09-01T00:00:00"})
    rotten = pipeline.detect_data_rot(days_threshold=540)
    # OLD should be rotten
    assert any(r["vendor_id"] == "OLD" for r in rotten)
    # NEW should not be rotten (if threshold 540 days, Sep 2026 - Sep 2026 ~0)
    # Actually NEW is recent, so not rotten
    assert all(r["vendor_id"] != "NEW" for r in rotten)

def test_stats(pipeline):
    pipeline.ingest_vendor({"vendor_id": "V1", "vendor_name": "Test"})
    stats = pipeline.get_stats()
    assert stats["total_vendors"] == 1
    assert stats["signature"] == "Mourad.Soltani"
    assert "author" in stats
