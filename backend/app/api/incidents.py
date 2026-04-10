import logging

import requests
from flask import Blueprint, current_app, jsonify, request

from app.services.aggragator import aggregate
from app.services.reporter import generate_report

incidents_bp = Blueprint("incidents", __name__)
logger = logging.getLogger(__name__)

_SEVERITY_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}


def _fire_webhook(report: dict) -> None:
    """POST a Slack-compatible alert to WEBHOOK_URL if configured."""
    url = current_app.config.get("WEBHOOK_URL", "")
    if not url:
        return

    emoji = _SEVERITY_EMOJI.get(report["severity"], "⚪")
    tags_str = ", ".join(report["tags"][:5]) if report["tags"] else "none"
    payload = {
        "text": (
            f"{emoji} *{report['severity']} Incident — {report['incident_id']}*\n"
            f"IOC: `{report['ioc']}` ({report['ioc_type']})\n"
            f"Risk score: {report['risk_score']}/100\n"
            f"Sources: {', '.join(report['sources'])}\n"
            f"Tags: {tags_str}"
        )
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as exc:
        logger.warning("Webhook delivery failed: %s", exc)


@incidents_bp.post("/incidents/report")
def create_report():
    """
    Resolve an IOC and return a structured incident report.
    """
    body = request.get_json(silent=True) or {}
    ioc = body.get("ioc", "").strip()

    if not ioc:
        return jsonify({"error": "ioc field is required"}), 400
    if len(ioc) > 255:
        return jsonify({"error": "ioc exceeds maximum length of 255 characters"}), 400

    indicator = aggregate(ioc, body.get("type") or None)
    report = generate_report(indicator)
    report_dict = report.to_dict()

    _fire_webhook(report_dict)

    return jsonify(report_dict), 201
