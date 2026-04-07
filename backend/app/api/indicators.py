from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Blueprint, jsonify, request

from app.cache import cache
from app.services.aggragator import aggregate

indicators_bp = Blueprint("indicators", __name__)

IOC_MAX_LEN = 255


def _validate_ioc(ioc: str):
    """Return an error response tuple or None if valid."""
    if not ioc:
        return jsonify({"error": "ioc field is required"}), 400
    if len(ioc) > IOC_MAX_LEN:
        return jsonify({"error": f"ioc exceeds maximum length of {IOC_MAX_LEN} characters"}), 400
    return None


def _cached_aggregate(ioc: str, ioc_type: str = None) -> dict:
    cache_key = f"indicator:{ioc_type or 'auto'}:{ioc}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    data = aggregate(ioc, ioc_type).to_dict()
    cache.set(cache_key, data, timeout=3600)
    return data


@indicators_bp.post("/indicators/lookup")
def lookup():
    body = request.get_json(silent=True) or {}
    ioc = body.get("ioc", "").strip()
    err = _validate_ioc(ioc)
    if err:
        return err
    return jsonify(_cached_aggregate(ioc, body.get("type")))


@indicators_bp.get("/indicators/ip/<ip>")
def lookup_ip(ip: str):
    err = _validate_ioc(ip)
    if err:
        return err
    return jsonify(_cached_aggregate(ip, "ip"))


@indicators_bp.get("/indicators/domain/<domain>")
def lookup_domain(domain: str):
    err = _validate_ioc(domain)
    if err:
        return err
    return jsonify(_cached_aggregate(domain, "domain"))


@indicators_bp.get("/indicators/hash/<file_hash>")
def lookup_hash(file_hash: str):
    err = _validate_ioc(file_hash)
    if err:
        return err
    return jsonify(_cached_aggregate(file_hash, "hash"))


@indicators_bp.post("/indicators/bulk")
def bulk_lookup():
    body = request.get_json(silent=True) or {}
    iocs = body.get("iocs", [])
    if not iocs or not isinstance(iocs, list):
        return jsonify({"error": "iocs must be a non-empty list"}), 400
    if len(iocs) > 50:
        return jsonify({"error": "max 50 IOCs per bulk request"}), 400

    invalid = [ioc for ioc in iocs if not isinstance(ioc, str) or len(ioc) > IOC_MAX_LEN]
    if invalid:
        return jsonify({"error": f"one or more IOCs exceed {IOC_MAX_LEN} characters or are not strings"}), 400

    results = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(_cached_aggregate, ioc): ioc for ioc in iocs}
        for future in as_completed(futures):
            ioc = futures[future]
            try:
                results[ioc] = future.result()
            except Exception:
                results[ioc] = {"error": "lookup failed"}

    return jsonify({"results": results, "count": len(results)})
