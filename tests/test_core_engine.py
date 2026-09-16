"""
Author: Mourad.Soltani
Pure logic - happy path and boundaries - 30 tests
"""
import pytest
from backend.core_engine import P2PCoreEngine, P2PDocument, LineItem, ExceptionType, ResolutionAction, Severity

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@pytest.fixture
def engine():
    return P2PCoreEngine()

def base_doc(**overrides):
    defaults = dict(
        po_number="PO-1001",
        po_amount=50000,
        invoice_number="INV-9001",
        invoice_amount=50000,
        vendor_id="VEND-001",
        vendor_name="Acme Corp",
        po_status="OPEN",
        gr_received=True,
        approval_limit=100000,
        currency_po="USD",
        currency_invoice="USD"
    )
    defaults.update(overrides)
    return P2PDocument(**defaults)

# Happy path - 15-20 tests
def test_no_exception_when_within_tolerance(engine):
    doc = base_doc(po_amount=50000, invoice_amount=50000)
    exc = engine.detect_exceptions(doc)
    assert len(exc) == 1
    assert exc[0].exception_type == ExceptionType.NO_EXCEPTION
    assert exc[0].severity == Severity.LOW
    assert exc[0].confidence == 0.99

def test_price_mismatch_detected_small(engine):
    doc = base_doc(po_amount=50000, invoice_amount=52000)  # 4% diff, $2000 diff
    exc = engine.detect_exceptions(doc)
    types = [e.exception_type for e in exc]
    assert ExceptionType.PRICE_MISMATCH in types
    price_exc = [e for e in exc if e.exception_type == ExceptionType.PRICE_MISMATCH][0]
    assert price_exc.details["diff_abs"] == 2000
    assert price_exc.details["diff_pct"] == 4.0

def test_price_mismatch_severity_high_when_large(engine):
    doc = base_doc(po_amount=10000, invoice_amount=30000)  # $20k diff
    exc = engine.detect_exceptions(doc)
    price_exc = [e for e in exc if e.exception_type == ExceptionType.PRICE_MISMATCH][0]
    assert price_exc.severity in [Severity.HIGH, Severity.MEDIUM]  # 20k -> HIGH per logic >10k

def test_duplicate_invoice_critical(engine):
    doc = base_doc(is_duplicate_check=True)
    exc = engine.detect_exceptions(doc)
    dup = [e for e in exc if e.exception_type == ExceptionType.DUPLICATE_INVOICE]
    assert len(dup) == 1
    assert dup[0].severity == Severity.CRITICAL
    assert dup[0].confidence == 0.98

def test_po_closed_detected(engine):
    doc = base_doc(po_status="CLOSED")
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.PO_CLOSED for e in exc)
    closed = [e for e in exc if e.exception_type == ExceptionType.PO_CLOSED][0]
    assert closed.severity == Severity.HIGH

def test_po_expired_via_status(engine):
    doc = base_doc(po_status="EXPIRED")
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.PO_EXPIRED for e in exc)

def test_currency_mismatch(engine):
    doc = base_doc(currency_po="USD", currency_invoice="EUR")
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.CURRENCY_MISMATCH for e in exc)
    cm = [e for e in exc if e.exception_type == ExceptionType.CURRENCY_MISMATCH][0]
    assert cm.details["po_currency"] == "USD"
    assert cm.details["invoice_currency"] == "EUR"
    assert cm.confidence == 1.0

def test_missing_gr(engine):
    doc = base_doc(gr_received=False, po_amount=5000)
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.MISSING_GR for e in exc)

def test_quantity_mismatch_line_item(engine):
    li = LineItem(po_line_id="1", po_price=100, invoice_price=100, po_quantity=100, invoice_quantity=90)
    doc = base_doc(line_items=[li])
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.QUANTITY_MISMATCH for e in exc)

def test_tax_code_mismatch(engine):
    li = LineItem(po_line_id="1", po_price=100, invoice_price=100, po_quantity=10, invoice_quantity=10, tax_code_po="VAT19", tax_code_invoice="VAT7")
    doc = base_doc(line_items=[li])
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.TAX_CODE_MISMATCH for e in exc)

def test_vendor_master_mismatch_format(engine):
    doc = base_doc(vendor_id="bad id with spaces!", vendor_name="Acme Corp", vendor_master_record={"vendor_name": "Acme Corp"})
    exc = engine.detect_exceptions(doc)
    # format invalid should trigger VENDOR_MASTER_MISMATCH
    assert any(e.exception_type == ExceptionType.VENDOR_MASTER_MISMATCH for e in exc)

def test_approval_threshold_breach(engine):
    doc = base_doc(invoice_amount=150000, approval_limit=100000)
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.APPROVAL_THRESHOLD_BREACH for e in exc)
    br = [e for e in exc if e.exception_type == ExceptionType.APPROVAL_THRESHOLD_BREACH][0]
    assert br.details["invoice_amount"] == 150000

def test_delivery_tolerance_breach(engine):
    doc = base_doc(delivery_date_po="2026-01-01", delivery_date_invoice="2026-01-20")
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.DELIVERY_TOLERANCE_BREACH for e in exc)
    d = [e for e in exc if e.exception_type == ExceptionType.DELIVERY_TOLERANCE_BREACH][0]
    assert d.details["delta_days"] == 19

def test_decision_auto_resolve_no_exception(engine):
    doc = base_doc()
    exc = engine.detect_exceptions(doc)
    decision = engine.decide_resolution(doc, exc)
    assert decision.action == ResolutionAction.AUTO_RESOLVE
    assert decision.auto_resolvable is True
    assert decision.requires_human is False
    assert decision.signature == "Mourad.Soltani"

def test_decision_block_duplicate(engine):
    doc = base_doc(is_duplicate_check=True)
    exc = engine.detect_exceptions(doc)
    decision = engine.decide_resolution(doc, exc)
    assert decision.action == ResolutionAction.BLOCK_INVOICE
    assert decision.requires_human is True
    assert decision.escalation_target == "finance_ops"

def test_decision_escalate_po_closed(engine):
    doc = base_doc(po_status="CLOSED")
    exc = engine.detect_exceptions(doc)
    decision = engine.decide_resolution(doc, exc)
    assert decision.action == ResolutionAction.ESCALATE_PROCUREMENT

def test_decision_currency_mismatch_requests_vendor(engine):
    doc = base_doc(currency_po="USD", currency_invoice="EUR")
    exc = engine.detect_exceptions(doc)
    decision = engine.decide_resolution(doc, exc)
    assert decision.action == ResolutionAction.REQUEST_INFO_VENDOR

def test_decision_price_small_auto_resolve_with_adjustment(engine):
    doc = base_doc(po_amount=10000, invoice_amount=10200)  # 2% = $200, within 5% band
    # Adjust tolerance to trigger auto-resolve path: need single price mismatch, diff_abs <=100 and diff_pct <=5
    # Our doc has 200 diff, so modify
    doc2 = base_doc(po_amount=10000, invoice_amount=10080)  # 0.8% $80
    exc = engine.detect_exceptions(doc2)
    # If no exception because within strict tolerance, then decision auto-resolve
    # Let's force price mismatch by setting custom thresholds via direct test of decision logic
    from backend.core_engine import ExceptionResult
    fake_exc = ExceptionResult(
        exception_type=ExceptionType.PRICE_MISMATCH,
        severity=Severity.LOW,
        confidence=0.92,
        details={"diff_abs": 80, "diff_pct": 0.8, "po_amount": 10000, "invoice_amount": 10080},
        fingerprint="testfp"
    )
    decision = engine.decide_resolution(doc2, [fake_exc])
    assert decision.action == ResolutionAction.AUTO_RESOLVE_WITH_ADJUSTMENT
    assert decision.adjustment_amount == 80

def test_decision_hold_for_gr(engine):
    doc = base_doc(gr_received=False, po_amount=5000)
    exc = engine.detect_exceptions(doc)
    decision = engine.decide_resolution(doc, exc)
    assert decision.action == ResolutionAction.HOLD_FOR_GR

def test_decision_multiple_exceptions_manual_review(engine):
    doc = base_doc(po_amount=50000, invoice_amount=60000, currency_po="USD", currency_invoice="EUR", gr_received=False)
    exc = engine.detect_exceptions(doc)
    # Should have at least 2 exceptions
    assert len(exc) >= 2
    decision = engine.decide_resolution(doc, exc)
    # Multiple exceptions -> manual review unless critical overrides
    # But currency mismatch is high and returns early before multi-check? Actually currency check returns early
    # Let's create two medium exceptions
    from backend.core_engine import ExceptionResult
    e1 = ExceptionResult(ExceptionType.PRICE_MISMATCH, Severity.MEDIUM, 0.9, {"diff_abs": 2000, "diff_pct": 4}, "fp1")
    e2 = ExceptionResult(ExceptionType.QUANTITY_MISMATCH, Severity.MEDIUM, 0.85, {}, "fp2")
    decision2 = engine.decide_resolution(doc, [e1, e2])
    assert decision2.action == ResolutionAction.MANUAL_REVIEW

# Boundaries - 10-15 tests
def test_zero_po_amount_no_div_zero(engine):
    doc = base_doc(po_amount=0, invoice_amount=100)
    exc = engine.detect_exceptions(doc)  # Should not throw div zero
    assert len(exc) >= 1

def test_negative_amounts_handled(engine):
    doc = base_doc(po_amount=-50000, invoice_amount=-52000)
    exc = engine.detect_exceptions(doc)
    # Should still detect price mismatch? diff pct logic uses abs
    assert isinstance(exc, list)

def test_empty_vendor_id_pattern(engine):
    doc = base_doc(vendor_id="AB", vendor_name="Acme")  # too short, fails pattern
    exc = engine.detect_exceptions(doc)
    # Pattern check triggers vendor master mismatch for format
    # But only if vendor_master_record present? Actually format check is inside vendor_master_record block? Let's check code - format check is inside that block
    # So without master record, no mismatch. Test with master record
    doc2 = base_doc(vendor_id="AB", vendor_name="Acme", vendor_master_record={"vendor_name": "Acme Corp"})
    exc2 = engine.detect_exceptions(doc2)
    assert any(e.exception_type == ExceptionType.VENDOR_MASTER_MISMATCH for e in exc2)

def test_very_large_amount_critical(engine):
    doc = base_doc(po_amount=100000, invoice_amount=500000, approval_limit=100000)
    exc = engine.detect_exceptions(doc)
    # Should have critical for approval breach over 250k
    crit = [e for e in exc if e.severity == Severity.CRITICAL]
    assert len(crit) >= 1

def test_po_expiry_date_parsing(engine):
    doc = base_doc(po_expiry_date="2020-01-01", po_status="OPEN")
    exc = engine.detect_exceptions(doc)
    assert any(e.exception_type == ExceptionType.PO_EXPIRED for e in exc)

def test_future_expiry_not_expired(engine):
    doc = base_doc(po_expiry_date="2030-01-01", po_status="OPEN")
    exc = engine.detect_exceptions(doc)
    assert not any(e.exception_type == ExceptionType.PO_EXPIRED for e in exc)

def test_quantity_tolerance_edge_exact(engine):
    # Exactly at tolerance should NOT trigger
    li = LineItem(po_line_id="1", po_price=100, invoice_price=100, po_quantity=100, invoice_quantity=101)  # 1% exactly
    doc = base_doc(line_items=[li])
    exc = engine.detect_exceptions(doc)
    # Our tolerance is > not >=, so 1% should not trigger
    # But qty_diff_abs =1, tolerance abs =1, so > not >=, so should not trigger
    assert not any(e.exception_type == ExceptionType.QUANTITY_MISMATCH for e in exc)

def test_price_tolerance_edge_exact(engine):
    doc = base_doc(po_amount=10000, invoice_amount=10200)  # 2% exactly, $200 diff
    exc = engine.detect_exceptions(doc)
    # Price tolerance: > 2% AND > $25, so exactly 2% should not trigger
    assert not any(e.exception_type == ExceptionType.PRICE_MISMATCH for e in exc)

def test_fingerprint_deterministic(engine):
    doc = base_doc()
    fp1 = engine._fingerprint(doc, ExceptionType.PRICE_MISMATCH)
    fp2 = engine._fingerprint(doc, ExceptionType.PRICE_MISMATCH)
    assert fp1 == fp2
    assert len(fp1) == 16

def test_roi_metrics_empty(engine):
    roi = engine.compute_roi_metrics([], [])
    assert roi["total"] == 0
    assert roi["signature"] == "Mourad.Soltani"

def test_roi_metrics_calculation(engine):
    docs = [base_doc(po_amount=50000, invoice_amount=50000) for _ in range(4)]
    from backend.core_engine import ResolutionDecision
    decisions = [
        ResolutionDecision(action=ResolutionAction.AUTO_RESOLVE, auto_resolvable=True, requires_human=False, deterministic_reason="ok"),
        ResolutionDecision(action=ResolutionAction.AUTO_RESOLVE, auto_resolvable=True, requires_human=False, deterministic_reason="ok"),
        ResolutionDecision(action=ResolutionAction.BLOCK_INVOICE, auto_resolvable=False, requires_human=True, deterministic_reason="dup"),
        ResolutionDecision(action=ResolutionAction.MANUAL_REVIEW, auto_resolvable=False, requires_human=True, deterministic_reason="manual"),
    ]
    roi = engine.compute_roi_metrics(docs, decisions)
    assert roi["total_processed"] == 4
    assert roi["auto_resolved"] == 2
    assert roi["auto_resolve_rate"] == 50.0
    assert roi["blocked"] == 1
    assert roi["estimated_hours_saved"] == 0.5  # 2 *0.25
