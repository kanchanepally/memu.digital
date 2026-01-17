# Memu (మేము): Own Your Family's Digital Life

> **Status:** Alpha. My family uses it daily (been since Oct/25). Ready for adventurous testers.

**Memu (మేము)** = "we" in Telugu. Your family's data belongs to *you*, not *them*.

---

## What Is This?

Every app wants to be "AI-powered" — and as a technology portfolio director, i see that they all need your data to work.

Here's the thing: your family's data is incredibly valuable **context**. Your photos know who you are and where you've been. Your chats know your inside jokes and plans. Your calendar knows your schedule. 

But that context is scattered across Google, Apple, Meta, and Amazon. Each has a slice. None let you use it in a unified way. And you can't take it with you.

**Memu consolidates your family's digital life onto hardware you own:**

- **Chat** (Matrix): Like WhatsApp, but on your server
- **Photos** (Immich): Like Google Photos, but on your drive  
- **AI Assistant** (Ollama): Like ChatGPT, but it never leaves your house

The magic is the **Context Engine** — an AI that knows your family because it has access to your photos *and* your chats *and* your history. All running locally  - and in your control.

---

## Why Ownership Matters

When you use Google Photos, Google can:
- Train models on your images
- Change the product whenever they want
- Raise prices or discontinue it
- Decide what features you get

When you own the hardware:
- Data never leaves your house
- You control what AI can access
- No subscription that can disappear
- Your kids inherit actual files, not account credentials

I'm not anti-cloud. I use cloud services for lots of things. But my family's photos and conversations? I want to **own** those, not rent them.

---

## Current Status

**What works:**
- ✅ Family group chat (E2E encrypted)
- ✅ Photo backup from phones (face recognition, search, albums)
- ✅ AI bot for lists, reminders, and family memory
- ✅ 2-step setup wizard (no YAML editing)
- ✅ Runs on ~$200 hardware

**What's in progress:**
- ⚠️ Remote access via Tailscale (optional, local network works without it)
- ⚠️ Cross-silo AI queries ("show me photos from Christmas") — on roadmap
- ⚠️ Alpha quality — tested on my family, probably has bugs
- ⚠️ Voice-based interaction with AI — on roadmap

---

## Hardware

### Recommended: Intel N100 Mini PC

| Component | Spec | Why |
|-----------|------|-----|
| CPU | Intel N100 | QuickSync for 4K video transcoding |
| RAM | **16GB (mandatory)** | Synapse + Immich ML + Ollama and associated context engineering layer need it |
| Storage | 1TB+ NVMe | 2TB if you have large photo libraries like ours! |
| Network | Gigabit Ethernet | Wi-Fi works, wired is more reliable |

**Cost:** ~$250-300 total

**Why N100?** I started on Raspberry Pi 5, which works great for chat and basic photos. But when my wife's better phone started shooting 4K video, the Pi struggled with transcoding and ran hot. The N100's QuickSync handles 4K smoothly at lower power.

### Alternative: Raspberry Pi 5

Still works for:
- Families who mostly take photos (not much 4K video)
- Lighter AI workloads
- Tighter budgets

**Minimum specs:** 8GB RAM (limited AI), 4GB RAM (no AI features)

---

## Installation

**Total time:** 10-15 minutes

### Step 1: Run the installer

```bash
git clone https://github.com/kanchanepally/memu.digital
cd memu.digital
sudo ./scripts/install.sh
```

### Step 2: Open the web wizard

1. Visit `http://[your-hostname].local` in your browser
2. Fill in 4 fields:
   - Family name (e.g., "smiths")
   - Admin password
   - Cloudflare token (optional — being replaced soon)
3. Click "Create My Memu Server"
4. Wait 2-3 minutes
5. Done!

**No YAML editing. No terminal after the initial script.**

### What Gets Installed
- Chat server (Matrix/Synapse)
- Photo backup (Immich)  
- AI assistant (Ollama with Llama 3.2)
- PostgreSQL database
- All dependencies and configs

---

## The Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Hardware                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Matrix  │  │  Immich  │  │  Ollama  │  │ Context  │    │
│  │  (Chat)  │  │ (Photos) │  │  (LLM)   │  │  Engine  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                   │
│              ┌──────────▼──────────┐                       │
│              │     PostgreSQL      │                       │
│              │  (shared + pgvector)│                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

- **Orchestration:** Docker Compose
- **Database:** PostgreSQL 15 with pgvector
- **Chat:** Matrix Synapse + Element
- **Photos:** Immich
- **AI:** Ollama (Llama 3.2 3B)
- **License:** AGPLv3 (open source, prevents cloud cloning)

---

## The AI Assistant

The bot lives in your family chat and handles:

| Command | What it does |
|---------|--------------|
| `/remember [fact]` | Stores info → "WiFi at grandma's is ABC123" |
| `/recall [query]` | Retrieves info → "What's grandma's WiFi?" |
| `/addtolist [items]` | Shared shopping list → "Add milk, eggs" |
| `/showlist` | Display current list |
| `/done [item]` | Mark item complete |
| `/remind [task] [time]` | Natural language → "Call mom tomorrow" |
| `/summarize` | AI summary of today's chat |

**Coming soon:** Cross-silo queries like "What photos do we have from Dad's birthday?" that search both chat mentions and photo metadata.

---

## Roadmap

| Phase | Timeline | Goal |
|-------|----------|------|
| **Alpha** (now) | Q1 2025 | DIY for technical families |
| **Beta** | Q2 2025 | Pre-configured hardware (~$350) |
| **v1.0** | Q4 2025 | Simple enough for my mom |

**Business model:**
- Software: Free forever (AGPLv3)
- Hardware: Buy once, own forever
- Optional relay service: ~$10/mo for easy remote access

---

## Contributing

**What I need help with:**

1. **Network architecture** — Headscale vs Tailscale? [Join the discussion](https://github.com/kanchanepally/memu.digital/issues)
2. **Testing** — Does this work on your hardware?
3. **Security** — Audit for privacy leaks (please!)
4. **Docs** — Make installation clearer

---

## The "AI-Assisted Development" Disclosure

**Full transparency:** I used Claude to help write code and documentation.

- I'm a technology portfolio director, not a full-time developer
- The architecture and decisions are mine
- It works — my family uses it daily
- I can explain any part of how it works

If AI-assisted development bothers you, this might not be your project. If "working product > purity of method," welcome aboard.

---

## FAQ

**Q: Why should I trust you?**  
A: You shouldn't trust me. Trust the code — it's open source. Audit it.

**Q: Is this really private?**  
A: Data never leaves your hardware. Zero telemetry. I literally don't know who uses this.

**Q: What if it breaks?**  
A: Open an issue. I'll help, or you fix it and send a PR.

**Q: Why not just use Nextcloud?**  
A: Nextcloud is great for files but doesn't have native chat or local AI integration.

**Q: Why not just use Synology?**  
A: Synology is excellent but expensive, no chat, and no local AI assistant.

---

## License

**AGPLv3** — Run it for your family freely. Modify and host for others? Share your code.

---

## Acknowledgments

Built on the shoulders of:
- [Matrix](https://matrix.org) — Federated chat
- [Immich](https://immich.app) — Self-hosted photos
- [Ollama](https://ollama.ai) — Local LLMs
- Everyone building for data sovereignty

---

**Questions?** [Open an issue](https://github.com/kanchanepally/memu.digital/issues)

**Updates?** ⭐ Star the repo

---

*Built by a dad who wanted his family to own their digital life.*
