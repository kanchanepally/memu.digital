# Memu - Product Bible

**Your Family's Chief of Staff.**
*Own your conversations. Own your photos. Own your intelligence.*

---

## 1. The Vision

### The Problem

Your family's digital life is scattered:
- **Google Photos** knows your faces and locations
- **WhatsApp** knows your conversations
- **Google Calendar** knows your schedule
- **Amazon** knows what you buy

Each company has a slice of your family's context. None of them share it with you. None of them let you use it together. And you can't take it with you.

Meanwhile, AI is transforming everything. Every app wants to be "AI-powered" — using *your* data to be useful. But that data flows to corporations, not to you.

### The Solution

**Memu is your family's Chief of Staff.**

It consolidates your family's digital life — conversations, photos, memories, schedule — onto hardware you own. The AI assistant knows your family because it has your *complete* context, not because it's selling your data to advertisers.

| What You Get | How It Works |
|--------------|--------------|
| **Ownership** | Data lives on your hardware. No landlord. |
| **Unified Context** | Chat + Photos + Calendar + Memory in one place |
| **Private Intelligence** | AI that serves you, not surveils you |
| **Proactive Help** | Morning briefings, reminders, event scheduling |
| **Inheritance** | Your kids get files, not account credentials |

### The Identity Pivot

Memu started as a "privacy server" — a box that hides your data. That framing was defensive and fear-based.

The real value is **proactive intelligence**. Memu isn't a bunker. It's a Chief of Staff — an AI appliance that organizes your family's chaos (schedule, shopping, chores, memories) because it has the full picture.

- **Old frame:** "A box that hides your data"
- **New frame:** "An AI that organizes your family's life — on your hardware"

Privacy is the foundation. Intelligence is the product.

### The Name

**Memu (మేము)** = "we" in Telugu.

Your data belongs to "we" — not "they."

---

## 2. The Product

Memu is a **family appliance** — not a server to configure, but a product that works.

### What It Replaces

| Big Tech Service | Memu Equivalent | Key Difference |
|------------------|-----------------|----------------|
| WhatsApp / iMessage | Memu Chat (Matrix) | You own the server |
| Google Photos / iCloud | Memu Photos (Immich) | You own the storage |
| Google Calendar | Memu Calendar (Baikal) | You own the schedule |
| Siri / Alexa / Google Assistant | Memu Assistant (Ollama) | AI never leaves your house |

### The Magic: Unified Context

Unlike Big Tech silos, Memu connects the dots:

> **"What flowers does Mom like?"**

The AI searches your chat history where Mom mentioned tulips, AND your photos tagged with flowers, AND your shopping lists. One query, full family context.

This is impossible with scattered services. It's natural with Memu.

### The Triple-Graph Context Engine

Memu's intelligence comes from connecting three data sources:

1. **Semantic Graph:** Chat history, saved facts, documents (Matrix + Memory Store)
2. **Visual Graph:** Photos, faces, places (Immich ML)
3. **Time Graph:** Family schedule, events, reminders (Baikal CalDAV)

The `memu_intelligence` service (Python) acts as the connector. It queries all three graphs to generate proactive value — morning briefings, natural language recall, event scheduling.

---

## 3. Architecture

### The Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR HARDWARE                           │
│              (Mini PC / Intel N100 / Pi 5)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │   CHAT   │  │  PHOTOS  │  │    AI    │  │ CALENDAR │   │
│   │  Matrix  │  │  Immich  │  │  Ollama  │  │  Baikal  │   │
│   │ (Synapse)│  │          │  │(Llama3.2)│  │ (CalDAV) │   │
│   └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│        └──────────────┼─────────────┼─────────────┘         │
│                       │             │                       │
│              ┌────────▼─────────────▼───────┐               │
│              │     CONTEXT ENGINE           │               │
│              │   memu_intelligence (Python) │               │
│              └────────────┬─────────────────┘               │
│                           │                                 │
│              ┌────────────▼─────────────────┐               │
│              │       PostgreSQL             │               │
│              │       + pgvector             │               │
│              └──────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Tailscale  │
                    │ (Secure VPN)│
                    └─────────────┘
                           │
                    ┌──────▼──────┐
                    │ Your Phone  │
                    │  Anywhere   │
                    └─────────────┘
```

### Hardware Requirements

| Spec | Minimum | Recommended |
|------|---------|-------------|
| **Device** | Raspberry Pi 5 | Intel N100 Mini PC |
| **RAM** | 8GB | 16GB (recommended for AI) |
| **Storage** | 256GB SSD | 1TB+ NVMe |
| **Network** | Ethernet | Gigabit Ethernet |
| **Cost** | ~$100 | ~$200-250 |

**Why N100 over Pi 5?** QuickSync hardware encoding for 4K video transcoding. If your family shoots lots of video, N100 is significantly smoother.

### Software Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **OS** | Debian 12 / Ubuntu 24 | Stable Linux base |
| **Orchestration** | Docker Compose | Container management |
| **Database** | PostgreSQL 15 + pgvector | Unified data + vector search |
| **Cache** | Redis 6.2 | Performance |
| **Chat** | Matrix Synapse | Federated messaging |
| **Chat UI** | Cinny Web + Matrix mobile apps (Element, FluffyChat, SchildiChat) | User interface |
| **Photos** | Immich | Photo backup + ML |
| **Calendar** | Baikal | CalDAV/CardDAV |
| **AI** | Ollama (Llama 3.2) | Local language model |
| **Context** | Custom Python service | The glue that connects everything |
| **Network** | Tailscale | Secure remote access (auto-HTTPS) |

> **Note:** Element Web was replaced by Cinny in Feb 2026 due to Element's WidgetStore crash on self-hosted setups. Cinny is lighter and more reliable. Mobile users can use any Matrix client.

---

## 4. Features

### 4.1 Memu Chat

**User Story:** "I want to message my family without Big Tech reading our conversations."

| Feature | Description |
|---------|-------------|
| Family group chat | Private rooms for your household |
| End-to-end encryption | Optional E2EE (Matrix Olm/Megolm) |
| Cross-device sync | Phone, tablet, desktop |
| Media sharing | Photos, videos, files |
| No ads, no mining | Your server, your rules |

**Web:** Cinny (built-in, branded as Memu Chat)
**Mobile:** Any Matrix app — Element, FluffyChat, or SchildiChat (iOS/Android)

### 4.2 Memu Photos

**User Story:** "I want my camera roll backed up to my own drive, not Google's."

| Feature | Description |
|---------|-------------|
| Auto-backup | Photos sync from phone automatically |
| Face recognition | Local ML identifies family members |
| Search | "Photos of Dad at the beach" |
| Albums | Organize by event, person, date |
| Original quality | No compression, full resolution |
| Memories | "On this day" nostalgia features |

**Apps:** Immich (iOS/Android)

### 4.3 Memu Calendar

**User Story:** "I want a shared family calendar that doesn't live in Google."

| Feature | Description |
|---------|-------------|
| Shared calendars | Family events visible to everyone |
| CalDAV sync | Works with iPhone Calendar, Android DAVx5, Thunderbird |
| Bot integration | Add events via chat: "Soccer practice Tuesday 5pm" |
| Morning briefings | Today's schedule delivered at 7am |

### 4.4 Memu Assistant

**User Story:** "I want an AI that knows my family — without sending our data to OpenAI."

| Command | What It Does |
|---------|--------------|
| `/remember [fact]` | Store family knowledge |
| `/recall [query]` | Cross-silo search: facts, chat, calendar AND photos |
| `/addtolist [items]` | Shared shopping list |
| `/showlist` | Display current list |
| `/done [item]` | Mark complete |
| `/remind [task] [time]` | Natural language reminders |
| `/schedule [event] [time]` | Add event to family calendar |
| `/calendar` | Show today's events (also: `week`, `tomorrow`) |
| `/briefing` | On-demand family briefing |
| `/summarize` | AI summary of recent chat |
| `/ai off/quiet/active` | Control how chatty the bot is (per room) |
| `/private` | See what Memu protects (encryption, local AI, etc.) |
| `/help` | Show all available commands |

**Natural Language:** You can also just talk naturally — "What's happening tomorrow?", "Add milk to the list", "Remind me to call the dentist". The bot understands intent without slash commands. In group chats, mention the bot by name.

**AI Volume Control:** Each room can have its own AI mode. `/ai off` makes the bot respond only to slash commands (silent partner). `/ai quiet` adds @mentions. `/ai active` enables full natural language processing (the default). Slash commands always work regardless of mode.

**Automatic:** Morning briefings are delivered daily at a configurable time with calendar, weather, news headlines (from RSS feeds), shopping list, and photo memories. All briefing settings are managed through the Admin Settings page — no .env editing needed.

### 4.5 Admin Settings

**User Story:** "I want to configure weather, calendar, and briefing settings without editing config files."

The Admin Settings page (`/admin/settings`) provides a web UI for all runtime configuration:

| Section | What It Configures |
|---------|--------------------|
| **Weather** | City, country code, OpenWeatherMap API key |
| **Calendar** | CalDAV username and password for Baikal |
| **Morning Briefing** | Time, enabled/disabled, target room ID |
| **News Feeds** | RSS feed URLs, headlines count per briefing |

Each save automatically restarts the intelligence service to pick up changes. No terminal access needed.

---

## 5. Installation

### The Promise

**10 minutes. No terminal after initial script. No YAML editing.**

### The Flow

```
1. Flash Linux to device (standard Debian/Ubuntu)
         ↓
2. Run: ./scripts/install.sh
         ↓
3. Open browser: http://memu.local
         ↓
4. Fill in 4 fields:
   - Family name
   - Admin password
   - (Optional) Tailscale auth key
         ↓
5. Click "Create My Memu Server"
         ↓
6. Wait 3-5 minutes
         ↓
7. Done. Service URLs shown on completion screen.
   Install a Matrix chat app + Immich on phones.
```

### What Gets Created

- Matrix homeserver with admin account
- Immich server ready for photo backup
- Baikal calendar ready for CalDAV sync
- AI assistant bot in your chat with morning briefings
- Secure remote access via Tailscale (if key provided)
- Admin dashboard for managing family members

---

## 6. Security & Privacy

### Data Sovereignty

| Principle | Implementation |
|-----------|----------------|
| **Your hardware** | Data lives on device you own |
| **Your network** | Tailscale encrypts all traffic |
| **Your keys** | E2EE keys never leave your devices |
| **Zero telemetry** | We don't know who uses Memu |
| **Network isolation** | All services on internal Docker network, only nginx exposed |

### Encryption

| Layer | Technology |
|-------|------------|
| Transit | TLS 1.3 (Tailscale) |
| Messages | Matrix E2EE (Olm/Megolm) |
| Storage | LUKS full-disk (recommended) |

### AI Privacy

- **Local only:** Ollama runs entirely on your hardware
- **No API calls:** Your prompts never leave your house
- **No training:** Your data doesn't improve someone else's model

---

## 7. Business Model

### Software
**Free forever.** AGPLv3 open source.

### Hardware (Future)
| Option | Price | What You Get |
|--------|-------|--------------|
| **DIY** | $0 | Bring your own hardware |
| **Memu Hub** | ~$350 | Pre-configured Mini PC + SSD |

### Services (Future, Optional)
| Service | Price | What You Get |
|---------|-------|--------------|
| **Relay** | ~$10/mo | Easy remote access without Tailscale setup |
| **Support** | TBD | Priority help |

**Philosophy:** Sell toasters, don't rent them.

---

## 8. What Memu Is NOT

| Not This | Why |
|----------|-----|
| A server for nerds | It's an appliance for families |
| A privacy bunker | It's about intelligence, not hiding |
| A Nextcloud clone | Nextcloud is files; Memu is context |
| A startup (yet) | It's a side project heading to Kickstarter |
| Feature-complete | It's alpha software, expect rough edges |

---

## 9. The Ask

If you're reading this, we need your help:

1. **Try it** — Install on your hardware, report what breaks
2. **Challenge it** — Is the value prop clear? What's missing?
3. **Spread it** — Know someone who'd want this? Tell them
4. **Build it** — PRs welcome, especially for testing and docs

---

## 10. Links

- **GitHub:** https://github.com/kanchanepally/memu.digital
- **License:** AGPLv3

---

*Built by a husband/dad who wanted his family to own their digital life.*

*Memu (మేము) = "we" — because your data belongs to you, not them.*
