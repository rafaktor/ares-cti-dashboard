from dataclasses import asdict, dataclass, field
from typing import Optional


# ── Severity thresholds ─
def classify_severity(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


# ── Recommended response actions by IOC type + severity ──────────

_ACTIONS: dict[str, dict[str, list[str]]] = {
    "ip": {
        "CRITICAL": [
            "Block IP on perimeter firewall immediately",
            "Add to threat intelligence blocklist",
            "Query SIEM for historical connections from this IP",
            "Notify SOC team — potential active threat",
            "Initiate endpoint investigation if internal host contacted this IP",
        ],
        "HIGH": [
            "Block IP on perimeter firewall",
            "Add to threat intelligence watchlist",
            "Review SIEM logs for connections to this IP (past 30 days)",
            "Alert on-call analyst",
        ],
        "MEDIUM": [
            "Flag IP for monitoring in SIEM",
            "Review historical traffic to/from this IP",
            "Add to investigation queue",
        ],
        "LOW": [
            "Log incident for tracking",
            "Monitor for future activity",
        ],
    },
    "domain": {
        "CRITICAL": [
            "Block domain at DNS resolver and proxy layer",
            "Add to threat intelligence blocklist",
            "Query SIEM for DNS lookups of this domain",
            "Check for phishing/typosquatting variants",
            "Notify SOC team immediately",
        ],
        "HIGH": [
            "Block domain at DNS resolver",
            "Review DNS query logs (past 30 days)",
            "Alert on-call analyst",
        ],
        "MEDIUM": [
            "Flag domain in DNS monitoring",
            "Review DNS query history",
            "Add to investigation queue",
        ],
        "LOW": [
            "Log incident for tracking",
            "Monitor DNS queries",
        ],
    },
    "hash": {
        "CRITICAL": [
            "Quarantine any file matching this hash immediately",
            "Trigger EDR scan across all endpoints",
            "Search SIEM/EDR for presence of this hash",
            "Isolate affected endpoints from network",
            "Preserve evidence and initiate forensic analysis",
        ],
        "HIGH": [
            "Block execution of this hash via EDR policy",
            "Scan endpoints for file presence",
            "Alert on-call analyst",
        ],
        "MEDIUM": [
            "Flag hash in EDR watchlist",
            "Review file execution history",
            "Add to investigation queue",
        ],
        "LOW": [
            "Log incident for tracking",
            "Monitor for file execution",
        ],
    },
}

_DEFAULT_ACTIONS = ["Log incident for tracking", "Monitor for future activity"]


def get_response_actions(ioc_type: str, severity: str) -> list[str]:
    return _ACTIONS.get(ioc_type, {}).get(severity, _DEFAULT_ACTIONS)


# ── Incident report dataclass ─

@dataclass
class IncidentReport:
    incident_id: str
    created_at: str
    ioc: str
    ioc_type: str
    risk_score: int
    severity: str
    sources: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    country: Optional[str] = None
    last_seen: Optional[str] = None
    recommended_actions: list = field(default_factory=list)
    status: str = "open"

    def to_dict(self) -> dict:
        return asdict(self)
