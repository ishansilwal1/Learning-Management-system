#!/usr/bin/env bash
# exit on error
set -o errexit

# Update pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate --no-input

# Create superuser for production
python manage.py create_production_superuser