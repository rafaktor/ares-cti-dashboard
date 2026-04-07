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
    RATELIMIT_DEFAULT = ["60 per hour", "10 per minute"]
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    RATELIMIT_ENABLED = False  # no rate limiting in local dev


class ProductionConfig(Config):
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URI = os.getenv("REDIS_URL", "memory://")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
