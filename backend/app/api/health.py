import requests
from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    checks = {
        "abuseipdb": (
            "https://api.abuseipdb.com/api/v2/check",
            {"Key": current_app.config["ABUSEIPDB_API_KEY"], "Accept": "application/json"},
        ),
        "alienvault": (
            "https://otx.alienvault.com/api/v1/user/me",
            {"X-OTX-API-KEY": current_app.config["ALIENVAULT_API_KEY"]},
        ),
        "virustotal": (
            "https://www.virustotal.com/api/v3/ip_addresses/8.8.8.8",
            {"x-apikey": current_app.config["VIRUSTOTAL_API_KEY"]},
        ),
    }

    services = {}
    for name, (url, headers) in checks.items():
        try:
            r = requests.get(url, headers=headers, timeout=5)
            services[name] = "ok" if r.status_code < 500 else "degraded"
        except Exception:
            services[name] = "unreachable"

    all_ok = all(v == "ok" for v in services.values())
    return jsonify({"status": "ok" if all_ok else "degraded", "services": services}), 200 if all_ok else 207
