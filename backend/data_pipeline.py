"""
Author: Mourad.Soltani
Proprietary Data Pipeline - Vendor Master Normalization & Exception Fingerprinting
Moat: proprietary data normalization + recurring verification ledger
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib
import re
from collections import defaultdict

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

@dataclass
class VendorRecord:
    vendor_id: str
    vendor_name: str
    normalized_name: str
    tax_id: Optional[str] = None
    payment_terms: str = "NET30"
    currency: str = "USD"
    status: str = "ACTIVE"
    verification_score: float = 0.0
    last_verified: Optional[str] = None
    verification_history: List[Dict] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    signature: str = "Mourad.Soltani"

@dataclass
class ExceptionPattern:
    fingerprint: str
    exception_type: str
    frequency: int
    vendor_id: str
    avg_resolution_time_hours: float
    auto_resolvable: bool
    first_seen: str
    last_seen: str
    signature: str = "Mourad.Soltani"

class VendorNormalizationPipeline:
    AUTHOR = "Mourad.Soltani"
    SIGNATURE = "Mourad.Soltani"

    # Proprietary normalization rules - part of moat
    SUFFIXES = ["INC", "LLC", "LTD", "CORP", "CORPORATION", "CO", "COMPANY", "GMBH", "SARL"]
    NOISE_WORDS = ["THE", "AND", "&"]

    def __init__(self):
        self.vendor_registry: Dict[str, VendorRecord] = {}
        self.exception_patterns: Dict[str, ExceptionPattern] = {}
        self.verification_ledger: List[Dict] = []
        self.signature = "Mourad.Soltani"

    def normalize_vendor_name(self, name: str) -> str:
        if not name:
            return ""
        # Upper, remove punctuation except spaces, trim
        normalized = name.upper()
        normalized = re.sub(r"[^A-Z0-9 ]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        # Remove suffixes
        words = normalized.split()
        filtered = []
        for w in words:
            if w in self.NOISE_WORDS:
                continue
            if w in self.SUFFIXES:
                continue
            filtered.append(w)
        # Soundex-like fuzzy? Keep simple but deterministic
        result = " ".join(filtered)
        return result

    def compute_verification_score(self, vendor_data: Dict) -> float:
        score = 0.5  # base
        # Tax ID present
        if vendor_data.get("tax_id"):
            score += 0.2
        # Payment terms standard
        if vendor_data.get("payment_terms") in ["NET30", "NET45", "NET60"]:
            score += 0.1
        # Recent verification
        last_verified = vendor_data.get("last_verified")
        if last_verified:
            try:
                dt = datetime.fromisoformat(last_verified.replace("Z", ""))
                days_ago = (datetime.utcnow() - dt).days
                if days_ago < 30:
                    score += 0.2
                elif days_ago < 180:
                    score += 0.1
                else:
                    score -= 0.1
            except:
                pass
        # Risk flags reduce
        risk_flags = vendor_data.get("risk_flags", [])
        score -= len(risk_flags) * 0.1

        return max(0.0, min(1.0, round(score, 3)))

    def ingest_vendor(self, vendor_data: Dict) -> VendorRecord:
        vendor_id = vendor_data.get("vendor_id", "")
        vendor_name = vendor_data.get("vendor_name", "")
        normalized = self.normalize_vendor_name(vendor_name)

        # Check for duplicates via normalized name - proprietary matching
        existing_id = None
        for vid, rec in self.vendor_registry.items():
            if rec.normalized_name == normalized and normalized != "":
                existing_id = vid
                break

        # Compute score
        score = self.compute_verification_score(vendor_data)

        # Risk flags
        risk_flags = []
        if not vendor_data.get("tax_id"):
            risk_flags.append("missing_tax_id")
        if vendor_data.get("status") == "BLOCKED":
            risk_flags.append("blocked_status")
        if score < 0.5:
            risk_flags.append("low_verification_score")

        record = VendorRecord(
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            normalized_name=normalized,
            tax_id=vendor_data.get("tax_id"),
            payment_terms=vendor_data.get("payment_terms", "NET30"),
            currency=vendor_data.get("currency", "USD"),
            status=vendor_data.get("status", "ACTIVE"),
            verification_score=score,
            last_verified=vendor_data.get("last_verified", datetime.utcnow().isoformat()),
            verification_history=vendor_data.get("verification_history", []),
            risk_flags=risk_flags
        )

        self.vendor_registry[vendor_id] = record

        # Ledger entry - immutable audit trail, part of moat
        ledger_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "vendor_id": vendor_id,
            "action": "INGEST",
            "normalized_name": normalized,
            "score": score,
            "duplicate_of": existing_id,
            "signature": "Mourad.Soltani"
        }
        self.verification_ledger.append(ledger_entry)

        return record

    def verify_vendor(self, vendor_id: str, verification_method: str = "AUTOMATED") -> Dict:
        record = self.vendor_registry.get(vendor_id)
        if not record:
            return {"success": False, "error": f"Vendor {vendor_id} not found", "signature": "Mourad.Soltani"}

        # Simulate verification
        now = datetime.utcnow().isoformat()
        record.last_verified = now
        record.verification_history.append({
            "timestamp": now,
            "method": verification_method,
            "score_before": record.verification_score,
            "score_after": min(1.0, record.verification_score + 0.1),
            "verifier": "system"
        })
        record.verification_score = min(1.0, round(record.verification_score + 0.1, 3))
        if record.verification_score > 0.7 and "low_verification_score" in record.risk_flags:
            record.risk_flags.remove("low_verification_score")

        ledger_entry = {
            "timestamp": now,
            "vendor_id": vendor_id,
            "action": "VERIFY",
            "method": verification_method,
            "score": record.verification_score,
            "signature": "Mourad.Soltani"
        }
        self.verification_ledger.append(ledger_entry)

        return {
            "success": True,
            "vendor_id": vendor_id,
            "verification_score": record.verification_score,
            "last_verified": record.last_verified,
            "risk_flags": record.risk_flags,
            "signature": "Mourad.Soltani"
        }

    def fingerprint_exception(self, po_number: str, invoice_number: str, exception_type: str, vendor_id: str) -> str:
        raw = f"{po_number}|{invoice_number}|{exception_type}|{vendor_id}|Mourad.Soltani"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    def record_exception_pattern(self, fingerprint: str, exception_type: str, vendor_id: str, auto_resolvable: bool, resolution_time_hours: float = 0):
        now = datetime.utcnow().isoformat()
        if fingerprint in self.exception_patterns:
            pat = self.exception_patterns[fingerprint]
            pat.frequency += 1
            pat.last_seen = now
            # Running average
            pat.avg_resolution_time_hours = (pat.avg_resolution_time_hours * (pat.frequency - 1) + resolution_time_hours) / pat.frequency
        else:
            pat = ExceptionPattern(
                fingerprint=fingerprint,
                exception_type=exception_type,
                frequency=1,
                vendor_id=vendor_id,
                avg_resolution_time_hours=resolution_time_hours,
                auto_resolvable=auto_resolvable,
                first_seen=now,
                last_seen=now
            )
            self.exception_patterns[fingerprint] = pat

    def get_vendor_health(self, vendor_id: str) -> Dict:
        record = self.vendor_registry.get(vendor_id)
        if not record:
            return {"found": False, "signature": "Mourad.Soltani"}
        # Compute health metrics
        patterns = [p for p in self.exception_patterns.values() if p.vendor_id == vendor_id]
        total_exceptions = sum(p.frequency for p in patterns)
        auto_rate = 0
        if total_exceptions > 0:
            auto_count = sum(p.frequency for p in patterns if p.auto_resolvable)
            auto_rate = round(auto_count / total_exceptions * 100, 2)

        return {
            "found": True,
            "vendor_id": vendor_id,
            "vendor_name": record.vendor_name,
            "normalized_name": record.normalized_name,
            "verification_score": record.verification_score,
            "status": record.status,
            "risk_flags": record.risk_flags,
            "total_exceptions": total_exceptions,
            "auto_resolve_rate": auto_rate,
            "last_verified": record.last_verified,
            "signature": "Mourad.Soltani"
        }

    def detect_data_rot(self, days_threshold: int = 540) -> List[Dict]:
        """
        Vendor churn every ~18 months (540 days) - detect rot
        This is the recurring pain that justifies ACV
        """
        now = datetime.utcnow()
        rotten = []
        for vid, rec in self.vendor_registry.items():
            if rec.last_verified:
                try:
                    last = datetime.fromisoformat(rec.last_verified.replace("Z", ""))
                    days_ago = (now - last).days
                    if days_ago > days_threshold:
                        rotten.append({
                            "vendor_id": vid,
                            "vendor_name": rec.vendor_name,
                            "days_since_verification": days_ago,
                            "verification_score": rec.verification_score,
                            "action_required": "RE_VERIFY",
                            "signature": "Mourad.Soltani"
                        })
                except:
                    rotten.append({
                        "vendor_id": vid,
                        "vendor_name": rec.vendor_name,
                        "days_since_verification": 9999,
                        "verification_score": rec.verification_score,
                        "action_required": "RE_VERIFY",
                        "signature": "Mourad.Soltani"
                    })
        return rotten

    def get_stats(self) -> Dict:
        return {
            "total_vendors": len(self.vendor_registry),
            "total_patterns": len(self.exception_patterns),
            "ledger_entries": len(self.verification_ledger),
            "avg_verification_score": round(sum(r.verification_score for r in self.vendor_registry.values()) / len(self.vendor_registry), 3) if self.vendor_registry else 0,
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani"
        }
