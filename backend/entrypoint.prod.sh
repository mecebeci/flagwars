#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running migrations..."
python manage.py migrate --noinput

if [ $# -eq 0 ]; then
    echo "Starting Gunicorn..."
    exec gunicorn django_project.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 3 \
        --timeout 60 \
        --access-logfile - \
        --error-logfile -
else
    echo "Executing command: $@"
    exec "$@"
fi