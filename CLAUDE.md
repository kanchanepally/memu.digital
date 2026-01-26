# CLAUDE.md - Memu Project Instructions for Claude Code

## Project Identity

**Memu (మేము)** = "we" in Telugu. A self-hosted family digital platform providing digital sovereignty - chat, photos, and AI running on hardware families own.

**Mission:** Give families ownership of their digital lives, not rental agreements with Big Tech.

**Stage:** Alpha → Beta transition. Validated by founder's family for 3+ months. Preparing for Kickstarter (April 2025).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HARDWARE LAYER                           │
│              Intel N100 Mini PC (Primary)                   │
│              Raspberry Pi 5 (Alternative)                   │
├─────────────────────────────────────────────────────────────┤
│                    CONTAINER LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Matrix  │  │  Immich  │  │  Ollama  │  │ Memu Bot │    │
│  │ Synapse  │  │  Photos  │  │   LLM    │  │  Python  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                   │
│              ┌──────────▼──────────┐                       │
│              │     PostgreSQL      │                       │
│              │   + pgvector        │                       │
│              └─────────────────────┘                       │
├─────────────────────────────────────────────────────────────┤
│                    NETWORK LAYER                            │
│              Tailscale (VPN) + Nginx (Proxy)               │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Service | Container | Purpose | Port |
|---------|-----------|---------|------|
| Chat Backend | `memu_synapse` | Matrix homeserver | 8008 (internal) |
| Chat UI | `memu_element` | Element Web | 80 via nginx |
| Photos | `memu_photos` | Immich server | 2283 (localhost) |
| AI | `memu_brain` | Ollama LLM | 11434 (internal) |
| Bot | `memu_intelligence` | Python Matrix bot | None (internal) |
| Database | `memu_postgres` | PostgreSQL + pgvector | 5432 (internal) |
| Network | `memu_tailscale` | Secure remote access | VPN tunnel |
| Proxy | `memu_proxy` | Nginx reverse proxy | 80 (exposed) |

---

## Development Principles

### 1. Thin Slice Delivery

Every feature must be:
- **Independent:** Works end-to-end without dependencies on future work
- **Valuable:** Delivers real user benefit
- **Testable:** Can be validated by a non-technical family member
- **Documented:** Includes user-facing explanation

**Bad:** "Add database schema for future calendar feature"
**Good:** "Family can add items to shopping list via bot command and see them on any device"

### 2. Family-First Validation

Before any feature ships:
- [ ] Does it work for a non-technical spouse?
- [ ] Would you explain this to your parents over the phone?
- [ ] Does it fail gracefully with helpful error messages?

### 3. Security by Default

- All backend services on internal Docker network only
- Only port 80 (nginx) exposed externally
- Remote access exclusively via Tailscale (authenticated, encrypted)
- No telemetry, no phone-home, no analytics
- Secrets in `.env`, never in code

### 4. Idempotent Operations

All scripts must be safe to run multiple times:
- Check before creating (databases, users, configs)
- Preserve existing secrets when re-running installers
- Use `--check` flags and conditional logic

---

## Code Standards

### Python (Intelligence Service)

```python
# Use async/await for all I/O
async def remember_fact(self, room_id: str, fact: str):
    """Store a fact in household memory.
    
    Args:
        room_id: Matrix room identifier
        fact: The fact to remember
        
    Returns:
        bool: True if stored successfully
    """
    # Implementation
```

- Type hints required
- Docstrings for public methods
- Logging via `logging` module, not print()
- Error handling with specific exceptions

### Bash (Install Scripts)

```bash
#!/bin/bash
set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }

# Check before creating
if [ ! -f /path/to/file ]; then
    # Create file
fi
```

- Always `set -e`
- Helper functions for logging
- Idempotent operations
- Comments explaining "why", not "what"

### Docker Compose

- Explicit container names (`container_name: memu_*`)
- Health checks on all services
- Depends_on with conditions (`condition: service_healthy`)
- Volume mounts for persistence
- Network isolation (`networks: - memu_net`)

---

## File Structure

```
memu.digital/
├── CLAUDE.md              # THIS FILE - AI instructions
├── docker-compose.yml     # Production stack
├── docker-compose.dev.yml # Development stack (lighter)
├── .env                   # Secrets (never commit)
├── .env.example           # Template for .env
│
├── bootstrap/             # Setup wizard
│   ├── app.py             # Flask application
│   └── templates/         # HTML templates
│
├── services/
│   └── intelligence/      # Memu Bot
│       ├── Dockerfile
│       ├── requirements.txt
│       └── src/
│           ├── main.py    # Entry point
│           ├── bot.py     # Matrix bot logic
│           ├── brain.py   # Ollama integration
│           ├── memory.py  # Database operations
│           └── config.py  # Environment config
│
├── synapse/               # Matrix homeserver config
│   └── homeserver.yaml    # Generated by wizard
│
├── nginx/                 # Reverse proxy
│   └── conf.d/
│       └── default.conf   # Generated by wizard
│
├── scripts/
│   ├── install.sh         # Main installer
│   ├── backup.sh          # Backup script
│   └── memu-admin.sh      # Admin tools
│
├── docs/
│   ├── architecture.md
│   ├── user_guide.md
│   └── migration.md
│
└── marketing/
    └── index.html         # Landing page
```

---

## Current State (January 2025)

### Working ✅
- 2-step installation (script → web wizard)
- Matrix chat with Element
- Immich photo backup
- Ollama local AI
- Bot commands: /remember, /recall, /addtolist, /showlist, /done, /remind, /summarize
- Tailscale remote access with auto-HTTPS
- Systemd service management

### Known Issues ⚠️
- No automated backups (manual script only)
- Element config needs manual hostname after Tailscale
- Bot token retrieval sometimes fails (retry logic exists)
- No USB installer yet

### Roadmap 🗺️
1. **USB Installer** - Boot, install Linux, install Memu automatically
2. **Branding** - Logo, color scheme, consistent UI
3. **User Documentation** - PDF guide, video walkthrough
4. **Kickstarter Prep** - Landing page, reward tiers, demo video

---

## Testing Checklist

Before any PR:

```bash
# 1. Fresh install test
./scripts/install.sh

# 2. Check all containers running
docker ps

# 3. Verify wizard accessible
curl http://localhost:8888

# 4. After wizard completion
docker compose logs synapse | grep -i error
docker compose logs intelligence | grep -i error

# 5. Test bot commands (in Element)
/showlist
/addtolist test item
/done test
```

---

## Common Tasks

### Adding a New Bot Command

1. Add handler in `services/intelligence/src/bot.py`:
```python
async def handle_newcommand(self, room_id: str, sender: str, content: str):
    # Implementation
    await self.send_text(room_id, "Response")
```

2. Register in `process_message()`:
```python
elif content.startswith('/newcommand'):
    await self.handle_newcommand(room_id, sender, content)
```

3. Update user documentation

### Adding a New Service

1. Add to `docker-compose.yml` with:
   - Explicit container_name
   - Health check
   - Network: memu_net
   - No external ports (unless necessary)

2. Update nginx config if web-accessible

3. Update architecture documentation

### Debugging

```bash
# View all logs
docker compose logs -f

# Specific service
docker compose logs -f intelligence

# Enter container
docker exec -it memu_intelligence /bin/bash

# Database access
docker exec -it memu_postgres psql -U memu_user -d immich
```

---

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SERVER_NAME` | Matrix domain | `smiths.memu.digital` |
| `DB_PASSWORD` | PostgreSQL password | (auto-generated) |
| `MATRIX_BOT_TOKEN` | Bot authentication | (auto-generated) |
| `TAILSCALE_AUTH_KEY` | Network access | `tskey-auth-...` |
| `AI_ENABLED` | Toggle AI features | `true` |
| `OLLAMA_MODEL` | LLM model name | `llama3.2` |

---

## Communication Style

When creating user-facing content:

- **Tone:** Warm, empowering, non-technical
- **Frame:** "Your family's data belongs to you"
- **Avoid:** Jargon, fear-mongering, anti-Big-Tech rhetoric
- **Include:** Concrete benefits, clear next steps

**Bad:** "Matrix is a federated protocol using Olm/Megolm encryption"
**Good:** "Your messages are encrypted - only your family can read them"

---

## Founder Context

HAREESH is building Memu as a side project while working full-time as a Portfolio Director. Key constraints:

- **Time:** Limited hours, must prioritize ruthlessly
- **Budget:** Bootstrap, no external funding yet
- **Testing:** Family is primary QA team
- **Goal:** Kickstarter launch April 2025, potential acquisition path

When suggesting work, consider:
- Can this be done in a 2-hour evening session?
- Does this move toward Kickstarter readiness?
- Will this help the next beta tester succeed?

---

## Quick Reference

```
┌─────────────────────────────────────────────────┐
│           MEMU DEVELOPMENT REFERENCE            │
├─────────────────────────────────────────────────┤
│                                                 │
│  START DEV ENVIRONMENT:                         │
│    docker compose -f docker-compose.dev.yml up  │
│                                                 │
│  RUN TESTS:                                     │
│    cd services/intelligence                     │
│    pytest tests/                                │
│                                                 │
│  REBUILD SERVICE:                               │
│    docker compose build intelligence            │
│    docker compose up -d intelligence            │
│                                                 │
│  VIEW LOGS:                                     │
│    docker compose logs -f [service]             │
│                                                 │
│  FRESH INSTALL TEST:                            │
│    ./scripts/uninstall.sh                       │
│    ./scripts/install.sh                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## License

AGPLv3 - All contributions must be open source.

---

*Last updated: January 2025*
*Maintainer: HAREESH (@kanchanepally)*
