# Linux Systems Administration Portfolio

A comprehensive home server infrastructure project demonstrating Linux systems administration, security hardening, and full-stack application deployment.

## Project Overview

**Three phases of real-world infrastructure:**

### Phase 1: Linux Automation Toolkit
- Automated backups with retention policy
- Log rotation and compression
- System health monitoring (CPU, memory, disk)
- Scheduled security updates

**Skills:** Bash scripting, cron scheduling, system administration

### Phase 2: Security Hardening
- UFW firewall configuration (deny-by-default)
- SSL/TLS with self-signed certificates
- Fail2ban intrusion prevention (3 failed attempts → 1 hour ban)
- SSH hardening (key-only auth, root login disabled)

**Skills:** Network security, firewall rules, authentication, threat mitigation

### Phase 3: Full-Stack Deployment
- Flask web application (Python)
- PostgreSQL database
- Nginx reverse proxy (HTTPS → Flask)
- Systemd service management

**Skills:** Application deployment, database integration, reverse proxy configuration, service management

## Architecture

Internet Request
↓
UFW Firewall (deny incoming, allow 22/80/443)
↓
Nginx (HTTPS:443, reverse proxy, SSL termination)
↓
Flask App (localhost:5000, systemd service)
↓
PostgreSQL (localhost:5432, local-only access)


## Key Technologies

- **OS:** Ubuntu 24.04 LTS
- **Scripting:** Bash
- **Web:** Flask, Nginx, Werkzeug
- **Database:** PostgreSQL
- **Security:** UFW, Fail2ban, OpenSSH
- **Process Management:** systemd
- **Version Control:** Git

## Project Structure

linux_automation_scripts/
├── backups/ # Backup script + cron logs
├── logs/ # Log rotation script
├── monitoring/ # System health monitoring
├── updates/ # Automated update script
└── home-server-infrastructure/
├── setup/ # Nginx + PostgreSQL setup
├── security/ # Firewall, SSL, Fail2ban, SSH configs
└── deployment/ # Flask deployment guide


## What I Learned

- **Linux Systems:** User management, permissions, cron, systemd
- **Security:** Defense-in-depth, firewall rules, certificate management, intrusion detection
- **DevOps:** Service management, reverse proxy, database integration
- **Problem-Solving:** Debugging permission issues, handling edge cases (spaces in filenames, sudo $HOME behavior)
- **Infrastructure:** Full-stack application deployment, production best practices

## How to Review

1. Check the documentation in each directory
2. Review the shell scripts in `backups/`, `logs/`, `monitoring/`, `updates/`
3. See security configurations in `home-server-infrastructure/security/`
4. Read the deployment guide for Flask application setup

All scripts tested and working on Ubuntu 24.04 LTS.
