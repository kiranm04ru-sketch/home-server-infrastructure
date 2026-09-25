# Flask Task Manager - Deployment Guide

## Current Deployment

The Flask Task Manager app is **deployed to production at `/opt/flask-app/`**

Do NOT store the app in the git repository. The source code and configuration are environment-specific.

## Installation Steps

1. Copy app to `/opt/flask-app/`
2. Create Python venv: `sudo -u flaskapp python3 -m venv /opt/flask-app/venv`
3. Install dependencies: `sudo -u flaskapp /opt/flask-app/venv/bin/pip install -r /opt/flask-app/requirements.txt`
4. Configure systemd service (see below)
5. Configure Nginx reverse proxy (see nginx config)

## Systemd Service

**File:** `/etc/systemd/system/flask-app.service`

Key settings:
- User: `flaskapp` (dedicated system user)
- Working Directory: `/opt/flask-app`
- Environment variables: PGHOST, PGUSER, PGPASSWORD, PGDATABASE (set in service file, never commit)
- Port: 5000 (localhost only, proxied by Nginx)

## Management

```bash
sudo systemctl start flask-app.service
sudo systemctl stop flask-app.service
sudo systemctl restart flask-app.service
sudo systemctl status flask-app.service
sudo journalctl -u flask-app.service -f
```

## Nginx Reverse Proxy

Nginx forwards HTTPS:443 traffic to Flask:5000

Config file: `/etc/nginx/sites-available/default`

## Database

- Database: `app_db`
- User: `<YOUR_PG_USER>`
- Host: localhost:5432
- Connection: `PGPASSWORD=<YOUR_PG_PASSWORD> psql -h localhost -U <YOUR_PG_USER> -d app_db`

Set `PGPASSWORD` environment variable in `~/.bashrc` to avoid password prompts.

## Architecture

Browser (HTTPS:443)
↓
Nginx Reverse Proxy
↓
Flask App (localhost:5000, systemd service)
↓
PostgreSQL (localhost:5432)


## Security Notes

- Never commit database passwords to git
- Store sensitive config in systemd service file or environment variables
- Use `.pgpass` or `PGPASSWORD` env var for local connections (not in code)
- Flask runs as dedicated `flaskapp` user (not root)
- PostgreSQL accessible only on localhost (firewall blocks external access)
