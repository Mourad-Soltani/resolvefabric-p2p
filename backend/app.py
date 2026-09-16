"""
Author: Mourad.Soltani
Flask HTTP Surface for ResolveFabric P2P
Production-grade, deterministic engine + live AI
"""

from flask import Flask, request, jsonify, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import config
from backend.core_engine import P2PCoreEngine, P2PDocument, LineItem
from backend.ai_layer import ResolveFabricAI, AICallError, AICostGuardError
from backend.integration import ERPIntegrationHub
from backend.data_pipeline import VendorNormalizationPipeline
from backend.workers.async_task import AsyncTaskRunner

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

# Initialize Flask
app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Initialize core components
core_engine = P2PCoreEngine()
ai_layer = ResolveFabricAI()
integration_hub = ERPIntegrationHub()
data_pipeline = VendorNormalizationPipeline()
task_runner = AsyncTaskRunner(data_pipeline=data_pipeline, integration_hub=integration_hub)

# Pre-ingest some vendor data for demo moat
_demo_vendors = [
    {"vendor_id": "VEND-001", "vendor_name": "Acme Corp", "tax_id": "12-3456789", "payment_terms": "NET30", "status": "ACTIVE"},
    {"vendor_id": "VEND-002", "vendor_name": "Globex Inc.", "tax_id": "98-7654321", "payment_terms": "NET45", "status": "ACTIVE"},
    {"vendor_id": "VEND-003", "vendor_name": "Initech LLC", "payment_terms": "NET30", "status": "BLOCKED"},
]
for v in _demo_vendors:
    data_pipeline.ingest_vendor(v)

AUTHOR = "Mourad.Soltani"
VERSION = "3.0.0"
SIGNATURE = "Mourad.Soltani"
PROJECT = "resolvefabric-p2p"

def make_envelope(data=None, error=None, status_code=200):
    envelope = {
        "signature": "Mourad.Soltani",
        "author": "Mourad.Soltani",
        "project": PROJECT,
        "version": VERSION,
    }
    if error:
        envelope["error"] = error
    if data is not None:
        envelope["data"] = data
    return jsonify(envelope), status_code

def validate_p2p_payload(payload):
    """Validate at HTTP boundary - wrong type -> 400, never 500"""
    if not isinstance(payload, dict):
        return False, "Payload must be JSON object"
    
    required = ["po_number", "po_amount", "invoice_number", "invoice_amount", "vendor_id", "vendor_name"]
    for field in required:
        if field not in payload:
            return False, f"Missing required field: {field}"
    
    # Type checks
    try:
        float(payload["po_amount"])
        float(payload["invoice_amount"])
    except (ValueError, TypeError):
        return False, "po_amount and invoice_amount must be numeric"
    
    if not isinstance(payload["po_number"], str) or not payload["po_number"].strip():
        return False, "po_number must be non-empty string"
    if not isinstance(payload["invoice_number"], str) or not payload["invoice_number"].strip():
        return False, "invoice_number must be non-empty string"
    if not isinstance(payload["vendor_id"], str) or not payload["vendor_id"].strip():
        return False, "vendor_id must be non-empty string"
    
    # Optional line_items validation
    if "line_items" in payload:
        if not isinstance(payload["line_items"], list):
            return False, "line_items must be list"
        for idx, li in enumerate(payload["line_items"]):
            if not isinstance(li, dict):
                return False, f"line_items[{idx}] must be object"
            for k in ["po_line_id", "po_price", "invoice_price", "po_quantity", "invoice_quantity"]:
                if k not in li:
                    return False, f"line_items[{idx}] missing {k}"
    
    return True, None

def payload_to_document(payload) -> P2PDocument:
    line_items = []
    for li in payload.get("line_items", []):
        line_items.append(LineItem(
            po_line_id=str(li.get("po_line_id", "")),
            po_price=float(li.get("po_price", 0)),
            invoice_price=float(li.get("invoice_price", 0)),
            po_quantity=float(li.get("po_quantity", 0)),
            invoice_quantity=float(li.get("invoice_quantity", 0)),
            po_currency=li.get("po_currency", payload.get("currency_po", "USD")),
            invoice_currency=li.get("invoice_currency", payload.get("currency_invoice", "USD")),
            tax_code_po=li.get("tax_code_po", ""),
            tax_code_invoice=li.get("tax_code_invoice", ""),
            description=li.get("description", "")
        ))
    
    return P2PDocument(
        po_number=str(payload["po_number"]),
        po_amount=float(payload["po_amount"]),
        invoice_number=str(payload["invoice_number"]),
        invoice_amount=float(payload["invoice_amount"]),
        vendor_id=str(payload["vendor_id"]),
        vendor_name=str(payload["vendor_name"]),
        po_status=str(payload.get("po_status", "OPEN")),
        po_expiry_date=payload.get("po_expiry_date"),
        gr_received=bool(payload.get("gr_received", True)),
        gr_quantity=float(payload.get("gr_quantity", 0)),
        po_quantity=float(payload.get("po_quantity", 0)),
        approval_limit=float(payload.get("approval_limit", 100000)),
        delivery_date_po=payload.get("delivery_date_po"),
        delivery_date_invoice=payload.get("delivery_date_invoice"),
        currency_po=payload.get("currency_po", "USD"),
        currency_invoice=payload.get("currency_invoice", "USD"),
        line_items=line_items,
        is_duplicate_check=bool(payload.get("is_duplicate_check", False)),
        previous_invoices=payload.get("previous_invoices", []),
        vendor_master_record=payload.get("vendor_master_record", {}),
        extra=payload.get("extra", {})
    )

@app.route("/")
def index():
    # Serve frontend if exists, else JSON
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_path.exists():
        return send_from_directory(str(frontend_path.parent), "index.html")
    return make_envelope(data={
        "message": "ResolveFabric P2P Exception Autonomy Platform",
        "author": "Mourad.Soltani",
        "endpoints": ["/health", "/api/v1/exceptions/analyze", "/api/v1/exceptions/resolve", "/api/v1/vendors/verify", "/api/v1/integrations/status"],
        "signature": "Mourad.Soltani"
    })

@app.route("/health")
def health():
    # Startup sanity check
    frontend_exists = (Path(__file__).parent.parent / "frontend" / "index.html").exists()
    cfg_errors = config.validate()
    
    data = {
        "status": "healthy" if not cfg_errors else "degraded",
        "project": PROJECT,
        "author": "Mourad.Soltani",
        "version": VERSION,
        "signature": "Mourad.Soltani",
        "ai_layer_configured": ai_layer.is_configured(),
        "integrations_configured": integration_hub.get_status(),
        "frontend_exists": frontend_exists,
        "config_errors": cfg_errors,
        "data_pipeline_stats": data_pipeline.get_stats(),
        "ai_stats": ai_layer.get_stats()
    }
    status = 200 if not cfg_errors else 200  # degraded but not 500
    return make_envelope(data=data, status_code=status)

@app.route("/api/v1/exceptions/analyze", methods=["POST"])
def analyze_exception():
    payload = request.get_json(silent=True)
    if payload is None:
        return make_envelope(error="Invalid JSON payload", status_code=400)
    
    valid, err = validate_p2p_payload(payload)
    if not valid:
        return make_envelope(error=err, status_code=400)
    
    try:
        doc = payload_to_document(payload)
        
        # Deterministic detection first
        exceptions = core_engine.detect_exceptions(doc)
        exc_dicts = [{"exception_type": e.exception_type.value, "severity": e.severity.value, "confidence": e.confidence, "details": e.details, "fingerprint": e.fingerprint, "signature": e.signature} for e in exceptions]
        
        # AI advisory - live call if configured, else mock
        use_mock = request.args.get("mock_ai", "false").lower() == "true" or not ai_layer.is_configured()
        try:
            ai_advisory = ai_layer.analyze_exception(payload, exc_dicts, use_mock=use_mock)
        except (AICallError, AICostGuardError) as e:
            # Fallback to mock on AI error - never fail the request
            ai_advisory = ai_layer._mock_response(payload, exc_dicts)
            ai_advisory["fallback_reason"] = str(e)
        
        # Deterministic decision - AI never has final word
        decision = core_engine.decide_resolution(doc, exceptions, ai_advisory=ai_advisory)
        
        # Record pattern for moat
        for exc in exceptions:
            if exc.exception_type.value != "NO_EXCEPTION":
                fp = data_pipeline.fingerprint_exception(doc.po_number, doc.invoice_number, exc.exception_type.value, doc.vendor_id)
                data_pipeline.record_exception_pattern(fp, exc.exception_type.value, doc.vendor_id, decision.auto_resolvable, 0.5)
        
        response_data = {
            "po_number": doc.po_number,
            "invoice_number": doc.invoice_number,
            "vendor_id": doc.vendor_id,
            "exceptions": exc_dicts,
            "ai_advisory": ai_advisory,
            "decision": {
                "action": decision.action.value,
                "auto_resolvable": decision.auto_resolvable,
                "requires_human": decision.requires_human,
                "adjustment_amount": decision.adjustment_amount,
                "adjustment_reason": decision.adjustment_reason,
                "escalation_target": decision.escalation_target,
                "next_steps": decision.next_steps,
                "deterministic_reason": decision.deterministic_reason,
                "ai_advisory_used": decision.ai_advisory_used,
                "ai_advisory_summary": decision.ai_advisory_summary,
                "signature": decision.signature
            },
            "moat_note": "AI advisory is non-binding; deterministic engine has final word per MOAT.md",
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani"
        }
        
        return make_envelope(data=response_data)
    
    except Exception as e:
        # Never 500 on bad input, but unexpected errors still JSON
        app.logger.exception("analyze_exception failed")
        return make_envelope(error=f"Internal processing error: {str(e)}", status_code=500)

@app.route("/api/v1/exceptions/resolve", methods=["POST"])
def resolve_exception():
    payload = request.get_json(silent=True)
    if payload is None:
        return make_envelope(error="Invalid JSON payload", status_code=400)
    
    # Expecting resolution action
    if "po_number" not in payload or "invoice_number" not in payload or "action" not in payload:
        return make_envelope(error="Missing po_number, invoice_number, or action", status_code=400)
    
    try:
        # Simulate posting to ERP
        connector = integration_hub._route(payload["po_number"])
        erp_resp = connector.post_resolution(payload)
        
        data = {
            "po_number": payload["po_number"],
            "invoice_number": payload["invoice_number"],
            "action_taken": payload["action"],
            "erp_posted": erp_resp.success,
            "erp_response": erp_resp.data,
            "erp_error": erp_resp.error,
            "resolution_id": erp_resp.data.get("resolution_id") if erp_resp.success else None,
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani"
        }
        return make_envelope(data=data, status_code=200 if erp_resp.success else 502)
    except Exception as e:
        return make_envelope(error=str(e), status_code=500)

@app.route("/api/v1/vendors/verify", methods=["POST"])
def verify_vendor():
    payload = request.get_json(silent=True)
    if payload is None:
        return make_envelope(error="Invalid JSON", status_code=400)
    vendor_id = payload.get("vendor_id")
    if not vendor_id or not isinstance(vendor_id, str):
        return make_envelope(error="vendor_id required as string", status_code=400)
    
    # Ingest if provided
    if "vendor_name" in payload:
        rec = data_pipeline.ingest_vendor(payload)
        verify_result = data_pipeline.verify_vendor(vendor_id, payload.get("method", "MANUAL"))
        data = {"ingested": True, "record": {"vendor_id": rec.vendor_id, "normalized": rec.normalized_name, "score": rec.verification_score}, "verification": verify_result}
    else:
        verify_result = data_pipeline.verify_vendor(vendor_id, payload.get("method", "MANUAL"))
        data = {"verification": verify_result}
    
    data["signature"] = "Mourad.Soltani"
    return make_envelope(data=data)

@app.route("/api/v1/vendors/health/<vendor_id>")
def vendor_health(vendor_id):
    if not vendor_id or not isinstance(vendor_id, str):
        return make_envelope(error="Invalid vendor_id", status_code=400)
    health_data = data_pipeline.get_vendor_health(vendor_id)
    if not health_data.get("found"):
        return make_envelope(error=f"Vendor {vendor_id} not found", status_code=404)
    return make_envelope(data=health_data)

@app.route("/api/v1/integrations/status")
def integrations_status():
    return make_envelope(data=integration_hub.get_status())

@app.route("/api/v1/data/stats")
def data_stats():
    return make_envelope(data=data_pipeline.get_stats())

@app.route("/api/v1/data/rot")
def data_rot():
    rotten = data_pipeline.detect_data_rot()
    return make_envelope(data={"rotten_count": len(rotten), "rotten": rotten[:20], "threshold_days": 540})

@app.route("/api/v1/tasks/reverification", methods=["POST"])
def task_reverification():
    result = task_runner.autonomous_reverification()
    return make_envelope(data=result)

@app.route("/api/v1/roi", methods=["POST"])
def compute_roi():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "documents" not in payload:
        return make_envelope(error="Expected {documents: [...]}", status_code=400)
    docs_raw = payload["documents"]
    if not isinstance(docs_raw, list):
        return make_envelope(error="documents must be list", status_code=400)
    
    docs = []
    decisions = []
    for raw in docs_raw:
        valid, err = validate_p2p_payload(raw)
        if not valid:
            continue
        doc = payload_to_document(raw)
        exc = core_engine.detect_exceptions(doc)
        # mock AI for ROI batch
        ai_adv = ai_layer._mock_response(raw, [{"exception_type": e.exception_type.value} for e in exc])
        dec = core_engine.decide_resolution(doc, exc, ai_advisory=ai_adv)
        docs.append(doc)
        decisions.append(dec)
    
    roi = core_engine.compute_roi_metrics(docs, decisions)
    return make_envelope(data=roi)

# Error handlers - JSON envelope with signature field on 400,404,413,500
@app.errorhandler(400)
def handle_400(e):
    return make_envelope(error="Bad request", status_code=400)

@app.errorhandler(404)
def handle_404(e):
    return make_envelope(error="Endpoint not found", status_code=404)

@app.errorhandler(413)
def handle_413(e):
    return make_envelope(error="Payload too large", status_code=413)

@app.errorhandler(500)
def handle_500(e):
    return make_envelope(error="Internal server error", status_code=500)

@app.errorhandler(RequestEntityTooLarge)
def handle_entity_too_large(e):
    return make_envelope(error=f"Payload exceeds {config.MAX_CONTENT_LENGTH} bytes", status_code=413)

# Startup sanity check
def startup_checks():
    frontend_path = Path(__file__).parent.parent / "frontend" / "index.html"
    if not frontend_path.exists():
        print(f"WARN: frontend/index.html missing at {frontend_path} - Mourad.Soltani")
    if config.AI_REQUIRED and not config.OPENAI_API_KEY:
        print("ERROR: AI_REQUIRED=true but OPENAI_API_KEY missing - failing boot per spec - Mourad.Soltani")
        sys.exit(1)
    cfg_errors = config.validate()
    if cfg_errors:
        for err in cfg_errors:
            print(f"CONFIG ERROR: {err}")

# Run startup checks on import
startup_checks()
