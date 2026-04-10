import logging
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.cache import cache
from app.config import config

limiter = Limiter(key_func=get_remote_address, default_limits=["60 per hour", "10 per minute"])


def _check_api_key(app: Flask):
    """Before-request guard: require X-API-Key on all /api/* routes."""
    if request.method == "OPTIONS":
        return
    required_key = app.config.get("DASHBOARD_API_KEY", "")
    if not required_key:
        # No key configured — open (useful during local dev without the env var)
        return
    if request.path.startswith("/api/"):
        provided = request.headers.get("X-API-Key", "")
        if provided != required_key:
            return jsonify({"error": "Unauthorized"}), 401


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    env = env or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config[env])

    # ── Logging ─────────────────────────────────────────────────────────────
    if not app.debug:
        logging.basicConfig(level=logging.INFO)

    # ── CORS ─────────────────────────────────────────────────────────────────
    origin = app.config.get("CORS_ORIGIN", "")
    CORS(app, origins=[origin] if origin else [], supports_credentials=False)

    # ── Cache ────────────────────────────────────────────────────────────────
    cache.init_app(app)

    # ── Rate limiter ─────────────────────────────────────────────────────────
    limiter.init_app(app)

    # ── Authentication ───────────────────────────────────────────────────────
    app.before_request(lambda: _check_api_key(app))

    # ── Blueprints ───────────────────────────────────────────────────────────
    from app.api.health import health_bp
    from app.api.incidents import incidents_bp
    from app.api.indicators import indicators_bp
    from app.api.threats import threats_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(threats_bp, url_prefix="/api")
    app.register_blueprint(indicators_bp, url_prefix="/api")
    app.register_blueprint(incidents_bp, url_prefix="/api")

    # ── Error handlers (no stack traces to callers) ──────────────────────────
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    @app.errorhandler(Exception)
    def unhandled(e):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500

    return app
