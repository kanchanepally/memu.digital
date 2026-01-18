# Memu User Guide

Welcome to your family's **Digital Sanctuary**. This guide will help you set up Memu and get your family connected.

---

## What You're Setting Up

Memu gives your family three things, all running on hardware you own:

| Service | What It Does | App to Download |
|---------|--------------|-----------------|
| **Chat** | Private family messaging | Element |
| **Photos** | Automatic photo backup | Immich |
| **AI Assistant** | Shopping lists, reminders, family memory | Built into Element |

Everything stays on your device. No company can see your data.

---

## Part 1: Hardware Setup

### What You Need
- Mini PC (Intel N100 recommended) or Raspberry Pi 5
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
Chat:   https://memu-hub.xxxxx.ts.net
Photos: https://memu-hub.xxxxx.ts.net:8443
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

### Step 2: Set Up Chat (Element)

**Download:** Element ([iOS](https://apps.apple.com/app/element-messenger/id1083446067) / [Android](https://play.google.com/store/apps/details?id=im.vector.app))

**One-time setup:**
1. Open Element
2. Tap **"Sign in"**
3. Tap **"Edit"** next to the server
4. Enter your server URL: `https://memu-hub.xxxxx.ts.net`
5. Sign in:
   - Username: `admin`
   - Password: [your password]

**Done!** The app remembers everything. Just open Element to chat.

---

### Step 3: Set Up Photos (Immich)

**Download:** Immich ([iOS](https://apps.apple.com/app/immich/id1613945652) / [Android](https://play.google.com/store/apps/details?id=app.alextran.immich))

**One-time setup:**
1. Open Immich
2. Enter server URL: `https://memu-hub.xxxxx.ts.net:8443`
3. Tap **"Create account"** 
4. Create your photo account (any email/password)

**Enable automatic backup:**
1. Go to Settings → Backup
2. Turn on **"Background Backup"**

**Done!** Your photos now sync automatically. Open Immich to see your library.

> **Note:** Immich uses separate accounts from chat. Each family member creates their own photo account.

---

## Part 5: Meet the AI Assistant 🤖

This is where the magic happens. The **Memu Bot** lives in your chat and helps your family:
- Keep a shared shopping list
- Remember important information
- Set reminders
- Summarize busy chat days

### Find the Bot

1. Open **Element**
2. Tap **+** to start a new chat
3. Search for: `@memu_bot:yourfamily.memu.digital`
   *(replace "yourfamily" with your actual family name)*
4. Tap on **memu_bot** to open a direct message

### Try These Commands

| Command | What It Does | Try It! |
|---------|--------------|---------|
| `/showlist` | See the shopping list | `/showlist` |
| `/addtolist` | Add items | `/addtolist milk, eggs, bread` |
| `/done` | Mark item bought | `/done milk` |
| `/remember` | Store a fact | `/remember WiFi is sunshine123` |
| `/recall` | Find a fact | `/recall WiFi` |
| `/remind` | Set a reminder | `/remind call mom tomorrow 3pm` |
| `/summarize` | Summarize today's chat | `/summarize` |

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
> 🤖 💡 Grandma's birthday is March 15

**Reminders:**
> 🧑 `/remind pick up kids at 3pm`  
> 🤖 ⏰ Reminder set for today 3:00 PM

The bot is available to everyone in the family. Lists and memories are shared!

---

## Part 6: Add Family Members

### Invite to Tailscale

1. Go to [Tailscale Admin](https://login.tailscale.com/admin/users)
2. Click **"Invite users"**
3. Enter their email
4. They accept the invite and install Tailscale

### Create Their Chat Account

```bash
sudo ./scripts/memu-admin.sh
# Select "1. Create New Chat User"
```

### Share These Instructions

Send this to each family member:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   JOIN OUR FAMILY MEMU
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Accept the Tailscale email invite

2. Install these apps:
   • Tailscale (required)
   • Element (for chat)
   • Immich (for photos)

3. In Element:
   → Server: https://memu-hub.xxxxx.ts.net
   → Ask me for your username & password

4. In Immich:
   → Server: https://memu-hub.xxxxx.ts.net:8443
   → Create your own account

5. Find the family bot in Element:
   → Search: @memu_bot:ourname.memu.digital
   → Try: /showlist

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Daily Life with Memu

### You Don't Need to Remember URLs

Once the apps are set up:
- **Chat:** Just open Element
- **Photos:** Just open Immich (auto-syncs in background)
- **Shopping list:** Message the bot in Element

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

```bash
sudo ./scripts/backup.sh
```

Copy backups to an external drive weekly. Your data is precious!

---

## Quick Reference

```
┌─────────────────────────────────────────────────┐
│             MEMU QUICK REFERENCE                │
├─────────────────────────────────────────────────┤
│                                                 │
│  APPS TO INSTALL:                               │
│    • Tailscale (required for connection)        │
│    • Element (chat)                             │
│    • Immich (photos)                            │
│                                                 │
│  AI BOT IN ELEMENT:                             │
│    @memu_bot:yourfamily.memu.digital            │
│                                                 │
│  USEFUL COMMANDS:                               │
│    /showlist     - see shopping list            │
│    /addtolist    - add items                    │
│    /done         - mark item complete           │
│    /remember     - store a fact                 │
│    /recall       - find a fact                  │
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