# Nginx + PostgreSQL Setup Guide

## What We Installed

### Nginx
- **Purpose:** Web server that receives HTTP requests and forwards them to apps
- **Port:** 80 (HTTP), 443 (HTTPS)
- **Status:** systemctl status nginx
- **Config:** /etc/nginx/

### PostgreSQL
- **Purpose:** Relational database for persistent data storage
- **Port:** 5432 (local access only)
- **Status:** systemctl status postgresql
- **Config:** /etc/postgresql/

## Users Created

- **PostgreSQL User:** kmistry
- **PostgreSQL Database:** app_db
- **Connection String:** postgresql://kmistry:password@localhost:5432/app_db

## How They Work Together

1. Client makes HTTP request to Nginx (port 80)
2. Nginx forwards request to Python/Node app (port 5000, 8000, etc)
3. App queries PostgreSQL (port 5432)
4. Database returns data
5. App processes and responds
6. Nginx sends response back to client

## Security Measures

- PostgreSQL user has limited privileges (only app_db access)
- PostgreSQL only listens on localhost (no remote access)
- Nginx site-specific config (default removed)

## Next Steps

- Configure Nginx as reverse proxy to Python app
- Set up firewall rules (ufw)
- Add HTTPS/SSL certificates
- Implement fail2ban for intrusion prevention
- Add monitoring and alerting
