import requests
from flask import current_app

VT_URL = "https://www.virustotal.com/api/v3"


def _headers() -> dict:
    return {"x-apikey": current_app.config["VIRUSTOTAL_API_KEY"]}


def lookup_ip(ip: str) -> dict:
    return _lookup(f"{VT_URL}/ip_addresses/{ip}")


def lookup_domain(domain: str) -> dict:
    return _lookup(f"{VT_URL}/domains/{domain}")


def lookup_hash(file_hash: str) -> dict:
    return _lookup(f"{VT_URL}/files/{file_hash}")


def _lookup(url: str) -> dict:
    try:
        resp = requests.get(url, headers=_headers(), timeout=current_app.config["REQUEST_TIMEOUT"])  # nosec B113
        resp.raise_for_status()
        data = resp.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})
        malicious = stats.get("malicious", 0)
        total = sum(stats.values()) or 1
        return {
            "score": int((malicious / total) * 100),
            "country": data.get("country"),
            "tags": data.get("tags", []),
            "last_seen": data.get("last_modification_date"),
            "raw": data,
        }
    except requests.RequestException as e:
        current_app.logger.error(f"VirusTotal error {url}: {e}")
        return {}
