# Memu Roadmap

**Current Status:** Alpha validated, building Chief of Staff intelligence features
**Last Updated:** February 2026

---

## Development Directives

Rules that apply to every phase:

1. **Do Not Break the Core:** Matrix (Chat), Immich (Photos), and Ollama (AI) MUST remain functional. We are adding capabilities, not replacing the foundation.
2. **Security First:** Zero Trust Ingress. No new ports exposed to host unless proxied via nginx. All service-to-service communication on internal `memu_net` Docker network.
3. **Idempotency:** All scripts (`install.sh`, `bootstrap/app.py`) must be safe to run multiple times without destroying user data.
4. **Family-first validation:** Before shipping, ask: would a non-technical family member use this without help?

---

## Phase 1: Foundation ✅ COMPLETE (Dec 2025 - Jan 2026)

- [x] Core stack: Matrix chat, Immich photos, Ollama AI, Baikal calendar
- [x] Tailscale integration (auto-HTTPS, secure remote access)
- [x] Morning briefings (calendar + weather + news headlines + photo memories + shopping list)
- [x] Family member onboarding (QR codes, welcome cards)
- [x] Admin dashboard with service health monitoring
- [x] Admin Settings page (weather, calendar, news feeds, briefing config — all via UI)
- [x] Cinny web client (replacing Element Web)
- [x] Cert renewal automation
- [x] Brand refresh (purple accent, system fonts, SVG badges)

---

## Phase 2: Chief of Staff Intelligence 🚧 NOW (Feb - Mar 2026)

### Done

#### Natural language intent ✅
Users talk naturally ("What's happening tomorrow?", "Add milk to the list") and the bot classifies intent and dispatches to the right handler. No slash commands required. DMs process all messages; group rooms require @mention or slash command.

#### Cross-silo recall ✅
`/recall` (or natural language) searches 4 data silos in parallel: saved facts, chat history, calendar events, and photo metadata. When multiple silos return results, the LLM synthesises a unified response connecting the dots across your family's data.
- **Why this matters:** No other product connects family chat + photos + calendar + AI into a single query on hardware you own.

#### Bot stability improvements ✅
Robust self-message detection with multi-layer identity checks and startup diagnostics. Prevents message processing loops across different deployment environments.

#### AI Volume Control ✅
Per-room control over how proactive the bot is:
- `/ai off` — Bot only responds to slash commands
- `/ai quiet` — Slash commands and explicit @mentions only
- `/ai active` — Full natural language processing (default)

Preference persists per-room so different spaces can have different settings. `/private` command also added to surface existing privacy protections (E2EE chat, local AI, per-user photo libraries).

### Building Now

#### Memu Dashboard 🔥 PRE-KICKSTARTER PRIORITY
A touchscreen-optimized web interface that gives the family AI a face. Vertical screen for kitchen counter or wall mount. See `docs/DASHBOARD-PRD.md` for full specification.

**MVP screens (5):**
1. Home — context carousel (weather, next event, photo memory), unified timeline
2. The Pantry — shopping list with voice-add via local Whisper
3. Logistics Command — calendar with AI conflict detection
4. Node Status — hardware health, storage, privacy proof
5. Memory Detail — photo with contextual recall from chat

**New infrastructure:**
- Memu API Gateway (FastAPI + WebSocket) — decouples bot brain from Matrix transport
- Voice I/O — Whisper (input) + Piper TTS (output), all local on the server
- Web frontend — React or vanilla JS + Tailwind, kiosk-mode optimised

**Why before Kickstarter:** The dashboard IS the Kickstarter hero image. It makes Memu visible, photographable, demeable. Without it, you're selling "install Docker and type commands."

#### On This Day photo memories
Surface Immich "on this day" photos in morning briefings and as a standalone command. Photos from this date in previous years.

#### Memu Guardian
A watchdog service that makes Memu self-maintaining. The principle: **after install.sh, the user never opens a terminal again.**

| Problem | Detection | Auto-Fix |
|---------|-----------|----------|
| Container crashes | Health check fails 3x | `docker restart`, notify family room only if restart fails |
| Disk filling up | `df` check every 5 min | Prune Docker images + rotate logs, notify with report |
| Cert expiring | Check cert file dates | Run renewal automatically |
| Tailscale disconnected | `tailscale status` | Reconnect, notify if it fails |
| Ollama model missing | Health check | `ollama pull` silently |
| High memory pressure | `free -m` check | Restart largest non-essential container |

Guardian communicates in plain language to the family chat room. Never shows container IDs, exit codes, or Docker jargon.

**Dashboard upgrade — traffic light model:**
- Green: "Everything is running perfectly. 47 days uptime. 23% storage used."
- Amber: "Storage is filling up (82%). Cleaned up 3GB automatically."
- Red: "Photos service is down. [Restart Photos] [Contact Support]"

### Deferred to Post-Kickstarter

#### Personal Data Export
Any family member can export their data in standard formats:
- Photos: original files in date folders
- Chat: HTML/text export
- Calendar: .ics file
- Memories: JSON/text file

Every family member should be able to take their data with them. Sovereignty means the freedom to leave.

### Coming Next

#### Proactive family suggestions
The AI notices patterns and surfaces them before you ask:
- "Birthday is in 3 weeks. Last year you started planning 2 days before."
- "The boiler service is overdue. Last mentioned done 11 months ago."
- "You have a parents' evening tomorrow. Last time you wanted to ask about maths."

#### Weekly family digest
Sunday evening summary: week's highlights, shopping list activity, chat summary, upcoming week preview.

### Planned (post-Kickstarter)

- **Parental controls** — Graduated freedom for teens: age-appropriate access levels that grow with the child
- **Guardian auto-updates** — Stable channel pulls tested images at 3am, verifies health, rolls back if broken
- **Guardian bot commands** — "Is everything working?", "How much storage?", "Update Memu"
- **Family knowledge graph** — Enhanced cross-silo intelligence with relationship mapping
- **Personal Data Export** — See deferred section above

---

## Phase 3: Kickstarter Prep (June 2026)

**Gate:** Phase 2 features must be done and family must be using them daily.

- [ ] 60-second demo video showing real family use
- [ ] Landing page refresh (memu.digital) with video and email signup
- [ ] 500+ email signups
- [ ] Press outreach
- [ ] Kickstarter page (reward tiers, stretch goals)
- [ ] Hardware supplier sourcing and testing

---

## Phase 4: Production (Post-Kickstarter, Pre-Ship)

- [ ] Auto-updates with rollback
- [ ] Bot maintenance commands
- [ ] Parental controls
- [ ] Pre-configured hardware bundles
- [ ] USB installer image
- [ ] Backup/restore via admin dashboard
- [ ] Security audit
- [ ] Family knowledge graph

---

## Not Building

- Video calls — too resource-intensive for target hardware
- Email hosting — deliverability nightmare
- Public federation — isolation is a feature for family privacy
- VPN server — Tailscale handles this better
- WhatsApp bridge — fragile, Meta breaks it regularly
- Vector embeddings — keyword search works at family scale
- Voice commands beyond dashboard — dashboard gets Whisper, but no always-on wake word yet
- Custom mobile app — existing Matrix/Immich clients work well
- Multi-device clustering — breaks the single-box ownership model

---

## Security Checklist

Before marking any feature complete:

1. **Network Isolation:** New services do NOT have `ports:` in docker-compose.yml. Only accessible via nginx proxy.
2. **Persistence:** Restarting the stack does not wipe data.
3. **Permissions:** Intelligence container has read-only access to Immich DB, read-write to its own memory store.
4. **API Safety:** New endpoints verify requests come from internal network or use shared secret token.

---

## Contributing

See `CLAUDE.md` for development principles and code standards. The best way to contribute is to run Memu with your own family and tell us what's missing.

---

*This roadmap reflects reality, not aspiration. We build what's validated, not what sounds cool.*
