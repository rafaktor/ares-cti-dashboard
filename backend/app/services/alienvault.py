import requests
from flask import current_app

OTX_URL = "https://otx.alienvault.com/api/v1"


def _headers() -> dict:
    return {"X-OTX-API-KEY": current_app.config["ALIENVAULT_API_KEY"]}


def lookup(ioc: str, ioc_type: str = "IPv4") -> dict:
    """ioc_type: IPv4 | domain | file"""
    section_map = {
        "IPv4": f"{OTX_URL}/indicators/IPv4/{ioc}/general",
        "domain": f"{OTX_URL}/indicators/domain/{ioc}/general",
        "file": f"{OTX_URL}/indicators/file/{ioc}/general",
    }
    url = section_map.get(ioc_type, section_map["IPv4"])
    try:
        resp = requests.get(url, headers=_headers(), timeout=current_app.config["REQUEST_TIMEOUT"])
        resp.raise_for_status()
        data = resp.json()
        pulse_count = data.get("pulse_info", {}).get("count", 0)
        return {
            "score": min(pulse_count * 10, 100),
            "country": data.get("country_code"),
            "tags": [t.get("name") for t in data.get("tags", []) if t.get("name")],
            "last_seen": data.get("date_updated"),
            "raw": data,
        }
    except requests.RequestException as e:
        current_app.logger.error(f"AlienVault error for {ioc}: {e}")
        return {}


def get_pulses(limit: int = 20) -> list:
    try:
        resp = requests.get(
            f"{OTX_URL}/pulses/subscribed",
            headers=_headers(),
            params={"limit": limit},
            timeout=current_app.config["REQUEST_TIMEOUT"],
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except requests.RequestException as e:
        current_app.logger.error(f"AlienVault pulses error: {e}")
        return []
