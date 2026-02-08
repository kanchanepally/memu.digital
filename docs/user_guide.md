# Memu User Guide

Welcome to your family's **Digital Sanctuary**. This guide will help you set up Memu and get your family connected.

---

## What You're Setting Up

Memu gives your family four things, all running on hardware you own:

| Service | What It Does | App to Download |
|---------|--------------|-----------------|
| **Chat** | Private family messaging | Any Matrix app (Element, FluffyChat) |
| **Photos** | Automatic photo backup | Immich |
| **Calendar** | Shared family schedule | iOS/Android built-in |
| **AI Assistant** | Shopping lists, reminders, briefings | Built into chat |


Everything stays on your device. No company can see your data.

## 🚀 Quick Start (For the Impatient)

1.  **Plug in** your Mini PC/Pi (Ethernet + Power).
2.  **Get a specific key** from [Tailscale](https://login.tailscale.com/admin/settings/keys).
3.  **Run** `sudo ./scripts/install.sh` on the device.
4.  **Visit** `http://<device-ip>:8888` to finish setup.

---

## Part 1: Hardware Setup

### What You Need
- Mini PC (Intel N100 recommended for 4K video) or Raspberry Pi 5
- 1TB+ SSD storage
- Power adapter
- Ethernet cable

### Connections

1. **Ethernet** — Connect to your home router
2. **Power** — Plug in and wait 2-3 minutes for boot

That's it. No monitor or keyboard needed.

> **Why Ethernet?** WiFi works, but wired is faster and more reliable for photo uploads.

---

## Part 2: Create Your Tailscale Account

Tailscale creates a **private network** for your family. Your Memu Hub is invisible to the internet — only family members with Tailscale can access it.

### Get Your Auth Key (5 minutes)

1. Go to [tailscale.com](https://tailscale.com) and create a free account
2. Open [Settings → Keys](https://login.tailscale.com/admin/settings/keys)
3. Click **"Generate auth key"**
4. Copy the key (looks like `tskey-auth-kBZxs...`)

Keep this key — you'll need it in the next step.

---

## Part 3: Run the Setup Wizard

### Install Memu

On the device that will run Memu:

```bash
git clone https://github.com/kanchanepally/memu.digital
cd memu.digital
sudo ./scripts/install.sh
```

### Access the Wizard

On a phone or laptop connected to the **same network**:

1. Open a browser
2. Go to: `http://<device-ip>:8888`
   *(Tip: Check your router's admin page to find the IP address of the new device)*

### Fill In Your Details

| Field | What to Enter |
|-------|---------------|
| **Family Name** | Your family identifier (e.g., "smiths") |
| **Admin Password** | A strong password — write it down, there's no reset! |
| **Tailscale Auth Key** | The key you generated above |

Click **"Create My Family Server"** and wait 3-5 minutes.

### Setup Complete!

When finished, you'll see your server addresses:

```
Chat:   http://memu-hub  (or https://memu-hub.xxxxx.ts.net)
Photos: http://memu-hub:2283
```

**Save these URLs** — you'll need them once to set up each app, then you can forget them.

---

## Part 4: Install the Apps

This is the important part. Once you set up the apps, you won't need to think about URLs again.

### Step 1: Install Tailscale on Every Device

Each family member's phone/laptop needs Tailscale:

1. Download **Tailscale** ([iOS](https://apps.apple.com/app/tailscale/id1470499037) / [Android](https://play.google.com/store/apps/details?id=com.tailscale.ipn))
2. Sign in with your Tailscale account
3. That's it — now your device can reach Memu from anywhere

---

### Step 2: Set Up Chat

**Web (built-in):** Open `http://memu-hub` in any browser — Memu Chat is ready to use.

**Mobile apps:** Download any Matrix-compatible chat app:
- **iOS:** [Element](https://apps.apple.com/app/element-messenger/id1083446067), [FluffyChat](https://apps.apple.com/app/fluffychat/id1551469600), or [SchildiChat](https://apps.apple.com/app/schildichat/id1634437512)
- **Android:** [Element](https://play.google.com/store/apps/details?id=im.vector.app) or [FluffyChat](https://play.google.com/store/apps/details?id=chat.fluffy.fluffychat)

**One-time setup:**
1. Open your chosen app
2. Tap **"Sign in"**
3. Set the homeserver to: `https://memu-hub.xxxxx.ts.net`
4. Sign in with your username and password

**Done!** The app remembers everything. Just open it to chat.

---

### Step 3: Set Up Photos (Immich)

**Download:** Immich ([iOS](https://apps.apple.com/app/immich/id1613945652) / [Android](https://play.google.com/store/apps/details?id=app.alextran.immich))

**One-time setup:**
1. Open Immich
2. Enter server URL: `http://memu-hub:2283`
3. Tap **"Create account"** 
4. Create your photo account (any email/password)

**Enable automatic backup:**
1. Go to Settings → Backup
2. Turn on **"Background Backup"**

**Done!** Your photos now sync automatically. Open Immich to see your library.

> **Note:** Immich uses separate accounts from chat. Each family member creates their own photo account.

---

### Step 4: Set Up Calendar (CalDAV)

Your family calendar syncs with the built-in calendar on your phone — no extra app needed!

**On iPhone/iPad:**
1. Go to **Settings → Calendar → Accounts → Add Account**
2. Tap **"Other"** → **"Add CalDAV Account"**
3. Enter:
   - Server: `https://memu-hub.xxxxx.ts.net/calendar/dav.php`
   - User Name: `memu` (or your configured username)
   - Password: [your calendar password from .env]
4. Tap **"Next"** and allow access

**On Android:**
1. Install **DAVx⁵** from Play Store (free, open source)
2. Add account → **"Login with URL and username"**
3. Enter:
   - Base URL: `https://memu-hub.xxxxx.ts.net/calendar/dav.php`
   - User name: `memu`
   - Password: [your calendar password]
4. Select your calendar and sync

**Done!** Family events now appear in your phone's calendar app. Add events from your phone or via the bot!

---

## Part 5: Meet the AI Assistant 🤖

This is where the magic happens. The **Memu Bot** lives in your chat and helps your family:
- **Cross-silo search** — ask one question, get answers from chat, calendar, photos AND saved facts
- Manage the family calendar
- Keep a shared shopping list
- Remember important information
- Set reminders
- Deliver morning briefings
- Summarize busy chat days

### Find the Bot

1. Open your Matrix chat app
2. Tap **+** to start a new chat
3. Search for: `@memu_bot:yourfamily.memu.digital`
   *(replace "yourfamily" with your actual family name)*
4. Tap on **memu_bot** to open a direct message

### Try These Commands

| Command | What It Does | Try It! |
|---------|--------------|---------|
| `/schedule` | Add to family calendar | `/schedule Soccer Tuesday 5pm` |
| `/calendar` | See today's schedule | `/calendar` |
| `/calendar week` | See this week | `/calendar week` |
| `/briefing` | Get a family briefing now | `/briefing` |
| `/showlist` | See the shopping list | `/showlist` |
| `/addtolist` | Add items | `/addtolist milk, eggs, bread` |
| `/done` | Mark item bought | `/done milk` |
| `/remember` | Store a fact | `/remember WiFi is sunshine123` |
| `/recall` | Cross-silo search | `/recall sailing` |
| `/remind` | Set a reminder | `/remind call mom tomorrow 3pm` |
| `/summarize` | Summarize today's chat | `/summarize` |

### Cross-Silo Search — The Magic Feature

This is what makes Memu different from any other assistant. When you ask a question with `/recall` (or just ask naturally), the bot searches **everywhere at once**:

- 💾 **Saved facts** (things you told it to remember)
- 💬 **Chat history** (actual conversations)
- 📅 **Calendar events** (past and upcoming)
- 📸 **Photos** (using Immich's smart search)

When results come from multiple sources, the AI **connects the dots** and gives you an insightful answer — not just raw search results.

**Examples:**

> 🧑 "What have we been doing on Saturdays?"
> 🤖 🔍 **Cross-silo search** (💾💬 📅 📸):
> Your Saturdays have been busy! The calendar shows sailing sessions most weeks since September. You have 15 photos from the harbour across those sessions. In chat, you mentioned needing a new life jacket in December — worth checking if that's sorted before next week's session.

> 👩 `/recall dentist`
> 🤖 🔍 **Cross-silo search** (💬 📅):
> The last dentist appointment was September 12th. In chat, the hygienist recommended coming back in six months — that's now overdue. Your calendar shows Thursday afternoon is free.

> 🧑 `/recall WiFi`
> 🤖 💾 **Saved Facts** about 'WiFi':
> • WiFi password is sunshine123 (saved 2025-12-01)

Simple queries that only match one source still work fast, without AI synthesis. The cross-silo intelligence kicks in when there's data across multiple sources to connect.

### How Families Use the Bot

**Shopping:**
> 🧑 `/addtolist milk, bread, cheese`
> 🤖 ✓ Added 3 items to the list
> 👩 `/done milk`
> 🤖 ✓ Marked as done: milk

**Family Memory:**
> 🧑 `/remember Grandma's birthday is March 15`
> 🤖 ✓ Remembered: Grandma's birthday is March 15
> 👩 `/recall grandma birthday`
> 🤖 💾 Grandma's birthday is March 15

**Reminders:**
> 🧑 `/remind pick up kids at 3pm`
> 🤖 ⏰ Reminder set for today 3:00 PM

The bot is available to everyone in the family. Lists and memories are shared!

### Morning Briefings ☀️

Every morning at 7am, the bot sends a briefing to your family chat:

```
🌅 Morning Briefing

Good morning, family! Today is Saturday, March 15th.
You have 3 events on the calendar - the big one is Emma's
soccer practice at 3pm. Weather looks lovely at 18°C.
We found 5 photo memories from this day! Have a great day! 💪
```

The briefing includes:
- Today's calendar events
- Current weather (if configured)
- "On This Day" photo memories
- Shopping list status

**Configure the time:** Set `BRIEFING_TIME=07:00` in your `.env` file.

**Get one now:** Type `/briefing` in any chat with the bot.

---

## Part 6: Add Family Members

### Invite to Tailscale

1. Go to [Tailscale Admin](https://login.tailscale.com/admin/users)
2. Click **"Invite users"**
3. Enter their email
4. They accept the invite and install Tailscale

### Create Their Chat Account

### Add Members via Dashboard

1.  Open your Admin Dashboard: `http://<device-ip>:8888/admin`
    *   *Or click "Admin Dashboard" if you are already logged in.*
2.  Click **"Add Family Member"**
3.  Enter their:
    *   **Name** (e.g., "Dad")
    *   **Username** (e.g., "dad")
4.  Click **"Create"**

You will see a **QR Code** and a **Welcome Link**.

### Share These Instructions

### Share These Instructions

Copy and paste this message to your family group chat:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   JOIN OUR FAMILY MEMU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Accept the Tailscale email invite

2. Install these apps:
   • Tailscale (required)
   • A Matrix chat app (Element or FluffyChat)
   • Immich (for photos)

3. For chat:
   → Web: http://memu-hub
   → Mobile: set homeserver to https://memu-hub.xxxxx.ts.net
   → Ask me for your username & password

4. In Immich:
   → Server: http://memu-hub:2283
   → Create your own account

5. Find the family bot in your chat app:
   → Search: @memu_bot:ourname.memu.digital
   → Try: /showlist

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Daily Life with Memu

### You Don't Need to Remember URLs

Once the apps are set up:
- **Chat:** Open `http://memu-hub` or your Matrix app
- **Photos:** Just open Immich (auto-syncs in background)
- **Shopping list:** Message the bot in chat

### Works Everywhere

As long as Tailscale is running, your apps connect automatically — home, work, school, travelling, anywhere.

### If Something's Not Connecting

| Check | How |
|-------|-----|
| Is Tailscale running? | Open Tailscale app — should say "Connected" |
| Is the Hub online? | Check it has power and ethernet |
| Still stuck? | Restart the app |

---

## Backup Your Data

Your family's data is precious. Memu automatically backs up everything:
- Photos and videos
- Chat messages and attachments
- AI memories and lists
- All configuration

### Automatic Backups

Memu runs automatic backups every night at 2am. You don't need to do anything!

To check backup status, message the bot in chat:
```
/backup-status
```

The bot will tell you:
- When the last backup ran
- How many backups are stored
- Whether you need to make a USB backup

### USB Backups (Recommended Weekly)

For extra safety, copy your backup to a USB drive weekly:

1. Plug a USB drive into your Memu Hub
2. The bot will automatically copy the latest backup
3. You'll get a message when it's done: "Safe to remove the drive"

Store this USB somewhere safe (different room, or a relative's house).

### Manual Backup

If you want to run a backup manually:
```bash
sudo /opt/memu/scripts/backup.sh
```

### Restore from Backup

If you need to restore (new hardware, disk failure):
```bash
sudo /opt/memu/scripts/restore.sh
```

This will show available backups and guide you through restoration.

---

## Quick Reference

```
┌─────────────────────────────────────────────────┐
│             MEMU QUICK REFERENCE                │
├─────────────────────────────────────────────────┤
│                                                 │
│  APPS TO INSTALL:                               │
│    • Tailscale (required for connection)        │
│    • Matrix chat app (Element/FluffyChat)        │
│    • Immich (photos)                             │
│    • DAVx⁵ (Android calendar sync, optional)    │
│                                                 │
│  AI BOT IN CHAT:                                 │
│    @memu_bot:yourfamily.memu.digital            │
│                                                 │
│  CALENDAR COMMANDS:                             │
│    /schedule      - add event to calendar       │
│    /calendar      - see today's events          │
│    /calendar week - see this week               │
│    /briefing      - get a family briefing       │
│                                                 │
│  LIST & MEMORY COMMANDS:                        │
│    /showlist      - see shopping list           │
│    /addtolist     - add items                   │
│    /done          - mark item complete          │
│    /remember      - store a fact                │
│    /recall        - CROSS-SILO SEARCH (all data)│
│    /remind        - set a reminder              │
│    /summarize     - summarize chat              │
│    /help          - show all commands           │
│                                                 │
│  AUTOMATIC:                                     │
│    ☀️ Morning briefing at 7am daily             │
│                                                 │
│  NOT CONNECTING?                                │
│    → Check Tailscale app is running             │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Getting Help

- **GitHub:** [github.com/kanchanepally/memu.digital/issues](https://github.com/kanchanepally/memu.digital/issues)
- **Logs:** `docker compose logs`
- **Restart:** `docker compose restart`

---

*Welcome to your Digital Sanctuary.*

*Memu (మేము) = "we" in Telugu — your data belongs to you, not them.*