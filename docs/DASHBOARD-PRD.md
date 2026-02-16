# Memu Dashboard — Product Requirements Document

**Status:** Pre-Kickstarter Priority
**Last Updated:** February 2026

---

## 1. What and Why

### The Problem

Memu's intelligence is trapped inside a chat interface. To interact with your family's Chief of Staff, you open a Matrix app and type commands. This is invisible — there's nothing to photograph, nothing to put on a kitchen counter, nothing to demo in 60 seconds.

### The Solution

A **touchscreen-optimised web dashboard** that gives Memu a face. It runs on a tablet (wall-mounted or counter-top) and surfaces the family's day at a glance: schedule, weather, shopping list, photo memories, and system health.

### Why Before Kickstarter

The dashboard IS the Kickstarter hero image. It makes Memu visible, photographable, and demeable. Without it, you're selling "install Docker and type commands." With it, you're selling a family appliance.

---

## 2. Design Principles

1. **Glanceable:** Information visible from 3 metres away. No interaction needed for the basics.
2. **Touch-first:** Big tap targets, swipe gestures, no hover states. Designed for kitchen hands.
3. **Memu brand:** Uses the Memu design system (purple accent gradient, system fonts). Not a separate product — this is Memu's face.
4. **Ambient:** Shifts context by time of day. Morning = logistics. Evening = memories.
5. **Local-first:** All data comes from local services. No external API calls from the frontend. Dashboard talks to the Memu API Gateway, which talks to existing services.

---

## 3. MVP Screens (5)

### Screen 1: Home

**Purpose:** The default idle state. Ambiently shows what matters right now.

**Layout:**
- **Top bar:** Weather (left), time (centre), system pulse indicator (right)
- **Context carousel (top 35%):** Swipeable tiles showing the most relevant context
- **Unified timeline (bottom 65%):** Vertical scroll of today's events, memories, and updates

**Morning mode:** Carousel shows weather + next event + commute context
**Evening mode:** Carousel shows "On This Day" photo memories + tomorrow's first event

**Key interactions:**
- Swipe carousel horizontally
- Tap system pulse to open Node Status
- Tap any event to expand details
- Tap any photo memory to open Memory Detail

### Screen 2: The Pantry (Shopping List)

**Purpose:** The family shopping list with voice input.

**Layout:**
- **Voice input bar (bottom):** "Tap to add items" — uses local Whisper for speech-to-text
- **Recently added (top):** Horizontal scroll of items just added via chat or voice
- **Categorised list (main):** Items grouped by category (Produce, Dairy, Pantry Staples, etc.) with checkboxes
- **Live sync indicator:** Shows when items are added from chat in real-time

**Key interactions:**
- Tap checkbox to mark item done (syncs to bot's `/done` command)
- Tap voice bar to add items by voice
- Swipe item left to delete
- Items added via chat appear instantly (WebSocket)

### Screen 3: Logistics Command (Calendar)

**Purpose:** The Chief of Staff view. Dense, functional calendar with AI conflict detection.

**Layout:**
- **Conflict console (top):** Red-bordered alert when events overlap, with action buttons (e.g., "Reschedule", "Delegate")
- **Day view (main):** Vertical time grid with event blocks
- **AI ghost events:** Translucent blocks showing AI suggestions (drive time estimates, suggested gaps)

**Key interactions:**
- Tap event to expand/edit
- Tap conflict action button to resolve
- Swipe between days
- Long-press empty slot to create event (dispatches to bot's `/schedule`)

### Screen 4: Node Status

**Purpose:** Reassurance. Proves the hardware is working and privacy is intact.

**Layout:**
- **Storage gauge:** Circular SVG showing used/free space
- **Service status:** Traffic-light indicators for each service (Chat, Photos, AI, Calendar)
- **System stats:** CPU, memory, temperature
- **Activity log:** Terminal-style scrolling log of recent activity

**States (traffic-light model):**
- **Green:** "Everything running perfectly. 47 days uptime. 23% storage used."
- **Amber:** "Storage filling up (82%). Cleaned up 3GB automatically."
- **Red:** "Photos service is down. [Restart Photos]"

### Screen 5: Memory Detail

**Purpose:** Full-screen photo view with contextual recall from chat history.

**Layout:**
- **Photo (full screen):** High-res image, letterboxed on dark background
- **Metadata badge (top-left):** Filename, device, file size
- **Context drawer (bottom sheet, peeking):** "Contextual Recall" — shows chat messages from the same day the photo was taken

**Key interactions:**
- Drag drawer up to see full chat context from that day
- Double-tap to zoom
- Swipe left/right for next/previous memory

---

## 4. Deferred Screens (Post-Kickstarter)

These were explored in design mockups but are not MVP:

| Screen | Why Deferred |
|--------|-------------|
| **Recipe Explorer** | Requires recipe database integration not yet built |
| **Hands-free Cooking** | Requires always-on voice (wake word), not yet built |
| **AI Persona & Voice** | TTS personality is nice-to-have, not core value |
| **Recipes & Pantry Sync** | Interesting cross-feature but adds scope |

---

## 5. New Infrastructure Required

### Memu API Gateway

A new FastAPI service that decouples the bot's brain from the Matrix transport layer. The dashboard needs real-time data without going through Matrix.

```
Dashboard (Browser)
    | HTTP + WebSocket
Memu API Gateway (FastAPI)
    | Internal calls
Existing services (Bot brain, Ollama, PostgreSQL, Immich, Baikal)
```

**Endpoints needed for MVP:**

| Endpoint | Method | Data Source |
|----------|--------|-------------|
| `/api/dashboard/home` | GET | Weather, next events, photo memories |
| `/api/dashboard/shopping` | GET/POST/DELETE | Shopping list (PostgreSQL) |
| `/api/dashboard/calendar` | GET | Today's/week's events (Baikal) |
| `/api/dashboard/calendar/conflicts` | GET | AI-detected conflicts |
| `/api/dashboard/status` | GET | Container health, disk, CPU, memory |
| `/api/dashboard/memories` | GET | On This Day photos (Immich) |
| `/api/dashboard/memory/{id}` | GET | Photo + contextual chat recall |
| `/ws/dashboard` | WebSocket | Real-time updates (new list items, events, status changes) |

### Voice I/O (Pantry screen only for MVP)

- **Input:** Whisper (local, running on the server) for speech-to-text
- **Output:** Piper TTS (local) for spoken confirmations — deferred to post-MVP
- Push-to-talk model for MVP (no wake word)

### Web Frontend

- **Stack:** React (or Preact for size) + Tailwind CSS
- **Mode:** Kiosk-optimised (full-screen, no browser chrome)
- **Responsive:** Primary target is tablet (portrait, 9-11"). Works on phone and desktop.
- **Served by:** Nginx (same proxy that serves Cinny), new location block `/dashboard/`

---

## 6. Design System

The dashboard uses the **Memu brand** design system, adapted for ambient/touch use:

| Token | Value | Usage |
|-------|-------|-------|
| Primary gradient | `#667eea` to `#764ba2` | Active states, accent bars, CTAs |
| Background | `#1A1C20` | Dark mode base |
| Surface | `#25282E` | Cards, panels |
| Text | `#EAE6D8` | Primary readable text |
| Muted | `#737985` | Timestamps, secondary info |
| Success | `#3B8D65` | System healthy, items done |
| Alert | `#CD5D4F` | Conflicts, service down |
| Font - Display | System font stack (Segoe UI, SF Pro, etc.) | Headings, large numbers |
| Font - Body | System font stack | Readable body text |
| Font - Data | `monospace` | Timestamps, stats, logs |
| Border radius | `4px` | Tight, clean corners |

> **Note:** The Stitch mockups used "Brushed Brass" (`#D4AF37`) as the primary accent and Google Fonts (Space Grotesk, Newsreader, JetBrains Mono). The production dashboard uses Memu's purple gradient and system fonts per the brand guidelines.

---

## 7. Build Plan

### Phase A: API Gateway (2 sessions)

1. New FastAPI service in `services/api-gateway/`
2. Docker container on `memu_net`, no external ports
3. Nginx proxy at `/api/dashboard/` and `/ws/dashboard`
4. Endpoints: home data, shopping list CRUD, calendar read, system status
5. WebSocket for real-time updates

### Phase B: Home + Node Status screens (2 sessions)

1. Frontend scaffold (React/Preact + Tailwind)
2. Home screen with context carousel and unified timeline
3. Node Status with storage gauge and service health
4. Nginx location block for `/dashboard/`
5. Kiosk mode CSS (full-screen, no-scroll body)

### Phase C: Pantry + Logistics screens (2 sessions)

1. Shopping list with categories and checkboxes
2. Real-time sync via WebSocket
3. Calendar day view with event blocks
4. Conflict detection display

### Phase D: Memory Detail + Voice (2 sessions)

1. Full-screen photo view with context drawer
2. Contextual recall (chat messages from photo date)
3. Whisper integration for voice-add to shopping list
4. Push-to-talk UI on Pantry screen

### Total estimate: 8 evening sessions

---

## 8. Docker Architecture

```yaml
# New service in docker-compose.yml
memu_api_gateway:
  build: ./services/api-gateway
  container_name: memu_api_gateway
  restart: unless-stopped
  networks:
    - memu_net
  environment:
    - DATABASE_URL=postgresql://...
    - OLLAMA_URL=http://brain:11434
    - CALDAV_URL=http://calendar/dav.php
    - IMMICH_URL=http://photos:3001
  depends_on:
    - postgres
    - brain
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3

# New frontend in docker-compose.yml
memu_dashboard:
  build: ./services/dashboard
  container_name: memu_dashboard
  restart: unless-stopped
  networks:
    - memu_net
  # Static files served by nginx, no direct port exposure
```

Nginx addition:
```nginx
location /dashboard/ {
    proxy_pass http://dashboard:80/;
    proxy_set_header Host $host;
}

location /api/dashboard/ {
    proxy_pass http://api-gateway:8000/;
    proxy_set_header Host $host;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

---

## 9. Success Criteria

| Metric | Target |
|--------|--------|
| First meaningful paint | < 2 seconds on local network |
| Touch response | < 100ms feedback |
| Kiosk uptime | Runs 24/7 without browser crash for 7+ days |
| Family adoption | Non-technical spouse uses it without prompting |
| Demo video | Dashboard is the hero shot in 60-second video |
| Kickstarter | "I want that" reaction from page visitors |

---

## 10. What This Enables

The API Gateway built for the dashboard unlocks future capabilities:
- **Mobile app** (React Native or PWA) reusing the same API
- **Voice assistant** (always-on wake word, post-Kickstarter)
- **Third-party integrations** (Home Assistant, etc.)
- **Guardian bot commands** via API instead of Matrix-only

The dashboard isn't just a screen. It's Memu's public face and the API layer that makes everything else possible.

---

*The dashboard makes Memu real. It turns "I installed Docker" into "Look at my family's command centre."*
