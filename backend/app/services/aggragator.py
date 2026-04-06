import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services import abuseipdb, alienvault, virustotal
from app.models.indicator import Indicator

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_HASH_RE = re.compile(r"^[a-fA-F0-9]{32,64}$")


def _detect_type(ioc: str) -> str:
    if _IP_RE.match(ioc):
        return "ip"
    if _HASH_RE.match(ioc):
        return "hash"
    return "domain"


def _build_tasks(ioc: str, ioc_type: str) -> dict:
    if ioc_type == "ip":
        return {
            "abuseipdb": lambda: abuseipdb.lookup(ioc),
            "alienvault": lambda: alienvault.lookup(ioc, ioc_type="IPv4"),
            "virustotal": lambda: virustotal.lookup_ip(ioc),
        }
    if ioc_type == "domain":
        return {
            "alienvault": lambda: alienvault.lookup(ioc, ioc_type="domain"),
            "virustotal": lambda: virustotal.lookup_domain(ioc),
        }
    # hash
    return {
        "alienvault": lambda: alienvault.lookup(ioc, ioc_type="file"),
        "virustotal": lambda: virustotal.lookup_hash(ioc),
    }


def _merge(ioc: str, ioc_type: str, results: dict) -> Indicator:
    scores = [v["score"] for v in results.values() if v.get("score") is not None]
    return Indicator(
        ioc=ioc,
        type=ioc_type,
        score=int(sum(scores) / len(scores)) if scores else 0,
        sources=list(results.keys()),
        tags=list({tag for v in results.values() for tag in v.get("tags", [])}),
        country=next((v["country"] for v in results.values() if v.get("country")), None),
        last_seen=next((str(v["last_seen"]) for v in results.values() if v.get("last_seen")), None),
        raw={source: v.get("raw", {}) for source, v in results.items()},
    )


def aggregate(ioc: str, ioc_type: str = None) -> Indicator:
    from flask import current_app
    ioc_type = ioc_type or _detect_type(ioc)
    tasks = _build_tasks(ioc, ioc_type)
    results = {}

    # Flask's current_app context doesn't propagate into threads — push it explicitly.
    app = current_app._get_current_object()

    def run(fn):
        with app.app_context():
            return fn()

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {executor.submit(run, fn): name for name, fn in tasks.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                app.logger.error(f"Aggregator error [{name}] for {ioc}: {e}")
                results[name] = {}

    return _merge(ioc, ioc_type, results)
