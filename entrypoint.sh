#!/bin/bash
set -e

echo "=== Barber CRM API Startup ==="

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Initialize database tables
echo "Initializing database tables..."
python init_db.py

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
