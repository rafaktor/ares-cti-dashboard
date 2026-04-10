import uuid
from datetime import datetime, timezone

from app.models.incident import IncidentReport, classify_severity, get_response_actions
from app.models.indicator import Indicator


def generate_report(indicator: Indicator) -> IncidentReport:
    """Build a structured incident report from a resolved Indicator."""
    severity = classify_severity(indicator.score)
    return IncidentReport(
        incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
        created_at=datetime.now(timezone.utc).isoformat(),
        ioc=indicator.ioc,
        ioc_type=indicator.type,
        risk_score=indicator.score,
        severity=severity,
        sources=indicator.sources,
        tags=indicator.tags,
        country=indicator.country,
        last_seen=indicator.last_seen,
        recommended_actions=get_response_actions(indicator.type, severity),
    )
