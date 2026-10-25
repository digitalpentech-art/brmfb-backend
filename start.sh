#!/usr/bin/env bash
set -e

echo "Checking database connection..."
python -c "
import time, socket, os, urllib.parse as urlparse
db_url = os.environ.get('DATABASE_URL', '')
if db_url and not db_url.startswith('sqlite'):
    url = urlparse.urlparse(db_url)
    hostname = url.hostname
    port = url.port or 5432
    if hostname:
        print(f'Attempting connection to database at {hostname}:{port}...')
        retries = 15
        while retries > 0:
            try:
                s = socket.create_connection((hostname, port), timeout=3)
                s.close()
                print('Database is online and reachable!')
                break
            except Exception as e:
                retries -= 1
                print(f'Database not ready yet ({e}), {retries} retries left...')
                if retries == 0:
                    print('Warning: Could not connect to database via socket, proceeding to migrate anyway...')
                    break
                time.sleep(2)
"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application
