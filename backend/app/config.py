import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 3600

    ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")
    ALIENVAULT_API_KEY = os.getenv("ALIENVAULT_API_KEY", "")
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")

    # Dashboard API key – set X-API-Key header to this value
    DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY", "")

    # Allowed CORS origin (e.g. https://yourportfolio.com)
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "")

    REQUEST_TIMEOUT = 10  # seconds per upstream call

    # Rate limiting
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    RATELIMIT_ENABLED = False  # no rate limiting in local dev


class ProductionConfig(Config):
    _redis_url = os.getenv("REDIS_URL", "")
    CACHE_TYPE = "RedisCache" if _redis_url else "SimpleCache"
    CACHE_REDIS_URL = _redis_url or None
    RATELIMIT_STORAGE_URI = _redis_url or "memory://"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
