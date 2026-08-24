# Ares CTI Dashboard

[![CI](https://github.com/rafaktor/ares-cti-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/rafaktor/ares-cti-dashboard/actions/workflows/ci.yml)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=rafaktor_ares-cti-dashboard&metric=alert_status)](https://sonarcloud.io/project/overview?id=rafaktor_ares-cti-dashboard)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=rafaktor_ares-cti-dashboard&metric=coverage)](https://sonarcloud.io/project/overview?id=rafaktor_ares-cti-dashboard)

Cyber Threat Intelligence dashboard — aggregates and visualizes threat feeds, IOCs, and security events in real time.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Recharts |
| Backend | Python / Flask |
| CI | GitHub Actions (tests, coverage, Bandit SAST) |
| Quality | SonarCloud |

## Local setup

```bash
# Backend
cd backend
pip install -r requirements.txt
flask run

# Frontend
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest tests/ --cov=app -v
```

Security scan:

```bash
bandit -r backend/app --severity-level medium
```

## Security

- All `/api/*` routes require the `X-API-Key` header (`DASHBOARD_API_KEY`);
  CORS is deny-by-default until `CORS_ORIGIN` is set
- Rate limiting via Flask-Limiter (Redis-backed in production)
- User-supplied IOCs are URL-encoded (`quote(..., safe="")`) before being
  interpolated into upstream VirusTotal / OTX request paths, so input can
  never inject path segments into third-party API calls
- Per-call timeouts on every upstream request; generic error handlers (no
  stack traces to callers)
- CI runs Bandit SAST + SonarCloud on every push
