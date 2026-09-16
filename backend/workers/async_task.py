"""
Author: Mourad.Soltani
Async tasks for autonomous re-verification and resolution
"""

import time
from datetime import datetime
from typing import Dict, List

__author__ = "Mourad.Soltani"
__signature__ = "Mourad.Soltani"

class AsyncTaskRunner:
    AUTHOR = "Mourad.Soltani"
    SIGNATURE = "Mourad.Soltani"

    def __init__(self, data_pipeline=None, integration_hub=None):
        self.data_pipeline = data_pipeline
        self.integration_hub = integration_hub
        self.signature = "Mourad.Soltani"
        self.task_log: List[Dict] = []

    def autonomous_reverification(self) -> Dict:
        """
        Autonomous re-verification job - runs daily, part of moat
        Vendor data rots every ~18 months, this job catches it
        """
        start = datetime.utcnow()
        if not self.data_pipeline:
            return {"success": False, "error": "No pipeline", "signature": "Mourad.Soltani"}

        rotten = self.data_pipeline.detect_data_rot(days_threshold=540)
        verified = []
        for entry in rotten[:10]:  # batch of 10 per run, cost guard
            vid = entry["vendor_id"]
            result = self.data_pipeline.verify_vendor(vid, verification_method="AUTONOMOUS_BATCH")
            if result.get("success"):
                verified.append(vid)

        elapsed = (datetime.utcnow() - start).total_seconds()
        log_entry = {
            "task": "autonomous_reverification",
            "timestamp": start.isoformat(),
            "rotten_detected": len(rotten),
            "verified": len(verified),
            "verified_ids": verified,
            "elapsed_seconds": round(elapsed, 3),
            "signature": "Mourad.Soltani"
        }
        self.task_log.append(log_entry)
        return log_entry

    def polling_gr_status(self, po_numbers: List[str]) -> Dict:
        if not self.integration_hub:
            return {"success": False, "error": "No integration hub", "signature": "Mourad.Soltani"}
        results = []
        for po in po_numbers:
            ctx = self.integration_hub.fetch_full_context(po, "UNKNOWN")
            gr = ctx.get("gr", {})
            results.append({"po_number": po, "gr_received": gr.get("gr_received", False), "signature": "Mourad.Soltani"})
        return {"results": results, "signature": "Mourad.Soltani", "task": "polling_gr_status"}

    def get_task_log(self) -> List[Dict]:
        return self.task_log
