from unittest.mock import patch

import pytest

from app import create_app
from app.models.incident import classify_severity, get_response_actions
from app.models.indicator import Indicator

# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app = create_app("development")
    app.config.update({"TESTING": True, "DASHBOARD_API_KEY": "", "WEBHOOK_URL": ""})
    with app.test_client() as c:
        yield c


_CRITICAL_IP = Indicator(
    ioc="198.51.100.1",
    type="ip",
    score=85,
    sources=["virustotal", "abuseipdb"],
    tags=["malware", "botnet"],
    country="RU",
    last_seen="2024-06-01T12:00:00",
    raw={},
)

_LOW_DOMAIN = Indicator(
    ioc="example.com",
    type="domain",
    score=10,
    sources=["alienvault"],
    tags=[],
    country=None,
    last_seen=None,
    raw={},
)

# ── Unit: severity classification ────────────────────────────────────────────

def test_classify_severity_critical():
    assert classify_severity(80) == "CRITICAL"
    assert classify_severity(99) == "CRITICAL"

def test_classify_severity_high():
    assert classify_severity(60) == "HIGH"
    assert classify_severity(79) == "HIGH"

def test_classify_severity_medium():
    assert classify_severity(40) == "MEDIUM"
    assert classify_severity(59) == "MEDIUM"

def test_classify_severity_low():
    assert classify_severity(0) == "LOW"
    assert classify_severity(39) == "LOW"

# ── Unit: response actions ────────────────────────────────────────────────────

def test_critical_ip_has_firewall_action():
    actions = get_response_actions("ip", "CRITICAL")
    assert any("firewall" in a.lower() for a in actions)

def test_critical_hash_has_quarantine_action():
    actions = get_response_actions("hash", "CRITICAL")
    assert any("quarantine" in a.lower() for a in actions)

def test_unknown_type_returns_default_actions():
    actions = get_response_actions("unknown_type", "HIGH")
    assert len(actions) > 0

# ── Integration: POST /api/incidents/report ───────────────────────────────────

def test_create_report_critical(client):
    with patch("app.api.incidents.aggregate", return_value=_CRITICAL_IP):
        res = client.post("/api/incidents/report", json={"ioc": "198.51.100.1"})

    assert res.status_code == 201
    data = res.get_json()

    assert data["ioc"] == "198.51.100.1"
    assert data["ioc_type"] == "ip"
    assert data["severity"] == "CRITICAL"
    assert data["risk_score"] == 85
    assert data["status"] == "open"
    assert data["incident_id"].startswith("INC-")
    assert len(data["recommended_actions"]) > 0
    assert data["country"] == "RU"


def test_create_report_low_score(client):
    with patch("app.api.incidents.aggregate", return_value=_LOW_DOMAIN):
        res = client.post("/api/incidents/report", json={"ioc": "example.com", "type": "domain"})

    assert res.status_code == 201
    data = res.get_json()
    assert data["severity"] == "LOW"


def test_create_report_missing_ioc(client):
    res = client.post("/api/incidents/report", json={})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_report_ioc_too_long(client):
    res = client.post("/api/incidents/report", json={"ioc": "a" * 256})
    assert res.status_code == 400


def test_create_report_no_body(client):
    res = client.post("/api/incidents/report", content_type="application/json", data="")
    assert res.status_code == 400
