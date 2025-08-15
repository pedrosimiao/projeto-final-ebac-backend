#!/bin/bash
set -eu

echo "Waiting for PostgreSQL server to be ready..."

while ! pg_isready -h ${DB_HOST:-db} -p 5432 -U ${POSTGRES_USER}; do
  echo "PostgreSQL server is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL server is up and running!"
echo "Running database migrations..."

poetry run python manage.py migrate
echo "Migrations applied."

echo "Seeding data..."
poetry run python manage.py seed_data --clear
echo "Seed data executed successfully."

echo "Setting permissions for media directory..."
mkdir -p /app/media
chmod -R 777 /app/media
echo "Media directory permissions set to 777."

echo "Collecting static files..."
poetry run python manage.py collectstatic --noinput
echo "Static files collected."


echo "Starting application..."
exec "$@"