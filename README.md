# Memu (మేము): The Family Server I Built Because I Got Paranoid

> **Status:** Alpha. Works on my Pi. Probably has bugs.

I'm a dad/husband who got spooked when Meta announced they'd train AI on WhatsApp photos. 
So I built a home server for my family.

**Memu (మేము)** = "we" in Telugu. Your data belongs to "us", not "they".

---

## What It Does

Replaces the cloud with a box in your living room:

- **Chat** (Matrix): Like WhatsApp, but your server
- **Photos** (Immich): Like Google Photos, but your drive  
- **AI** (Ollama): Like ChatGPT, but stays in your house

My family's been using it for 3 months. It works. Mostly.

---

## Why I Built This

**The trigger:** I got paranoid about where my family's data goes.

Even with E2EE, WhatsApp collects metadata (who you talk to, when, device info). 
Google Photos' ToS allows ML training. iCloud is convenient but you're renting, 
not owning.

I wanted the convenience of the cloud, but with actual ownership. Like buying 
a photo album instead of renting shelf space at someone else's house.

I tried existing solutions:
- Synology: No chat, no AI
- Nextcloud: Just files, complicated setup
- FreedomBox: Too technical, abandoned

So I built *Memu*. It's rough, but it's mine.

---

## Current Reality Check

**What actually works:**
- ✅ Family group chat (Matrix, E2EE if you want)
- ✅ Photo backup from phones (face recognition, search)
- ✅ AI bot for lists/reminders ("what's on the shopping list?")
- ✅ Runs on a Pi 5 in my closet

**What's janky:**
- ⚠️ Remote access uses Cloudflare Tunnel (just found out it violates ToS for video streaming)
- ⚠️ Setup takes 1-2 hours (not "plug and play" yet)
- ⚠️ Using Element/Immich apps directly (haven't white-labeled yet)

**What I'm working on:**
- Network layer redesign (Headscale? Tailscale? Both? [Help me decide](../../issues/1))
- Actual "setup wizard" (web UI, no terminal)
- Pre-configured hardware you can just buy

---

## Installation
  
  **Total time: 3-5 minutes**
  
  ### Requirements
  - Raspberry Pi 5 (8GB recommended) OR x86 mini PC
  - 500GB+ SSD (1TB recommended)
  - Ethernet connection
  
  ### Setup
  
  **Step 1: System Installation** (30 seconds)
```bash
  git clone https://github.com/yourusername/memu
  cd memu
  sudo ./scripts/install.sh
```
  
  **Step 2: Configure Your Family** (2-3 minutes)
  1. Visit `http://[your-pi-hostname].local` in browser
  2. Fill in 4 fields:
     - Family name (e.g., "smiths")
     - Admin password
     - Cloudflare token (optional - will be replaced soon)
  3. Click "Create My Memu Server"
  4. Wait 2-3 minutes
  5. Done!
  
  ### What Gets Installed
  - Chat server (Matrix/Synapse)
  - Photo backup (Immich)
  - AI assistant (Ollama)
  - All dependencies and configs
  
---

## The "Vibecoding" Disclosure

**Full transparency:** I used Claude (AI) to help write code and docs.

Before you judge:
- I'm a portfolio director, not a full-time developer
- The architecture is mine (I designed it, I debugged it)
- It actually works (my family uses it every day)
- I can answer any technical question about how it works

**Why I'm telling you:** Reddit hates "LLM slop." Fair. But I'd rather be 
honest than pretend I hand-coded 10,000 lines of Python at 2am.

If you think AI-assisted development disqualifies this project, that's okay. 
This might not be for you.

If you think "working product > purity of method," read on.

---

## The Tech Stack

**Simple version:** Docker + Matrix + Immich + Ollama

**Detailed:**
- Orchestration: Docker Compose
- Database: PostgreSQL 15 (one DB for everything)
- Chat: Synapse (Matrix homeserver)
- Photos: Immich (Google Photos clone)
- AI: Ollama (Llama 3.2 3B, ~2GB model)
- Network: Cloudflare Tunnel (for now, but changing this - see Issue #1)

All open source. No proprietary parts.

---

## The Vision (If This Works)

**Phase 1** (now): DIY for technical people  
**Phase 2** (Q2 2025): Pre-configured boxes (~$400-500)  
**Phase 3** (Q4 2025): My mom can use it

**Business model:**
- Software: Free forever (AGPLv3)
- Hardware: Buy once, no subscriptions
- Optional relay: $5/mo (if you want remote access, funds development)

I want to sell toasters, not rent them.

---

## Contributing

**What I need help with:**

1. **Network architecture** - Should I use Headscale? Tailscale? Both? [Issue #1](../../issues/1)
2. **Testing** - Does this work on Pi 4? On Ubuntu laptops? On your weird NUC?
3. **Docs** - Make the install guide less terrible
4. **Security** - Audit for privacy leaks (seriously, please)

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License & Philosophy

**AGPLv3** (strongest copyleft)

Translation:
- Run it for your family? No obligations.
- Modify and host it for others? Must share your code.
- Prevents big companies from stealing this and closing it.

**Zero telemetry.** I literally don't know who uses this. By design.

---

## FAQ

**Q: Why should I trust you?**  
A: You shouldn't. That's why the code is open source. Audit it.

**Q: This looks complicated.**  
A: It is. For now. I'm working on making it simpler. Help me?

**Q: What if it breaks?**  
A: Open an issue. I'll help you fix it. Or you fix it and send a PR.

**Q: Is this secure?**  
A: I think so? But I'm not a security expert. If you are, please review it.

---

## Inspiration

Standing on the shoulders of:
- Tim Berners-Lee (Solid project - data sovereignty)
- The Matrix team (federated chat)
- The Immich team (self-hosted photos)
- Everyone who thinks families deserve to own their data

---

**⭐ Star if you want updates. Or don't. Your choice.**

Questions? [Open an issue](../../issues).

---

*Built by a paranoid dad for other paranoid parents.*
