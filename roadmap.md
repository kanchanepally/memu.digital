# Memu Roadmap

**Current Status:** Alpha validated, entering Chief of Staff intelligence phase
**Last Updated:** February 2026

---

## Development Directives

Rules that apply to every phase:

1. **Do Not Break the Core:** Matrix (Chat), Immich (Photos), and Ollama (AI) MUST remain functional. We are adding capabilities, not replacing the foundation.
2. **Security First:** Zero Trust Ingress. No new ports exposed to host unless proxied via nginx. All service-to-service communication on internal `memu_net` Docker network.
3. **Idempotency:** All scripts (`install.sh`, `bootstrap/app.py`) must be safe to run multiple times without destroying user data.
4. **Family-first validation:** Before shipping, ask: would a non-technical spouse use this without help?

---

## Phase 1: Validation ✅ COMPLETE (Dec 2025 - Jan 2026)

Everything in this phase shipped and is running in production.

- [x] Reddit validation (r/selfhosted, r/LocalLLaMA — technical engagement, no dismissals)
- [x] Tailscale integration replacing Cloudflare (auto-HTTPS via `tailscale cert`)
- [x] Family calendar (Baikal CalDAV, `/schedule`, `/calendar` commands)
- [x] Morning briefings (calendar + weather + Immich memories + shopping list)
- [x] Family member onboarding (QR codes, welcome cards, welcome pages)
- [x] Admin dashboard with service health monitoring
- [x] Cinny replacing Element Web (Element WidgetStore crash on self-hosted)
- [x] Cert renewal automation (weekly systemd timer)
- [x] Unified recall (searches saved facts + chat history)
- [x] Brand refresh (purple accent, system fonts, SVG badges, no Google Fonts)

**Validation Result:** Problem is real. At least 4 people building similar things. "Context beats capability" framing resonates.

---

## Phase 2: Chief of Staff Intelligence 🚧 NOW (Feb - Mar 2026)

Ordered by priority. Each item is scoped to 1-3 evening sessions.

### 1. Natural language intent ✅ DONE
Kill the slash command requirement. Users talk naturally ("What's happening tomorrow?", "Add milk to the list") and the bot classifies intent via `analyze_intent()` in brain.py (structured JSON), dispatches to existing handlers. DMs process all messages; group rooms require @mention or slash command.

### 2. On This Day photo memories
Surface Immich "on this day" photos in morning briefings and as a standalone command. Query Immich API for photos from this date in previous years.
- **Effort:** 1 session
- **Dependencies:** Immich API key in config
- **Files:** `services/intelligence/src/agents/briefing.py`, new photo memory tool

### 3. Weekly family digest
Sunday evening summary: week's calendar highlights, shopping list activity, chat summary, upcoming week preview. Delivered to family room.
- **Effort:** 1 session
- **Dependencies:** Briefing agent pattern (already built)
- **Files:** New `services/intelligence/src/agents/digest.py`, scheduler in `main.py`

### 4. Cross-silo recall
When user asks "What did we discuss about Dad's birthday?", search chat history AND calendar events AND saved facts. Unified context response.
- **Effort:** 3 sessions
- **Dependencies:** Calendar tool + memory store + brain summarization
- **Files:** `services/intelligence/src/memory.py` (add calendar search), `bot.py` (enhanced recall)

### 5. Kitchen Dashboard
Zero-friction tablet PWA for the kitchen fridge (iPad/tablet).
- **Effort:** 5-6 sessions
- **Dependencies:** FastAPI wrapper around intelligence service

**Technical spec:**
- Wrap `memu_intelligence` bot in FastAPI (`uvicorn` as entry point, bot as background task)
- New API endpoints:
  - `GET /api/dashboard/summary` — events, shopping list count, weather
  - `GET /api/shopping-list` — current list
  - `POST /api/shopping-list/add` — add item
  - `GET /api/photos/random` — proxy to Immich for "on this day" or favorite photo
- Frontend: React + Vite + TypeScript + Tailwind CSS in `services/kitchen-os/`
- UI: 3-column grid (clock/calendar | shopping list | photo slideshow), dark mode default
- Docker: multi-stage build (Node build -> nginx Alpine serve)
- Routing: `/kitchen` -> kitchen_os, `/chat` -> Cinny, `/api` -> intelligence FastAPI

### 6. Family knowledge graph
Structured relationships between family members, preferences, and facts. "What flowers does Mom like?" becomes a graph query, not a keyword search.
- **Effort:** 2 sessions
- **Dependencies:** Memory store schema extension
- **Files:** `services/intelligence/src/memory.py` (schema), `brain.py` (graph-aware prompts)

---

## Phase 3: Kickstarter Prep (April 2026)

**Only start if Phase 2 delivers 3+ features and family is using them daily.**

- [ ] 60-second demo video showing real family use
- [ ] Landing page refresh (memu.digital)
- [ ] Press outreach (1-2 tech publications)
- [ ] 500+ email signups target
- [ ] Open letter + Solid Forum post
- [ ] Kickstarter page draft (reward tiers, stretch goals)

---

## Phase 4: Production (Post-Kickstarter)

- [ ] Pre-configured hardware bundles (Intel N100 + 1TB NVMe)
- [ ] USB installer (boot, install Linux, install Memu automatically)
- [ ] One-click updates via admin dashboard
- [ ] Security audit
- [ ] Backup/restore automation

---

## Kill List

### Never building:
- Video calls — too resource-intensive for target hardware
- Email hosting — deliverability nightmare, not worth the complexity
- Public federation — isolation is a feature for family privacy
- VPN server — Tailscale handles this better than we ever could

### Deferred indefinitely:
- WhatsApp bridge — fragile, Meta breaks it regularly, maintenance burden too high
- Vector embeddings — keyword search works fine at family scale (~1000 facts)
- Voice commands (Whisper) — too much hardware complexity for current stage
- Custom mobile app — Element/FluffyChat/Immich work well enough
- Multi-device clustering — breaks the single-box ownership model

---

## Security Checklist

Before marking any feature complete:

1. **Network Isolation:** New services do NOT have `ports:` in docker-compose.yml. Only accessible via nginx proxy.
2. **Persistence:** Restarting the stack does not wipe data (calendar events, settings, photos).
3. **Permissions:** Intelligence container has read-only access to Immich DB, read-write to its own memory store.
4. **API Safety:** New endpoints verify requests come from internal network or use shared secret token.

---

## Decision Framework

After each phase:
1. **Is the family actually using it?** If not, don't build more.
2. **Would I explain this to a non-technical spouse?** If not, simplify.
3. **Does this move toward Kickstarter?** If not, deprioritize.

---

## Success Metrics

| Milestone | Target | Status |
|-----------|--------|--------|
| Reddit validation | 10+ "I'd try this" | Done |
| Family daily use | 3+ members active | Done |
| Email signups | 500+ | In progress |
| Demo video shared | People forward it | Not started |
| Kickstarter launch | April 2026 | Planned |

---

*This roadmap reflects reality, not aspiration. We build what's validated, not what sounds cool.*
