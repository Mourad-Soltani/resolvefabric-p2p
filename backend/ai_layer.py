"""
Author: Mourad.Soltani
Live AI Integration Layer - Real API calls to hosted model
ResolveFabric P2P - AI suggests, deterministic engine decides (moat)
"""

import os
import time
import json
import hashlib
from typing import Dict, Optional, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import config

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

class AICallError(Exception):
    pass

class AICostGuardError(Exception):
    pass

class ResolveFabricAI:
    AUTHOR = "Mourad.Soltani"
    VERSION = "3.0.0"
    SIGNATURE = "Mourad.Soltani"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.OPENAI_MODEL
        self.base_url = config.OPENAI_BASE_URL.rstrip("/")
        self.timeout = config.AI_TIMEOUT_SECONDS
        self.max_retries = config.AI_MAX_RETRIES
        self.max_tokens = config.AI_MAX_TOKENS
        self.cost_guard_cents = config.AI_COST_GUARD_CENTS
        self.signature = "Mourad.Soltani"

        # Session with retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._call_count = 0
        self._total_tokens_est = 0

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def _estimate_cost_cents(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Rough estimate for gpt-4o-mini: $0.15 per 1M input, $0.60 per 1M output ~ 0.015c per 1k input, 0.06c per 1k output
        # For guard, use conservative 0.15c per 1k combined
        total_k = (prompt_tokens + completion_tokens) / 1000
        return total_k * 0.15

    def _build_prompt(self, doc: Dict, exceptions: List[Dict]) -> List[Dict]:
        system = """You are ResolveFabric AI, an expert P2P exception analyst for Mourad.Soltani platform.
Your job is to provide ADVISORY analysis only - you never make final decisions.
- Analyze the PO vs Invoice exception
- Suggest root cause in 1 sentence
- Suggest vendor communication wording (max 2 sentences)
- Suggest internal next steps (max 3 bullet points)
- Keep tone professional, audit-ready
- Never say you are making the final decision
- Author signature: Mourad.Soltani"""

        user = f"""Analyze this P2P exception case:

PO: {doc.get('po_number')} Amount: {doc.get('po_amount')} Currency: {doc.get('currency_po')} Status: {doc.get('po_status')}
Invoice: {doc.get('invoice_number')} Amount: {doc.get('invoice_amount')} Currency: {doc.get('currency_invoice')}
Vendor: {doc.get('vendor_id')} - {doc.get('vendor_name')}
Exceptions detected: {json.dumps(exceptions, indent=2)}
Line items: {json.dumps(doc.get('line_items', []), indent=2)}

Provide JSON with keys: root_cause, vendor_email_draft, internal_next_steps (list), risk_level (LOW/MEDIUM/HIGH), confidence (0-1), summary (1 sentence).
Author: Mourad.Soltani"""

        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

    def analyze_exception(self, doc: Dict, exceptions: List[Dict], use_mock: bool = False) -> Dict:
        """
        Real live AI call - with deterministic fallback for tests
        """
        self._call_count += 1

        # Cost guard check before call
        est_input_tokens = len(json.dumps(doc)) // 4 + len(json.dumps(exceptions)) // 4 + 500
        est_cost = self._estimate_cost_cents(est_input_tokens, self.max_tokens)
        if est_cost > self.cost_guard_cents:
            raise AICostGuardError(f"Estimated cost {est_cost}c exceeds guard {self.cost_guard_cents}c")

        if use_mock or not self.is_configured():
            return self._mock_response(doc, exceptions)

        messages = self._build_prompt(doc, exceptions)

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            start = time.time()
            resp = self.session.post(url, headers=headers, json=payload, timeout=self.timeout)
            elapsed = time.time() - start

            if resp.status_code == 401:
                raise AICallError("Invalid API key - check OPENAI_API_KEY")
            if resp.status_code == 429:
                raise AICallError("Rate limited by AI provider")
            resp.raise_for_status()

            data = resp.json()
            # Track token usage
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", est_input_tokens)
            completion_tokens = usage.get("completion_tokens", 200)
            self._total_tokens_est += prompt_tokens + completion_tokens

            # Cost check after
            actual_cost = self._estimate_cost_cents(prompt_tokens, completion_tokens)
            if actual_cost > self.cost_guard_cents * 2:  # allow burst but log
                print(f"WARN: Cost {actual_cost}c exceeded 2x guard")

            content = data["choices"][0]["message"]["content"]
            # Parse JSON
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # Try extract JSON block
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                if start_idx >=0 and end_idx>0:
                    parsed = json.loads(content[start_idx:end_idx])
                else:
                    parsed = {"summary": content[:200], "raw": content}

            # Enrich with metadata, ensure signature
            parsed["model_used"] = self.model
            parsed["latency_ms"] = round(elapsed * 1000, 2)
            parsed["tokens_used"] = prompt_tokens + completion_tokens
            parsed["signature"] = "Mourad.Soltani"
            parsed["author"] = "Mourad.Soltani"
            parsed["advisory_only"] = True
            parsed["deterministic_engine_final"] = True

            return parsed

        except requests.exceptions.Timeout:
            # Fallback to mock on timeout - but log
            print(f"AI timeout after {self.timeout}s, using fallback")
            fallback = self._mock_response(doc, exceptions)
            fallback["fallback_reason"] = "timeout"
            return fallback
        except requests.exceptions.RequestException as e:
            raise AICallError(f"AI API call failed: {str(e)}")
        except Exception as e:
            raise AICallError(f"Unexpected AI error: {str(e)}")

    def _mock_response(self, doc: Dict, exceptions: List[Dict]) -> Dict:
        """
        Deterministic mock for tests - hand-verifiable, no randomness
        """
        exc_types = [e.get("exception_type", "UNKNOWN") for e in exceptions]
        has_price = "PRICE_MISMATCH" in exc_types
        has_dup = "DUPLICATE_INVOICE" in exc_types
        has_gr = "MISSING_GR" in exc_types

        if has_dup:
            root_cause = "Duplicate invoice number detected in AP history"
            summary = "Critical duplicate - block payment per policy"
            risk = "HIGH"
            email = "We have identified this invoice as a duplicate of a previously processed invoice. Please provide credit memo or confirm if resubmission is intentional."
        elif has_price:
            root_cause = "Unit price variance exceeds tolerance, likely contract price update not reflected"
            summary = "Price variance requires vendor clarification"
            risk = "MEDIUM"
            email = "We noticed a price variance between PO and invoice. Could you confirm if contract pricing was updated? Please provide supporting documentation."
        elif has_gr:
            root_cause = "Goods receipt not posted, receiving may be pending"
            summary = "Hold pending GR confirmation"
            risk = "LOW"
            email = "Your invoice is on hold pending goods receipt confirmation. Our receiving team has been notified."
        else:
            root_cause = "Exception requires manual validation per policy"
            summary = f"Exception types {exc_types} routed for manual review"
            risk = "MEDIUM"
            email = "We are reviewing your invoice and require additional information. Our AP team will contact you shortly."

        return {
            "root_cause": root_cause,
            "vendor_email_draft": email,
            "internal_next_steps": [
                "Validate exception details against PO contract",
                "Check vendor master for recent updates",
                "Route to appropriate approver if needed"
            ],
            "risk_level": risk,
            "confidence": 0.87,
            "summary": summary,
            "model_used": "mock-deterministic",
            "latency_ms": 12,
            "tokens_used": 150,
            "signature": "Mourad.Soltani",
            "author": "Mourad.Soltani",
            "advisory_only": True,
            "deterministic_engine_final": True,
            "mock": True
        }

    def get_stats(self) -> Dict:
        return {
            "call_count": self._call_count,
            "total_tokens_est": self._total_tokens_est,
            "model": self.model,
            "configured": self.is_configured(),
            "signature": "Mourad.Soltani"
        }
