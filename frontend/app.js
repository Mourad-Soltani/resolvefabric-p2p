// Author: Mourad.Soltani - ResolveFabric P2P Frontend (DOM APIs only, never innerHTML on user input)
(function() {
    const $ = (id) => document.getElementById(id);

    function safeText(el, text) {
        // Use textContent, never innerHTML on user input - per spec
        el.textContent = text;
    }

    function renderJSON(el, obj) {
        // Safe rendering - textContent only
        try {
            const pretty = JSON.stringify(obj, null, 2);
            el.textContent = pretty;
        } catch (e) {
            el.textContent = "Render error: " + e.message;
        }
    }

    async function fetchJSON(url, opts) {
        const resp = await fetch(url, opts);
        const data = await resp.json();
        return { status: resp.status, data };
    }

    async function loadHealth() {
        const el = $("healthStatus");
        safeText(el, "Loading health...");
        try {
            const { data } = await fetchJSON("/health");
            renderJSON(el, data);
        } catch (e) {
            safeText(el, "Health error: " + e.message);
        }
    }

    function getFormPayload() {
        return {
            po_number: $("po_number").value.trim(),
            po_amount: parseFloat($("po_amount").value),
            invoice_number: $("invoice_number").value.trim(),
            invoice_amount: parseFloat($("invoice_amount").value),
            vendor_id: $("vendor_id").value.trim(),
            vendor_name: $("vendor_name").value.trim(),
            po_status: $("po_status").value,
            currency_po: $("currency_po").value.trim() || "USD",
            currency_invoice: $("currency_invoice").value.trim() || "USD",
            approval_limit: parseFloat($("approval_limit").value),
            gr_received: $("gr_received").value === "true",
            is_duplicate_check: $("is_duplicate").value === "true",
            previous_invoices: [],
            line_items: [],
            extra: { signature: "Mourad.Soltani" }
        };
    }

    async function analyze(payload) {
        const el = $("result");
        safeText(el, "Analyzing... deterministic engine + live AI advisory - Mourad.Soltani");
        try {
            const { status, data } = await fetchJSON("/api/v1/exceptions/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (status >= 400) {
                renderJSON(el, { error: data.error || "Error", status, signature: "Mourad.Soltani" });
            } else {
                renderJSON(el, data);
            }
        } catch (e) {
            safeText(el, "Analyze error: " + e.message + " - Mourad.Soltani");
        }
    }

    // Events
    document.addEventListener("DOMContentLoaded", () => {
        loadHealth();
        $("refreshHealth").addEventListener("click", loadHealth);

        $("exceptionForm").addEventListener("submit", (e) => {
            e.preventDefault();
            const payload = getFormPayload();
            analyze(payload);
        });

        $("btnDuplicate").addEventListener("click", () => {
            const p = getFormPayload();
            p.invoice_number = "INV-9001-DUP";
            p.is_duplicate_check = true;
            p.previous_invoices = ["INV-9001-DUP"];
            analyze(p);
        });

        $("btnCurrency").addEventListener("click", () => {
            const p = getFormPayload();
            p.currency_invoice = "EUR";
            analyze(p);
        });

        $("btnNoExc").addEventListener("click", () => {
            const p = getFormPayload();
            p.po_amount = 50000;
            p.invoice_amount = 50000;
            p.po_status = "OPEN";
            p.gr_received = true;
            p.currency_invoice = "USD";
            p.is_duplicate_check = false;
            analyze(p);
        });

        $("btnVerify").addEventListener("click", async () => {
            const el = $("vendorResult");
            safeText(el, "Verifying...");
            const payload = {
                vendor_id: $("v_vendor_id").value.trim(),
                vendor_name: $("v_vendor_name").value.trim(),
                method: "MANUAL_UI"
            };
            try {
                const { data } = await fetchJSON("/api/v1/vendors/verify", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                renderJSON(el, data);
            } catch (e) {
                safeText(el, "Verify error: " + e.message);
            }
        });

        $("btnHealth").addEventListener("click", async () => {
            const el = $("vendorResult");
            const vid = $("v_vendor_id").value.trim();
            safeText(el, "Loading vendor health...");
            try {
                const { data } = await fetchJSON(`/api/v1/vendors/health/${encodeURIComponent(vid)}`);
                renderJSON(el, data);
            } catch (e) {
                safeText(el, "Health error: " + e.message);
            }
        });

        $("btnRot").addEventListener("click", async () => {
            const el = $("vendorResult");
            safeText(el, "Detecting data rot (18mo churn)...");
            try {
                const { data } = await fetchJSON("/api/v1/data/rot");
                renderJSON(el, data);
            } catch (e) {
                safeText(el, "Rot error: " + e.message);
            }
        });

        $("btnROI").addEventListener("click", async () => {
            const el = $("roiResult");
            safeText(el, "Running ROI simulation...");
            // Generate 10 sample docs
            const docs = [];
            for (let i = 0; i < 10; i++) {
                const isDup = i === 2;
                const isPrice = i % 3 === 0;
                docs.push({
                    po_number: i % 2 === 0 ? "PO-1001" : "PO-1002",
                    po_amount: 50000,
                    invoice_number: isDup ? "INV-DUP-001" : `INV-${9000+i}`,
                    invoice_amount: isPrice ? 52000 : 50000,
                    vendor_id: "VEND-001",
                    vendor_name: "Acme Corp",
                    po_status: "OPEN",
                    currency_po: "USD",
                    currency_invoice: "USD",
                    approval_limit: 100000,
                    gr_received: i !== 4,
                    is_duplicate_check: isDup,
                    previous_invoices: isDup ? ["INV-DUP-001"] : [],
                    line_items: []
                });
            }
            try {
                const { data } = await fetchJSON("/api/v1/roi", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ documents: docs })
                });
                renderJSON(el, data);
            } catch (e) {
                safeText(el, "ROI error: " + e.message);
            }
        });
    });
})();
