#!/bin/bash
set -eu

SEED_FLAG="/app/seeded.flag"
echo "Waiting for PostgreSQL server to be ready..."

while ! pg_isready -h db -p 5432 -U ${POSTGRES_USER}; do
  echo "PostgreSQL server is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL server is up and running!"
echo "Running database migrations..."

poetry run python manage.py migrate
echo "Migrations applied."

if [ ! -f "$SEED_FLAG" ]; then
  echo "Seed data flag not found. Running seed_data.py..."
  poetry run python manage.py seed_data --clear
  echo "Seed data executed successfully."
  touch "$SEED_FLAG"
  echo "Seed data flag created: $SEED_FLAG"

else
  echo "Seed data flag found. Skipping seed_data.py execution."
fi

echo "Setting permissions for media directory..."
chmod -R 777 /app/media
echo "Media directory permissions set to 777."

echo "Starting application..."
exec "$@"