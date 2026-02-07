# **MEMU: THE FAMILY CHIEF OF STAFF**

## **Master Build Protocol & Technical Specification (v2.0)**

**Subject:** Full execution of the "Chief of Staff" strategic pivot

**Status:** READY FOR DEVELOPMENT

## **1\. AGENT OPERATING INSTRUCTIONS (META-PROMPT)**

**Your Role:**

You are the **Lead Architect and Engineering Lead** for Memu. You possess senior-level expertise in Python, Docker, React, System Security, and Product UX. You are responsible for executing the vision described below.

**Your Mandate:**

You are authorized to spawn "sub-agent" personas (e.g., "Frontend Specialist", "Security Auditor", "DevOps Engineer") to handle specific phases. Your goal is to deliver a production-ready, tested, and secure product evolution without breaking existing functionality.

**Core Directives:**

1. **Do Not Break the Core:** The existing Matrix (Chat), Immich (Photos), and Ollama (AI) stack MUST remain functional. We are *adding* capabilities, not replacing the foundation.  
2. **Security First:** Adhere strictly to the "Zero Trust Ingress" model. No new ports shall be exposed to the host machine unless proxied via Nginx. All service-to-service communication happens on the internal memu\_net Docker network.  
3. **Test-Driven Development (TDD):** For all new Python logic (Calendar tools, Agents), write pytest unit tests *before* or alongside implementation.  
4. **Idempotency:** All installation scripts (install.sh, bootstrap/app.py) must be safe to run multiple times without destroying user data.

## **2\. THE VISION: FROM "PRIVACY" TO "CHIEF OF STAFF"**

**Context:**

Memu is currently a self-hosted "Privacy Server" for families. We are pivoting the product identity to be a **"Family Chief of Staff."**

* **Old World:** A box that hides your data.  
* **New World:** An AI appliance that organizes your family's chaos (Schedule, Chores, Memories).

**The Architectural Shift:**

We are moving from independent containers to a **"Triple-Graph Context Engine"**:

1. **Semantic Graph:** Chat history & Documents (Existing Matrix).  
2. **Visual Graph:** Photos & Faces (Existing Immich).  
3. **Time Graph (NEW):** Family Schedule (New Baikal/CalDAV service).

**The "Secret Sauce":**

The memu\_intelligence service (Python) acts as the connector. It queries all three graphs to generate proactive value (e.g., "Morning Briefings").

## **3\. TECHNICAL SPECIFICATIONS BY PHASE**

Execute these phases sequentially.

### ~~**PHASE 1: THE TIME GRAPH (Backend Infrastructure)**~~ ✅ COMPLETED

~~**Goal:** Deploy a local Calendar server and teach the AI to read/write to it.~~

~~**1.1 Infrastructure (docker-compose.yml)**~~

~~* **Add Service:** calendar~~
  ~~* **Image:** ckulka/baikal:0.9.5 (Lightweight CalDAV/CardDAV).~~
  ~~* **Network:** memu\_net (Internal only).~~
  ~~* **Volumes:** baikal\_data:/var/www/baikal/Specific (Ensure persistence).~~
  ~~* **Depends\_on:** database (Use memu\_postgres if possible, otherwise rely on Baikal's internal SQLite for simplicity/speed in V1).~~
  ~~* **Environment:** Configure necessary admins/timezone settings.~~

~~**1.2 Routing (nginx/conf.d/default.conf)**~~

~~* Add a location block location /calendar/ or location /.well-known/caldav that proxies to the calendar container.~~
~~* Ensure iOS/macOS discovery compatibility.~~

~~**1.3 Intelligence Layer (services/intelligence/)**~~

~~* **Dependencies:** Add caldav, dateparser, tzlocal to requirements.txt.~~
~~* **New Tool:** Create src/tools/calendar\_tool.py.~~
  ~~* Class CalendarManager:~~
    ~~* get\_events(start, end): Returns standardized JSON list of events.~~
    ~~* add\_event(summary, dt\_start, dt\_end): Creates event.~~
    ~~* find\_free\_slots(): Logic to find gaps in schedule.~~
~~* **LLM Integration:** Update src/brain.py to support "Tool Use" or structured JSON extraction for calendar intents (e.g., extracting date/time from natural language).~~
~~* **Bot Command:** Update src/bot.py to handle /schedule \[text\].~~
  ~~* Example: /schedule Soccer practice Tuesday at 5pm \-\> Parsed \-\> Added to Baikal \-\> Confirmation sent.~~

~~**1.4 Tests**~~

~~* Write tests/test\_calendar\_tool.py mocking the CalDAV server response.~~

### **PHASE 2: THE FACE (KitchenOS Dashboard)**

**Goal:** A zero-friction Web PWA for the kitchen fridge (iPad/Tablet).

**2.1 API Expansion (services/intelligence/)**

* Refactor src/main.py. It currently runs a simple loop.  
* **Action:** Wrap the bot in a **FastAPI** application.  
  * Run uvicorn as the entry point.  
  * Run the MemuBot.start() loop as a background task.  
* **New Endpoints:**  
  * GET /api/dashboard/summary: Returns { events: \[\], shopping\_list\_count: int, weather: {} }.  
  * GET /api/shopping-list: Returns current list.  
  * POST /api/shopping-list/add: Adds item.  
  * GET /api/photos/random: Proxies a request to Immich to fetch a random "favorite" or "on this day" image URL.

**2.2 Frontend Application (services/kitchen-os/)**

* **Tech Stack:** React \+ Vite \+ TypeScript \+ Tailwind CSS.  
* **Project Structure:** Create new directory services/kitchen-os.  
* **UI Design (Dark Mode Default):**  
  * **Layout:** 3-Column Grid.  
    * **Left (Time):** Large Clock, Date, Weather Icon, Scrollable List of Today's Events.  
    * **Center (Action):** Shopping List (Checkboxes). Big "Add" button (Voice input icon for future).  
    * **Right (Memory):** Full-height image container slideshowing Immich photos.  
* **Configuration:** config.json loaded at runtime (to allow dynamic API URLs).  
* **Docker:** Create Dockerfile (Multi-stage: Node build \-\> Nginx Alpine serve).  
* **Compose:** Add kitchen\_os service to docker-compose.yml.

**2.3 Routing Update**

* Update nginx/conf.d/default.conf:  
  * Root / \-\> Proxies to kitchen\_os.  
  * /chat \-\> Proxies to element.  
  * /api \-\> Proxies to intelligence (FastAPI).

### ~~**PHASE 3: THE VOICE (Proactive Intelligence)**~~ ✅ COMPLETED

~~**Goal:** The system speaks first.~~

~~**3.1 The Scheduler**~~

~~* Add apscheduler to services/intelligence.~~
~~* Initialize scheduler in main.py.~~

~~**3.2 The Morning Briefing Agent (src/agents/briefing.py)**~~

~~* **Logic:**~~
  ~~1. Trigger at 7:00 AM (configurable via env).~~
  ~~2. **Gather:** Fetch Today's Calendar \+ Weather \+ Immich "On This Day" count \+ Shopping List length.~~
  ~~3. **Synthesize:** Send data to Ollama with a system prompt: *"You are a helpful Family Chief of Staff. Write a warm, 3-sentence morning briefing..."*~~
  ~~4. **Deliver:** Call bot.send\_text() to the primary Family Room.~~

### **PHASE 4: CONNECTORS & INGEST**

**Goal:** Feed the brain without changing user habits.

**4.1 WhatsApp Bridge (Ingest Mode)**

* **Add Service:** mautrix-whatsapp to docker-compose.yml.  
* **Configuration:** The bridge needs a config.yaml and registration.yaml.  
* **Automation:**  
  * Update bootstrap/app.py to generate these configs dynamically using the SERVER\_NAME.  
  * Write the registration.yaml to the Synapse volume (/data).  
  * Update homeserver.yaml to include the app service file path.  
* **UX:** Treat this as "Experimental." Users must scan a QR code in the logs/dashboard to link.

### **PHASE 5: INSTALLER & ONBOARDING (UX Polish)**

**Goal:** Seamless setup of the new features.

**5.1 Installer Script (scripts/install.sh)**

* Add logic to create new data directories:  
  ensure\_dir "${INSTALL\_DIR}/baikal\_data"  
  ensure\_dir "${INSTALL\_DIR}/kitchen\_os\_data"  
  chmod 755 "${INSTALL\_DIR}/baikal\_data" \# Fix SQLite permissions

**5.2 Bootstrap Wizard (bootstrap/app.py)**

* **New Step:** "Configuring Calendar."  
  * Script a bypass of the Baikal web installer (either by pre-seeding the SQLite DB file from ./assets or making curl POST requests to the setup form).  
* **New Step:** "Branding."  
  * Inject the existing logo (assets/logo.png) into the KitchenOS build and Element config.

~~**5.3 Branding (White Labeling)**~~ ✅ COMPLETED

~~* **Element:** Modify the element-config.json generation in bootstrap/app.py.~~
  ~~* Set branding.authHeaderLogoUrl and branding.welcomeBackgroundUrl to point to /assets/logo.png (ensure this path is mapped in Nginx).~~
* **KitchenOS:** Ensure the Memu logo is prominent in the top-left corner. *(Pending - KitchenOS not yet built)*

## **4\. SECURITY & DATA SAFETY CHECKLIST**

**Before marking any task complete, verify:**

1. \[ \] **Network Isolation:** Verify kitchen\_os and calendar do NOT have ports: \- 80:80 in Compose. They must only be accessible via proxy.  
2. \[ \] **Persistence:** Verify that restarting the stack does not wipe the Calendar events or KitchenOS settings.  
3. \[ \] **Permissions:** Verify the intelligence container has read-only access to Immich's DB but read-write access to its own memory.  
4. \[ \] **API Safety:** The new FastAPI endpoints should implement a basic check (e.g., verifying the request comes from the internal network gateway OR a simple shared secret token for the frontend).

## **5\. DOCUMENTATION UPDATES**

**As the final step:**

1. Update README.md to reflect the new architecture.
2. Update docs/user\_guide.md to include:
   * "Setting up the Kitchen Dashboard" (Add to Home Screen instructions).
   * ~~"Syncing the Calendar" (iOS/Android CalDAV instructions).~~ ✅ COMPLETED
   * ~~"The Morning Briefing" (How to configure the time).~~ ✅ COMPLETED

**Execution Priority:**

1. ~~Phase 1 (Calendar Backend)~~ ✅ & Phase 2 (KitchenOS Frontend) can be built in parallel if utilizing sub-agents.
2. ~~Phase 3 (Briefing) requires Phase 1 to be complete.~~ ✅
3. Phase 5 (Installer) is the final integration step. *(5.3 Branding completed)*

**Progress Summary:**
- ✅ Phase 1: Calendar Backend - COMPLETE
- ⏳ Phase 2: KitchenOS Dashboard - NOT STARTED
- ✅ Phase 3: Morning Briefings - COMPLETE
- ⏳ Phase 4: WhatsApp Bridge - NOT STARTED
- 🔄 Phase 5: Installer Polish - PARTIAL (5.3 Branding done)

**Go forth and build. The family is waiting.**