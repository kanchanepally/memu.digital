# docs/archive — historical & superseded documents

These docs are kept for history but **no longer describe the current system**. Do not rely on or edit them. For current truth use the canonical docs (below).

| Archived file | Why archived | Current source of truth |
|---|---|---|
| `architecture.md` | Merged into the single engineering doc | `../TECHNICAL_REFERENCE.md` |
| `backup-system.md` | Shipped, but the design changed (now hot `pg_dumpall`, zero downtime — this spec's "stop services" approach was reversed) | `../infrastructure-v1.1.md` |
| `family-onboarding.md` | Feature shipped (QR codes + welcome cards); spec is historical and its route names differ from what shipped | `bootstrap/app.py` (`/api/family/*`, `/welcome/<username>`) |
| `health-dashboard.md` | Mostly shipped (`/api/health` + admin dashboard); in-dashboard service-restart was specced but not built | `bootstrap/app.py:761`, `admin-dashboard.html` |
| `personas/BUILDER.md`, `personas/GUIDE.md`, `personas/LAUNCH.md` | Old "agent persona" files (Jan 2026), superseded by `CLAUDE.md` (operating model) and the platform GTM doc. `LAUNCH.md` also predates the Kickstarter→Founding-50 pivot | `../../CLAUDE.md` |

*Archived 2026-05-30 during a docs-to-code reconciliation pass.*
