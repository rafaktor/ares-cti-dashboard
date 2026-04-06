import os
from flask import Flask
from app.config import config
from app.cache import cache


def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    env = env or os.getenv("FLASK_ENV", "default")
    app.config.from_object(config[env])

    cache.init_app(app)

    from app.api.health import health_bp
    from app.api.threats import threats_bp
    from app.api.indicators import indicators_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(threats_bp, url_prefix="/api")
    app.register_blueprint(indicators_bp, url_prefix="/api")

    return app
