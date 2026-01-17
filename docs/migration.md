# Migration Guide

**Move Memu between devices (Cloud ↔ Hardware) without losing data.**

---

## 🛑 The Golden Rule: Immutable Identity

**You cannot change your `SERVER_NAME` (Family Name) during migration.**

Matrix chat history is cryptographically tied to the server name (e.g., `smiths.memu.digital`).
- If you start on DigitalOcean as `temp.memu.digital`...
- And try to move to Hardware as `smiths.memu.digital`...
- **You will lose all chat history and user accounts.**

**Recommendation:** Pick your forever name (e.g., `smiths`) on Day 1, even if you are just testing on a cloud server.

---

## What Needs Moving?

There are 3 parts to a Memu installation. You must move all three.

| Part | What is it? | Location |
|---|---|---|
| **1. Files** | Photos, Uploads, Configs | `./photos`, `./synapse`, `.env`, `nginx/` |
| **2. Database** | Chat history, User accounts, Metadata | Docker Volume (`pgdata`) |
| **3. Keys** | Secrets, Tailscale Auth | Inside `.env` and `./synapse` |

---

## Step-by-Step Migration

**Scenario:** Moving from **Source Device** (e.g., DigitalOcean) to **Target Device** (e.g., N100).

### Phase 1: Backup Source
*Run these commands on the OLD machine.*

1. **Stop Services** (leaves Database running for dump)
   ```bash
   cd memu-os
   docker compose stop
   docker compose start database
   ```

2. **Dump Database**
   ```bash
   # Dump the entire postgres database to a file
   docker exec -t memu_postgres pg_dumpall -c -U memu_user > memu_backup.sql
   ```

3. **Stop Database**
   ```bash
   docker compose down
   ```

4. **Package Files**
   ```bash
   # Create a tarball of everything (Photos + Configs + DB Dump)
   # We exclude node_modules or temp files if any
   cd ..
   tar -czf memu_migration.tar.gz memu-os/
   ```

### Phase 2: Transfer
*Copy the file to the NEW machine.*

**Option A: SCP (Linux/Mac)**
```bash
scp memu_migration.tar.gz user@192.168.1.50:~/
```

**Option B: USB Drive**
Copy the `.tar.gz` file to a USB stick and plug it into the new machine.

### Phase 3: Restore Target
*Run these commands on the NEW machine.*

1. **Prepare Environment**
   - Install Docker & Docker Compose (or run `install.sh` just to set up dependencies, but **STOP** before running the wizard).
   - Ideally, clean the directory: `rm -rf memu-os`

2. **Extract Files**
   ```bash
   tar -xzf memu_migration.tar.gz
   cd memu-os
   ```

3. **Start Database Only**
   ```bash
   docker compose up -d database
   # Wait 10 seconds for it to initialize
   sleep 10
   ```

4. **Restore Database**
   ```bash
   # Import the SQL dump
   cat memu_backup.sql | docker exec -i memu_postgres psql -U memu_user
   ```

5. **Start Everything**
   ```bash
   docker compose up -d
   ```

6. **Verify**
   - Check `docker ps`
   - Visit your site `http://localhost` or `http://<IP>`
   - **Important:** If your IP address changed, you may need to update your Tailscale IP or re-authenticate.

---

## Specific Scenarios

### Cloud ➡️ Hardware (The "Trial Run")
**Use Case:** You started on DigitalOcean to test Memu, now your N100 arrived.
1. Follow the steps above exactly.
2. **Tailscale:** Your new hardware will generate a *new* local IP.
   - If you used the Setup Wizard to generate a `TAILSCALE_AUTH_KEY`, check if the new device automatically connected.
   - If not, run `docker compose logs tailscale` to see the auth link.

### Hardware ➡️ Hardware (Upgrade)
**Use Case:** Moving from Raspberry Pi 5 to Intel N100.
1. Follow the steps above.
2. **Architecture:** Since both use Docker, the architecture difference (ARM64 vs AMD64) is handled automatically by Docker pulling the correct images. The *data* (Postgres dump) is architecture-independent.

### Cloud ➡️ Cloud (Migration)
**Use Case:** Moving from DigitalOcean to Hetzner.
1. Follow the steps above.
2. **DNS:** If you manually set `A` records for your domain, update them to the new IP. (If using Tailscale, this is automatic).
