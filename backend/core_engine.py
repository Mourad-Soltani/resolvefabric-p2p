"""
Author: Mourad.Soltani
Deterministic Core Engine for P2P Exception Handling
ResolveFabric P2P - The deterministic engine is the moat; AI never has final word
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
import hashlib
from datetime import datetime

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

class ExceptionType(Enum):
    PRICE_MISMATCH = "PRICE_MISMATCH"
    QUANTITY_MISMATCH = "QUANTITY_MISMATCH"
    MISSING_GR = "MISSING_GR"
    DUPLICATE_INVOICE = "DUPLICATE_INVOICE"
    VENDOR_MASTER_MISMATCH = "VENDOR_MASTER_MISMATCH"
    TAX_CODE_MISMATCH = "TAX_CODE_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    PO_CLOSED = "PO_CLOSED"
    PO_EXPIRED = "PO_EXPIRED"
    APPROVAL_THRESHOLD_BREACH = "APPROVAL_THRESHOLD_BREACH"
    DELIVERY_TOLERANCE_BREACH = "DELIVERY_TOLERANCE_BREACH"
    NO_EXCEPTION = "NO_EXCEPTION"
    UNKNOWN = "UNKNOWN"

class ResolutionAction(Enum):
    AUTO_RESOLVE = "AUTO_RESOLVE"
    AUTO_RESOLVE_WITH_ADJUSTMENT = "AUTO_RESOLVE_WITH_ADJUSTMENT"
    ESCALATE_PROCUREMENT = "ESCALATE_PROCUREMENT"
    ESCALATE_FINANCE = "ESCALATE_FINANCE"
    REQUEST_INFO_VENDOR = "REQUEST_INFO_VENDOR"
    REQUEST_INFO_REQUESTER = "REQUEST_INFO_REQUESTER"
    BLOCK_INVOICE = "BLOCK_INVOICE"
    HOLD_FOR_GR = "HOLD_FOR_GR"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"

class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class LineItem:
    po_line_id: str
    po_price: float
    invoice_price: float
    po_quantity: float
    invoice_quantity: float
    po_currency: str = "USD"
    invoice_currency: str = "USD"
    tax_code_po: str = ""
    tax_code_invoice: str = ""
    description: str = ""

@dataclass
class P2PDocument:
    po_number: str
    po_amount: float
    invoice_number: str
    invoice_amount: float
    vendor_id: str
    vendor_name: str
    po_status: str = "OPEN"  # OPEN, CLOSED, EXPIRED
    po_expiry_date: Optional[str] = None
    gr_received: bool = True
    gr_quantity: float = 0
    po_quantity: float = 0
    approval_limit: float = 100000
    delivery_date_po: Optional[str] = None
    delivery_date_invoice: Optional[str] = None
    currency_po: str = "USD"
    currency_invoice: str = "USD"
    line_items: List[LineItem] = field(default_factory=list)
    is_duplicate_check: bool = False
    previous_invoices: List[str] = field(default_factory=list)
    vendor_master_record: Dict = field(default_factory=dict)
    extra: Dict = field(default_factory=dict)

@dataclass
class ExceptionResult:
    exception_type: ExceptionType
    severity: Severity
    confidence: float
    details: Dict
    fingerprint: str
    signature: str = "Mourad.Soltani"

@dataclass
class ResolutionDecision:
    action: ResolutionAction
    auto_resolvable: bool
    requires_human: bool
    adjustment_amount: float = 0.0
    adjustment_reason: str = ""
    escalation_target: Optional[str] = None
    next_steps: List[str] = field(default_factory=list)
    deterministic_reason: str = ""
    signature: str = "Mourad.Soltani"
    ai_advisory_used: bool = False
    ai_advisory_summary: Optional[str] = None

class P2PCoreEngine:
    """
    Deterministic decision engine - heart of the moat.
    All decisions are traceable, auditable, and repeatable.
    AI layer may suggest, but this engine decides.
    Author: Mourad.Soltani
    """
    AUTHOR = "Mourad.Soltani"
    VERSION = "3.0.0"
    SIGNATURE = "Mourad.Soltani"

    # Thresholds - enterprise-grade, configurable but deterministic
    PRICE_TOLERANCE_PCT = 2.0  # 2% tolerance
    PRICE_TOLERANCE_ABS = 25.0  # $25 absolute
    QUANTITY_TOLERANCE_PCT = 1.0
    QUANTITY_TOLERANCE_ABS = 1.0
    DELIVERY_TOLERANCE_DAYS = 5
    HIGH_VALUE_THRESHOLD = 50000
    CRITICAL_VALUE_THRESHOLD = 250000

    VENDOR_ID_PATTERN = re.compile(r"^[A-Z0-9\-]{4,20}$")

    def __init__(self):
        self.signature = "Mourad.Soltani"

    def _fingerprint(self, doc: P2PDocument, exc_type: ExceptionType) -> str:
        raw = f"{doc.po_number}|{doc.invoice_number}|{doc.vendor_id}|{exc_type.value}|{doc.po_amount}|{doc.invoice_amount}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def detect_exceptions(self, doc: P2PDocument) -> List[ExceptionResult]:
        results: List[ExceptionResult] = []

        # Rule 1: Duplicate invoice check - highest priority, critical
        if doc.is_duplicate_check or doc.invoice_number in doc.previous_invoices:
            results.append(ExceptionResult(
                exception_type=ExceptionType.DUPLICATE_INVOICE,
                severity=Severity.CRITICAL,
                confidence=0.98,
                details={"invoice_number": doc.invoice_number, "previous_match": True},
                fingerprint=self._fingerprint(doc, ExceptionType.DUPLICATE_INVOICE)
            ))

        # Rule 2: PO Status checks
        if doc.po_status.upper() == "CLOSED":
            results.append(ExceptionResult(
                exception_type=ExceptionType.PO_CLOSED,
                severity=Severity.HIGH,
                confidence=0.99,
                details={"po_status": doc.po_status, "po_number": doc.po_number},
                fingerprint=self._fingerprint(doc, ExceptionType.PO_CLOSED)
            ))
        elif doc.po_status.upper() == "EXPIRED":
            results.append(ExceptionResult(
                exception_type=ExceptionType.PO_EXPIRED,
                severity=Severity.HIGH,
                confidence=0.99,
                details={"po_status": doc.po_status},
                fingerprint=self._fingerprint(doc, ExceptionType.PO_EXPIRED)
            ))
        else:
            # Check expiry date
            if doc.po_expiry_date:
                expiry = self._parse_date(doc.po_expiry_date)
                if expiry and expiry < datetime.utcnow():
                    results.append(ExceptionResult(
                        exception_type=ExceptionType.PO_EXPIRED,
                        severity=Severity.HIGH,
                        confidence=0.95,
                        details={"po_expiry_date": doc.po_expiry_date},
                        fingerprint=self._fingerprint(doc, ExceptionType.PO_EXPIRED)
                    ))

        # Rule 3: Currency mismatch
        if doc.currency_po != doc.currency_invoice:
            results.append(ExceptionResult(
                exception_type=ExceptionType.CURRENCY_MISMATCH,
                severity=Severity.HIGH,
                confidence=1.0,
                details={"po_currency": doc.currency_po, "invoice_currency": doc.currency_invoice},
                fingerprint=self._fingerprint(doc, ExceptionType.CURRENCY_MISMATCH)
            ))

        # Rule 4: Missing GR
        if not doc.gr_received and doc.po_amount > 1000:
            results.append(ExceptionResult(
                exception_type=ExceptionType.MISSING_GR,
                severity=Severity.MEDIUM,
                confidence=0.90,
                details={"gr_received": doc.gr_received, "po_amount": doc.po_amount},
                fingerprint=self._fingerprint(doc, ExceptionType.MISSING_GR)
            ))

        # Rule 5: Price mismatch - line level + header level
        price_diff_pct = 0
        if doc.po_amount != 0:
            price_diff_pct = abs(doc.po_amount - doc.invoice_amount) / abs(doc.po_amount) * 100
        price_diff_abs = abs(doc.po_amount - doc.invoice_amount)

        if price_diff_pct > self.PRICE_TOLERANCE_PCT and price_diff_abs > self.PRICE_TOLERANCE_ABS:
            sev = Severity.LOW
            if price_diff_abs > 1000:
                sev = Severity.MEDIUM
            if price_diff_abs > 10000:
                sev = Severity.HIGH
            if doc.invoice_amount > self.CRITICAL_VALUE_THRESHOLD:
                sev = Severity.CRITICAL
            results.append(ExceptionResult(
                exception_type=ExceptionType.PRICE_MISMATCH,
                severity=sev,
                confidence=0.92,
                details={
                    "po_amount": doc.po_amount,
                    "invoice_amount": doc.invoice_amount,
                    "diff_pct": round(price_diff_pct, 2),
                    "diff_abs": round(price_diff_abs, 2)
                },
                fingerprint=self._fingerprint(doc, ExceptionType.PRICE_MISMATCH)
            ))

        # Rule 6: Quantity mismatch
        if doc.line_items:
            for li in doc.line_items:
                if li.po_quantity != 0:
                    qty_diff_pct = abs(li.po_quantity - li.invoice_quantity) / abs(li.po_quantity) * 100
                    qty_diff_abs = abs(li.po_quantity - li.invoice_quantity)
                    if qty_diff_pct > self.QUANTITY_TOLERANCE_PCT and qty_diff_abs > self.QUANTITY_TOLERANCE_ABS:
                        results.append(ExceptionResult(
                            exception_type=ExceptionType.QUANTITY_MISMATCH,
                            severity=Severity.MEDIUM,
                            confidence=0.89,
                            details={
                                "po_line_id": li.po_line_id,
                                "po_quantity": li.po_quantity,
                                "invoice_quantity": li.invoice_quantity,
                                "diff_pct": round(qty_diff_pct, 2)
                            },
                            fingerprint=self._fingerprint(doc, ExceptionType.QUANTITY_MISMATCH) + f"-{li.po_line_id}"
                        ))
        else:
            # header qty
            if doc.po_quantity != 0:
                qty_diff_pct = abs(doc.po_quantity - doc.gr_quantity) / abs(doc.po_quantity) * 100 if doc.po_quantity else 0
                if qty_diff_pct > self.QUANTITY_TOLERANCE_PCT and doc.gr_quantity != 0:
                    results.append(ExceptionResult(
                        exception_type=ExceptionType.QUANTITY_MISMATCH,
                        severity=Severity.MEDIUM,
                        confidence=0.85,
                        details={"po_quantity": doc.po_quantity, "gr_quantity": doc.gr_quantity},
                        fingerprint=self._fingerprint(doc, ExceptionType.QUANTITY_MISMATCH)
                    ))

        # Rule 7: Tax code mismatch
        if doc.line_items:
            for li in doc.line_items:
                if li.tax_code_po and li.tax_code_invoice and li.tax_code_po != li.tax_code_invoice:
                    results.append(ExceptionResult(
                        exception_type=ExceptionType.TAX_CODE_MISMATCH,
                        severity=Severity.MEDIUM,
                        confidence=0.93,
                        details={"po_tax": li.tax_code_po, "invoice_tax": li.tax_code_invoice, "line_id": li.po_line_id},
                        fingerprint=self._fingerprint(doc, ExceptionType.TAX_CODE_MISMATCH)
                    ))

        # Rule 8: Vendor master mismatch
        if doc.vendor_master_record:
            master_name = doc.vendor_master_record.get("vendor_name", "").lower()
            if master_name and doc.vendor_name.lower() not in master_name and master_name not in doc.vendor_name.lower():
                # fuzzy mismatch
                if len(doc.vendor_name) > 3:
                    results.append(ExceptionResult(
                        exception_type=ExceptionType.VENDOR_MASTER_MISMATCH,
                        severity=Severity.HIGH,
                        confidence=0.88,
                        details={"master_name": doc.vendor_master_record.get("vendor_name"), "invoice_name": doc.vendor_name},
                        fingerprint=self._fingerprint(doc, ExceptionType.VENDOR_MASTER_MISMATCH)
                    ))
            # Vendor ID format check
            if not self.VENDOR_ID_PATTERN.match(doc.vendor_id):
                results.append(ExceptionResult(
                    exception_type=ExceptionType.VENDOR_MASTER_MISMATCH,
                    severity=Severity.MEDIUM,
                    confidence=0.80,
                    details={"vendor_id": doc.vendor_id, "reason": "format_invalid"},
                    fingerprint=self._fingerprint(doc, ExceptionType.VENDOR_MASTER_MISMATCH) + "-format"
                ))

        # Rule 9: Approval threshold
        if doc.invoice_amount > doc.approval_limit:
            sev = Severity.MEDIUM if doc.invoice_amount < doc.approval_limit * 1.5 else Severity.HIGH
            if doc.invoice_amount > self.CRITICAL_VALUE_THRESHOLD:
                sev = Severity.CRITICAL
            results.append(ExceptionResult(
                exception_type=ExceptionType.APPROVAL_THRESHOLD_BREACH,
                severity=sev,
                confidence=0.97,
                details={"invoice_amount": doc.invoice_amount, "approval_limit": doc.approval_limit},
                fingerprint=self._fingerprint(doc, ExceptionType.APPROVAL_THRESHOLD_BREACH)
            ))

        # Rule 10: Delivery tolerance
        if doc.delivery_date_po and doc.delivery_date_invoice:
            d_po = self._parse_date(doc.delivery_date_po)
            d_inv = self._parse_date(doc.delivery_date_invoice)
            if d_po and d_inv:
                delta_days = abs((d_inv - d_po).days)
                if delta_days > self.DELIVERY_TOLERANCE_DAYS:
                    results.append(ExceptionResult(
                        exception_type=ExceptionType.DELIVERY_TOLERANCE_BREACH,
                        severity=Severity.LOW if delta_days < 15 else Severity.MEDIUM,
                        confidence=0.86,
                        details={"delta_days": delta_days, "po_date": doc.delivery_date_po, "invoice_date": doc.delivery_date_invoice},
                        fingerprint=self._fingerprint(doc, ExceptionType.DELIVERY_TOLERANCE_BREACH)
                    ))

        if not results:
            results.append(ExceptionResult(
                exception_type=ExceptionType.NO_EXCEPTION,
                severity=Severity.LOW,
                confidence=0.99,
                details={"message": "No exception detected, within tolerances"},
                fingerprint=self._fingerprint(doc, ExceptionType.NO_EXCEPTION)
            ))

        return results

    def decide_resolution(self, doc: P2PDocument, exceptions: List[ExceptionResult], ai_advisory: Optional[Dict] = None) -> ResolutionDecision:
        """
        Deterministic resolution - AI advisory is optional and never overrides critical rules.
        This is the core moat statement: AI suggests, deterministic engine decides.
        """
        if not exceptions:
            return ResolutionDecision(
                action=ResolutionAction.AUTO_RESOLVE,
                auto_resolvable=True,
                requires_human=False,
                deterministic_reason="No exceptions detected",
                ai_advisory_used=bool(ai_advisory)
            )

        # Prioritize by severity
        critical = [e for e in exceptions if e.severity == Severity.CRITICAL]
        high = [e for e in exceptions if e.severity == Severity.HIGH]
        medium = [e for e in exceptions if e.severity == Severity.MEDIUM]

        # Critical rules - always block or escalate, AI cannot override
        for exc in critical:
            if exc.exception_type == ExceptionType.DUPLICATE_INVOICE:
                return ResolutionDecision(
                    action=ResolutionAction.BLOCK_INVOICE,
                    auto_resolvable=False,
                    requires_human=True,
                    escalation_target="finance_ops",
                    deterministic_reason=f"Critical duplicate invoice detected: {exc.details}",
                    next_steps=["Block payment", "Notify AP lead", "Contact vendor for credit memo"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )
            if exc.exception_type == ExceptionType.APPROVAL_THRESHOLD_BREACH and doc.invoice_amount > self.CRITICAL_VALUE_THRESHOLD:
                return ResolutionDecision(
                    action=ResolutionAction.REQUIRE_APPROVAL,
                    auto_resolvable=False,
                    requires_human=True,
                    escalation_target="cfo_office",
                    deterministic_reason=f"Critical value breach: {doc.invoice_amount} > {self.CRITICAL_VALUE_THRESHOLD}",
                    next_steps=["Route to CFO approval", "Attach business justification", "Hold payment"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )

        # High severity - deterministic handling
        for exc in exceptions:
            if exc.exception_type == ExceptionType.PO_CLOSED:
                return ResolutionDecision(
                    action=ResolutionAction.ESCALATE_PROCUREMENT,
                    auto_resolvable=False,
                    requires_human=True,
                    escalation_target="procurement",
                    deterministic_reason="PO is closed, cannot invoice against closed PO per policy",
                    next_steps=["Verify PO closure reason", "Request new PO if needed", "Hold invoice"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )
            if exc.exception_type == ExceptionType.PO_EXPIRED:
                return ResolutionDecision(
                    action=ResolutionAction.ESCALATE_PROCUREMENT,
                    auto_resolvable=False,
                    requires_human=True,
                    escalation_target="procurement",
                    deterministic_reason="PO expired, requires re-validation",
                    next_steps=["Check PO extension policy", "Contact requester"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )
            if exc.exception_type == ExceptionType.CURRENCY_MISMATCH:
                return ResolutionDecision(
                    action=ResolutionAction.REQUEST_INFO_VENDOR,
                    auto_resolvable=False,
                    requires_human=True,
                    deterministic_reason=f"Currency mismatch {exc.details}",
                    next_steps=["Request corrected invoice in PO currency", "Verify FX policy"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )
            if exc.exception_type == ExceptionType.VENDOR_MASTER_MISMATCH:
                return ResolutionDecision(
                    action=ResolutionAction.ESCALATE_FINANCE,
                    auto_resolvable=False,
                    requires_human=True,
                    escalation_target="vendor_master_team",
                    deterministic_reason=f"Vendor master mismatch {exc.details}",
                    next_steps=["Validate vendor master record", "Initiate vendor re-verification workflow"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )

        # Medium / Low - potentially auto-resolvable
        # Price mismatch logic
        price_excs = [e for e in exceptions if e.exception_type == ExceptionType.PRICE_MISMATCH]
        if price_excs and len(exceptions) == 1:
            exc = price_excs[0]
            diff_abs = exc.details.get("diff_abs", 0)
            diff_pct = exc.details.get("diff_pct", 0)
            # Auto-resolve if within extended tolerance but outside strict
            if diff_abs <= 100 and diff_pct <= 5.0:
                # AI may suggest adjustment wording, but engine decides amount
                adjustment = doc.invoice_amount - doc.po_amount
                ai_summary = None
                if ai_advisory:
                    ai_summary = ai_advisory.get("summary")
                return ResolutionDecision(
                    action=ResolutionAction.AUTO_RESOLVE_WITH_ADJUSTMENT,
                    auto_resolvable=True,
                    requires_human=False,
                    adjustment_amount=adjustment,
                    adjustment_reason=f"Auto-adjustment within 5% tolerance: PO {doc.po_amount} vs Invoice {doc.invoice_amount}",
                    deterministic_reason=f"Price diff {diff_pct}% / ${diff_abs} within auto-resolve band",
                    next_steps=[f"Apply adjustment of {adjustment}", "Log for audit"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_summary
                )
            else:
                return ResolutionDecision(
                    action=ResolutionAction.REQUEST_INFO_VENDOR,
                    auto_resolvable=False,
                    requires_human=True,
                    deterministic_reason=f"Price mismatch {diff_pct}% exceeds auto-resolve tolerance",
                    next_steps=["Request vendor price justification", "Check contract pricing"],
                    ai_advisory_used=bool(ai_advisory),
                    ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
                )

        # Missing GR - hold
        if any(e.exception_type == ExceptionType.MISSING_GR for e in exceptions):
            return ResolutionDecision(
                action=ResolutionAction.HOLD_FOR_GR,
                auto_resolvable=False,
                requires_human=False,
                deterministic_reason="Missing goods receipt, hold until GR posted",
                next_steps=["Poll GR status", "Notify receiving", "Auto-release on GR"],
                ai_advisory_used=bool(ai_advisory),
                ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
            )

        # Quantity mismatch - similar logic
        qty_excs = [e for e in exceptions if e.exception_type == ExceptionType.QUANTITY_MISMATCH]
        if qty_excs and len(exceptions) == 1:
            return ResolutionDecision(
                action=ResolutionAction.REQUEST_INFO_REQUESTER,
                auto_resolvable=False,
                requires_human=True,
                deterministic_reason="Quantity mismatch requires requester confirmation",
                next_steps=["Contact requester for quantity confirmation", "Verify GR"],
                ai_advisory_used=bool(ai_advisory),
                ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
            )

        # Default for multi-exception or unhandled
        if len(exceptions) > 1:
            return ResolutionDecision(
                action=ResolutionAction.MANUAL_REVIEW,
                auto_resolvable=False,
                requires_human=True,
                deterministic_reason=f"Multiple exceptions ({len(exceptions)}) require manual triage: {[e.exception_type.value for e in exceptions]}",
                next_steps=["Route to AP specialist", "Consolidate exception details"],
                ai_advisory_used=bool(ai_advisory),
                ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
            )

        # Single remaining exception
        single = exceptions[0]
        if single.exception_type == ExceptionType.NO_EXCEPTION:
            return ResolutionDecision(
                action=ResolutionAction.AUTO_RESOLVE,
                auto_resolvable=True,
                requires_human=False,
                deterministic_reason="No exception, auto-resolve",
                next_steps=["Post for payment"],
                ai_advisory_used=bool(ai_advisory),
                ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
            )

        # Fallback
        return ResolutionDecision(
            action=ResolutionAction.MANUAL_REVIEW,
            auto_resolvable=False,
            requires_human=True,
            deterministic_reason=f"Exception {single.exception_type.value} routed to manual review per policy",
            next_steps=["Manual triage"],
            ai_advisory_used=bool(ai_advisory),
            ai_advisory_summary=ai_advisory.get("summary") if ai_advisory else None
        )

    def compute_roi_metrics(self, docs: List[P2PDocument], resolutions: List[ResolutionDecision]) -> Dict:
        total = len(docs)
        if total == 0:
            return {"total": 0, "auto_resolved": 0, "auto_rate": 0, "signature": "Mourad.Soltani"}
        auto = sum(1 for r in resolutions if r.auto_resolvable)
        blocked = sum(1 for r in resolutions if r.action == ResolutionAction.BLOCK_INVOICE)
        escalated = sum(1 for r in resolutions if r.requires_human)
        # Estimated hours saved: 15 min per auto-resolved
        hours_saved = auto * 0.25
        # Estimated cost avoidance from duplicate blocking
        cost_avoidance = blocked * 5000  # conservative estimate

        return {
            "total_processed": total,
            "auto_resolved": auto,
            "auto_resolve_rate": round(auto / total * 100, 2),
            "blocked": blocked,
            "escalated": escalated,
            "estimated_hours_saved": round(hours_saved, 2),
            "estimated_cost_avoidance": cost_avoidance,
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani"
        }
