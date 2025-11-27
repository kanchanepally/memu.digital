# Memu OS - Product Specification & Bible v5.0 (Live Beta)

**The Single Source of Truth.**  
*If it is in this document, it is being built. If it is not here, it is out of scope.*

---

## 1. The Manifesto: From Privacy to Sanctuary

**The Philosophy:** We do not sell "Privacy Tech" (which implies hiding). We sell "Digital Real Estate" (which implies ownership). Memu is a **Digital Sanctuary**: A physical vault in the user's home where their data lives, protected from Big Tech surveillance and commercial exploitation.

**The Trust & Safety Promise (Edge-Based Safety):** We reject the false choice between Safety and Privacy. We enforce safety at the **Edge (The Device)**, not the Cloud.
- **Local Intelligence:** All AI processing (Photos, Chat, Summaries) happens on-device.
- **Zero Telemetry:** We do not track user activity.
- **Ownership:** The user owns the hardware and the data.

---

## 2. The Product: The Memu Suite

Memu OS is a **vertically integrated Appliance** that hosts a suite of best-in-class applications:

### The Three Layers:

#### 1. The Hardware (Memu Hub)
*   **Server:** Raspberry Pi 5 (8GB RAM)
*   **Storage:** NVMe SSD (1TB recommended) via PCIe HAT
*   **Network:** Gigabit Ethernet + Cloudflare Tunnel (Zero Trust)
*   **AI Accelerator:** Raspberry Pi AI Kit (Hailo-8L NPU) - *Ready for future vision tasks*

#### 2. The Operating System (Memu OS)
*   **Base:** Debian 12 (Bookworm)
*   **Orchestration:** Docker Compose (`memu-suite`)
*   **Database:** Unified PostgreSQL 15 (handling Synapse, Immich, and Intelligence data)
*   **Cache:** Redis 6.2
*   **Proxy:** Nginx + Cloudflared

#### 3. The Application Suite
Instead of a monolithic custom app, we deploy pre-configured, "skinned" versions of industry-standard protocols.

| Capability | Backend Engine | Frontend App (User) | Branding Strategy |
| :--- | :--- | :--- | :--- |
| **Photos** | **Immich** | **Immich Mobile App** | "Memu Photos" |
| **Chat** | **Matrix (Synapse)** | **Element X / Web** | "Memu Chat" |
| **Intelligence** | **Ollama + Python** | **Memu Bot (@memu_bot)** | "Memu Assistant" |

---

## 3. Feature Specifications

### Feature 1: Memu Chat (Communication)
**User Story:** "I want to text my family privately, with no data mining."

**Implementation:**
*   **Backend:** Matrix Synapse (Homeserver).
*   **Frontend:** Element Web (hosted locally) & Element X (Mobile).
*   **Security:** End-to-End Encryption (E2EE) enabled by default.
*   **Access:** `https://rachandhari.memu.digital`

### Feature 2: Memu Photos (The Vault)
**User Story:** "I want my camera roll backed up automatically to my own drive."

**Implementation:**
*   **Backend:** Immich Server (High-performance Go/Node).
*   **AI:** Local Machine Learning for face recognition and object detection.
*   **Storage:** Original files stored on NVMe SSD.
*   **Access:** `https://rachandhari.memu.digital/api` (Mobile App)

### Feature 3: Memu Intelligence (The Brain)
**User Story:** "I want a smart assistant that knows my family context but is private."

**Implementation:**
*   **Engine:** Ollama (running Llama 3.2 3B).
*   **Controller:** Custom Python Service (`memu_intelligence`).
*   **Interface:** Matrix Bot (`@memu_bot`).

**Capabilities (Live Now):**
1.  **Memory:**
    *   `/remember [fact]` - Stores info in Vector/SQL memory.
    *   `/recall [query]` - Retrieves info using Semantic Search.
2.  **Organization:**
    *   `/addtolist [items]` - Adds to shared shopping list.
    *   `/showlist` - Displays current list.
    *   `/done [item]` - Marks items as complete.
3.  **Time Management:**
    *   `/remind [task] [time]` - Uses AI to parse natural language (e.g., "in 10 mins").
    *   **Auto-Notification:** Bot pings the user when due.
4.  **Summarization:**
    *   `/summarize` - AI reads the day's chat logs and creates a bulleted summary.

---

## 4. System Architecture

### 4.1 Container Stack (`docker-compose.memu.yml`)

The system runs as a unified Docker Compose stack on the `hearth` network.

*   **Core Services:**
    *   `memu_postgres`: Unified DB for all services.
    *   `memu_redis`: Shared cache.
    *   `memu_tunnel`: Cloudflare Tunnel (Ingress).
    *   `memu_proxy`: Nginx (Local routing).

*   **Chat Services:**
    *   `memu_synapse`: Matrix Homeserver.
    *   `memu_element`: Web Chat UI.

*   **Photo Services:**
    *   `memu_photos_server`: Immich Core.
    *   `memu_photos_workers`: Background tasks.
    *   `memu_photos_ml`: Machine Learning.

*   **Intelligence Services:**
    *   `memu_brain`: Ollama API.
    *   `memu_intelligence`: Python Logic Bridge.

### 4.2 Networking
*   **Ingress:** Cloudflare Tunnel (No open ports on router).
*   **Internal:** Docker Bridge Network (`memu-suite_default`).
*   **DNS:** `rachandhari.memu.digital` resolves to the Tunnel edge.

### 4.3 Data Hierarchy
*   **Root:** `~/hearth-os` (Codebase & Configs).
*   **Data Volumes:**
    *   `memu-suite_pgdata`: Database files.
    *   `memu-suite_ollama_data`: AI Models.
    *   `memu-suite_immich_upload`: Photo files (External SSD).

---

## 5. Security & Privacy

### 5.1 Encryption
*   **Transmission:** TLS 1.3 via Cloudflare.
*   **Message Content:** Matrix E2EE (Olm/Megolm). Keys held by user devices only.
*   **Storage:** LUKS Full Disk Encryption (Recommended for SSD).

### 5.2 AI Privacy
*   **Air-Gapped AI:** The Ollama container has no outbound internet access (except for initial model pull).
*   **Local Processing:** All prompts and images stay on the Pi.

---

## 6. Development Roadmap

### Phase 1: Foundation (Completed) ✅
*   [x] Hardware Setup (Pi 5 + NVMe).
*   [x] Docker Infrastructure (Unified Stack).
*   [x] Matrix Chat (Synapse + Element).
*   [x] Immich Photos (Full Suite).
*   [x] Cloudflare Tunnel Access.

### Phase 2: Intelligence (Completed) ✅
*   [x] Ollama Integration (Llama 3.2).
*   [x] Python Bot Framework.
*   [x] Features: Memory, Lists, Summaries.
*   [x] Features: Natural Language Reminders.

### Phase 3: Refinement (Current Focus) 🚧
*   [ ] **Backup Automation:** Cron jobs for `backup_memu.sh`.
*   [ ] **Dashboard:** Simple Web UI for system status (CPU/Temp/Storage).
*   [ ] **Multi-User Onboarding:** Streamlined invite flow.

### Phase 4: Expansion (Future)
*   [ ] **Home Automation:** Home Assistant Integration.
*   [ ] **Voice:** Whisper STT for voice commands to bot.
*   [ ] **Federation:** Connect with other Memu families.

---

## 7. Success Metrics (Current Status)

*   **Uptime:** >99% (Stable).
*   **Performance:**
    *   Chat Latency: <200ms.
    *   AI Response: <5s (Llama 3.2).
    *   Photo Scroll: 60fps (Immich).
*   **Data Integrity:** 100% (Postgres + Backup Scripts).

---

## 8. Admin & Maintenance

### Key Commands
*   **Start:** `docker compose up -d`
*   **Logs:** `docker compose logs -f [service]`
*   **Backup:** `./scripts/backup_memu.sh`
*   **Update:** `git pull && docker compose build && docker compose up -d`

### Troubleshooting
*   **Bot Silent?** Check `memu_intelligence` logs.
*   **Photos Not Syncing?** Check `memu_photos_server` logs.
*   **Site Offline?** Check `memu_tunnel` logs.