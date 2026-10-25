# BRMFB Backend Deployment Guide

This guide outlines the step-by-step process for deploying the **brmfb-backend** Django application to production environments (such as Render, AWS, Heroku, or a VPS).

---

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database & Migrations](#database--migrations)
4. [Static & Media Files](#static--media-files)
5. [Deploying to Render (Platform-as-a-Service)](#deploying-to-render-platform-as-a-service)
6. [Deploying to a VPS (Ubuntu / Linux) via Gunicorn & Nginx](#deploying-to-a-vps-ubuntu--linux-via-gunicorn--nginx)
7. [Production Security Checklist](#production-security-checklist)

---

## 1. Prerequisites
- Python 3.10+ (Python 3.14 recommended / tested)
- PostgreSQL (recommended for production) or SQLite
- Redis (for Celery background tasks / caching)

---

## 2. Environment Configuration

Copy `.env.example` to `.env` and configure production-grade environment variables:

```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secure-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
DATABASE_URL=postgres://user:password@host:port/dbname
```

---

## 3. Database & Migrations

Before launching the app in production, run database migrations:

```bash
python manage.py migrate
```

To seed initial permissions, roles, or data (if applicable):
```bash
python manage.py loaddata initial_data.json
```

---

## 4. Static & Media Files

Collect all static files into `staticfiles/` directory for serving via Web Server / CDN:

```bash
python manage.py collectstatic --noinput
```

---

## 5. Deploying to Render (Platform-as-a-Service)

The repository includes a `render.yaml` blueprint for seamless deployment on Render.

1. Push your repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), click **New** -> **Blueprint**.
3. Connect your repository (`digitalpentech-art/brmfb-backend`).
4. Configure environment variables in Render dashboard (`SECRET_KEY`, `DATABASE_URL`, etc.).
5. Render will automatically build using `requirements/production.txt` and start Gunicorn via `config.wsgi:application`.

---

## 6. Deploying to a VPS (Ubuntu / Linux) via Gunicorn & Nginx

### Step A: Install System Dependencies
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv nginx postgresql libpq-dev
```

### Step B: Set Up Virtual Environment & App
```bash
git clone https://github.com/digitalpentech-art/brmfb-backend.git /var/www/brmfb-backend
cd /var/www/brmfb-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements/production.txt
```

### Step C: Configure Gunicorn Systemd Service (`/etc/systemd/system/brmfb.service`)
```ini
[Unit]
Description=BRMFB Backend Gunicorn Daemon
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/brmfb-backend
ExecStart=/var/www/brmfb-backend/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start brmfb
sudo systemctl enable brmfb
```

### Step D: Configure Nginx Reverse Proxy (`/etc/nginx/sites-available/brmfb`)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /var/www/brmfb-backend/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/brmfb /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

---

## 7. Production Security Checklist

- [ ] `DEBUG = False` in production settings.
- [ ] Strong, randomized `SECRET_KEY`.
- [ ] `ALLOWED_HOSTS` explicitly defined with domain names.
- [ ] SSL/TLS certificate installed (via Let's Encrypt / Certbot) ensuring HTTPS.
- [ ] Secure cookies enabled (`SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`).
