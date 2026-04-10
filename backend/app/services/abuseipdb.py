import requests
from flask import current_app

ABUSEIPDB_URL = "https://api.abuseipdb.com/api/v2/check"


def lookup(ip: str) -> dict:
    try:
        resp = requests.get(  # nosec B113 — timeout is set via config
            ABUSEIPDB_URL,
            headers={"Key": current_app.config["ABUSEIPDB_API_KEY"], "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": True},
            timeout=current_app.config["REQUEST_TIMEOUT"],
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})
        return {
            "score": data.get("abuseConfidenceScore", 0),
            "country": data.get("countryCode"),
            "tags": list({r.get("category") for r in data.get("reports", []) if r.get("category")}),
            "last_seen": data.get("lastReportedAt"),
            "raw": data,
        }
    except requests.RequestException as e:
        current_app.logger.error(f"AbuseIPDB error for {ip}: {e}")
        return {}
