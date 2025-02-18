#!/bin/sh

# Ensure directories exist and have proper permissions
mkdir -p /app/data
mkdir -p /app/media/uploads
mkdir -p /app/staticfiles
chmod -R 777 /app/data
chmod -R 777 /app/media
chmod -R 777 /app/staticfiles

# Remove the database file to ensure a clean state
rm -f /app/data/db.sqlite3

# Clean up any existing migrations (except __init__.py)
find /app/files/migrations -type f -not -name '__init__.py' -delete

# Create and run migrations
echo "Creating migrations..."
python manage.py makemigrations

echo "Running migrations..."
# Run migrate without specifying apps to ensure all migrations are applied in the correct order
python manage.py migrate

# Start server
echo "Starting server..."
gunicorn --bind 0.0.0.0:8000 core.wsgi:application 