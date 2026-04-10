# Ares CTI Dashboard

[![CI](https://github.com/rodriguezgonzalez/ares-cti-dashboard/actions/workflows/ci.yml/badge.svg)](https://github.com/rodriguezgonzalez/ares-cti-dashboard/actions/workflows/ci.yml)
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
