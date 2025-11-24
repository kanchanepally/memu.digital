# Memu OS - Product Specification & Bible v3.0**

**The Single Source of Truth.**  
 *If it is in this document, it is being built. If it is not here, it is out of scope.*

---
## 1. Product Definition**

Memu OS is a **vertically integrated Private Cloud Appliance** consisting of three inseparable layers:

**The Three Layers:**

**1. The Hardware (Memu Hub)**

* Physical server: Raspberry Pi 5 (8GB RAM recommended)  
* Storage: NVMe SSD (256GB minimum, 1TB recommended)  
* Form factor: Fanless case with passive cooling  
* Network: Gigabit Ethernet \+ WiFi 6  
* Power: USB-C PD (27W official adapter)  
* Status indicator: Single RGB LED

**2. The Operating System (Memu OS)**

* Base: Debian 12 (Bookworm) Lite 64-bit  
* Containerization: Docker \+ Docker Compose  
* Process supervisor: systemd  
* Auto-updates: GitOps pull model  
* Zero-configuration networMemug: mDNS (Avahi)

**3. The Interface (Memu Mobile)**

* Technology: React Native (single codebase, iOS \+ Android)  
* Architecture: Offline-first with sync  
* Design system: Custom (family-focused, not corporate)

---
**The Core Value Proposition**

**"The convenience of iCloud, with the sovereignty of a hard drive."**

Users get:

* Cloud-like experience (always accessible, always synced)  
* Self-hosting reality (data never leaves their home)  
* No recurring cloud fees (one-time hardware \+ optional relay)

---
## 2. Feature Specifications**

**Feature 1: Memu Chat (Communication Layer)**

**User Story:**  
 *"I want to text my wife and share photos of the kids without Meta mining the metadata."*

**Technology Stack:**

* **Backend:** Matrix Synapse v1.96+ (homeserver)  
* **Database:** PostgreSQL 15  
* **Protocol:** Matrix (HTTP REST \+ JSON)  
* **Client library:** matrix-js-sdk (React Native wrapper)

**Detailed Requirements:**

**2.1.1 End-to-End Encryption (E2EE)**

* Default: ON for all direct messages and family rooms  
* Algorithm: Olm (1-to-1) \+ Megolm (group chat)  
* Key storage: React Native Secure Storage (Keychain on iOS, KeyStore on Android)  
* Key backup: Encrypted backup to Hub (user sets recovery passphrase)  
* Device verification: QR code or emoji comparison

**2.1.2 Media Handling**

* Images sent in chat:  
  * Compressed to \<500KB for transmission (JPEG quality 85%)  
  * Original HEIC/PNG automatically copied to Memu Memories (full resolution)  
  * Thumbnail generated on-device (256x256px) for fast loading  
* Videos:  
  * Compressed to 720p for chat transmission  
  * Original 4K version saved to Memories  
  * Maximum chat video: 2 minutes or 50MB

**2.1.3 Offline Mode**

* App caches last 1,000 messages per room (SQLite local database)  
* Drafts queue locally if Hub unreachable  
* On reconnection, messages sync in chronological order  
* Conflict resolution: Last-write-wins (Matrix handles this)

**2.1.4 Push Notifications**

* **Android:** UnifiedPush (self-hosted, privacy-preserving)  
* **iOS:** APNs via ntfy.sh relay (encrypted payload, relay sees only "New message" metadata)  
* Battery optimization: Notification channels, not polling  
* Settings: Per-room notification preferences (all/mentions/off)

**2.1.5 Message Features**

* Text formatting: Markdown (bold, italic, code blocks)  
* Reactions: Emoji reactions (Unicode, not custom)  
* Replies: Thread-style (quote parent message)  
* Editing: Edit sent messages (shows "edited" timestamp)  
* Deletion: Soft delete (removes from view, not from database for E2EE reasons)  
* Read receipts: Optional (privacy setting)

---

**Feature 2: Memu Memories (Storage Layer)**

**User Story:**  
 *"I want my camera roll backed up automatically when I walk in the door, and to search for 'dog' to find pictures of our pet."*

**Technology Stack:**

* **Engine:** Immich v1.91+ (open-source Google Photos alternative)  
* **Database:** PostgreSQL 15 (shared with Synapse)  
* **Object storage:** Local filesystem (/Memu/data/media)  
* **Transcoding:** FFmpeg with hardware acceleration (Pi 5 H.265 encoder)  
* **Face detection:** CLIP (REMOVE - use Immich's built-in face recognition)  
* **ML:** Immich's built-in ML service (TensorFlow Lite optimized for ARM)

**Detailed Requirements:**

**2.2.1 Background Sync**

* Trigger: Device connects to known WiFi SSID (user configures in setup)  
* Method: Differential sync (only new/modified files)  
* Protocol: HTTPS upload to Immich API  
* Frequency: Check every 30 minutes when on WiFi, upload immediately when new photo taken  
* Battery: Only sync when battery \>20% or charging  
* Cellular: User-configurable (default: WiFi only)

**2.2.2 Machine Learning (On-Device)**

* Use Immich's built-in ML service, NOT separate CLIP/ONNX  
* Immich ML service runs:  
  * Object detection (e.g., "dog", "beach", "birthday cake")  
  * Face detection and clustering (groups faces, user labels names)  
  * Image embeddings for similarity search  
* **Schedule:** ML jobs run 2 AM - 6 AM only (prevent thermal throttling)  
* **Performance:** Process \~100 photos per hour on Pi 5  
* **Priority:** New uploads processed first, backlog processed incrementally

**2.2.3 Timeline View**

* UI: Infinite scroll, reverse chronological  
* Grouping: By day (e.g., "Today", "Yesterday", "November 20, 2024")  
* Thumbnails: 256x256px JPEG (generated by Immich)  
* Loading: Lazy load (fetch 50 at a time as user scrolls)  
* Caching: App caches last 200 thumbnails locally

**2.2.4 Search**

* **Text search:** Metadata (filename, date, location if available)  
* **Object search:** "dog", "car", "food" (via ML tags)  
* **Face search:** "Show me photos of Mom"  
* **Date search:** "Photos from July 2024"  
* **Combination:** "Dog at beach in summer"

**2.2.5 Albums**

* **Shared albums:** Multiple family members can add/remove photos  
* **Privacy:** Albums are private by default, explicit sharing required  
* **Collaboration:** Real-time sync (one person adds photo, others see it instantly)  
* **Example albums:** "Summer Holiday 2025", "Mia's Birthday", "House Renovation"

**2.2.6 Media Management**

* **Duplicate detection:** Immich detects and flags duplicates (perceptual hashing)  
* **Favorites:** Star important photos (synced across devices)  
* **Archive:** Hide photos from main timeline without deleting  
* **Trash:** 30-day soft delete (recoverable), then permanent deletion

---

**Feature 3: Memu Intelligence (The Brain)**

**Definition:**  
 Memu Intelligence is NOT a chatbot. It is a **Local LLM Service** that powers specific utility features. It runs **strictly offline**.

**Technology Stack:**

* **Engine:** Ollama (local LLM server)  
* **Model:** Llama 3.2 3B Instruct (quantized to 4-bit, \~2GB RAM)  
  * **Why Llama 3.2 3B:** Fast enough on Pi 5, good instruction following, small footprint  
  * **Alternative:** Phi-3 Mini (3.8B) if better performance needed  
* **Context:** 8K token context window  
* **RAG (Retrieval):** ChromaDB (vector database for household notes/documents)

**Use Cases:**

**2.3.1 Smart Task Extraction**

**Input:** User types in Chat:  
 "We need to buy milk and book the dentist."

**Process:**

1. Message sent to Synapse (normal chat message)  
2. Memu Intelligence monitors new messages (via Matrix webhook)  
3. LLM prompt:

   Extract actionable tasks from: "We need to buy milk and book the dentist."

   Return JSON: \[{"task": "...", "category": "..."}\]

4. LLM response:

json

\ \ \
   \[

 	{"task": "Buy milk", "category": "Shopping"},

 	{"task": "Book dentist appointment", "category": "Health"}

   \]
\ \ \

5. Tasks written to Tasks database

**Output:** 

Tasks app shows:

- [  ] Buy milk (Shopping)

- [  ] Book dentist appointment (Health)

 
**User sees:** Bot reply in chat: "✅ Added 2 tasks to your list"

---

**2.3.2 Natural Query (Household Knowledge)**

**Input:** User asks in Chat: 

\`"What is the WiFi password for the guest network?"\`

**Process:**

1. Memu Intelligence searches RAG database (ChromaDB)

2. Finds document: "Kitchen Note: Guest WiFi \= GuestHouse2025"

3. LLM generates response using retrieved context
 

**Output:** 

Bot replies: \*"Your guest WiFi password is 'GuestHouse2025' (from your Kitchen note)."\*

---

**2.3.3 Photo Search Enhancement**

**Input:** User types in Memories search: 

\`"Photos of the kids at the beach last summer"\`

 

**Process:**

1. LLM parses intent:

   - Objects: \["kids", "beach"\]

   - Time: \["summer 2024"\]

2. Converts to Immich search query:

\`\`\`

   objects:beach AND date:2024-06-01..2024-08-31

\`\`\`

**Output:** Returns matching photos

---

**2.3.4 Constraints & Limits**

- **No internet access:** LLM cannot browse web, only local data

- **No personal data training:** Model is frozen, never fine-tuned on user data

- **Rate limiting:** Max 10 queries/minute per user (prevent abuse/overheating)

- **Thermal protection:** If Pi temp \>75°C, Intelligence service pauses

- **Context limit:** 8K tokens (\~6,000 words of context)

---

## 3. System Architecture: "Memu OS"

Memu OS transforms a Raspberry Pi into a consumer appliance, not a Linux server.

### 3.1 The Boot Process

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

 

5. **Health Check (40-50 seconds)**

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

### 3.2 The File System Hierarchy

**READ-ONLY (Immutable OS):**

\`\`\`

/boot       	→ Bootloader, kernel, device tree

/Memu/system 	→ OS code (Git repo, never edited by user)

  ├── docker-compose.yml

  ├── nginx.conf

  ├── update.sh

  └── version.txt

\`\`\`

**READ-WRITE (User Data - THE HOLY GRAIL):**

\`\`\`

/Memu/data   	→ ALL user data lives here

  ├── postgres/     	→ Database files

  ├── media/        	→ Photos, videos (Immich storage)

  │   ├── upload/   	→ Original files

  │   ├── thumbs/   	→ Thumbnails

  │   └── encoded/  	→ Transcoded videos

  ├── synapse/      	→ Matrix homeserver data

  │   ├── media\_store/  → Chat attachments

  │   └── homeserver.db → (if using SQLite, but we use Postgres)

  ├── config/       	→ User preferences

  │   ├── users.json	→ Family member accounts

  │   └── wifi.json 	→ Known SSIDs for auto-sync

  └── ollama/       	→ LLM models

  	└── models/   	→ Downloaded Llama/Phi models

\`\`\`


**Why this matters:**

- **Backup:** Only \`/Memu/data\` needs bacMemug up (everything else is reproducible)

- **Updates:** Pull new \`/Memu/system\` from Git, restart containers (data untouched)

- **Recovery:** If OS corrupts, flash new SD card, mount NVMe at \`/Memu/data\`, data intact


---

 

### 3.3 NetworMemug Architecture

**Local Network (Primary):**

\`\`\`

Device → WiFi/Ethernet → Router → Pi (192.168.1.x)

Access via: http:*//Memu.local:8080*

\`\`\`


**Remote Access (Optional):**

\`\`\`

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

---

**3.4 Update Mechanism**

**Philosophy:** GitOps - the Pi is always trying to match the Git repo state.

**Process:**

1. User taps "Update Hub" in mobile app  
2. App sends API call: POST /api/system/update  
3. Memu Supervisor runs:

bash

   cd /Memu/system

   git fetch origin

   git reset --hard origin/main

   docker-compose pull

   docker-compose up -d --build

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

\`\`\`

**Why containers:**

- Isolation (services don't conflict)

- Updates (pull new image, restart)

- Portability (same setup on any Pi)

- Rollback (keep old images for 30 days)

---

 

## 4. The "No-Terminal" Guarantee*

 

**The Golden Rule:** If a user has to open a terminal, we have failed.

 

### 4.1 Initial Setup*


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

### 4.2 Updates*

**Via mobile app:**

- Tap Settings → Hub Status → "Update Available" badge

- Tap "Update Now"

- Progress bar shows: Downloading → Installing → Restarting

- Notification: "Hub updated successfully\!"

**No terminal, no SSH, no commands.**

---

### 4.3 Troubleshooting*

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

 

## 5. Data & Privacy*

### 5.1 Trust Model

**Open Core:**

- All source code: AGPLv3 (on GitHub)

- Users can audit every line of code

- Community contributions welcome

- No proprietary blobs (except Pi firmware)


**No Telemetry:**

- Hub does NOT phone home (except update checks)

- Update checks: Anonymous (no user ID sent)

- Crash reports: Opt-in only (user explicitly enables)

- Analytics: Zero. We track nothing.

---

### 5.2 Data Ownership*

**User owns:**

- All photos, videos, messages

- All ML models (downloaded, not cloud-based)

- All metadata (who, when, where)

**User controls:**

- Who has access (family members only)

- Where data lives (their home)

- When to delete (no retention policies)

**Data portability:**

- "Export All Data" button in web UI

- Downloads ZIP file:

  - \`/photos\` → All original photos/videos

  - \`/messages.json\` → Matrix chat export

  - \`/tasks.json\` → Tasks database export

- User can move data to another Memu Hub or different system

---

### 5.3 Encryption*

**At rest:**

- NVMe SSD: LUKS full-disk encryption (optional, Phase 2\)

- Database: PostgreSQL with encryption extensions (optional)

**In transit:**

- Local network: HTTP (low risk, trusted network)

- Remote access: HTTPS via Cloudflare tunnel (TLS 1.3)

- Matrix: E2EE for message content (Olm/Megolm)

- Photo sync: HTTPS (TLS 1.3)

**Keys:**

- Matrix E2EE keys: Stored on user devices (Secure Storage)

- Disk encryption keys: User-set passphrase (not recoverable if lost)

- TLS certificates: Auto-renewed by Cloudflare or Let's Encrypt

---

## 6. Hardware Specifications*

### 6.1 Memu Hub (Raspberry Pi 5 Configuration)*

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
### 6.2 Performance Targets*

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

 

## 7. Development Roadmap*

### Phase 1: MVP (Months 1-3) ✅ IN PROGRESS*

**Goal:** Prove core product works for one family.

**Features:**

- ✅ Memu Chat (Matrix \+ E2EE)
- [ ] Remote access (Cloudflare tunnel integration)

- [ ] Memu Memories (Immich photo backup \+ search)

- [ ] Memu Intelligence (basic task extraction only)

- [ ] Setup wizard (web-based)

- [ ] Mobile app (chat \+ photos)

**Hardware:** Raspberry Pi 5 \+ NVMe
**Users:** Me \+ wife (validation test)

---
 
### Phase 2: Beta (Months 4-6)*

**Goal:** 20 families using it daily.

**Features:**

- ✅ All Phase 1 features (hardened)

- Tasks app (shared to-dos, shopping lists)

- Push notifications (UnifiedPush \+ APNS)

- Shared albums


**Hardware:** Same (Pi 5 \+ NVMe)
**Users:** 20 beta families
---

### Phase 3: Launch (Months 7-12)*

**Goal:** 100 paying customers.

**Features:**

- Auto-updates (GitOps)

- Backup to external USB drive

- Family calendar (shared events)

- Bluetooth diagnostics (LED status)

- Web admin panel (service management)

**Hardware:** Productized (custom case, logo, packaging)
**Users:** 100 paying customers

**Business model:** $149 hardware \+ $6/mo relay (optional)

---

### Phase 4: Scale (Year 2\)*

**Goal:** 1,000 customers, profitable.

**Features:**

- Document storage (Nextcloud integration)

- Home automation (MQTT bridge to smart devices)

- Media server (Jellyfin for movies/music)

- Multi-hub federation (families connect across hubs)

**Hardware:** Pi 5 or Pi 6 (when available)

---

## 8. Non-Goals (Out of Scope)*

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

## 9. Success Metrics*

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

 

## 10. Open Questions & Decisions Needed*


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

 

## 11. Appendix: Technical Specifications*

### 11.1 API Endpoints (Internal)*

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

 

### 11.2 Database Schema (Simplified)*

 

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

 

### 11.3 Mobile App Architecture*

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

**12. The One-Page Summary (For Investors/Partners)**

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