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

    REQUEST_TIMEOUT = 10  # seconds per upstream call


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
