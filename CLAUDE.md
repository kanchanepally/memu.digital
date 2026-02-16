# CLAUDE.md - Memu Operating Instructions

**Last updated:** February 2026

---

## Project Identity

**Memu (మేము)** = "we" in Telugu. A self-hosted family AI platform -- chat, photos, calendar, and intelligence running on hardware families own.

**Tagline:** Your Family's Chief of Staff.

**Stage:** Alpha validated. Building toward Kickstarter (June 2026). Family has been using it daily for 3+ months.

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
2. **Check the private strategy** (`C:\Users\Lenovo\Code\memu\STRATEGY-PRIVATE.md`) -- has anything changed?
3. **Check the decision log** (`C:\Users\Lenovo\Code\memu\decisions\`) -- any recent decisions or feedback?
4. **Ask:** "What's the most important thing to build tonight?"

At the end of every session that produces a meaningful insight:

1. **Update MEMORY.md** if a technical pattern was learned
2. **Update the decision log** if a strategic decision was made
3. **Update roadmap.md** if priorities shifted

### The Priority Filter

Before building anything, run it through this filter (in order):

```
1. Is it on the critical path to Kickstarter?
   → Memu Dashboard > Guardian > Demo video
   → If no, STOP. Defer it.

2. Does it complete a thin slice?
   → Works end-to-end, independently valuable
   → If no, scope it down until it does.

3. Can a non-technical family member tell the difference?
   → If they won't notice it, it's infrastructure, not product.
   → Infrastructure is fine, but don't confuse it with progress.

4. Does it make the demo video better?
   → The demo video is the product. Features that aren't demo-able
     don't drive the Kickstarter.
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
| `../STRATEGY-PRIVATE.md` | Pricing, competitive intel, funnel strategy, market sizing, risk register | Monthly or when market shifts |
| `../decisions/YYYY-MM-topic.md` | Decision log -- what was decided, why, what we learned | After significant decisions |
| `../decisions/feedback-log.md` | Raw feedback from family, beta users, Reddit | As feedback arrives |
| `.claude/memory/MEMORY.md` | Technical patterns Claude needs across sessions | After learning something reusable |

**Rule:** Private docs contain the honest internal thinking. Pricing rationale, competitive weaknesses, funnel conversion assumptions, and "here's what's actually hard" notes. These inform decisions but never leak to the public repo.

### Decision Log Format

When a meaningful decision is made, capture it in `../decisions/`:

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
| Network | `memu_tailscale` | Secure remote access |
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

## Current State (February 2026)

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
- Tailscale remote access with auto-HTTPS
- Cert renewal automation (weekly)
- Admin dashboard with service health
- Family member onboarding (QR codes, welcome cards)
- Brand consistency (purple accent, system fonts, SVG badges)

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
- **Budget:** Bootstrap, no external funding yet.
- **Testing:** Family is primary QA team.
- **Goal:** Kickstarter launch June 2026.

When suggesting work:
- Can this be done in a 2-hour evening session?
- Does this move toward Kickstarter readiness?
- Will the family notice and use it?
- Does this make the 60-second demo video better?

---

## License

AGPLv3 - All contributions must be open source.

---

*Maintainer: Hareesh Kanchanepally (@kanchanepally)*
