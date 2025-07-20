#!/bin/bash
set -ex # set -e para salir si un comando falla, set -x para depuración

sleep 20

echo "Running database migrations..."
python manage.py migrate
python manage.py makemigrations
python manage.py makemigrations clubes
python manage.py makemigrations users
echo "Migrations complete."

echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000