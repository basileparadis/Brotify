#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Make migrations and migrate
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Start Celery worker
echo "Starting Celery worker..."
celery -A Brotify worker -l info -D

# Start the server using the PORT environment variable
echo "Starting Django server on port ${PORT:-5000}..."
exec python manage.py runserver 0.0.0.0:${PORT:-5000}