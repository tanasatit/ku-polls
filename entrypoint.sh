#!/bin/sh
set -e

echo "Waiting for database..."
while ! nc -z "$DATABASE_HOST" "$DATABASE_PORT"; do
  sleep 1
done
echo "Database is ready!"

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
