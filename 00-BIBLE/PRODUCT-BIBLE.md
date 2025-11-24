# Memu OS - Product Specification & Bible v4.0**

**The Single Source of Truth.**  
 *If it is in this document, it is being built. If it is not here, it is out of scope.*

---
## 1. The Manifesto: From Privacy to Sanctuary

**The Philosophy:** We do not sell "Privacy Tech" (which implies hiding). We sell "Digital Real Estate" (which implies ownership). Memu is a **Digital Sanctuary**: A physical vault in the user's home where their data lives, protected from Big Tech surveillance and commercial exploitation.

**The Trust & Safety Promise (Edge-Based Safety):** We reject the false choice between Safety and Privacy. We enforce safety at the **Edge (The Device)**, not the Cloud.
- **CSAM/Harm Prevention:** The Memu Hub uses local, on-device AI (Hailo NPU) to classify and block harmful content _before_ it is written to storage.
- **Abuse Prevention:** Immutable local audit logs prevent coercive controllers from hiding their tracks.
- **The "Paper Trail":** We require valid payment methods for Relay access to deter anonymous criminal usage.
## 2. The Product: The Memu Suite**

Memu OS is a **vertically integrated Appliance** that hosts a suite of best-in-class applications:

**The Three Layers:**

1. **The Hardware (Memu Hub)**

* Physical server: Raspberry Pi 5 (8GB RAM recommended)  
* Storage: NVMe SSD (256GB minimum, 1TB recommended)  
* Form factor: Fanless case with passive cooling  
* Network: Gigabit Ethernet + WiFi 6  +Cloudflare Tunnel (Zero configuration remote access).
* Power: USB-C PD (27W official adapter)  
* Status indicator: Single RGB LED
* **AI Accelerator:** **Raspberry Pi AI Kit (Hailo-8L NPU)** – _Crucial for local safety scanning._

2. **The Operating System (Memu OS)**

* Base: Debian 12 (Bookworm) Lite 64-bit  
* Containerization: Docker \+ Docker Compose  
* Process supervisor: systemd  
* Auto-updates: GitOps pull model  
* Zero-configuration networMemug: mDNS (Avahi)
* **Database:** Unified Postgres (with `pgvecto.rs` extension) + Redis.
* **Update System:** GitOps (Pull-based updates via `cron`).

3. **The Application Suite (The User Experience)**

Instead of a monolithic custom app, we deploy pre-configured, "skinned" versions of industry-standard protocols.

| Capability       | Backend Engine     | Frontend App (User)       | Branding Strategy                                       |
| ---------------- | ------------------ | ------------------------- | ------------------------------------------------------- |
| **Photos**       | **Immich**         | **Immich Mobile App**     | Server Name: "Memu Sanctuary"                           |
| **Chat**         | **Matrix/Synapse** | **Element (Memu Config)** | Custom Theme & Default Home Server                      |
| **Safety**       | **Hailo/Local AI** | **Middleware**            | Invisible "Guardian" process                            |
| **Intelligence** | **Ollama**         | **Middleware**           | Create automatic plans, tasks, digital family organiser |

---
## 3. Feature Specifications**

### Feature 1: Memu Chat 

**User Story:** "I want to text my wife and share photos without Meta mining the metadata."

**Implementation:**
- **Backend:** Matrix Synapse (Stock)
- **Frontend:** Element Web (Hosted locally) + Element Mobile (App Store)
- **Configuration:** "Skinned" via `config.json` and QR Code onboarding.


**Core Capabilities (Inherited from Element):**
- **E2EE:** ON by default. Keys stored in device Secure Enclave.
- **Media:** Auto-compressed for transit, full-res saved to Memories.
- **Offline Mode:** Local caching of last 1,000 messages.
- **Push:** UnifiedPush (Android) / APNs Relay (iOS).

### Feature 2: Memu Memories (The Vault)

**User Story:** "I want my camera roll backed up automatically, and I want to find 'dog' instantly."

**Implementation:**

- **Backend/Frontend:** Immich (Stock)
    
- **AI Hardware Strategy:**
    
    - **Vision (Face/Object):** Offloaded to **Hailo-8L NPU** (via Immich ML container).
        
    - **Transcoding:** Hardware accelerated (Pi 5 VideoCore).
        

**Core Capabilities:**

- **Sync:** Background differential sync (WiFi only default).
    
- **Search:** Semantic search (CLIP model running on NPU).
    
- **Family Albums:** Shared albums with granular privacy.
    

### Feature 3: Memu Intelligence (The Brain)

**User Story:** "I want a smart assistant that knows my family context but never sends data to the cloud."

**Implementation:**

- **Engine:** Ollama (Local LLM Server).
    
- **Model:** Llama 3.2 3B Instruct (4-bit Quantized).
    
- **Memory:** ChromaDB (Vector Store for RAG).
    
- **Interface:** "Memu Bot" (A Matrix Bot user in the family room).
    

**Capabilities:**

1. **Smart Task Extraction:**
    
    - _Trigger:_ Bot listens to messages in "Family" room.
        
    - _Action:_ Extracts tasks ("Buy milk") -> Saves to Todo list.
        
2. **Natural Query:**
    
    - _Query:_ "What is the WiFi password?"
        
    - _Action:_ RAG search against stored "Home Notes."
        
3. **Privacy Guard:**
    
    - _Constraint:_ LLM has **NO** internet access. It is air-gapped within the container.
        
    - _Thermal Throttling:_ Service pauses if CPU temp > 75°C.

---
## 4. System Architecture: "Memu OS"

Memu OS transforms a Raspberry Pi into a consumer appliance, not a Linux server.

### 4.1 The Boot Process

**Step-by-step boot sequence:**
 
1. **Hardware Boot (0-5 seconds)**
   - Pi 5 EEPROM firmware loads from SPI flash
   - Bootloader checks NVMe SSD for OS
   
2. **OS Load (5-15 seconds)**
   - Debian 12 Bookworm kernel loads from \`/boot\`
   - initramfs mounts NVMe as root filesystem
   - systemd becomes PID 1

3. **Memu Supervisor Start (15-20 seconds)**
   - \`Memu-supervisor.service\` starts (systemd unit)
   - Supervisor checks \`/Memu/system/version.txt\` for current OS version
   - Checks \`/Memu/data\` mount status
   
4. **Container Orchestration (20-40 seconds)**
   - \`docker-compose up -d\` in \`/Memu/system/docker-compose.yml\`
   - Services start in order (defined by \`depends\_on\`):
	 	1. PostgreSQL (database)
	 	2. Synapse (Matrix homeserver)
	 	3. Immich (photo backend)
	 	4. Ollama (LLM server)
	 	5. Nginx (reverse proxy, serves Element Web \+ APIs)

3. **Health Check (40-50 seconds)**
   - Supervisor pings \`http:*//localhost:8080/health\`*
   - Each service reports status (healthy/unhealthy)
   - LED indicator:
	 	- **Solid Green:** All services healthy
	 	- **Flashing Yellow:** Services starting
	 	- **Flashing Red:** Service failed (check logs via web UI)
	 	- **Solid Red:** Critical failure (OS corruption, hardware issue)

 6. **Network Broadcasting (50-60 seconds)**
  - Avahi (mDNS) broadcasts: \`Memu.local\`
   - Users can access via \`http:*//Memu.local:8080\` on local network*
 
**Total boot time:** \~60 seconds from power-on to usable

---

### 4.2 The File System Hierarchy

**READ-ONLY (Immutable OS):**

```

/boot       	→ Bootloader, kernel, device tree

/Memu/system 	→ OS code (Git repo, never edited by user)
  ├── docker-compose.yml
  ├── nginx.conf
  ├── update.sh
  └── version.txt
```

**READ-WRITE (User Data - THE HOLY GRAIL):**

```

/Memu/data   	→ ALL user data lives here

  ├── postgres/     	→ Database files
  ├── media/        	→ Photos, videos (Immich storage)
     ├── upload/   	→ Original files
     ├── thumbs/   	→ Thumbnails
     └── encoded/  	→ Transcoded videos
  ├── synapse/      	→ Matrix homeserver data
     ├── media\_store/  → Chat attachments
     └── homeserver.db → (if using SQLite, but we use Postgres)
  ├── config/       	→ User preferences
     ├── users.json	→ Family member accounts
     └── wifi.json 	→ Known SSIDs for auto-sync
  └── ollama/       	→ LLM models
  	└── models/   	→ Downloaded Llama/Phi models

```

**Why this matters:**
- **Backup:** Only \`/Memu/data\` needs bacMemug up (everything else is reproducible)
- **Updates:** Pull new \`/Memu/system\` from Git, restart containers (data untouched)
- **Recovery:** If OS corrupts, flash new SD card, mount NVMe at \`/Memu/data\`, data intact

---
### 4.3 Networking Architecture

**Local Network (Primary):**

```
Device → WiFi/Ethernet → Router → Pi (192.168.1.x)
Access via: http:*//Memu.local:8080*
```


**Remote Access (Optional):**

```

Device → Internet → Cloudflare Tunnel → Pi

Access via: https:*//smithfamily.relay.Memu.app*

**Ports:**

* 8080: Main web interface (Element Web, admin panel)  
* 8008: Matrix homeserver (for mobile clients)  
* 2283: Immich API (for mobile photo sync)  
* 11434: Ollama API (internal only, not exposed)  
* 80/443: Nginx reverse proxy (handles all routing)

**Firewall:**

* Local: All ports open on 192.168.x.x  
* Remote: Only Cloudflare tunnel ingress (no open ports on router)
  
```
---

**3.4 Update Mechanism**

**Philosophy:** GitOps - the Pi is always trying to match the Git repo state.

**Process:**

1. User taps "Update Hub" in mobile app  
2. App sends API call: POST /api/system/update  
3. Memu Supervisor runs:
```
bash
   cd /Memu/system
   git fetch origin
   git reset --hard origin/main
   docker-compose pull
   docker-compose up -d --build
```
4. Services restart with new code  
5. App notifies: "Update complete\!" (or shows error log if failed)

**Safety:**

* Before update: Snapshot /Memu/data/postgres (automatic backup)  
* If update fails: Rollback to previous Git commit  
* Critical updates: Supervisor checks /Memu/data integrity before proceeding

**Update channels:**

* **Stable:** Major releases only (default for customers)  
* **Beta:** Weekly updates (opt-in for early adopters)  
* **Dev:** Daily builds (internal testing only)

---

**3.5 Container Architecture**

**Docker Compose Services:**
```
yaml

services:

  postgres:

	image: postgres:15-alpine

	*\# Shared database for Synapse \+ Immich*

	
  synapse:

	image: matrixdotorg/synapse:latest

	depends\_on: \[postgres\]

	*\# Matrix homeserver*

	

  immich:

	image: ghcr.io/immich-app/immich-server:latest

	depends\_on: \[postgres\]

	*\# Photo backend*

	

  immich-ml:

	image: ghcr.io/immich-app/immich-machine-learning:latest

	*\# ML service (object detection, face recognition)*

	

  ollama:

	image: ollama/ollama:latest

	*\# LLM server*

	

  nginx:

	image: nginx:alpine

	depends\_on: \[synapse, immich\]

	*\# Reverse proxy, serves Element Web*

```

**Why containers:**

- Isolation (services don't conflict)
- Updates (pull new image, restart)
- Portability (same setup on any Pi)
- Rollback (keep old images for 30 days)

---
## 5. The "No-Terminal" Guarantee*

**The Golden Rule:** If a user has to open a terminal, we have failed.
### 5.1 Initial Setup*

**Method:** Web-based wizard at \`http://Memu.local:8080/setup\`

**Steps:**

1. **Welcome screen** (detected via mDNS)

2. **Create admin account** (username, password)

3. **Add family members** (invite codes sent via email/SMS)

4. **Configure WiFi** (for automatic photo sync)

5. **Remote access setup:**

   - Option A: Managed relay ($6/month)

   - Option B: Own Cloudflare tunnel (guided setup)

   - Option C: Local only (free)

6. **First sync:** App prompts to enable camera upload


**Time to complete:** \<5 minutes

---

### 5.2 Updates*

**Via mobile app:**

- Tap Settings → Hub Status → "Update Available" badge

- Tap "Update Now"

- Progress bar shows: Downloading → Installing → Restarting

- Notification: "Hub updated successfully\!"

**No terminal, no SSH, no commands.**

---

### 5.3 Troubleshooting*

**LED Status Indicators:**

- **Solid Green:** All systems operational

- **Flashing Yellow:** Starting up or updating

- **Flashing Red:** Service failure (user can check web UI)

- **Solid Red:** Critical failure
 

**Web UI (http://Memu.local:8080/admin):**

- System health dashboard

- Service status (Synapse: ✅, Immich: ✅, etc.)

- Error logs (user-friendly, not raw logs)

- Action buttons: "Restart Service", "Download Logs" (for support)

**Mobile app troubleshooting:**

- Connection test (taps "Test Hub", app pings all services)

- Network diagnostics (checks if on correct WiFi)

- Guided fixes: "Hub not reachable? Try these steps..."


**Phase 2 (Advanced):**

- Bluetooth LE beacon broadcasts health status

- App can diagnose even without network connection
---
## 6. Data & Privacy

### 6.1 Trust Model: "Safety without Surveillance"

**Open Core:**

- **Source Code:** AGPLv3 (Repository on GitHub).
    
- **Transparency:** Users can audit the `docker-compose.yml` and startup scripts to verify exactly what code is running.
    
- **No Blobs:** No proprietary logic aside from hardware firmware (Raspberry Pi / Hailo).
    

**The "Edge-Based" Safety Promise:**

- **Scanning:** Safety scanning (CSAM/Nudity) occurs **locally** on the Hailo-8L NPU.
    
- **Data Flow:** Image $\to$ RAM $\to$ NPU Check $\to$ Storage.
    
- **Privacy:** The image never leaves the device for scanning. No "hashes" are sent to a central Memu server for verification.
    

**No Telemetry:**

- **The Hub:** Does NOT phone home.
    
- **Update Checks:** Anonymous pull request (GitOps) to public repositories. No User ID is tracked.
    
- **Crash Reports:** Opt-in only.
    
- **Analytics:** Zero. We track nothing.
    

### 6.2 Data Ownership & Portability

**User Ownership:**

- **Photos/Videos:** Stored as standard files (JPEG/HEIC/MP4) on the NVMe drive. Not locked in a proprietary database format.
    
- **Messages:** Stored in a local PostgreSQL database (exportable).
    
- **AI Models:** Downloaded once and run locally. No API calls to OpenAI/Anthropic.
    

**Data Portability (The "Exit Strategy"):** We believe you should stay because you want to, not because you are trapped.

- **Photos:** Since files are stored in a standard directory structure (`/mnt/memu_storage/photos/YYYY/MM`), users can simply plug the drive into a PC to retrieve them. No "Export" tool needed for raw files.
    
- **Chat:** Matrix offers GDPR-compliant export tools. We provide an Admin Script to dump the database to JSON.
    
- **Migration:** The entire `data` volume can be copied to a new Hub to migrate instantly.
    

### 6.3 Encryption & Security Architecture

**At Rest:**

- **NVMe Storage:** LUKS Full-Disk Encryption (Phase 2 Implementation).
    
- **Database:** Standard PostgreSQL security (User/Pass protected within Docker Network).
    

**In Transit:**

- **Remote Access:** Fully encrypted via **Cloudflare Tunnel** (TLS 1.3). No open ports on the home router.
    
- **Chat:** Matrix End-to-End Encryption (E2EE) via Olm/Megolm protocols.
    
    - _Note:_ Memu Hub stores encrypted message blobs. Only user devices (phones/laptops) hold the decryption keys.
        
- **Internal Network:** Docker containers communicate via an isolated internal bridge network.
    

**Intelligence Privacy (The "Air Gap"):**

- The **Memu Intelligence** container (Ollama) is configured with **no outbound internet access** (except for initial model download).
    
- It cannot leak prompts or family context to the web, even if it wanted to.

---

## 7. Hardware Specifications*

### 7.1 Memu Hub (Raspberry Pi 5 Configuration)*

**Minimum spec (for up to 4 users, 10K photos):**

- Raspberry Pi 5 (4GB RAM)

- 256GB NVMe SSD

- Official Pi 5 Case

- 27W USB-C Power Supply


**Recommended spec (for 6+ users, 50K+ photos):**

- Raspberry Pi 5 (8GB RAM)

- 1TB NVMe SSD

- NVMe Base HAT (PCIe Gen 3 x1)

- Passive cooling case (Argon NEO 5\)

- 27W USB-C Power Supply

**Power consumption:**

- Idle: 3-5W

- Active (photo upload): 8-12W

- ML processing: 12-15W

- Annual electricity cost: \~$15-25/year (US average)
---
### 7.2 Performance Targets*

**Matrix Chat:**

- Message latency (local): \<100ms

- Message latency (remote): \<500ms

- Concurrent users: 10 (family)

- Messages/day: Unlimited

**Photo Sync:**

- Upload speed: 10-20 photos/minute (on gigabit ethernet)

- ML processing: \~100 photos/hour (during 2-6 AM window)

- Search latency: \<2 seconds for 50K photo library

- Timeline load: \<1 second for 200 thumbnails


**LLM (Intelligence):**

- Query latency: 5-15 seconds (Llama 3.2 3B on Pi 5\)

- Token generation: \~10 tokens/second

- Context window: 8K tokens

- Concurrent queries: 1 (queued if multiple)
---
## 8. Development Roadmap

### Phase 1: The Foundation (Months 1-3) ✅ IN PROGRESS

**Goal:** A stable, "self-driving" appliance for one family (The Founder).

**Hardware:** Raspberry Pi 5 (8GB) + NVMe SSD + **Hailo-8L AI Kit**.

**Core Deliverables:**

- [x] **Infrastructure:** Unified Docker Compose (Immich, Synapse, Redis, Postgres, Cloudflared).
    
- [x] **Memu Chat:** Matrix Synapse backend + Element Web (Self-Hosted).
    
- [ ] **Memu Memories:** Immich backend + Hardware Accelerated ML (Hailo NPU).
    
- [ ] **Memu Intelligence:** Ollama service running Llama 3.2 (Backend only).
    
- [ ] **Branding:**
    
    - [ ] Skinned Element Web (`config.json` + Assets).
        
    - [ ] "Magic Link" QR Code generator for mobile onboarding.
        
- [ ] **Networking:** Automated Cloudflare Tunnel token injection via Setup Wizard.
    

**Success Metric:** Wife uses it for a week without asking "How do I log in?"

### Phase 2: The Experience (Months 4-6)

**Goal:** 20 Beta Families using it daily.

**Hardware:** Same (Pi 5 + NVMe + Hailo).

**Core Deliverables:**

- [ ] **The "Memu Bot":** A Matrix bot that interfaces with the local Ollama instance (Task extraction & Q/A).
    
- [ ] **Edge Safety Layer:** Middleware to pass new photo uploads through Nudity Classification model on the NPU _before_ storage.
    
- [ ] **Federation Pilot:** Connect your Hub with one external family member (e.g., Sister) to validate the "Constellation" architecture.
    
- [ ] **Notifications:** Configure UnifiedPush (Android) and APNs Relay (iOS) for reliable alerts.
    
- [ ] **Backup:** One-click script to backup "Golden Copy" to an external USB drive.
    

**Success Metric:** 20 families active, <5 support tickets per week.

### Phase 3: The Product (Months 7-12)

**Goal:** 100 Paying Customers (Launch).

**Hardware:** "Productized" Bundle (Custom Case + Branded Packaging).

**Core Deliverables:**

- [ ] **Auto-Update System:** Robust GitOps (Pull-based) updates that can rollback on failure.
    
- [ ] **Service Dashboard:** A simple Web Admin UI to restart containers and view disk usage/temperatures.
    
- [ ] **Data Migration Tool:** "Import from Google Takeout" script.
    
- [ ] **Billing Integration:** Stripe integration for the optional "Memu Relay" subscription.
    

**Business Model:** $149 Hardware + Optional $6/mo Relay (High Bandwidth).

### Phase 4: The Ecosystem (Year 2+)

**Goal:** 1,000 Customers & Profitability.

**Core Deliverables:**

- [ ] **Home Automation:** MQTT Bridge (Home Assistant integration) for the "Smart Home" aspect.
    
- [ ] **Documents:** Nextcloud or Paperless-ngx integration for scanning/storing family docs.
    
- [ ] **Multi-Hub HA:** High Availability (Secondary Hub takes over if Primary fails).
    
- [ ] **Custom Mobile App:** _Only now_ do we consider building a custom React Native wrapper to unify the experience.

---

## 9. Non-Goals (Out of Scope)*

**What Memu OS will NEVER be:**

❌ A social network (no friend requests, no public profiles) 

❌ A cloud service (data never touches our servers) 

❌ A subscription trap (hardware is one-time, relay is optional) 

❌ An ad platform (no monetization via user data) 

❌ A smart home hub (Phase 4 at earliest, not core) 

❌ An email server (too complex, low value-add) 

❌ A VPN service (not our core competency) 


**Focus:** Family communication, photos, basic organization. Nothing more.

---

## 10. Success Metrics*

### Product Metrics:*

**Engagement:**

- Daily active users: \>80% of family members

- Messages sent/day per family: \>10

- Photos uploaded/week per family: \>20

**Reliability:**

- Uptime: \>99.5% (measured via mobile app pings)

- Data loss incidents: 0

- Failed updates: \<5%


**Performance:**

- Photo search query time: \<2 seconds (95th percentile)

- Chat message latency: \<500ms (95th percentile)

- App crash rate: \<1% of sessions

### Business Metrics (Phase 3+):*

**Revenue:**

- Units sold/month: 50 (by Month 12\)

- Relay subscribers: 30% of hardware customers

- MRR: $900 (30 relay subs × $6/mo × 50% margin)

**Costs:**

- Hardware COGS: $75 (Pi \+ SSD \+ case \+ shipping)

- Relay infrastructure: $0.50/customer/month

- Support: \<2 hours/customer/month


**Unit economics:**

- Hardware margin: $74 ($149 - $75 COGS)

- Relay margin: $5.50/mo ($6 - $0.50 infrastructure)

- LTV (5 years): $149 \+ ($5.50 × 60 months) \= $479


---

 

## 11. Open Questions & Decisions Needed*


**Technical:**

- [ ] Llama 3.2 3B vs Phi-3 Mini (benchmark on Pi 5\)

- [ ] Full-disk encryption: Default ON or user opt-in?

- [ ] Backup strategy: USB drive vs cloud (Backblaze B2)?

 

**Product:**

- [ ] Tasks app: Separate app or tab in main app?

- [ ] Calendar: Build from scratch or integrate existing (Nextcloud Calendar)?

- [ ] Multi-hub federation: Matrix native or custom protocol?

 

**Business:**

- [ ] Relay pricing: $6/mo or $60/yr?

- [ ] Hardware pricing: $149 or $199?

- [ ] Support model: Community forum or email support?


**Brand:**

- [ ] Final name: Memu, Memo, Illu, or other?

- [ ] Domain: .app, .family, .io?

- [ ] Logo/visual identity

 
---

 

## 12. Appendix: Technical Specifications*

### 12.1 API Endpoints (Internal)*

**Memu Supervisor API (for mobile app):**

\`\`\`

GET  /api/system/status   	→ Service health

POST /api/system/update       → Trigger update

GET  /api/system/logs     	→ Error logs

POST /api/system/restart/:service → Restart service

\`\`\`

 

**Matrix (Synapse):**

\`\`\`

POST /\_matrix/client/v3/login → User login

GET  /\_matrix/client/v3/sync  → Message sync

POST /\_matrix/client/v3/rooms/:roomId/send/:eventType → Send message

\`\`\`

 

**Immich:**

\`\`\`

POST /api/upload              → Upload photo

GET  /api/assets          	→ List photos

POST /api/search              → Search photos

GET  /api/assets/:id/thumbnail → Get thumbnail

\`\`\`

 

**Ollama:**

\`\`\`

POST /api/generate            → LLM query

GET  /api/tags            	→ List models

POST /api/pull                → Download model

\`\`\`

 

---

 

### 12.2 Database Schema (Simplified)*

 

**PostgreSQL databases:**

 

**\`synapse\` (Matrix homeserver):**

- \`users\` → Matrix user accounts

- \`rooms\` → Chat rooms

- \`events\` → Messages (encrypted content)

- \`room\_memberships\` → Who's in which room

 

**\`immich\` (Photo backend):**

- \`assets\` → Photos/videos metadata

- \`smart\_info\` → ML tags (objects, faces)

- \`albums\` → User-created albums

- \`users\` → Immich user accounts (synced with Matrix users)

 

**\`Memu\_tasks\` (Custom, Phase 2):**

- \`tasks\` → To-do items

- \`task\_assignments\` → Who's responsible

- \`categories\` → Shopping, Admin, etc.

---

 

### 12.3 Mobile App Architecture*

**Technology:**

- React Native 0.72+

- TypeScript (strict mode)

- State management: Zustand (lightweight, not Redux)

- Navigation: React Navigation v6

- Offline: WatermelonDB (local SQLite)


**Key libraries:**

- \`matrix-js-sdk\`: Matrix client

- \`react-native-image-picker\`: Camera/gallery access

- \`react-native-background-upload\`: Photo sync while app backgrounded

- \`react-native-push-notification\`: UnifiedPush/APNS

- \`react-native-keychain\`: Secure key storage


**App structure:**

\`\`\`

/src

  /screens

	/Chat     	→ Matrix chat UI

	/Memories 	→ Photo timeline

	/Tasks    	→ To-do lists (Phase 2\)

	/Settings 	→ Hub config, account

  /services

	/matrix.ts	→ Matrix API wrapper

	/immich.ts	→ Photo sync logic

	/storage.ts   → Local database

  /components

	/ChatBubble   → Message UI

	/PhotoGrid	→ Timeline grid

	/TaskItem 	→ Task checkbox

---

**13. The One-Page Summary (For Investors/Partners)**

**Memu OS: The Private Cloud Appliance**

**What:** A Raspberry Pi \+ custom software that replaces iCloud, WhatsApp, and Google Photos for families.

**Why:** Families want convenience without surveillance. Memu delivers cloud-like UX with self-hosting sovereignty.

**How:**

* Hardware: $149 Pi 5 \+ NVMe  
* Software: Open-source (Matrix, Immich, Ollama)  
* Interface: Mobile app (iOS \+ Android)

**Revenue:**

* Hardware sale: $149 (50% margin)  
* Optional relay: $6/month (92% margin)  
* LTV (5 years): $479

**Market:**

* TAM: 130M US households  
* SAM: 13M privacy-aware families (10%)  
* SOM: 100K families (0.8% of SAM) \= $48M revenue

**Traction (Phase 1):**

* WorMemug prototype ✅  
* 1 family validated (you) ✅  
* 20 beta families (Month 4 target)

**Ask:** $500K seed (18-month runway to 1,000 customers, profitability)

---