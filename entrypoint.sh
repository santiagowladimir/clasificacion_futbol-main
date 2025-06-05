#!/bin/bash
# entrypoint.sh

# Espera a que la base de datos esté lista (opcional, si no usas wait-for-it.sh)
# Si ya usas wait-for-it.sh en docker-compose, puedes omitir este sleep o un wait-for-it aquí.
# sleep 10 # Descomenta si no usas wait-for-it.sh en docker-compose y necesitas un delay

echo "Running database migrations..."
python manage.py makemigrations # Puede que no necesites makemigrations en cada inicio, solo migrate
python manage.py migrate
echo "Migrations complete."

# Ejecuta el comando principal de tu aplicación como el proceso principal del contenedor
echo "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000