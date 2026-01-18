# Memu User Guide

Welcome to your family's **Digital Sanctuary**. This guide will help you set up Memu and get your family connected.

---

## What You're Setting Up

Memu gives your family three things, all running on hardware you own:

| Service | What It Does | App to Use |
|---------|--------------|------------|
| **Chat** | Private family messaging | Element |
| **Photos** | Automatic photo backup | Immich |
| **AI Assistant** | Shopping lists, reminders, family memory | Built into Chat |

Everything stays on your device. No company can see your data.

---

## Part 1: Hardware Setup

### What's in the Box
- Memu Hub (Mini PC or Raspberry Pi)
- Power adapter
- Ethernet cable

### Connections

1. **Ethernet** — Connect the Hub to your home router
2. **Power** — Plug in and wait 2-3 minutes for boot

That's it. No monitor or keyboard needed.

> **Why Ethernet?** WiFi works, but wired is faster and more reliable for photo uploads. You can switch to WiFi later if needed.

---

## Part 2: Create Your Tailscale Account

Tailscale is how your family connects to Memu from anywhere — home, work, school, or travelling. It's free for personal use.

### Why Tailscale?

Traditional servers expose ports to the internet, making them targets for hackers. Tailscale creates a **private network** that only your family can access. Your Memu Hub is invisible to the rest of the internet.

### Get Your Auth Key (5 minutes)

1. Go to [tailscale.com](https://tailscale.com) and create a free account
2. Open [Settings → Keys](https://login.tailscale.com/admin/settings/keys)
3. Click **"Generate auth key"**
4. Copy the key (looks like `tskey-auth-kBZxs...`)

Keep this key handy — you'll need it in the next step.

---

## Part 3: Run the Setup Wizard

### Access the Wizard

On a phone or laptop connected to the **same WiFi as your Memu Hub**:

1. Open a browser
2. Go to: **http://memu.local**

> **Can't reach it?** Try `http://memu-hub.local` or check your router's device list for the IP address.

### Fill In Your Details

| Field | What to Enter |
|-------|---------------|
| **Family Name** | Your family identifier (e.g., "smiths", "garcia-family") |
| **Admin Password** | A strong password — write it down, there's no reset |
| **Tailscale Auth Key** | The key you generated above |

Click **"Create My Family Server"** and wait 2-3 minutes.

### What Gets Created

- ✅ Chat server with your admin account
- ✅ Photo backup server
- ✅ AI assistant bot
- ✅ Connection to your family's Tailscale network

---

## Part 4: Connect Your Devices

Once setup completes, you'll see your connection details:

| | |
|---|---|
| **Server Address** | `http://memu-hub` |
| **Your Username** | `@admin:yourfamily.memu.digital` |
| **Password** | The one you just created |

### Install Tailscale on Your Phone/Laptop

Before the apps work, each device needs Tailscale:

1. Download **Tailscale** from your app store
2. Sign in with the same account you created earlier
3. You'll see "Connected" — that's it

Now `http://memu-hub` works from anywhere.

---

### Set Up Chat (Element)

**Download:** Element ([iOS](https://apps.apple.com/app/element-messenger/id1083446067) / [Android](https://play.google.com/store/apps/details?id=im.vector.app) / [Desktop](https://element.io/download))

**Connect:**
1. Open Element
2. Tap **"Sign in"**
3. Tap **"Edit"** next to the server address
4. Enter: `http://memu-hub`
5. Sign in with:
   - Username: `admin`
   - Password: [your password]

**First thing to do:** Create a room called "Family" and you're ready to chat.

---

### Set Up Photos (Immich)

**Download:** Immich ([iOS](https://apps.apple.com/app/immich/id1613945652) / [Android](https://play.google.com/store/apps/details?id=app.alextran.immich))

**Connect:**
1. Open Immich
2. Enter server URL: `http://memu-hub:2283`
3. Tap **"Create account"** (Photos uses separate accounts from Chat)
4. Create your photo account with any email/password

**Enable backup:**
1. Go to Settings → Backup
2. Turn on **"Background Backup"**
3. Your camera roll will start syncing

> **Why separate accounts?** Immich and Matrix are different systems. Your photo account is independent from your chat account. You can use different credentials if you want.

---

### Meet the AI Assistant

The Memu bot lives in your chat. No separate app needed.

**Find the bot:**
1. Open Element
2. Start a new chat
3. Search for: `@memu_bot:yourfamily.memu.digital`
4. Send: "Hello!"

**What it can do:**

| Command | Example |
|---------|---------|
| `/remember [fact]` | `/remember WiFi password is sunshine123` |
| `/recall [query]` | `/recall WiFi password` |
| `/addtolist [items]` | `/addtolist milk, eggs, bread` |
| `/showlist` | Shows your shopping list |
| `/done [item]` | `/done milk` |
| `/remind [task] [time]` | `/remind call mom tomorrow 3pm` |
| `/summarize` | Summarizes today's chat |

---

## Part 5: Add Family Members

### Invite to Tailscale

1. Go to [Tailscale Admin Console](https://login.tailscale.com/admin/machines)
2. Click **"Invite users"**
3. Enter their email address
4. They'll get an invite to join your network

### Help Them Connect

Share these instructions with each family member:

> **Getting Started with Our Family Memu**
>
> 1. Check your email for a Tailscale invite and accept it
> 2. Download the **Tailscale** app and sign in
> 3. Download **Element** for chat → Server: `http://memu-hub`
> 4. Download **Immich** for photos → Server: `http://memu-hub:2283`
>
> Ask [you] for login help!

### Create Their Chat Accounts

You'll need to create Matrix accounts for family members:

```bash
# SSH into your Memu or run locally
docker exec -it memu_synapse register_new_matrix_user \
  -u [username] \
  -p [password] \
  -c /data/homeserver.yaml \
  http://localhost:8008
```

Or use the admin script:
```bash
sudo ./scripts/memu-admin.sh
# Select "1. Create New Chat User"
```

---

## Everyday Use

### At Home
Everything just works. Apps connect automatically.

### Away From Home
Make sure Tailscale is running on your device. Check the Tailscale app shows "Connected".

### Troubleshooting Connection Issues

| Problem | Solution |
|---------|----------|
| "Can't reach server" | Is Tailscale running? Check the app. |
| Element won't connect | Verify server is `http://memu-hub` (not https) |
| Immich won't connect | Use `http://memu-hub:2283` (note the port) |
| Photos not backing up | Check Immich Settings → Backup is enabled |
| Tailscale shows "Offline" | Check your Memu Hub has power and ethernet |

### Checking Server Health

```bash
# See all running services
docker ps

# Check specific service logs
docker logs memu_synapse      # Chat
docker logs memu_photos       # Photos
docker logs memu_tailscale    # Network
docker logs memu_intelligence # AI Bot
```

---

## Understanding Your Setup

### Your Two Identities

| Type | Example | Used For |
|------|---------|----------|
| **Access URL** | `http://memu-hub` | Connecting apps to your server |
| **Matrix Identity** | `@dad:smiths.memu.digital` | Your username in chats |

The Matrix identity (`smiths.memu.digital`) appears in usernames and room addresses. It doesn't need to be a working website — it's just an identifier.

### What Lives Where

| Data | Location | Backed Up? |
|------|----------|------------|
| Chat history | PostgreSQL database | Via backup script |
| Photos | `./photos` folder | Via backup script |
| AI memory | PostgreSQL database | Via backup script |
| Config | `.env`, `./synapse` | Part of project folder |

### Backup Your Data

```bash
# Run the backup script
sudo ./scripts/backup.sh

# Backups saved to ./backups/
```

We recommend copying backups to an external drive weekly.

---

## Optional: WiFi Setup

Prefer WiFi over Ethernet? Here's how to switch.

**You'll need:** A keyboard and monitor connected to the Hub (temporarily)

1. Log in to the Hub (username: `memu-user` or your configured user)
2. Run: `sudo nmtui`
3. Select **"Activate a connection"**
4. Choose your WiFi network and enter the password
5. Once connected, unplug Ethernet

---

## Getting Help

- **GitHub Issues:** [github.com/kanchanepally/memu/issues](https://github.com/kanchanepally/memu/issues)
- **Check Logs:** `docker compose logs` shows what's happening
- **Restart Services:** `docker compose restart` fixes most issues

---

## Quick Reference Card

Print this for your fridge:

```
┌─────────────────────────────────────────┐
│           MEMU QUICK REFERENCE          │
├─────────────────────────────────────────┤
│  Server Address:  http://memu-hub       │
│  Photos Address:  http://memu-hub:2283  │
│                                         │
│  Chat App:        Element               │
│  Photos App:      Immich                │
│                                         │
│  Not connecting?  Is Tailscale running? │
│                                         │
│  Admin:           [your username]       │
│  Password:        [stored safely]       │
└─────────────────────────────────────────┘
```

---

*Welcome to your Digital Sanctuary.*