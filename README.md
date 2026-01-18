# Memu (మేము): Own Your Family's Digital Life

> **Status:** Alpha. My family uses it daily (since Oct '25). Ready for adventurous testers.

**Memu (మేము)** = "we" in Telugu. Your family's data belongs to *you*, not *them*.

---

## What Is This?

Every app wants to be "AI-powered" — and as a technology portfolio director, I see that they all need your data to work.

Here's the thing: your family's data is incredibly valuable **context**. Your photos know who you are and where you've been. Your chats know your inside jokes and plans. Your calendar knows your schedule.

But that context is scattered across Google, Apple, Meta, and Amazon. Each has a slice. None let you use it in a unified way. And you can't take it with you.

**Memu consolidates your family's digital life onto hardware you own:**

| Service | What It Replaces | The Difference |
|---------|------------------|----------------|
| **Chat** (Matrix) | WhatsApp, iMessage | You own the server |
| **Photos** (Immich) | Google Photos, iCloud | You own the storage |
| **AI Assistant** (Ollama) | ChatGPT, Siri | It never leaves your house |

The magic is the **Context Engine** — an AI that knows your family because it has access to your photos *and* your chats *and* your history. All running locally, all in your control.

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
- ✅ 10-minute setup wizard (no YAML editing)
- ✅ Remote access via Tailscale (works from anywhere)
- ✅ Runs on ~$250 hardware

**What's in progress:**
- ⚠️ Cross-silo AI queries ("show me photos from Christmas") — on roadmap
- ⚠️ Voice-based interaction with AI — on roadmap
- ⚠️ Alpha quality — tested on my family, probably has bugs

---

## Hardware

### Recommended: Intel N100 Mini PC

| Component | Spec | Why |
|-----------|------|-----|
| CPU | Intel N100 | QuickSync for 4K video transcoding |
| RAM | **16GB** | Synapse + Immich ML + Ollama need it |
| Storage | 1TB+ NVMe | 2TB if you have large photo libraries |
| Network | Gigabit Ethernet | WiFi works, wired is more reliable |

**Cost:** ~$250-300 total

**Why N100?** I started on Raspberry Pi 5, which works great for chat and basic photos. But when my wife's phone started shooting 4K video, the Pi struggled with transcoding. The N100's QuickSync handles 4K smoothly.

### Alternative: Raspberry Pi 5

Still works for:
- Families who mostly take photos (not much 4K video)
- Lighter AI workloads
- Tighter budgets

**Minimum specs:** 8GB RAM (limited AI), 4GB RAM (no AI features)

---

## Installation

**Total time:** 10-15 minutes

### Prerequisites

You'll need a **Tailscale account** (free) for your family to connect from anywhere.

1. Create account at [tailscale.com](https://tailscale.com)
2. Go to [Settings → Keys](https://login.tailscale.com/admin/settings/keys)
3. Generate an **Auth Key**
4. Copy it (looks like `tskey-auth-...`)

### Step 1: Run the Installer

```bash
git clone https://github.com/kanchanepally/memu.digital
cd memu.digital
sudo ./scripts/install.sh
```

### Step 2: Open the Web Wizard

1. Visit `http://memu.local` in your browser (same network as the device)
2. Fill in:
   - **Family name** (e.g., "smiths") — becomes part of your chat identity
   - **Admin password** — write it down, no reset option
   - **Tailscale auth key** — connects your family's private network
3. Click **"Create My Family Server"**
4. Wait 2-3 minutes

**No YAML editing. No terminal commands after the initial script.**

### Step 3: Connect Your Apps

Once setup completes, install Tailscale on your phone/laptop, then:

| App | Server Address | Notes |
|-----|----------------|-------|
| **Element** (Chat) | `http://memu-hub` | Sign in with `admin` + your password |
| **Immich** (Photos) | `http://memu-hub:2283` | Create a new account (separate from chat) |

The `http://memu-hub` address works from anywhere — home, work, travelling — as long as Tailscale is running.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Hardware                            │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Matrix  │  │  Immich  │  │  Ollama  │  │ Context  │    │
│  │  (Chat)  │  │ (Photos) │  │   (AI)   │  │  Engine  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                   │
│              ┌──────────▼──────────┐                       │
│              │     PostgreSQL      │                       │
│              │   (unified data)    │                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                          │
                   ┌──────▼──────┐
                   │  Tailscale  │  ← Your family's private network
                   └──────┬──────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │  Dad's  │      │  Mom's  │      │  Kid's  │
   │  Phone  │      │  Laptop │      │  Tablet │
   └─────────┘      └─────────┘      └─────────┘
```

**Why Tailscale?** Traditional servers expose ports to the internet — hackers scan for them constantly. Tailscale creates a private network that only your family can access. Your Memu Hub is invisible to the rest of the internet.

---

## The AI Assistant

The bot lives in your family chat:

| Command | What It Does |
|---------|--------------|
| `/remember [fact]` | Store info → `/remember WiFi at grandma's is ABC123` |
| `/recall [query]` | Retrieve info → `/recall grandma WiFi` |
| `/addtolist [items]` | Shared list → `/addtolist milk, eggs, bread` |
| `/showlist` | Display current list |
| `/done [item]` | Mark complete → `/done milk` |
| `/remind [task] [time]` | Natural language → `/remind call mom tomorrow 3pm` |
| `/summarize` | AI summary of today's chat |

**Coming soon:** Cross-silo queries like "What photos do we have from Dad's birthday?" that search both chat mentions and photo metadata.

---

## Quick Reference

```
┌─────────────────────────────────────────┐
│         MEMU QUICK REFERENCE            │
├─────────────────────────────────────────┤
│  Chat Server:     http://memu-hub       │
│  Photos Server:   http://memu-hub:2283  │
│                                         │
│  Chat App:        Element               │
│  Photos App:      Immich                │
│                                         │
│  Not connecting?  Is Tailscale on?      │
└─────────────────────────────────────────┘
```

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

---

## Contributing

**What I need help with:**

1. **Testing** — Does this work on your hardware?
2. **Security** — Audit for privacy leaks (please!)
3. **Docs** — Make installation clearer
4. **Features** — PRs welcome

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
A: Synology is excellent but expensive (~$600+), no chat, and no local AI assistant.

**Q: Do I need a domain name?**
A: No. Your server is `http://memu-hub` via Tailscale. Your chat identity uses `yourfamily.memu.digital` but that's just an identifier, not a website you need to own.

**Q: What if I'm not technical?**
A: If you can follow instructions to plug in hardware and click through a wizard, you can do this. The hard part is already done.

---

## License

**AGPLv3** — Run it for your family freely. Modify and host for others? Share your code.

---

## Acknowledgments

Built on the shoulders of:
- [Matrix](https://matrix.org) — Federated chat
- [Immich](https://immich.app) — Self-hosted photos
- [Ollama](https://ollama.ai) — Local LLMs
- [Tailscale](https://tailscale.com) — Private networking
- Everyone building for data sovereignty

---

**Questions?** [Open an issue](https://github.com/kanchanepally/memu.digital/issues)

**Updates?** ⭐ Star the repo

---

*Built by a dad/husband who wanted his family to own their digital life.*