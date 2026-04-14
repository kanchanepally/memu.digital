# Infrastructure v1.1 — Lessons from Production

**Status:** Active (applied April 2026)
**Context:** This document captures architectural decisions made after a series
of production incidents on the founder's Tier 2 HP Z2 deployment during
March–April 2026. The fixes are now baked into `install.sh`, `backup.sh`,
`docker-compose.yml`, and the setup wizard so future installs don't hit the
same walls.

---

## The three incidents

### Incident 1 — Tailscale-in-Docker lockout

**What happened.** Tailscale was running as a Docker container
(`memu_tailscale`) alongside the rest of the stack. During a routine
`docker compose down` (part of the nightly backup, see Incident 3), the
Tailscale container also went down. The founder, travelling at the time,
lost all remote access to the box. SSH wasn't reachable. The only way back
in would have been physical access.

**What we learned.** Remote access is the last thing you want bundled with
the application stack. The moment you need to fix something on the box
remotely is exactly the moment you can't afford to lose the network.

**What we changed.** Tailscale now installs on the host OS via the upstream
installer (`curl -fsSL https://tailscale.com/install.sh | sh`). `tailscaled`
runs as a systemd service independent of Docker. You can tear the entire
Memu stack down and the box is still reachable. `install.sh` handles this
automatically; the web wizard authenticates the host daemon via
`sudo tailscale up --authkey=...`.

### Incident 2 — Boot ordering race

**What happened.** After a reboot (or after the nightly backup's restart),
4 containers would be stuck in "Created" state. They never actually started.
The database would come up, but the services depending on it wouldn't
transition from Created → Up because Docker Compose's dependency resolution
has a known gap: a dependency being "started" isn't the same as being
"healthy." Containers whose healthcheck prerequisites hadn't fully passed
just sat there forever.

**What we learned.** `depends_on:` as a simple list is a lie. It only means
"start this after that one has started" — not "after that one is healthy."
For services that do real work during startup (like Synapse, which reads
a config and talks to Postgres before it will serve traffic), you need
`condition: service_healthy`. And because Docker's healthcheck ordering
can still race on cold boots, you want a watchdog that catches whatever
slips through.

**What we changed.**
- `docker-compose.yml` — the `proxy` service's `depends_on` now uses
  `condition: service_healthy` on `synapse`.
- A new systemd unit, `memu-watchdog.timer`, fires at boot+90s and daily
  at 02:05 (right after the backup). It runs a short bash script that
  looks for memu containers in "Created" state and `docker start`s them
  manually. Logs to the journal.

### Incident 3 — Nightly backup downtime + disk exhaustion

**What happened.** The original `backup.sh` ran `docker compose down` every
night at 2am to get a consistent snapshot of the PostgreSQL data directory
(`pgdata`). This meant two things: (a) the stack was offline for however
long the backup took — sometimes 15+ minutes when photos had grown — and
(b) on bring-back-up, Incident 2 fired. Cascading failure. On top of that,
backups accumulated on the system disk and eventually filled it up, which
silently broke Docker because `overlay2` had nowhere to write.

**What we learned.** PostgreSQL has a built-in tool for exactly this job:
`pg_dumpall` produces a consistent logical backup while the database is
running. Taking the stack down for backups was never necessary. And
backups belong on a secondary drive, not the system disk — hard drive
space for backups is a different risk profile from hard drive space for
running services.

**What we changed.**
- `scripts/backup.sh` now uses `docker exec memu_postgres pg_dumpall`.
  No `docker compose down`. The stack stays up. `pg_dumpall` captures ALL
  databases (immich, synapse, and future tenants like `memu_core`) in a
  single SQL dump.
- `scripts/install.sh` auto-detects `/mnt/memu-data` at install time and,
  if mounted, points the backup systemd unit at `/mnt/memu-data/backups`
  and `/mnt/memu-data/tmp`. On the founder's HP Z2 this is a 4TB IronWolf.
- `scripts/restore.sh` detects the backup format (new SQL dump vs. legacy
  raw volume files) and restores accordingly.

---

## The four architectural principles that came from this

1. **Remote access is independent of the application stack.** Tailscale on
   host, not in Docker. `docker compose down` must never lock the admin out.

2. **Every critical operation has a watchdog.** Container recovery is
   reactive (we detect "Created" state and kick it). It's not perfect —
   preventive would be better — but reactive beats silent.

3. **Backups must not cause downtime.** `pg_dumpall`, not `docker compose
   down`. The database handles it. The stack should not be forced to
   restart nightly.

4. **Plan for disk space exhaustion.** Secondary drive preferred. System
   disk fill is a silent killer. Backup destination auto-detects.

---

## What changed in the code

| File | What changed |
|------|--------------|
| `docker-compose.yml` | Removed `tailscale:` service and `tailscale_data:` volume. Proxy `depends_on` uses `condition: service_healthy` on synapse. |
| `scripts/install.sh` | Added A1.5 (host Tailscale install), A8 (watchdog systemd units), A9 (backup dir auto-detection). All idempotent. |
| `scripts/backup.sh` | Hot backup via `pg_dumpall`. No compose-down. Reads `BACKUP_DIR` and `TMPDIR` from environment. |
| `scripts/restore.sh` | Format-aware. New v1.1 SQL dumps via `psql`, legacy raw-volume restores still work. |
| `scripts/renew-certs.sh` | Generates certs via host `tailscale cert`, copies into the shared Docker volume. |
| `bootstrap/app.py` | Tailscale auth switched to host CLI (`sudo tailscale up`). Auth key no longer written to `.env`. Health dashboard reads host `tailscale status`. |
| `bootstrap/templates/setup.html` | Help text updated to describe host-level Tailscale. |
| `CLAUDE.md` | New "Architecture Principles (v1.1+)" section. Current State updated. |

---

## What's still not perfect

- **Backups still include photos daily** (~24GB on this machine). Making
  photos weekly while everything else stays daily is cleaner but hasn't
  been done yet. Tracked for v1.2.
- **No disk-space alerting.** We prefer the secondary drive if present and
  warn at install time if there isn't one, but there's nothing that pages
  the admin when either disk gets tight.
- **Watchdog is reactive.** It catches containers stuck in "Created" state
  *after* the fact. A preventive approach — e.g., tightening health-check
  windows and retry semantics so containers don't get stuck in the first
  place — would be better.
- **Backup restore is not automatically tested.** Restoring requires a
  real backup file and a test environment; `scripts/restore.sh` needs
  manual verification when its format handling changes.

---

## Hareesh's HP Z2 notes

The HP Z2 was the source-of-truth for "what working looks like" while
this branch was being built. All of the changes here mirror what was
already running in production for weeks before landing in the repo.
Future `git pull` on that box should be a no-op in terms of behaviour:
same Tailscale on host, same watchdog, same `pg_dumpall` backup, same
`/mnt/memu-data` destination. The only manual step is cleaning up any
`#MIGRATED#` comments in the local `docker-compose.yml` so the file
matches the new repo version.
