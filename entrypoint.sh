#!/bin/sh

set -e

echo "--- Applying database migrations ---"
python manage.py migrate --noinput

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput --clear

echo "--- Starting Django development server ---"
exec python manage.py runserver 0.0.0.0:8000