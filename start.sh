#!/usr/bin/env bash
set -e

echo "Checking and patching database URL if needed..."
python -c "
import os, urllib.parse as urlparse
db_url = os.environ.get('DATABASE_URL', '')
if db_url and not db_url.startswith('sqlite'):
    parsed = urlparse.urlparse(db_url)
    if parsed.hostname and '.' not in parsed.hostname:
        new_hostname = f'{parsed.hostname}.frankfurt-postgres.render.com'
        user_pass = f'{parsed.username}:{parsed.password}@' if parsed.username else ''
        port_str = f':{parsed.port}' if parsed.port else ':5432'
        netloc = f'{user_pass}{new_hostname}{port_str}'
        new_url = urlparse.urlunparse((parsed.scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        print(f'Patched DATABASE_URL hostname to FQDN: {new_hostname}')
        with open('/tmp/db_url.env', 'w') as f:
            f.write(f'export DATABASE_URL=\"{new_url}\"\n')
"

if [ -f /tmp/db_url.env ]; then
    source /tmp/db_url.env
fi

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

echo "Ensuring default superuser exists..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@brmfb.com')
password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'AdminPassword123!')
if not User.objects.filter(email=email).exists():
    try:
        User.objects.create_superuser(email=email, password=password)
        print(f'Default superuser created successfully: {email}')
    except Exception as e:
        print(f'Could not create superuser: {e}')
else:
    print('Superuser already exists.')
"

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application
