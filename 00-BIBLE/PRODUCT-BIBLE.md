# Memu - Product Bible 

**Your Family's Context Layer.**  
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

**Memu is your family's context layer.**

It consolidates your family's digital life — conversations, photos, memories — onto hardware you own. The AI assistant knows your family because it has your *complete* context, not because it's selling your data to advertisers.

| What You Get | How It Works |
|--------------|--------------|
| **Ownership** | Data lives on your hardware. No landlord. |
| **Unified Context** | Chat + Photos + Memory in one place |
| **Private Intelligence** | AI that serves you, not surveils you |
| **Inheritance** | Your kids get files, not account credentials |

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
| Siri / Alexa / Google Assistant | Memu Assistant (Ollama) | AI never leaves your house |

### The Magic: Unified Context

Unlike Big Tech silos, Memu connects the dots:

> **"What flowers does Mom like?"**

The AI searches your chat history where Mom mentioned tulips, AND your photos tagged with flowers, AND your shopping lists. One query, full family context.

This is impossible with scattered services. It's natural with Memu.

---

## 3. Architecture

### The Three Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     YOUR HARDWARE                           │
│              (Mini PC / Intel N100 / Pi 5)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │    CHAT     │  │   PHOTOS    │  │     AI      │        │
│   │   Matrix    │  │   Immich    │  │   Ollama    │        │
│   │  (Synapse)  │  │             │  │ (Llama 3.2) │        │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│          │                │                │                │
│          └────────────────┼────────────────┘                │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │  CONTEXT ENGINE │                        │
│                  │   (The Magic)   │                        │
│                  └────────┬────────┘                        │
│                           │                                 │
│                  ┌────────▼────────┐                        │
│                  │   PostgreSQL    │                        │
│                  │   + pgvector    │                        │
│                  └─────────────────┘                        │
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
| **RAM** | 4GB (limited AI) | 8GB+ (full features) |
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
| **Chat UI** | Element Web/Mobile | User interface |
| **Photos** | Immich | Photo backup + ML |
| **AI** | Ollama (Llama 3.2) | Local language model |
| **Context** | Custom Python service | The glue that connects everything |
| **Network** | Tailscale | Secure remote access |

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

**Apps:** Element X (iOS/Android), Element Web

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

### 4.3 Memu Assistant

**User Story:** "I want an AI that knows my family — without sending our data to OpenAI."

| Command | What It Does |
|---------|--------------|
| `/remember [fact]` | Store family knowledge |
| `/recall [query]` | Retrieve from memory |
| `/addtolist [items]` | Shared shopping list |
| `/showlist` | Display current list |
| `/done [item]` | Mark complete |
| `/remind [task] [time]` | Natural language reminders |
| `/summarize` | AI summary of today's chat |

**Future (Roadmap):**
- Cross-silo queries: "Show photos from when we discussed Dad's birthday"
- Voice commands via Whisper
- Proactive suggestions: "Mom mentioned tulips last week — her birthday is coming up"

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
6. Wait 2-3 minutes
         ↓
7. Done. Install Element + Immich apps on phones.
```

### What Gets Created

- Matrix homeserver with admin account
- Immich server ready for photo backup
- AI assistant bot in your chat
- Secure remote access via Tailscale

---

## 6. Security & Privacy

### Data Sovereignty

| Principle | Implementation |
|-----------|----------------|
| **Your hardware** | Data lives on device you own |
| **Your network** | Tailscale encrypts all traffic |
| **Your keys** | E2EE keys never leave your devices |
| **Zero telemetry** | We don't know who uses Memu |

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

## 7. Roadmap

### Phase 1: Foundation ✅ Complete
- [x] Matrix chat (Synapse + Element)
- [x] Photo backup (Immich)
- [x] Local AI (Ollama)
- [x] Web setup wizard
- [x] Basic bot commands

### Phase 2: Validation 🚧 Current
- [x] Open source release
- [x] Documentation
- [ ] Community feedback (Reddit)
- [ ] Hardware compatibility testing
- [ ] Tailscale integration (replacing Cloudflare)

### Phase 3: Polish (Post-Validation)
- [ ] RAM auto-detection and model selection
- [ ] Improved error messages
- [ ] Backup/restore automation
- [ ] System health dashboard

### Phase 4: Context Intelligence (Future)
- [ ] Cross-silo queries (chat + photos)
- [ ] Semantic search across all data
- [ ] Voice commands (Whisper)
- [ ] Proactive family assistant

### Phase 5: Appliance (If Validated)
- [ ] Pre-configured hardware bundles
- [ ] One-click updates
- [ ] Family member onboarding flow
- [ ] Mobile app (unified Memu app)

---

## 8. Business Model

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

## 9. Success Metrics

### For Validation (Now)
- [ ] 50+ engaged comments on Reddit
- [ ] 10+ "I would use this" responses
- [ ] Clear feedback on what's missing
- [ ] No critical security issues found

### For Product (Future)
| Metric | Target |
|--------|--------|
| Setup success rate | >90% |
| Chat latency | <200ms |
| AI response time | <5s |
| Photo sync reliability | >99% |
| Family adoption | 3+ members active |

---

## 10. What Memu Is NOT

| Not This | Why |
|----------|-----|
| A server for nerds | It's an appliance for families |
| A privacy bunker | It's about ownership, not hiding |
| A Nextcloud clone | Nextcloud is files; Memu is context |
| A startup (yet) | It's a side project seeking validation |
| Feature-complete | It's alpha software, expect rough edges |

---

## 11. The Ask

If you're reading this, we need your help:

1. **Try it** — Install on your hardware, report what breaks
2. **Challenge it** — Is the value prop clear? What's missing?
3. **Spread it** — Know someone who'd want this? Tell them
4. **Build it** — PRs welcome, especially for testing and docs

---

## 12. Links

- **GitHub:** https://github.com/kanchanepally/memu.digital
- **License:** AGPLv3

---

*Built by a dad who wanted his family to own their digital life.*

*Memu (మేము) = "we" — because your data belongs to you, not them.*