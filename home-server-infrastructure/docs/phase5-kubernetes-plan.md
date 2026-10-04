# Phase 5 Plan: Single-Node Kubernetes with k3s

> Status: planned, not started. Requires the Phase 4 stack fix to land first.
> Sized for a ~5–10 hour/week budget across 3–4 sessions.

## Goal

Learn container orchestration — the core DevOps skill — by migrating the
task-manager stack from Docker Compose onto a real (single-node) Kubernetes
cluster, with hand-written manifests so every object is understood, not
generated.

## Hardware and Constraints

| Resource | Value | Implication |
|---|---|---|
| CPU | 20 cores | Plenty for k3s + app + monitoring |
| RAM | 14 GiB (~4–5 GiB free in daily use) | The binding constraint — keep requests/limits lean |
| Disk | 289 GiB free | No constraint |
| Host | daily-driver laptop, Ubuntu 26.04 | Cluster pauses on sleep/reboot; that's fine for learning |

## Why k3s

| Option | Verdict |
|---|---|
| **k3s (chosen)** | Single binary, ~512 MiB overhead, ships Traefik ingress + local-path storage provisioner — a real cluster with production-shaped concepts |
| kind / minikube | Dev/test clusters that come and go; less like a server workload |
| kubeadm | Full-fat Kubernetes; more moving parts, heavier RAM tax on 14 GiB |

## Port Plan (resolve the 80/443 conflict)

The compose stack currently owns 80/443; k3s's Traefik ingress needs them.

**Chosen: stop the compose stack during Phase 5** (`docker compose down`).
Named volumes survive `down`, so `docker compose up -d` remains a working
fallback at any time. Alternative (run both concurrently with compose on
8080/8443) costs ~1 GiB RAM and complicates the ingress story — rejected.

## Steps (each ends with a verification)

**Session A — Preflight + install (~1.5 h)**

1. Snapshot current state: `docker compose ps`, save output to this repo's
   docs folder; `pg_dump` the database to `~/backups` (belt-and-suspenders).
   Verify: backup file exists and is non-trivial in size.
2. `docker compose down`; verify 80/443 are free: `ss -tln | grep -E ':(80|443)'`
   returns nothing.
3. Install k3s: `curl -sfL https://get.k3s.io | sh -`
   Verify: `sudo k3s kubectl get nodes` shows the node `Ready`.
4. Non-root kubectl: `sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config &&
   sudo chown $(id -u):$(id -g) ~/.kube/config && chmod 600 ~/.kube/config`
   Verify: `kubectl get nodes` as the regular user.
   (Optional: install `k9s` for a terminal UI.)

**Session B — Namespace, secrets, database (~2 h)**

5. `kubectl create namespace taskapp`; verify with `kubectl get ns`.
6. Secret: `kubectl create secret generic db-credentials --from-env-file=.env -n taskapp`
   Verify: `kubectl describe secret`. Note the trade-off: Secrets are base64
   (obfuscation, not encryption) — Sealed Secrets/SOPS are listed as later-phase
   hardening.
7. Postgres `StatefulSet` + headless `Service` + `PVC` (local-path class).
   Mount `init.sql` via `ConfigMap` — the official image runs it on first
   volume init, same as compose does. Reuses the existing file unchanged.
   Resource guidance: requests `250m/256Mi`, limits `1/1Gi`.
   Verify: `kubectl get pods -n taskapp` → Running; `kubectl logs` shows
   "database system is ready to accept connections".

**Session C — App + ingress (~2 h)**

8. Flask `Deployment` (2 replicas) + `Service`. Probes on `/health` :5000 —
   it already reports DB connectivity, so **readiness** reflects the real
   dependency chain. Keep **liveness** thresholds generous (a DB outage
   shouldn't restart-loop the app). Resources: requests `100m/128Mi`,
   limits `500m/512Mi` — leaves headroom for Phase 6 monitoring (~1.5–2 GiB
   for kube-prometheus-stack) on a busy desktop.
9. `Ingress` (Traefik) with a TLS Secret created from the existing self-signed
   pair (`kubectl create secret tls ... --cert/--key`).
10. Images: build with the existing Dockerfiles, then
    `docker save taskapp-flask:latest | sudo k3s ctr images import -`
    (postgres:16 is pulled from Docker Hub by the cluster directly).
    Verify: `sudo k3s ctr images ls | grep taskapp`.
11. End-to-end: `curl -k https://localhost/health` → `{"status": "healthy"...}`.

**Session D — Drills + docs (~2 h)**

12. Orchestration drills (the actual learning):
    - `kubectl scale deployment flask --replicas=4`, watch the pods spread
    - rolling update: change the image tag, `kubectl rollout status`, then
      `kubectl rollout undo`
    - `kubectl delete pod <name>` and watch the controller replace it
    - `kubectl describe pod` / `kubectl logs` on a deliberately broken manifest
13. Docs: add the cluster diagram to `docs/architecture.md`, update the README,
    write the lessons-learned note.

## Data Migration

The task list is demo data — plan on a **fresh database** (init.sql runs on
the new PVC). The step-1 `pg_dump` exists if a restore is ever wanted:
`kubectl exec -i <postgres-pod> -- psql -U $PGUSER -d app_db < dump.sql`.

## Risks / Notes

- RAM is the constraint: with the desktop using ~10 GiB, keep the cluster's
  requests lean and add limits everywhere so Kubernetes (not the OOM killer)
  decides what to shed.
- Laptop sleep pauses everything; on wake the node simply re-joins.
- The compose files stay in the repo as the documented fallback path.
