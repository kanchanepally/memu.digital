# Memu Home: Own Your Family's Digital Life

> **Status:** Alpha. My family uses it daily (since Oct '25). Ready for adventurous testers.

**Memu (మేము)** = "we" in Telugu. Your family's data belongs to *you*, not *them*.

---

## What Is This?

Every app wants to be "AI-powered" — and as a technology portfolio director, I see that they all need your data to work.

Your family's data is incredibly valuable **context**. Your photos know who you are and where you've been. Your chats know your inside jokes and plans. Your calendar knows your schedule. But that context is scattered across Google, Apple, Meta, and Amazon. Each has a slice. None let you use it in a unified way. And you can't take it with you.

**Memu Home** (this repository) orchestrates your family's digital life onto hardware you own, replacing big tech silos with self-hosted sovereign infrastructure:

| Service | What It Replaces | The Difference |
|---------|------------------|----------------|
| **Chat** (Matrix) | WhatsApp, iMessage | You own the server |
| **Photos** (Immich) | Google Photos, iCloud | You own the storage |
| **Calendar** (Baikal)| Google Calendar | You own the schedule |
| **AI Base** (Ollama) | ChatGPT, Siri | It never leaves your house |

**Memu Home** is the "box". It runs the foundational infrastructure. It is designed to be paired seamlessly with **Memu** (the `memu-core` app repository), which acts as the intelligent Chief of Staff engine that reads from these services and presents a unified Mobile App experience.

---

## Hardware Recommendations

### Recommended: Intel N100 Mini PC

| Component | Spec | Why |
|-----------|------|-----|
| CPU | Intel N100 | QuickSync for 4K video transcoding |
| RAM | **16GB** | Synapse + Immich ML need it |
| Storage | 1TB+ NVMe | 2TB if you have large photo libraries |
| Network | Gigabit Ethernet | WiFi works, wired is more reliable |

**Cost:** ~$250-300 total

### Alternative: Raspberry Pi 5

Still works for:
- Families who mostly take photos (not much 4K video)
- Tighter budgets
- Minimum specs: 8GB RAM

---

## Installation

**Total time:** 10-15 minutes

### Prerequisites

You'll need a **Tailscale account** (free) for your family to connect from anywhere. Create one at [tailscale.com](https://tailscale.com). You don't need to install anything on the Memu device yourself; the installer handles that.

### Step 1: Run the Installer

```bash
git clone https://github.com/kanchanepally/memu.digital
cd memu.digital
sudo ./scripts/install.sh
```

This installs Docker, Tailscale (on the host OS so remote access survives Docker restarts), a nightly backup timer, and a container watchdog. All idempotent — safe to re-run.

### Step 2: Open the Web Wizard

1. Visit `http://<device-ip>:8888` in your browser (same network as the device)
2. Fill in:
   - **Family name** (e.g., "smiths")
   - **Admin password** — write it down!
   - **Tailscale auth key**
3. Click **"Create My Family Server"**
4. Wait 3-5 minutes

### Step 3: Install the Apps

The setup wizard shows your server URLs when complete. You'll enter them once, then forget them.

**Every family member needs:**
1. **Tailscale** ([iOS](https://apps.apple.com/app/tailscale/id1470499037) / [Android](https://play.google.com/store/apps/details?id=com.tailscale.ipn)) 
2. **Any Matrix chat app** (Element, FluffyChat)
3. **Immich** (for photos)

To gain ambient intelligence on top of this data, deploy **Memu Core** (the `memu-core` repository) alongside this stack. It will seamlessly interact with your local AI, Chat, and Calendar to power the Memu mobile app experience.

---

## Technical & Product Vision

For complete details on the overarching vision, architecture documentation, design systems, and roadmaps spanning the entire Memu platform (Memu Home + Memu Mobile App), please visit the `memu-platform` repository.

- [Memu UX Design System](https://github.com/kanchanepally/memu-platform/blob/main/03-UX-DESIGN-SYSTEM.md)
- [Platform Roadmap](https://github.com/kanchanepally/memu-platform/blob/main/04-ROADMAP.md)

## Contributing

**What I need help with:**
1. **Testing** — Does this work on your hardware?
2. **Security** — Audit for privacy leaks.
3. **Docs** — Make installation clearer.

## License

**AGPLv3** — Run it for your family freely. Modify and host for others? Share your code.

---

**Questions?** [Open an issue](https://github.com/kanchanepally/memu.digital/issues)

**Updates?** ⭐ Star the repo