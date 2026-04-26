# CLAUDE.md - Memu Operating Instructions

**Last updated:** April 2026 (v1.1 — infrastructure hardening)

---

## Platform Context

Memu OS is one half of the Memu platform. The other half is **memu-core** (early-adopter intelligence layer with mobile app, WhatsApp, Claude API). They compose together: memu-core can dock into memu-os via `docker-compose.home.yml`.

| Document | Location |
|----------|----------|
| memu-core instructions | `C:\Users\Lenovo\Code\memu-core\CLAUDE.md` |
| Platform README (umbrella entry) | `C:\Users\Lenovo\Code\memu-platform\README.md` |
| Bible (vision + manifesto) | `C:\Users\Lenovo\Code\memu-platform\01-BIBLE.md` |
| Architecture | `C:\Users\Lenovo\Code\memu-platform\02-ARCHITECTURE.md` |
| Design System (Indigo Sanctuary) | `C:\Users\Lenovo\Code\memu-platform\03-DESIGN-SYSTEM.md` |
| Roadmap | `C:\Users\Lenovo\Code\memu-platform\04-ROADMAP.md` |
| Pricing/GTM (canonical) | `C:\Users\Lenovo\Code\memu-platform\Pricing and economics\files\memu-gtm-pricing-funding-strategy.md` |
| Privacy Framework | `C:\Users\Lenovo\Code\memu-platform\06-PRIVACY-SECURITY.md` |
| Mobile App Spec | `C:\Users\Lenovo\Code\memu-platform\08-MOBILE-APP-SPEC.md` |
| Engineering backlog (cross-repo) | `C:\Users\Lenovo\Code\memu-platform\memu-core-build-backlog 15 April 2026.md` (read **Part 0** first) |
| Z2 deploy procedure | `C:\Users\Lenovo\Code\memu-platform\12-Z2-DEPLOY.md` |
| Household runbook | `C:\Users\Lenovo\Code\memu-platform\13-HOUSEHOLD-RUNBOOK.md` |

*Note: 07-AGENT-FRAMEWORK and the original Vision/Pricing/UX-Design-System docs have been archived under `_legacy_archive/` pending V3-style rewrites.*

---

## Project Identity

**Memu (మేము)** = "we" in Telugu. A self-hosted family AI platform -- chat, photos, calendar, and intelligence running on hardware families own.

**Tagline:** Your Family's Chief of Staff.

**Stage (2026-04-18):** v1.1 in production on Z2. Family using it daily for 6+ months. Active work: Tier-2 (Hybrid) convergence with memu-core (Milestone B in backlog) and Pod drives (Story 3.5 / B8–B11 — Rach's primary unmet need). Kickstarter June 2026 is **deferred**; commercial path is Founding-50 paid beta first (see `C:\Users\Lenovo\Code\memu-platform\Pricing and economics\files\memu-gtm-pricing-funding-strategy.md`).

**What makes Memu different:** No other product connects family chat + photos + calendar + AI into a single query on hardware the family owns. The unique value is cross-silo intelligence -- "What should I get my wife for her birthday?" searches chats, photos, calendar, and memories to give a real answer.

---

## How We Work: The Operating Model

### The Build Cycle

Memu is built by a solo founder (Hareesh) in evening sessions, with Claude as engineering partner. Every session must be purposeful.

```
┌─────────────────────────────────────────────────────────┐
│                    THE MEMU LOOP                         │
│                                                          │
│   LEARN ──────► DECIDE ──────► BUILD ──────► TEST ──┐   │
│     ▲                                                │   │
│     │                                                │   │
│     └────────────────────────────────────────────────┘   │
│                                                          │
│   Every loop must complete. No building without          │
│   learning. No learning without testing.                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**LEARN:** Feedback arrives from family use, beta testers, Reddit, market changes. It gets captured locally (not in git) and categorised: bug, UX friction, feature request, positioning insight, or competitive signal.

**DECIDE:** Before building anything, ask:
1. Does this move toward Kickstarter? If not, defer.
2. Is this on the critical path? (See roadmap.md for the priority stack)
3. Can it ship as a thin slice in 1-2 evening sessions?
4. Will the family notice and use it?

**BUILD:** One thin slice per session. Working end-to-end before moving to the next thing. No half-built features, no "we'll wire it up later."

**TEST:** Family uses it. If they don't notice or don't use it, it didn't matter. Capture what happened and feed it back into LEARN.

### Session Protocol

At the start of every Claude session:

1. **Check the roadmap** (`roadmap.md`) -- what's the current priority?
2. **Check the private strategy** (`C:\Users\Lenovo\OneDrive\Obsidian-Ventures\01-Projects\Memu\STRATEGY-PRIVATE.md`) -- has anything changed?
3. **Check the decision log** (`C:\Users\Lenovo\OneDrive\Obsidian-Ventures\01-Projects\Memu\decisions\`) -- any recent decisions or feedback?
4. **Ask:** "What's the most important thing to build tonight?"

At the end of every session that produces a meaningful insight:

1. **Update MEMORY.md** if a technical pattern was learned
2. **Update the decision log** if a strategic decision was made
3. **Update roadmap.md** if priorities shifted

### The Priority Filter

Before building anything, run it through this filter (in order):

```
1. Is it on the critical path to Tier-2 in Hareesh's house OR
   Tier-1 ready for the 20-family Founding-50 beta?
   → Convergence (Milestone B) > Pod drives (B8-B11) > Tier-1 hardening (Milestone C)
   → See backlog Part 0 for the active milestone sequence.
   → If no, STOP. Defer it.

2. Does it complete a thin slice?
   → Works end-to-end, independently valuable
   → If no, scope it down until it does.

3. Will Hareesh, Rach, or a Founding-50 beta family notice the difference?
   → If they won't notice it, it's infrastructure, not product.
   → Infrastructure is fine, but don't confuse it with progress.

4. Does it move the evidence dashboard?
   → Cost/family, MAU, 30-day retention, NPS, referral rate.
   → These are the five numbers that unlock the next funding round.
```

### What NOT to Build

The biggest risk for a solo founder is building a feature factory. Guard against:

- **Resume-driven development:** Building things that sound impressive but don't serve families
- **Premature abstraction:** Don't build frameworks, build features
- **Scope creep via "while I'm here":** Fix what you came to fix, nothing more
- **Polish before proof:** Don't perfect the UI before the feature is validated

---

## Information Architecture: What Goes Where

### PUBLIC (in this git repo, visible to open source community)

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `CLAUDE.md` | Operating instructions, how to build, decision framework | When process changes |
| `roadmap.md` | What we're building, priority order, technical specs | When priorities shift |
| `docs/00-BIBLE/PRODUCT-BIBLE.md` | Vision, positioning, architecture, features | When strategy evolves |
| `README.md` | Getting started, installation | When user-facing flow changes |
| All code | The product | Every session |

**Rule:** Public docs describe WHAT and HOW. They don't contain pricing, competitive analysis, marketing tactics, or honest market sizing. They're useful to contributors and users.

### PRIVATE (local only, never committed)

| File | Purpose | Update Frequency |
|------|---------|-----------------|
| `C:\Users\Lenovo\OneDrive\Obsidian-Ventures\01-Projects\Memu\STRATEGY-PRIVATE.md` | Pricing, competitive intel, funnel strategy, market sizing, risk register | Monthly or when market shifts |
| `C:\Users\Lenovo\OneDrive\Obsidian-Ventures\01-Projects\Memu\decisions\` | Decision log -- what was decided, why, what we learned | After significant decisions |
| `C:\Users\Lenovo\OneDrive\Obsidian-Ventures\Writing\Memu\_drafts\` | Memu content drafts (blog posts, launch copy) | As content is created |
| `.claude/memory/MEMORY.md` | Technical patterns Claude needs across sessions | After learning something reusable |

**Rule:** Private docs contain the honest internal thinking. Pricing rationale, competitive weaknesses, funnel conversion assumptions, and "here's what's actually hard" notes. These inform decisions but never leak to the public repo.

### Decision Log Format

When a meaningful decision is made, capture it in `C:\Users\Lenovo\OneDrive\Obsidian-Ventures\01-Projects\Memu\decisions\`:

```markdown
# Decision: [Short Title]
**Date:** YYYY-MM-DD
**Context:** What prompted this decision
**Options Considered:** What we weighed
**Decision:** What we chose
**Reasoning:** Why
**What We'll Learn:** How we'll know if this was right
**Revisit By:** When to check if this still holds
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR HARDWARE                            │
│              Intel N100 Mini PC / Raspberry Pi 5             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │   CHAT   │  │  PHOTOS  │  │    AI    │  │ CALENDAR │    │
│   │  Matrix  │  │  Immich  │  │  Ollama  │  │  Baikal  │    │
│   │ (Synapse)│  │  (v1.0)  │  │(Llama3.2)│  │ (CalDAV) │    │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│        └──────────────┼─────────────┼─────────────┘          │
│                       │             │                        │
│              ┌────────▼─────────────▼───────┐                │
│              │   INTELLIGENCE SERVICE       │                │
│              │   memu_intelligence (Python) │                │
│              │   Bot + Brain + Memory       │                │
│              └──────────────┬───────────────┘                │
│                             │                                │
│              ┌──────────────▼───────────────┐                │
│              │   GUARDIAN (planned)          │                │
│              │   Auto-heal + Monitor + Notify│               │
│              └──────────────┬───────────────┘                │
│                             │                                │
│              ┌──────────────▼───────────────┐                │
│              │       PostgreSQL + pgvector   │                │
│              └──────────────────────────────┘                │
├─────────────────────────────────────────────────────────────┤
│   Bootstrap (Flask) ──► Setup Wizard + Admin Dashboard       │
│   Nginx ──► Reverse proxy (only exposed port: 80/443)       │
│   Tailscale ──► Secure remote access (auto-HTTPS)           │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Service | Container | Purpose |
|---------|-----------|---------|
| Chat Backend | `memu_synapse` | Matrix homeserver |
| Chat UI | `memu_cinny` | Cinny web client (replaced Element Feb 2026) |
| Photos | `memu_photos` | Immich server + ML |
| AI | `memu_brain` | Ollama LLM (Llama 3.2) |
| Bot | `memu_intelligence` | Python Matrix bot -- brain, memory, calendar tools |
| Calendar | `memu_calendar` | Baikal CalDAV/CardDAV |
| Database | `memu_postgres` | PostgreSQL + pgvector |
| Network | *host OS* (`tailscaled`) | Secure remote access (v1.1+: not in Docker) |
| Proxy | `memu_proxy` | Nginx reverse proxy |
| Bootstrap | `memu_bootstrap` | Setup wizard + admin dashboard |

---

## Development Principles

### 1. Thin Slice Delivery

Every feature works end-to-end independently. No partial implementations. No "we'll wire it up later."

**Bad:** "Add database schema for future calendar feature"
**Good:** "Family can ask 'What's happening tomorrow?' and get an answer from the calendar"

### 2. Family-First Validation

Before shipping:
- Does it work for a non-technical spouse?
- Would you explain this over the phone to your parents?
- Does it fail gracefully with helpful messages?

### 3. Security by Default

- All services on internal Docker network (`memu_net`)
- Only nginx exposed (port 80/443)
- Remote access via Tailscale only
- No telemetry, no phone-home, no analytics
- Secrets in `.env`, never in code

### 4. Idempotent Everything

Scripts safe to run multiple times. Check before creating. Preserve existing secrets.

### 5. The Appliance Principle

After `install.sh`, the user never opens a terminal again. Everything manageable via admin dashboard or bot chat. Error messages in plain English, never Docker jargon.

---

## Code Standards

### Python (Intelligence Service)

- Async/await for all I/O
- Type hints required
- Docstrings for public methods
- Logging via `logging` module, not print()
- Error handling with specific exceptions

### Bash (Install Scripts)

- Always `set -e`
- Helper functions for logging
- Idempotent operations
- Comments explain "why", not "what"

### Docker Compose

- Explicit container names (`container_name: memu_*`)
- Health checks on all services
- `restart: unless-stopped` on all services
- Volume mounts for persistence
- Network isolation (`networks: - memu_net`)
- No external ports except nginx

---

## File Structure

```
memu-os/
├── CLAUDE.md                    # THIS FILE - Operating instructions
├── docker-compose.yml           # Production stack
├── .env                         # Secrets (never commit)
├── roadmap.md                   # Priority stack and execution plan
│
├── bootstrap/                   # Setup wizard + admin dashboard
│   ├── app.py                   # Flask application
│   └── templates/               # HTML templates (setup, login, admin, welcome)
│
├── services/
│   └── intelligence/            # Memu Bot (the brain)
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           ├── main.py          # Entry point + scheduler
│           ├── bot.py           # Matrix bot logic + NL dispatch
│           ├── brain.py         # Ollama integration + intent analysis
│           ├── memory.py        # PostgreSQL memory store
│           ├── config.py        # Environment config
│           ├── tools/           # Calendar, shopping list tools
│           └── agents/          # Briefing, digest agents
│
├── synapse/                     # Matrix homeserver config
├── nginx/                       # Reverse proxy config
├── scripts/
│   ├── install.sh               # Main installer
│   └── renew-certs.sh           # Cert renewal (weekly systemd timer)
│
└── docs/
    ├── 00-BIBLE/
    │   └── PRODUCT-BIBLE.md     # Product vision and strategy
    └── user_guide.md            # End-user documentation
```

---

## Current State (April 2026 — v1.1)

### Working
- 2-step installation (script + web wizard, 10 minutes)
- Matrix chat with Cinny (web) + any Matrix mobile app
- Immich photo backup with ML
- Baikal CalDAV family calendar
- Ollama local AI (Llama 3.2)
- Natural language intent (no slash commands needed)
- Cross-silo recall (search across chat, photos, calendar, memories)
- Morning briefings (weather, calendar, news headlines, photo memories, shopping list)
- Admin Settings page (weather, calendar, news feeds, briefing config — all via UI)
- Bot commands: /remember, /recall, /addtolist, /showlist, /done, /remind, /schedule, /calendar, /briefing, /summarize, /ai, /private, /help
- AI volume control (/ai off/quiet/active per room)
- /private command (show what Memu protects)
- Tailscale remote access via host OS (survives Docker lifecycle)
- Container watchdog with automatic recovery
- Zero-downtime backups via pg_dumpall
- Backup auto-detects secondary drive at /mnt/memu-data
- Cert renewal automation (weekly)
- Admin dashboard with service health
- Family member onboarding (QR codes, welcome cards)
- Brand consistency (purple accent, system fonts, SVG badges)

### Known Issues / Not Yet Done
- Daily backups include photos (~24GB). Daily/weekly split is planned but not yet done.
- No disk-space alerting yet (watchdog is reactive, not preventive).
- Watchdog catches stuck-in-"Created" containers but doesn't predict them.

## Architecture Principles (v1.1+)

1. **Remote access is independent of the application stack.** Tailscale runs on
   the host OS, not inside Docker. Any Docker operation — down, up, restart,
   rebuild — must never affect the admin's ability to reach the machine remotely.

2. **No load-bearing single point of failure.** Every critical operation has
   a watchdog, a health check, or a recovery path. The system should degrade
   gracefully, not lock itself out.

3. **Backups must not cause downtime.** Use pg_dumpall, not docker compose down.
   The database is designed to handle this. The application stack is not
   designed to be stopped and restarted every night.

4. **Idempotent install scripts.** Running install.sh twice must not break an
   existing install or duplicate anything. Every section guards with
   `if ! command -v`, `if [ ! -f ]`, or equivalent.

5. **Disk space monitoring.** Secondary drive (/mnt/memu-data) preferred for
   backups. System disk fill is a silent killer — plan for it.

### Building Now (Critical Path)
See `roadmap.md` and `docs/DASHBOARD-PRD.md`:
1. ~~Natural language intent~~ ✅
2. ~~Cross-silo recall~~ ✅
3. ~~AI volume control + /private~~ ✅
4. ~~Morning briefings with weather + news~~ ✅
5. ~~Admin Settings page~~ ✅
6. **Memu Dashboard** — touchscreen UI for the family (pre-Kickstarter priority)
7. Memu Guardian (self-maintaining appliance)

---

## Testing Checklist

Before any commit:

```bash
# 1. Fresh install test (when setup flow changes)
./scripts/install.sh

# 2. Check all containers running
docker ps

# 3. Verify wizard accessible
curl http://localhost:8888

# 4. After wizard completion
docker compose logs synapse | grep -i error
docker compose logs intelligence | grep -i error

# 5. Test bot (in any Matrix client)
# Slash commands:
/showlist
/addtolist test item
/done test
# Natural language (DM the bot):
"What's happening tomorrow?"
"Add milk to the list"
"Give me a briefing"
```

---

## Adding New Capabilities

### New Bot Command or Intent

1. Add handler in `services/intelligence/src/bot.py`
2. If slash command: register in `process_message()` command block
3. If natural language: add intent to `analyze_intent()` prompt in `brain.py`, add dispatch in NL else branch of `process_message()`
4. Test in DM and group room

### New Service

1. Add to `docker-compose.yml` (container_name, health check, memu_net, no external ports)
2. Add nginx proxy rule if web-accessible
3. Add to Guardian monitoring (when Guardian exists)
4. Update architecture docs

---

## Brand & Design System

- **Primary accent:** `#667eea` to `#764ba2` gradient
- **Logo:** Three overlapping circles + "memu" wordmark (inline SVG)
- **Fonts:** System font stack only: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- **Tone:** Warm, empowering, non-technical. "Your family's data belongs to you."
- **Never use:** Google Fonts, old red accent (`#e94560`), Element references, technical jargon in user-facing content

---

## Founder Context

Hareesh is building Memu as a side project while working full-time as a Portfolio Director. Constraints:

- **Time:** Evening sessions only. Must prioritise ruthlessly.
- **Budget:** Bootstrap. Google for Startups Cloud credits applied for; SEIS path open after Memu Ltd registration.
- **Testing:** Family is primary QA team. Hareesh + Rach are the first paying customers under the Tier-2 framing.
- **Goal (2026-04-18):** Tier-2 (Hybrid) working in Hareesh's house → Tier-1 hosted ready for ~20 Founding-50 beta families → evidence-based decision on Kickstarter (autumn 2026 at earliest).

When suggesting work:
- Can this be done in a 2-hour evening session?
- Does this move Milestone B (Tier-2 in house) or Milestone C (Tier-1 hosted ready) forward?
- Will Hareesh, Rach, or a Founding-50 beta family notice and use it?
- Does this move one of the five evidence-dashboard metrics?

---

## License

AGPLv3 - All contributions must be open source.

---

*Maintainer: Hareesh Kanchanepally (@kanchanepally)*
