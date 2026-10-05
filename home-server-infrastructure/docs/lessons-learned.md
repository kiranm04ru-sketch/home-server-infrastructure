# Lessons Learned — Phase 4 Troubleshooting Log

Real incidents from running this stack, written up the way you'd explain
them in an interview: symptom → root cause → fix → the general lesson.

## 1. The database that never came back

**Symptom:** App returned `500 {"error":"Database connection failed"}`.
nginx and Flask were up; the postgres container was simply *gone* (exited
cleanly, exit code 0, ~44 hours earlier).

**Root cause:** The postgres compose service had no `restart:` policy, so a
deliberate stop (`docker stop` / troubleshooting) was permanent. Flask and
nginx had `restart: unless-stopped` — which is why a host reboot brought
back two of three services and quietly left the third dead.

**Fix:** `restart: unless-stopped` on every service; verified across a real
reboot.

**Lesson:** Decide restart behavior *explicitly* for each service. "It
worked until a reboot" almost always means an undeclared restart policy.

## 2. Rotating a database password is a two-sided operation

**Symptom:** After rotating `.env`, the app still failed to authenticate.

**Root cause:** `POSTGRES_PASSWORD` only takes effect at *first
initialization* of the data volume. The volume already existed, so the
role's stored password was still the old one — the env change did nothing.

**Fix:** `ALTER ROLE <user> WITH PASSWORD '<new>'` from inside the
container (the official postgres image trusts local unix-socket
connections, so the change needs no old password), then verify with a
real TCP connection from the *application's* network context.

**Lesson:** A credential has two sides — the secret file and the stored
credential — and rotation must update both. (Corollary: unix-socket trust
inside the container means anyone with docker access is effectively the DB
administrator; that's fine on this box, but it's why docker-group access
is treated as root-equivalent.)

## 3. The `localhost` trap: shell variables beat `.env`

**Symptom:** `.env` was provably correct (`PGHOST=postgres`, matching
passwords), yet the Flask container started with `PGHOST=localhost` and
an 11-character password that matched *nothing* in `.env`.

**Root cause:** `docker compose` interpolation gives **shell environment
variables precedence over `.env`**. A stale block in `~/.bashrc` —
exported months earlier for Phase 3 `psql` convenience, including two
conflicting `PGPASSWORD` exports — rode along into every shell, into the
agent daemon, and into the container environment.

**Fix:** Removed the exports (credentials live in `.env` only); recreated
with a clean environment; confirmed with `docker compose config`, which
prints exactly what the containers will receive.

**Lesson:** Keep credentials in exactly one place, and when environment
driven behavior confuses you, `docker compose config` shows the truth.
(Also: never `export PGPASSWORD` — it leaks into every child process,
including compose.)

## 4. nginx 502 after recreating a container that's still "up"

**Symptom:** After `docker compose up -d` recreated Flask (new container
IP), nginx — untouched, still running — returned `502 Bad Gateway`.

**Root cause:** nginx resolves upstream names (`server flask:5000`) once
at startup and caches the IP. The upstream container got a new IP; nginx
kept dialing the old one.

**Fix (dev):** `docker restart home-server-nginx` after any upstream
recreate. **Fix (production):** `resolver 127.0.0.11 valid=10s;` plus a
variable in `proxy_pass` so nginx re-resolves periodically.

**Lesson:** "The proxy is running" and "the proxy can reach its upstream"
are different health checks.

## 5. A healthcheck that passed while logging FATALs

**Symptom:** postgres logs filled with `FATAL: database "kmistry" does
not exist` every 10 seconds — the healthcheck interval — while the
container reported healthy.

**Root cause:** `pg_isready -U kmistry` defaults the dbname to the
username, so the probe connected to a nonexistent database. The server
still *responded*, which pg_isready counts as healthy.

**Fix:** `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}` — the probe
now exercises the actual database the app depends on.

**Lesson:** A healthcheck should test the thing you actually depend on,
not merely prove a process is listening.

## Carried forward from earlier Phase 4 work

- **Flask must bind `0.0.0.0`** (not `127.0.0.1`) inside its container, or
  other containers can't reach it.
- **Postgres init scripts run against the default database**, so
  `init.sql` must `CREATE DATABASE app_db; \c app_db;` explicitly.
- **Docker's published ports bypass UFW** — debug-only ports are
  loopback-bound (`127.0.0.1:5432:5432`); see `security/firewall-rules.md`.
