#!/usr/bin/env bash
# =============================================================================
#  build.sh — Render Build Script for Student Management System
#  Render runs this script before starting the web service.
# =============================================================================
set -o errexit  # Exit immediately on error

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate

echo "==> Build complete."
