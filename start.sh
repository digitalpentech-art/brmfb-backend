#!/usr/bin/env bash
set -e

echo "Checking database connection..."
python -c "
import time, os, psycopg2
db_url = os.environ.get('DATABASE_URL', '')
if db_url and not db_url.startswith('sqlite'):
    print('Attempting connection to database...')
    retries = 15
    while retries > 0:
        try:
            conn = psycopg2.connect(db_url, connect_timeout=3)
            conn.close()
            print('Database is online and reachable!')
            break
        except Exception as e:
            retries -= 1
            print(f'Database not ready yet ({e}), {retries} retries left...')
            if retries == 0:
                print('Warning: Could not connect to database via psycopg2, proceeding to migrate anyway...')
                break
            time.sleep(2)
"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application
