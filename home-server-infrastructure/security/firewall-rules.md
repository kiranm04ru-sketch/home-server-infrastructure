# UFW Firewall Configuration

## What a Firewall Does

A firewall is a filter at the network layer that decides, per connection, whether
traffic is allowed to reach the machine at all. UFW (Uncomplicated Firewall) is the
front-end Ubuntu ships for managing Linux's built-in netfilter rules.

The philosophy here is **deny by default**: anything not explicitly allowed is
dropped. A service that cannot be reached cannot be probed or exploited — this
shrinks the attack surface from "everything listening" to "exactly what I intend
to expose."

## Current Setup

- **Incoming:** deny by default (all unsolicited connections dropped)
- **Outgoing:** allow by default (the server can reach the internet)
- **Explicit allows:** SSH, HTTP, HTTPS only

| Rule | Purpose |
|---|---|
| `22/tcp` (SSH) | Remote administration. Key-only auth + Fail2ban (see `fail2ban-setup.md`) |
| `80/tcp` (HTTP) | Nginx redirect → HTTPS. Not an app entry point |
| `443/tcp` (HTTPS) | The only application entry point (TLS terminates at Nginx) |

PostgreSQL has **no allow rule by design**: the Flask app reaches it through the
internal Docker network, never through the host's firewall.

## Verification

```bash
# Full rule view (needs sudo)
sudo ufw status verbose

# What is actually listening on the host, and on which interface
ss -tlnp | grep -E ':(22|80|443|5000|5432)\s'

# From ANOTHER machine on the LAN (expect: 443 open, 5000/5432 filtered/refused)
nc -zv <server-ip> 443
nc -zv <server-ip> 5432
```

## Docker and UFW — the Gotcha

**Docker's published ports bypass UFW.** When a container publishes a port,
Docker writes its own iptables rules (the `DOCKER` chain) that match before
UFW's rules run. A compose file containing `ports: - "5432:5432"` puts
PostgreSQL on **every interface**, reachable from the LAN even with a
default-deny firewall. This is a classic surprise on Docker hosts and a
frequent finding in security reviews.

**The fix used in this repo:** publish debug-only ports on the loopback
interface, so they never leave the host:

```yaml
# docker-compose.yml
services:
  postgres:
    ports:
      - "127.0.0.1:5432:5432"   # psql debugging from the host only
  flask:
    ports:
      - "127.0.0.1:5000:5000"   # curl the app directly (bypassing TLS) from the host only
  nginx:
    ports:
      - "80:80"                  # intended public entry points stay published
      - "443:443"
```

The containers talk to each other over the `home-server-net` bridge network by
service name (`flask:5000`, `postgres:5432`), so binding 5000/5432 to loopback
costs nothing functionally.

**Further hardening (optional):** the `ufw-docker` utility or hand-written rules
in the `DOCKER-USER` chain can make UFW govern Docker's forwarded traffic too.
Loopback binds are the simpler, robust approach used here.

## Defense in Depth

The firewall is one layer of four:

1. **UFW** — only 22/80/443 are reachable at all
2. **Fail2ban** — repeated SSH failures are banned at the connection level
3. **TLS 1.2+** — traffic that gets in is encrypted (see `ssl-tls-setup.md`)
4. **Least privilege** — the app's DB user owns only `app_db`; debug ports stay
   on loopback

No single layer is assumed to be perfect; each shrinks what an attacker can
reach even if another fails.

## Troubleshooting

```bash
# See rule numbers (for deleting a mistaken rule)
sudo ufw status numbered

# Remove a rule by spec or number
sudo ufw delete allow 8080/tcp
sudo ufw delete 3

# If you lock yourself out over SSH: use the physical console,
# then re-allow before disconnecting:
sudo ufw allow 22/tcp
```

## Production Notes

- `ufw limit 22/tcp` rate-limits SSH connections as an alternative or complement
  to Fail2ban.
- When adding a service later (e.g., a Kubernetes ingress), keep the posture:
  allow one entry port, keep databases and debug interfaces off the network.
