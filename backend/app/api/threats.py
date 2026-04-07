from flask import Blueprint, jsonify, request
from app.cache import cache
from app.services import alienvault

threats_bp = Blueprint("threats", __name__)


@threats_bp.get("/threats/feed")
@cache.cached(timeout=300, query_string=True)
def threat_feed():
    limit = min(max(request.args.get("limit", 20, type=int), 1), 100)
    pulses = alienvault.get_pulses(limit=limit)
    feed = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "tags": p.get("tags", []),
            "indicators_count": p.get("indicators_count", 0),
            "created": p.get("created"),
            "author": p.get("author_name"),
        }
        for p in pulses
    ]
    return jsonify({"feed": feed, "count": len(feed)})


@threats_bp.get("/threats/stats")
@cache.cached(timeout=600)
def threat_stats():
    pulses = alienvault.get_pulses(limit=100)
    tag_counts: dict = {}
    for pulse in pulses:
        for tag in pulse.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    return jsonify({
        "total_pulses": len(pulses),
        "top_tags": [{"tag": t, "count": c} for t, c in top_tags],
    })
