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

Ordered by priority. Items 1-4 are **critical path to Kickstarter** -- nothing else ships until these are done.

### 1. Natural language intent ✅ DONE
Kill the slash command requirement. Users talk naturally ("What's happening tomorrow?", "Add milk to the list") and the bot classifies intent via `analyze_intent()` in brain.py (structured JSON), dispatches to existing handlers. DMs process all messages; group rooms require @mention or slash command.

### 2. On This Day photo memories
Surface Immich "on this day" photos in morning briefings and as a standalone command. Query Immich API for photos from this date in previous years.
- **Effort:** 1 session
- **Dependencies:** Immich API key in config
- **Files:** `services/intelligence/src/agents/briefing.py`, new photo memory tool

### 3. Cross-silo recall ⭐ KEY DIFFERENTIATOR ✅ DONE
`/recall` (or natural language) now searches 4 silos in parallel: saved facts, chat history, calendar events, and Immich photo metadata. When 2+ silos return results, the LLM synthesises a unified "Chief of Staff" response connecting the dots. Single-silo queries still display fast formatted results without synthesis overhead.
- **Implementation:** `calendar_tool.py` (search_events), `bot.py` (_cross_silo_search, _search_calendar, _search_photos, _format_cross_silo_context), `brain.py` (synthesise_cross_silo)
- **Why this matters:** This is the feature that makes the demo video. No other product connects family chat + photos + calendar + AI into a single query. This is the purchase decision.

### 4. Memu Guardian ⭐ SELF-MAINTAINING APPLIANCE
A watchdog service that makes Memu self-maintaining. The principle: **after install.sh, the user never opens a terminal again.**

- **Effort:** 4 sessions (core + notifications + dashboard)
- **Dependencies:** Docker socket access, existing health check endpoints
- **Files:** New `services/guardian/` service, updates to `bootstrap/templates/admin-dashboard.html`
- **Why this is #4:** Without Guardian, every hardware buyer becomes a support ticket at month 3. With Guardian, Memu is a product, not a project.

**What Guardian does automatically (no human needed):**

| Problem | Detection | Auto-Fix |
|---------|-----------|----------|
| Container crashes | Health check fails 3x | `docker restart`, notify family room only if restart fails |
| Disk at 80% | `df` check every 5 min | Prune old Docker images + rotate logs, notify with storage report |
| Disk at 95% | `df` check | Pause Immich uploads, emergency prune, alert family room |
| Cert expiring (<14 days) | Check cert file dates | Run `renew-certs.sh` automatically |
| Tailscale disconnected | `tailscale status` | `tailscale up`, notify if reconnection fails |
| Ollama model missing | Health check | `ollama pull` silently |
| High memory pressure | `free -m` check | Restart largest non-essential container |

**How Guardian communicates:**
- Posts plain-language messages to the family chat room ("Photos service restarted. Everything is working now.")
- Never shows container IDs, exit codes, or Docker jargon
- Weekly "all systems healthy" message so silence doesn't mean "broken and nobody noticed"

**Dashboard upgrade -- traffic light model:**
- One big green/amber/red circle: "Everything is running perfectly. 47 days uptime. 23% storage used."
- Amber: "Storage is filling up (82%). Cleaned up 3GB automatically."
- Red: "Photos service is down. [Restart Photos] [Contact Support]"
- No terminal needed. Single action buttons for any problem.

### 5. Proactive family suggestions
The AI notices patterns and surfaces them before you ask:
- "Sarah's birthday is in 3 weeks. Last year you started planning 2 days before."
- "The boiler service is overdue. Last mentioned done in March 2025."
- "You have a parents' evening tomorrow. Last time you wanted to ask about maths."
- **Effort:** 2 sessions
- **Dependencies:** Cross-silo recall (item 3), scheduler
- **Files:** New `services/intelligence/src/agents/insights.py`, scheduler in `main.py`

### 6. Weekly family digest
Sunday evening summary: week's calendar highlights, shopping list activity, chat summary, upcoming week preview. Delivered to family room.
- **Effort:** 1 session
- **Dependencies:** Briefing agent pattern (already built)
- **Files:** New `services/intelligence/src/agents/digest.py`, scheduler in `main.py`

### Deferred to post-Kickstarter:
- **Kitchen Dashboard** — Nice but not a purchase driver. 5-6 sessions. Build after shipping to backers.
- **Family knowledge graph** — Enhances cross-silo recall but keyword search works at family scale. 2 sessions. Build when cross-silo recall proves the concept.

---

## Phase 3: Kickstarter Prep (April 2026)

**Gate:** Phase 2 items 1-4 must be done and family must be using them daily.

- [ ] 60-second demo video showing real family use (cross-silo recall is the hero moment, Guardian health is a beat)
- [ ] Landing page refresh (memu.digital) with video, email signup, Kickstarter countdown
- [ ] 500+ email signups target
- [ ] Press outreach (1-2 tech publications)
- [ ] Open letter + Solid Forum post
- [ ] Kickstarter page draft (reward tiers, stretch goals)
- [ ] Identify 2 wholesale N100 mini PC suppliers, get sample units, test image flashing

---

## Phase 4: Production (Post-Kickstarter, Pre-Ship)

Ship these before hardware reaches backers:

- [ ] Guardian auto-updates: stable channel pulls tested images at 3am, verifies health, rolls back if broken. "Memu updated overnight." (2 sessions)
- [ ] Guardian bot commands: "Is everything working?", "How much storage?", "Update Memu", "Restart photos" (1 session)
- [ ] Pre-configured hardware bundles (Intel N100 + 1TB NVMe, white-label from wholesale supplier)
- [ ] USB installer image (boot, install Linux, install Memu automatically)
- [ ] Backup/restore automation via admin dashboard
- [ ] Security audit
- [ ] Kitchen Dashboard (5-6 sessions)
- [ ] Family knowledge graph (2 sessions)

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
