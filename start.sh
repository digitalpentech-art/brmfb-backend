#!/usr/bin/env bash
set -e

echo "Checking database connection..."
python -c "
import time, socket, os, urllib.parse as urlparse
db_url = os.environ.get('DATABASE_URL', '')
if db_url:
    url = urlparse.urlparse(db_url)
    hostname = url.hostname
    port = url.port or 5432
    print(f'Attempting connection to database at {hostname}:{port}...')
    while True:
        try:
            s = socket.create_connection((hostname, port), timeout=3)
            s.close()
            print('Database is online and reachable!')
            break
        except Exception as e:
            print(f'Database not ready yet ({e}), retrying in 2 seconds...')
            time.sleep(2)
"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application
