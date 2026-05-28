"""Vercel Python serverless entrypoint.

Serves the existing Flask app (backend/app) for every /api/* route.
Vercel's @vercel/python runtime auto-detects the module-level `app`
WSGI callable and wraps it as a serverless function.
"""
import os
import sys

# Make the backend package importable: backend/app/__init__.py -> create_app()
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app import create_app  # noqa: E402

app = create_app("production")
