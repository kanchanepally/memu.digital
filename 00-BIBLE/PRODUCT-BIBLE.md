# Hearth Product Bible - AI Agent Instructions

> **This document is the single source of truth for all Hearth development.**

## TODO

# Hearth Product Bible
## AI Agent Development Instructions v1.0

> **This document is the single source of truth for all Hearth development decisions.**  
> If this document says it, build it. If it doesn't say it, don't build it.

---

# PART 1: PRODUCT VISION & POSITIONING

## The Core Thesis

**AWS went down. Signal stopped working. Families on Hearth kept chatting.**

That's the entire positioning. We're not building "another messaging app." We're building **personal digital infrastructure** that families own, like they own their WiFi router.

## What We're Building (Two Products, Same Core)

### Hearth Family (Build First - 90 Days)
**For**: Households (2-6 people)  
**Replaces**: WhatsApp + Google Photos + Shared Notes  
**Value Prop**: "Works even when Big Tech goes down"

**Three Features Only**:
1. **Messages** - Private family chat
2. **Photos** - Shared family gallery
3. **Tasks/Plans** - AI-powered memory and to-do lists

### Hearth Schools (Build Later - After Family Proven)
**For**: UK/EU primary schools (50-300 families)  
**Replaces**: ClassDojo, Seesaw (without the data harvesting)  
**Value Prop**: "Strategic autonomy - student data stays in Britain"

**Different Features** (TBD after teacher research):
- Teacher-parent communication (not just messaging)
- Learning documentation (not just photos)
- Pedagogy-informed design (not behavioral manipulation)

## Positioning Framework

### Before AWS Outage
❌ "Private alternative to WhatsApp"  
❌ "Self-hosted family chat"  
❌ "Own your data"

### After AWS Outage (Current)
✅ **"The family chat that works when Big Tech doesn't"**  
✅ **"Personal infrastructure as essential as your WiFi router"**  
✅ **"£299 one-time. Yours forever. No AWS. No subscriptions."**

## Competitive Positioning

| Competitor | Their Weakness | Our Advantage |
|------------|----------------|---------------|
| **WhatsApp** | AWS-dependent, metadata harvesting | Self-hosted, zero cloud dependency |
| **Signal** | Centralized US servers, AWS outage vulnerable | Distributed, works offline on local network |
| **Element** | Too technical, poor UX, focused on governments | Consumer-first, beautiful UX, family-focused |
| **Telegram** | Russian servers, sketchy encryption | UK-based, proven Matrix E2EE, full sovereignty |
| **Google Photos** | Scans all photos for ads | Zero scanning, zero corporate access |

## The Element Problem (And Our Opportunity)

**Element's failures** (documented in user reviews):
- Confusing onboarding ("What's a homeserver?")
- Technical terminology everywhere
- Clunky UI/UX (feels like IRC, not WhatsApp)
- Built for tech people, not families
- Government/enterprise focus killed consumer experience

**Our solution**:
- Never mention "homeserver" or "Matrix" to users
- Onboarding: Scan QR code on your Pi. Done.
- UI: Looks and feels like WhatsApp (familiar = good)
- Built for your mum, not developers
- Consumer obsession from day 1

---

# PART 2: TECHNICAL ARCHITECTURE

## System Overview

```
┌─────────────────────────────────────────────┐
│         Hearth Mobile App (iOS/Android)     │
│         - React Native                      │
│         - Custom UI (NOT Element)           │
│         - Matrix SDK underneath             │
└─────────────┬───────────────────────────────┘
              │
              │ Matrix Protocol (E2EE)
              │
┌─────────────▼───────────────────────────────┐
│         Raspberry Pi 5 (User's Home)        │
│  ┌─────────────────────────────────────┐   │
│  │  Synapse (Matrix Server)            │   │
│  │  PostgreSQL (Data Storage)          │   │
│  │  Hearth Services (Photos/Tasks/AI)  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Core Technology Stack

### Backend (Raspberry Pi)
- **OS**: Raspberry Pi OS Lite (64-bit, Bookworm)
- **Container Engine**: Docker Compose
- **Matrix Server**: Synapse (latest stable)
- **Database**: PostgreSQL 15
- **Reverse Proxy**: Caddy 2 (auto-HTTPS)
- **AI**: Ollama with Phi-3-mini (Week 2+)
- **Language**: Python 3.11 for services

### Mobile App (Custom - NOT Element)
- **Framework**: React Native (latest stable)
- **Matrix SDK**: matrix-js-sdk
- **State Management**: Zustand (simple, not Redux)
- **UI Library**: React Native Paper (Material Design)
- **Navigation**: React Navigation 6
- **Image Handling**: react-native-image-picker + react-native-fast-image
- **Local Storage**: @react-native-async-storage/async-storage
- **Network**: Axios for REST, Matrix SDK for real-time

### Design System
- **Inspiration**: WhatsApp (familiar), Signal (clean), Telegram (fluid)
- **NOT Element**: Avoid their UX mistakes entirely
- **Colors**: Warm, inviting (not corporate blue)
- **Typography**: SF Pro (iOS), Roboto (Android)
- **Animations**: Smooth, 60fps, delightful micro-interactions

## Key Architectural Principles

### 1. Zero Cloud Dependency
```
❌ NO: AWS, Google Cloud, Azure, Cloudflare Workers
✅ YES: User's Pi, user's network, user's control
⚠️ MAYBE: Cloudflare Tunnel (for remote access only, not data storage)
```

### 2. Offline-First Design
```
The app MUST work when:
- Pi is offline (queued messages)
- Phone is offline (cached data)
- Internet is down (local network still works)
```

### 3. Appliance-Like Simplicity
```
Setup flow (total time: 5 minutes):
1. Plug in Pi
2. Open Hearth app
3. Scan QR code from Pi
4. Done
```

No "homeserver" configuration. No server URLs. No technical jargon.

### 4. Privacy by Architecture
```
User data paths:
✅ Phone → Local WiFi → Pi (encrypted)
✅ Pi → User's chosen backup (encrypted)
❌ NEVER: Phone → Our servers → Pi
❌ NEVER: Any telemetry without explicit opt-in
```

---

# PART 3: MOBILE APP SPECIFICATIONS

## Design Philosophy

**Golden Rule**: If your mum can't use it without asking for help, it's broken.

### UX Principles
1. **Familiar > Novel**: Copy WhatsApp's UX patterns (they're proven)
2. **Zero Config**: No settings needed for 95% of users
3. **Fast**: Every action completes in <300ms or shows progress
4. **Forgiving**: Easy undo, clear error messages, never lose data
5. **Beautiful**: Not corporate, not techy, warm and human

## App Structure

### Bottom Navigation (4 Tabs)

```
┌─────────────────────────────────────────────┐
│  [💬 Chats]  [📸 Photos]  [✓ Tasks]  [⚙️]  │
└─────────────────────────────────────────────┘
```

**DO NOT** call it "Rooms" or "Spaces" (Element mistake)  
**DO** call it "Chats" (familiar from WhatsApp)

### Tab 1: Chats

**Home Screen**:
```
┌─────────────────────────────────────────────┐
│  Hearth                               [+]   │
├─────────────────────────────────────────────┤
│  👤  Mum                           2m ago   │
│      ✓✓ Thanks for picking up mi...        │
├─────────────────────────────────────────────┤
│  👨‍👩‍👧‍👦  Family                      1h ago   │
│      Dad: I'll be home at 6pm              │
├─────────────────────────────────────────────┤
│  👤  Dad                          Yesterday │
│      Can you grab milk?                    │
└─────────────────────────────────────────────┘
```

**Chat Screen** (Copy WhatsApp exactly):
```
┌─────────────────────────────────────────────┐
│  ← Mum                              [⋮]    │
├─────────────────────────────────────────────┤
│                                             │
│   [Grey bubble]                             │
│   Hey, can you pick up groceries?          │
│   10:23                                     │
│                                             │
│                      [Blue bubble]          │
│                      Sure, what do we need? │
│                                      10:24  │
│                                             │
│   [Grey bubble]                             │
│   Milk, bread, and eggs                    │
│   10:25                                     │
│                                             │
├─────────────────────────────────────────────┤
│  [+]  [Message...]              [🎤] [📷]  │
└─────────────────────────────────────────────┘
```

**Key Features**:
- End-to-end encrypted (show 🔒 indicator)
- Read receipts (✓✓ like WhatsApp)
- Voice messages (hold to record)
- Photo/video sharing (camera button)
- Emoji reactions (long-press message)
- Reply/forward (swipe gestures)

### Tab 2: Photos

**Grid View** (Instagram-style):
```
┌─────────────────────────────────────────────┐
│  Photos                              [+]    │
├─────────────────────────────────────────────┤
│  Today                                      │
│  ┌──────┬──────┬──────┐                    │
│  │ img  │ img  │ img  │                    │
│  └──────┴──────┴──────┘                    │
│                                             │
│  Yesterday                                  │
│  ┌──────┬──────┬──────┐                    │
│  │ img  │ img  │ img  │                    │
│  └──────┴──────┴──────┘                    │
│                                             │
│  Last Week                                  │
│  ┌──────┬──────┬──────┐                    │
│  │ img  │ img  │ img  │                    │
│  └──────┴──────┴──────┘                    │
└─────────────────────────────────────────────┘
```

**Photo Detail View**:
```
┌─────────────────────────────────────────────┐
│  ←                                    [⋮]   │
│                                             │
│                                             │
│            [Full Screen Image]              │
│                                             │
│                                             │
│                                             │
├─────────────────────────────────────────────┤
│  "Beach day with kids"                      │
│  📍 Brighton   📅 21 Oct 2025               │
│  Uploaded by Dad                            │
└─────────────────────────────────────────────┘
```

**Key Features**:
- Auto-upload from camera roll (optional, off by default)
- Chronological and album views
- Captions and location tags
- Multiple photo selection
- Download to device
- Share to specific family members
- Never compressed (full quality storage)

### Tab 3: Tasks

**Category View**:
```
┌─────────────────────────────────────────────┐
│  Tasks                               [+]    │
├─────────────────────────────────────────────┤
│  🛒 Shopping (3)                       →    │
│  🏠 Housework (1)                      →    │
│  🚗 Errands (0)                        →    │
│  👶 Kids (2)                           →    │
│  🌱 Garden (0)                         →    │
│  📋 Other (1)                          →    │
└─────────────────────────────────────────────┘
```

**Task List** (Category Detail):
```
┌─────────────────────────────────────────────┐
│  ← Shopping                          [+]    │
├─────────────────────────────────────────────┤
│  ☐  Milk                                    │
│      Added by Mum • 2h ago                  │
├─────────────────────────────────────────────┤
│  ☐  Bread                                   │
│      Added by Mum • 2h ago                  │
├─────────────────────────────────────────────┤
│  ☐  Eggs                                    │
│      Added by Dad • 1h ago                  │
├─────────────────────────────────────────────┤
│  ☑  Chicken (completed)                     │
│      Completed by Dad • 30m ago             │
└─────────────────────────────────────────────┘
```

**Add Task**:
```
┌─────────────────────────────────────────────┐
│  ← New Task                                 │
├─────────────────────────────────────────────┤
│  Task                                       │
│  ┌─────────────────────────────────────┐   │
│  │ Buy milk                            │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Category                                   │
│  🛒 Shopping                           ▼   │
│                                             │
│  Due Date (Optional)                        │
│  📅 No due date                        ▼   │
│                                             │
│  Notes (Optional)                           │
│  ┌─────────────────────────────────────┐   │
│  │ Get the organic one                │   │
│  └─────────────────────────────────────┘   │
│                                             │
│         [Cancel]        [Add Task]          │
└─────────────────────────────────────────────┘
```

**AI Features** (Week 2+):
- Natural language: Type "We need milk" in chat → Auto-added to Shopping
- Smart categorization: "Fix the fence" → Garden category
- Due date extraction: "Buy milk tomorrow" → Due date set
- Voice commands: "/remember WiFi password is X"

### Tab 4: Settings

**Simple, Minimal**:
```
┌─────────────────────────────────────────────┐
│  ← Settings                                 │
├─────────────────────────────────────────────┤
│  👤  John Smith                             │
│      @john:family.hearth.local              │
│      [Edit Profile]                         │
├─────────────────────────────────────────────┤
│  Notifications                         →    │
│  Privacy & Security                    →    │
│  Data & Storage                        →    │
├─────────────────────────────────────────────┤
│  Help & Support                        →    │
│  About Hearth                          →    │
├─────────────────────────────────────────────┤
│  [Sign Out]                                 │
└─────────────────────────────────────────────┘
```

**DO NOT**:
- Expose Matrix terminology ("homeserver", "federation", "rooms")
- Show cryptographic fingerprints (unless user taps "Advanced")
- Require configuration of server URLs
- Have 50 settings options (Element mistake)

**DO**:
- Keep it to 5-7 top-level options max
- Hide technical details under "Advanced" section
- Default everything to sensible values
- Make "Sign Out" require confirmation

---

# PART 4: ONBOARDING FLOW

## The Critical 5 Minutes

**Goal**: User goes from "I have a Pi" to "I'm chatting" in <5 minutes

### Step 1: Pi Setup (User does this once)

**Physical**:
1. Unbox Pi
2. Insert microSD (pre-flashed with Hearth OS)
3. Plug in power
4. Plug in Ethernet (or connect to WiFi via web UI)
5. Pi boots and shows QR code on connected screen OR serves web page at hearth.local

**Screen Shows**:
```
┌─────────────────────────────────────────────┐
│                                             │
│           Welcome to Hearth                 │
│                                             │
│     [Large QR Code]                         │
│                                             │
│  Scan this code with the Hearth app        │
│  to connect your phone                      │
│                                             │
│  Or visit: http://hearth.local              │
│                                             │
└─────────────────────────────────────────────┘
```

### Step 2: App Setup (User does this on phone)

**Download Hearth app** from App Store/Play Store

**Open app → Onboarding**:

**Screen 1: Welcome**
```
┌─────────────────────────────────────────────┐
│                                             │
│              🏠                             │
│                                             │
│          Welcome to Hearth                  │
│                                             │
│   Your family's private space for           │
│   messages, photos, and plans               │
│                                             │
│                                             │
│                                             │
│              [Get Started]                  │
│                                             │
└─────────────────────────────────────────────┘
```

**Screen 2: Scan QR**
```
┌─────────────────────────────────────────────┐
│  ← Back                                     │
│                                             │
│        Scan Your Hearth Hub                 │
│                                             │
│   ┌─────────────────────────────────────┐  │
│   │                                     │  │
│   │      [Camera Viewfinder]            │  │
│   │                                     │  │
│   │      [QR Code Overlay]              │  │
│   │                                     │  │
│   └─────────────────────────────────────┘  │
│                                             │
│   Point your camera at the QR code         │
│   on your Hearth Hub's screen              │
│                                             │
│              [Enter Code Manually]          │
└─────────────────────────────────────────────┘
```

**What happens when QR scanned**:
1. App extracts: `hearth://setup?ip=192.168.1.100&token=abc123`
2. App connects to Pi
3. App auto-configures Matrix homeserver URL
4. App proceeds to account creation

**Screen 3: Create Account**
```
┌─────────────────────────────────────────────┐
│  ←                                          │
│                                             │
│           Create Your Account               │
│                                             │
│   Name                                      │
│   ┌─────────────────────────────────────┐  │
│   │ John                                │  │
│   └─────────────────────────────────────┘  │
│                                             │
│   Username                                  │
│   ┌─────────────────────────────────────┐  │
│   │ john                                │  │
│   └─────────────────────────────────────┘  │
│   Your username will be: @john:family...    │
│                                             │
│   Password                                  │
│   ┌─────────────────────────────────────┐  │
│   │ ••••••••                            │  │
│   └─────────────────────────────────────┘  │
│                                             │
│              [Create Account]               │
│                                             │
└─────────────────────────────────────────────┘
```

**Screen 4: You're In!**
```
┌─────────────────────────────────────────────┐
│                                             │
│              ✓                              │
│                                             │
│          You're all set!                    │
│                                             │
│   Your Hearth is ready. Invite your        │
│   family members to join.                   │
│                                             │
│   Invite code (share this):                 │
│   ┌─────────────────────────────────────┐  │
│   │  HEARTH-XYZW-1234                   │  │
│   │  [Copy]  [Share]                    │  │
│   └─────────────────────────────────────┘  │
│                                             │
│              [Start Chatting]               │
│                                             │
└─────────────────────────────────────────────┘
```

### Step 3: Invite Family Members

**Send invite code via SMS/WhatsApp/Email**:
```
"Hey! I've set up Hearth for our family.

Download the Hearth app:
iPhone: [App Store link]
Android: [Play Store link]

Use code: HEARTH-XYZW-1234

- John"
```

**Family member opens app**:
- Downloads app
- Opens app → "Join a Hearth"
- Enters code: `HEARTH-XYZW-1234`
- App auto-configures, creates account
- Done!

---

# PART 5: AI DEVELOPMENT INSTRUCTIONS

## For Software Development

### Backend Services (Python)

**File Structure**:
```
services/
├── intelligence/           # AI command processor
│   ├── src/
│   │   ├── main.py        # Main loop
│   │   ├── commands.py    # Command handlers
│   │   ├── ai.py          # Ollama integration
│   │   └── db.py          # Database helpers
│   ├── Dockerfile
│   └── requirements.txt
├── photos/                 # Photo management
│   ├── src/
│   │   ├── api.py         # REST API
│   │   ├── storage.py     # File handling
│   │   └── metadata.py    # EXIF, tags
│   ├── Dockerfile
│   └── requirements.txt
└── tasks/                  # Task management
    ├── src/
    │   ├── api.py         # REST API
    │   ├── tasks.py       # Task logic
    │   └── categories.py  # Category management
    ├── Dockerfile
    └── requirements.txt
```

**Code Style**:
- Python 3.11+
- Type hints everywhere
- Async/await for I/O
- Docstrings for all public functions
- Black formatter (line length 100)
- pytest for testing
- Keep functions <50 lines

**Example**:
```python
async def handle_remember_command(
    message: Dict[str, Any],
    db: Database
) -> CommandResponse:
    """
    Store a fact in household memory.
    
    Example: "/remember WiFi password is MyPass123"
    
    Args:
        message: Message dict with content, sender, timestamp
        db: Database connection
        
    Returns:
        CommandResponse with success/failure and reply text
    """
    content = message["content"].replace("/remember", "").strip()
    
    if not content:
        return CommandResponse(
            success=False,
            reply="Usage: /remember [fact to store]"
        )
    
    await db.memories.insert({
        "content": content,
        "created_by": message["sender"],
        "created_at": datetime.now()
    })
    
    return CommandResponse(
        success=True,
        reply=f"✓ Remembered: {content}"
    )
```

### Mobile App (React Native)

**File Structure**:
```
hearth-mobile/
├── src/
│   ├── screens/
│   │   ├── ChatsScreen.tsx
│   │   ├── ChatDetailScreen.tsx
│   │   ├── PhotosScreen.tsx
│   │   ├── TasksScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/
│   │   ├── MessageBubble.tsx
│   │   ├── PhotoGrid.tsx
│   │   ├── TaskItem.tsx
│   │   └── common/
│   ├── services/
│   │   ├── matrix.ts          # Matrix SDK wrapper
│   │   ├── photos.ts          # Photo API
│   │   ├── tasks.ts           # Task API
│   │   └── storage.ts         # Local storage
│   ├── store/
│   │   ├── auth.ts            # Auth state
│   │   ├── chats.ts           # Chat state
│   │   ├── photos.ts          # Photo state
│   │   └── tasks.ts           # Task state
│   ├── navigation/
│   │   └── RootNavigator.tsx
│   ├── theme/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   └── utils/
│       ├── date.ts
│       ├── encryption.ts
│       └── validation.ts
├── ios/
├── android/
└── package.json
```

**Code Style**:
- TypeScript strict mode
- Functional components only (no classes)
- Custom hooks for logic reuse
- Prettier formatting
- ESLint with Airbnb config
- Jest + React Native Testing Library

**Example Component**:
```typescript
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { CheckBox } from 'react-native-paper';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string) => void;
  onPress: (id: string) => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({
  task,
  onToggle,
  onPress,
}) => {
  return (
    <TouchableOpacity
      style={styles.container}
      onPress={() => onPress(task.id)}
      activeOpacity={0.7}
    >
      <CheckBox
        status={task.completed ? 'checked' : 'unchecked'}
        onPress={() => onToggle(task.id)}
      />
      <View style={styles.content}>
        <Text
          style={[
            styles.title,
            task.completed && styles.completedTitle,
          ]}
        >
          {task.title}
        </Text>
        <Text style={styles.meta}>
          {task.category} • Added by {task.createdBy}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  content: {
    flex: 1,
    marginLeft: 12,
  },
  title: {
    fontSize: 16,
    color: '#000',
  },
  completedTitle: {
    textDecorationLine: 'line-through',
    color: '#999',
  },
  meta: {
    fontSize: 13,
    color: '#666',
    marginTop: 4,
  },
});
```

### Matrix SDK Integration

**DO**:
```typescript
// Wrap Matrix SDK in a clean service layer
class MatrixService {
  private client: MatrixClient;
  
  async sendMessage(roomId: string, text: string): Promise<void> {
    await this.client.sendTextMessage(roomId, text);
  }
  
  async getTimeline(roomId: string, limit: number): Promise<Message[]> {
    const timeline = await this.client.getTimeline(roomId, limit);
    return timeline.map(this.formatMessage);
  }
  
  // Hide Matrix complexity from UI components
}
```

**DON'T**:
```typescript
// Don't let Matrix types leak into UI components
// BAD:
<ChatScreen matrixClient={client} room={room} />

// GOOD:
<ChatScreen messages={messages} onSend={sendMessage} />
```

---

# PART 6: CRITICAL "DON'Ts"

## Never Do These Things

### 1. Don't Copy Element's UX Mistakes
❌ "Homeserver" terminology  
❌ "Federation" in UI  
❌ "Room" instead of "Chat"  
❌ Cryptographic key verification in onboarding  
❌ IRC-style UI  
❌ Technical settings exposed  

### 2. Don't Add Cloud Dependencies
❌ AWS for anything  
❌ Google Firebase  
❌ Pushy/OneSignal for notifications (use self-hosted Ntfy)  
❌ Analytics (unless explicitly opt-in, self-hosted)  

### 3. Don't Overcomplicate
❌ 50 features in v1  
❌ "Advanced" options everywhere  
❌ Configuration files users need to edit  
❌ Command-line setup  

### 4. Don't Harvest Data
❌ Telemetry by default  
❌ Crash reports with PII  
❌ "Improve our service" tracking  
❌ Any data that leaves the Pi without encryption  

### 5. Don't Break Offline Mode
❌ Features that require internet  
❌ "No connection" error screens (queue instead)  
❌ Loss of functionality on local network  

---

# PART 7: SUCCESS METRICS

## Week 1-4 (MVP Testing)

**Technical Metrics**:
- [ ] Setup time < 5 minutes (actual user tests)
- [ ] Message latency < 300ms (local network)
- [ ] Photo upload < 2 seconds for 5MB image
- [ ] App crash rate < 0.1%
- [ ] Pi uptime > 99%

**UX Metrics**:
- [ ] Wife can set up without asking for help
- [ ] Non-technical friend can complete onboarding
- [ ] Users prefer Hearth to WhatsApp for family chat
- [ ] Zero "what's a homeserver?" questions
- [ ] Users actually use Tasks feature (not just chat)

**Business Metrics**:
- [ ] Would pay £8.99/month for hosted version (survey)
- [ ] Would pay £299 for pre-configured Pi kit (survey)
- [ ] Would recommend to other families (NPS > 8)

## Day 90 Decision Criteria

**Ship It If**:
- ✅ You and wife use it daily instead of WhatsApp
- ✅ 3+ other families successfully installed and use it
- ✅ Zero catastrophic data loss incidents
- ✅ Average setup time < 10 minutes
- ✅ Users say "I love this" not "this is interesting"

**Pivot If**:
- ⚠️ Technical issues block daily use
- ⚠️ Setup too complicated (>15 min average)
- ⚠️ Users revert to WhatsApp after 1 week
- ⚠️ "Cool but I wouldn't pay for it"

**Stop If**:
- ❌ Fundamental protocol issues (Matrix too slow/unreliable)
- ❌ Can't achieve sub-10min setup
- ❌ Zero user enthusiasm ("meh")
- ❌ You don't use it yourself

---

# PART 8: GO-TO-MARKET STRATEGY

## Phase 1: Household Testing (Weeks 1-12)

### Target: 10 Households

**Who**:
- Your household (Week 1)
- 3 friends with kids (Weeks 2-4)
- 3 families from school parent group (Weeks 5-8)
- 3 families from online privacy communities (Weeks 9-12)

**How to recruit**:
```
Message:
"Hey! I've built a private family chat server that runs on a 
Raspberry Pi. No Big Tech, no data harvesting, no subscriptions.

Think: WhatsApp that works even when AWS is down.

Would you be willing to test it for a month? I'll set it up 
for you, totally free. Just need honest feedback.

Interested?"
```

**What you provide**:
- Pre-configured Pi (you set up)
- Mobile app (TestFlight/Play Store beta)
- 30-minute setup visit or video call
- Weekly check-ins

**What you measure**:
- Daily active usage
- Messages sent per day
- Photos uploaded per week
- Tasks created/completed
- Time to first "wow" moment
- Support requests (count and type)

## Phase 2: Hacker News Launch (Week 13)

### Post-Launch Strategy

**Timing**: After you have 10 successful household deployments

**HN Post Title**:
```
"Show HN: Hearth – Family chat that worked during AWS outage"
```

**Post Content**:
```
Hi HN,

Three weeks ago, AWS went down. Signal stopped working. 
But families using Hearth kept chatting.

I'm a product director and parent who got tired of family 
data being harvested. So I built Hearth: a private family 
server that runs on a Raspberry Pi (£250) in your home.

Three features:
- Messages (Matrix protocol, E2EE)
- Photos (full quality, unlimited)
- Tasks (AI-powered, runs locally)

It's not Element with better UX. It's a purpose-built family 
app that happens to use Matrix underneath.

Key differences from Signal/WhatsApp:
- No AWS dependency (self-hosted)
- No metadata harvesting
- Works offline on local network
- One-time cost, no subscriptions

I've been testing with 10 families for 3 months. Setup takes 
5 minutes. They actually prefer it to WhatsApp now.

Code: github.com/yourusername/hearth-family
Demo: hearth.community/demo
Blog post: Why we need post-AWS alternatives

Questions/feedback welcome. Happy to help anyone set it up.
```

**Engagement Strategy**:
- Respond to EVERY comment in first 6 hours
- Share technical details openly
- Acknowledge limitations honestly
- Offer to help people install it
- Link to demo video showing 5-min setup

**Success Metrics**:
- Front page for >2 hours
- 500+ GitHub stars in 48 hours
- 50+ people express interest in testing
- 3-5 blog posts about it
- 1-2 podcast/interview requests

## Phase 3: Community Building (Weeks 14-26)

### Build in Public

**Weekly Blog Posts**:
1. "Week 1: 47 families installed Hearth"
2. "What broke: Top 5 installation issues"
3. "Why families prefer Hearth to WhatsApp"
4. "Technical deep-dive: How we achieve sub-5min setup"
5. "Cost analysis: £299 vs WhatsApp over 5 years"
6. "Interview: A family's first month on Hearth"

**Content Channels**:
- Blog: hearth.community/blog
- Twitter: Daily updates, user stories
- YouTube: Setup videos, feature demos
- Reddit: r/selfhosted, r/privacy
- Hacker News: Follow-up posts at milestones

**Community Platforms**:
- GitHub Discussions (primary support)
- Matrix room: #hearth-family:matrix.org
- Monthly video calls with users

### Metrics to Track Publicly

**Transparency Dashboard** (hearth.community/metrics):
```
Families using Hearth: 147
Messages sent today: 8,432
Photos uploaded this week: 1,203
Average setup time: 6m 23s
Uptime (average): 99.7%
Support tickets (open): 12
GitHub stars: 1,847

Last updated: 2 minutes ago
```

## Phase 4: Monetization (Week 27+)

### Three Revenue Streams

**1. DIY Kit (£299)**
```
What you get:
- Pre-configured Raspberry Pi 5 (8GB)
- 1TB SSD pre-installed
- Hearth OS pre-loaded
- Premium case (fanless, metal)
- Power supply + ethernet cable
- Quick-start guide

Setup: Plug in, scan QR code, done.

Margin: ~£120 per unit
Target: 50 units/month by Month 6
```

**2. Hosted Version (£8.99/month)**
```
For families who want Hearth without hardware:
- We run your Pi in a secure UK datacenter
- Same privacy (encrypted, zero-knowledge)
- Remote access built-in
- Automated backups
- Priority support

Margin: ~£6/month per customer
Target: 200 customers by Month 12
```

**3. School Edition (£499/year)**
```
DO NOT BUILD YET

After Hearth Family is proven:
- 30 days interviewing teachers
- Study pedagogy + edtech
- Design school-specific features
- Pilot with 3-5 schools
- Iterate based on real classroom needs

This is a separate product decision tree.
```

### Pricing Philosophy

**Family Edition**:
- Free: Open-source software (always)
- £299: Pre-configured hardware (one-time)
- £8.99/month: Hosted version (optional)

**Never charge for**:
- Core features
- Security updates
- App downloads
- Support (basic)

**Optional paid add-ons**:
- Premium support (email/phone)
- Custom hardware (NUC instead of Pi)
- Extended warranty
- Migration services (WhatsApp → Hearth)

---

# PART 9: DEVELOPMENT ROADMAP

## Week 1-2: MVP Backend

**Deliverables**:
- [ ] Docker Compose stack running
- [ ] Synapse configured and stable
- [ ] PostgreSQL with family schema
- [ ] Basic photo upload API
- [ ] Basic task CRUD API
- [ ] Installation script tested on fresh Pi

**Definition of Done**:
- You can SSH to Pi and run `./install.sh`
- Services start automatically
- Database persists across reboots
- Can create account via command line

## Week 3-4: Mobile App Core

**Deliverables**:
- [ ] React Native project scaffolded
- [ ] Matrix SDK integrated
- [ ] Login/signup screens
- [ ] Chat list screen
- [ ] Chat detail screen (send/receive)
- [ ] Basic navigation working

**Definition of Done**:
- Can scan QR code to connect to Pi
- Can create account in app
- Can send and receive messages
- Messages persist across app restarts
- Works on both iOS and Android

## Week 5-6: Photos & Tasks

**Deliverables**:
- [ ] Photo gallery screen
- [ ] Photo upload from camera/library
- [ ] Photo detail view
- [ ] Task list screen
- [ ] Add/edit/complete tasks
- [ ] Task categories

**Definition of Done**:
- Can upload photo and see it in gallery
- Can create task and mark complete
- Data syncs across devices
- Offline mode queues actions

## Week 7-8: Polish & Testing

**Deliverables**:
- [ ] Onboarding flow complete
- [ ] Settings screen
- [ ] Notifications working
- [ ] Error handling throughout
- [ ] Loading states everywhere
- [ ] Tested with 3 non-technical users

**Definition of Done**:
- Wife can install without help
- Friend can install without help
- Zero crashes in 24h of use
- Feels "finished" not "prototype"

## Week 9-12: Field Testing

**Deliverables**:
- [ ] 10 households using daily
- [ ] Weekly feedback collected
- [ ] Top 10 bugs fixed
- [ ] Performance optimized
- [ ] Documentation complete

**Definition of Done**:
- 8/10 families prefer it to WhatsApp
- Average setup time < 10 minutes
- Zero data loss incidents
- Ready for public launch

## Week 13-16: AI Features

**Deliverables**:
- [ ] Ollama integrated on Pi
- [ ] `/remember` command working
- [ ] `/recall` command working
- [ ] Natural language task creation
- [ ] Smart categorization

**Definition of Done**:
- "We need milk" → Added to shopping list
- "/remember wifi password" → Stored securely
- AI responds in <3 seconds
- Works offline (queues when Pi unavailable)

## Week 17+: Community & Scale

**Deliverables**:
- [ ] GitHub repo public
- [ ] Documentation site live
- [ ] Community support channels
- [ ] First 100 external users
- [ ] Pre-order page for hardware

---

# PART 10: TECHNICAL SPECIFICATIONS

## Raspberry Pi Requirements

### Minimum (Testing)
- Raspberry Pi 5 (4GB)
- 32GB microSD (boot only)
- 128GB USB SSD (data)
- Official power supply
- Ethernet recommended

### Recommended (Production)
- Raspberry Pi 5 (8GB)
- 32GB microSD (boot only)
- 1TB NVMe SSD with M.2 HAT
- Fanless metal case
- UPS battery backup
- Ethernet connection

### Software Stack Versions
```yaml
OS: Raspberry Pi OS Lite 64-bit (Bookworm)
Docker: 24.0+
Docker Compose: 2.20+
Synapse: 1.98+ (latest stable)
PostgreSQL: 15.x
Python: 3.11+
Node.js: 20.x LTS (for build tools only)
```

## Database Schema

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matrix_user_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Photos
CREATE TABLE photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    mime_type VARCHAR(100),
    file_size INTEGER,
    width INTEGER,
    height INTEGER,
    caption TEXT,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    taken_at TIMESTAMP,
    uploaded_by UUID REFERENCES users(id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    matrix_event_id VARCHAR(255),
    tags TEXT[]
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    notes TEXT,
    category VARCHAR(50) DEFAULT 'general',
    due_date DATE,
    priority VARCHAR(20) DEFAULT 'normal',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by UUID REFERENCES users(id)
);

-- Memories (AI knowledge base)
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category VARCHAR(50),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0
);

-- Plans (Future events)
CREATE TABLE plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    plan_date DATE NOT NULL,
    location TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false
);

-- Indexes
CREATE INDEX idx_photos_uploaded ON photos(uploaded_at DESC);
CREATE INDEX idx_photos_user ON photos(uploaded_by);
CREATE INDEX idx_tasks_category ON tasks(category, completed);
CREATE INDEX idx_tasks_due ON tasks(due_date) WHERE completed = false;
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_plans_date ON plans(plan_date) WHERE completed = false;
```

## API Endpoints

### Photos API

```
GET    /api/photos              # List all photos
GET    /api/photos/:id          # Get photo details
POST   /api/photos              # Upload new photo
PATCH  /api/photos/:id          # Update caption/tags
DELETE /api/photos/:id          # Delete photo
GET    /api/photos/download/:id # Download original file
```

### Tasks API

```
GET    /api/tasks               # List all tasks
GET    /api/tasks/:id           # Get task details
POST   /api/tasks               # Create new task
PATCH  /api/tasks/:id           # Update task
DELETE /api/tasks/:id           # Delete task
POST   /api/tasks/:id/complete  # Mark as complete
GET    /api/tasks/categories    # List categories with counts
```

### Memories API (AI)

```
POST   /api/memories/remember   # Store a memory
POST   /api/memories/recall     # Search memories
GET    /api/memories            # List all memories
DELETE /api/memories/:id        # Delete memory
```

### All APIs require:
- Authentication: Bearer token (Matrix access token)
- Rate limiting: 100 requests/minute per user
- Response format: JSON
- Error format: `{"error": "message", "code": "ERROR_CODE"}`

## Mobile App Tech Stack

```json
{
  "dependencies": {
    "react": "18.2.0",
    "react-native": "0.73.0",
    "react-navigation": "^6.1.9",
    "matrix-js-sdk": "^32.0.0",
    "zustand": "^4.4.7",
    "react-native-paper": "^5.11.1",
    "react-native-image-picker": "^7.1.0",
    "react-native-fast-image": "^8.6.3",
    "@react-native-async-storage/async-storage": "^1.21.0",
    "axios": "^1.6.2",
    "date-fns": "^3.0.0",
    "react-native-permissions": "^4.0.0",
    "react-native-push-notification": "^8.1.1"
  },
  "devDependencies": {
    "@testing-library/react-native": "^12.4.0",
    "@types/react": "^18.2.45",
    "typescript": "^5.3.3",
    "eslint": "^8.55.0",
    "prettier": "^3.1.1",
    "jest": "^29.7.0"
  }
}
```

---

# PART 11: QUALITY STANDARDS

## Code Quality Requirements

### Backend (Python)

**Must Have**:
- Type hints on all functions
- Docstrings in Google style
- Unit tests (>70% coverage)
- Integration tests for APIs
- Async/await for I/O operations
- Proper error handling (no bare except)
- Logging at appropriate levels

**Code Review Checklist**:
- [ ] No hardcoded secrets
- [ ] SQL injection prevention (parameterized queries)
- [ ] Input validation on all endpoints
- [ ] Rate limiting implemented
- [ ] Error messages don't leak internal details
- [ ] Database transactions used correctly
- [ ] Memory leaks checked

### Mobile (React Native)

**Must Have**:
- TypeScript strict mode enabled
- Functional components (no classes)
- Custom hooks for reusable logic
- PropTypes or TypeScript interfaces
- Error boundaries
- Loading states
- Empty states
- Accessibility labels

**Performance Requirements**:
- App launch < 2 seconds
- Screen transitions 60fps
- List scrolling smooth (no jank)
- Image loading lazy + cached
- Network requests optimized
- Bundle size < 50MB

**Accessibility Requirements**:
- VoiceOver/TalkBack compatible
- Touch targets >44x44pt
- Color contrast ratio >4.5:1
- Text scales with system settings
- No information conveyed by color alone

## Security Standards

### Authentication
- Matrix access tokens only
- No passwords stored in app
- Biometric login option (device keychain)
- Auto-logout after 30 days inactive
- Secure token storage (Keychain/KeyStore)

### Data Protection
- Photos encrypted at rest (optional)
- Database can use LUKS encryption
- Backups encrypted before upload
- No plain-text secrets in configs
- TLS 1.3 for all network traffic

### Privacy
- No telemetry by default
- Crash reports opt-in only
- No third-party SDKs
- Local-first architecture
- User can export all data
- User can delete all data

---

# PART 12: SUPPORT & DOCUMENTATION

## User Documentation

### Quick Start Guide (1 page)
```
1. Plug in your Hearth Hub
2. Download Hearth app
3. Scan QR code
4. Create account
5. Invite family

Done! Start chatting.
```

### Troubleshooting Guide

**Common Issues**:

**"Can't connect to Hearth Hub"**
- Check Pi is powered on (green LED)
- Check phone is on same WiFi
- Try typing http://hearth.local in browser
- Restart Pi if needed

**"Messages not sending"**
- Check internet connection
- Messages will send when back online
- Check Pi is running (green LED)

**"Photos not uploading"**
- Check storage space on Pi
- Check photo size (<100MB limit)
- Check internet connection

**"Forgot password"**
- No central password reset
- Create new account OR
- Access Pi directly to reset

### API Documentation

Auto-generated with OpenAPI:
- Interactive API explorer
- Example requests/responses
- Authentication guide
- Rate limit info
- Error code reference

Host at: `http://PI_IP:3000/api/docs`

---

# PART 13: TESTING STRATEGY

## Testing Pyramid

### Unit Tests (70%)
```python
def test_remember_command_stores_memory():
    """Test that /remember command saves to database"""
    message = {
        "content": "/remember WiFi password is Test123",
        "sender": "@john:family.local",
        "timestamp": datetime.now()
    }
    
    response = await handle_remember_command(message, db)
    
    assert response.success == True
    assert "Remembered" in response.reply
    
    # Verify database
    memory = await db.memories.find_one({"created_by": "@john:family.local"})
    assert "WiFi password is Test123" in memory["content"]
```

### Integration Tests (20%)
```python
def test_photo_upload_and_retrieval():
    """Test full photo upload flow"""
    # Upload photo
    with open("test.jpg", "rb") as f:
        response = client.post(
            "/api/photos",
            files={"file": f},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 201
    photo_id = response.json()["id"]
    
    # Retrieve photo list
    response = client.get(
        "/api/photos",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    photos = response.json()["photos"]
    assert any(p["id"] == photo_id for p in photos)
    
    # Download photo
    response = client.get(
        f"/api/photos/download/{photo_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
```

### E2E Tests (10%)
```typescript
describe('Full Onboarding Flow', () => {
  it('should complete onboarding in under 5 minutes', async () => {
    const startTime = Date.now();
    
    // Launch app
    await device.launchApp();
    
    // Scan QR code (mocked)
    await element(by.id('scanQRButton')).tap();
    await mockQRCodeScan('hearth://setup?ip=192.168.1.100&token=test123');
    
    // Create account
    await element(by.id('nameInput')).typeText('Test User');
    await element(by.id('usernameInput')).typeText('testuser');
    await element(by.id('passwordInput')).typeText('SecurePass123!');
    await element(by.id('createAccountButton')).tap();
    
    // Verify success screen
    await expect(element(by.text('You\'re all set!'))).toBeVisible();
    
    const endTime = Date.now();
    const duration = (endTime - startTime) / 1000;
    
    expect(duration).toBeLessThan(300); // 5 minutes = 300 seconds
  });
});
```

## User Acceptance Testing

### Test Scenarios

**Scenario 1: New User Setup**
```
Given: Fresh Pi, user has never used Hearth
When: User follows quick start guide
Then: User should be chatting within 5 minutes
```

**Scenario 2: Daily Usage**
```
Given: User has Hearth installed
When: User opens app 3x per day for a week
Then: App should feel fast, reliable, familiar
```

**Scenario 3: Offline Mode**
```
Given: User is connected to home WiFi but internet is down
When: User sends messages and adds tasks
Then: Everything should work locally, sync later
```

**Scenario 4: Family Invite**
```
Given: User has Hearth set up
When: User invites spouse via invite code
Then: Spouse can join in <5 minutes without technical help
```

---

# PART 14: LAUNCH CHECKLIST

## Pre-Launch (1 Week Before)

- [ ] 10+ successful household installations
- [ ] Average setup time < 10 minutes
- [ ] Zero critical bugs in backlog
- [ ] All E2E tests passing
- [ ] Documentation complete
- [ ] Privacy policy finalized
- [ ] Terms of service ready
- [ ] Support email configured
- [ ] GitHub repo cleaned up
- [ ] Demo video recorded
- [ ] Website live
- [ ] App Store listing prepared
- [ ] Play Store listing prepared
- [ ] HN post drafted
- [ ] Blog post written
- [ ] Tweet thread ready
- [ ] Press kit prepared

## Launch Day

**Morning (before HN post)**:
- [ ] Final production deploy
- [ ] All services health-checked
- [ ] Support channels monitored
- [ ] Coffee consumed ☕

**Submit to HN** (8-9 AM Pacific):
- [ ] Post submitted
- [ ] Monitor comments
- [ ] Respond to every question
- [ ] Share on Twitter simultaneously

**Throughout Day**:
- [ ] Answer support emails <1 hour
- [ ] Fix critical bugs immediately
- [ ] Deploy hotfixes if needed
- [ ] Document all feedback

**Evening**:
- [ ] Write daily update blog post
- [ ] Thank everyone who helped
- [ ] Plan next day's priorities
- [ ] Celebrate! 🎉

## Post-Launch (First Week)

**Daily Tasks**:
- [ ] Monitor GitHub issues
- [ ] Respond to all support requests
- [ ] Ship bug fixes rapidly
- [ ] Collect user feedback
- [ ] Write daily progress updates

**Weekly Tasks**:
- [ ] Publish metrics transparently
- [ ] Write retrospective blog post
- [ ] Plan next week's features
- [ ] Thank contributors publicly

---

# PART 15: DECISION FRAMEWORKS

## When to Add a Feature

Ask these questions in order:

### 1. Does it serve the core use case?
**Core use case**: Family staying connected privately

✅ Voice messages → YES (better than typing)  
❌ Video streaming → NO (not communication)

### 2. Does it add complexity?
If yes, can we hide it?

✅ Backup to cloud → Complex, but hide in settings  
❌ Blockchain integration → Complex and unnecessary

### 3. Do 3+ users request it?
If yes, is it the same underlying need?

✅ "Calendar" + "Events" + "Plans" → Same need  
❌ One-off requests → Probably not

### 4. Can we build it in 1 week?
If no, can we ship a simpler version?

✅ Basic calendar → 1 week  
❌ Full Google Calendar clone → Months

### 5. Does it compromise privacy?
If yes, stop immediately.

❌ Cloud sync → Breaks sovereignty  
❌ Analytics → Breaks privacy  
❌ Centralized server → Breaks architecture

## When to Say No

**Say NO to**:
- Features that require cloud services
- Enterprise features (SSO, Active Directory)
- Blockchain/crypto/web3 integration
- AI that requires external APIs
- Video streaming/conferencing (use Jitsi link)
- Social network features (public profiles, likes)
- Monetization via ads or data
- Features that need >1 month to build

**Say YES to**:
- Features that enhance core use case
- Simplifications that reduce complexity
- Privacy enhancements
- Accessibility improvements
- Performance optimizations
- Bug fixes (always yes)

## When to Pivot

**Consider pivoting if**:
- Users don't use it after 1 week
- Setup time can't get below 15 minutes
- Too many support requests per user
- Matrix protocol has fundamental issues
- You don't enjoy working on it

**Pivot options**:
1. Different target market (schools vs families)
2. Different delivery (hosted vs self-hosted)
3. Different scope (just photos, or just tasks)
4. Different tech (ditch Matrix, build custom)

**Don't pivot until Day 90**. Give it a fair shot.

---

# APPENDIX A: GLOSSARY

## Terms to NEVER Use in UI

❌ **Homeserver** → Say: "Your Hearth Hub"  
❌ **Federation** → Don't mention it  
❌ **Room** → Say: "Chat"  
❌ **Space** → Say: "Family" or don't mention  
❌ **Client** → Say: "App"  
❌ **Matrix** → Don't mention (it's infrastructure)  
❌ **Encryption keys** → Don't show unless Advanced  
❌ **mxc:// URLs** → Never show to users

## Terms That Are OK

✅ **Messages** → Familiar from WhatsApp  
✅ **Photos** → Clear and simple  
✅ **Tasks** → Better than "To-dos"  
✅ **Settings** → Universal  
✅ **Invite** → Clear action  
✅ **Family** → Warm and relatable

---

# APPENDIX B: INSPIRATION & ANTI-PATTERNS

## Apps to Emulate (UX)

✅ **WhatsApp** - Familiar, fast, simple  
✅ **Signal** - Clean, private, trustworthy  
✅ **Telegram** - Fluid, delightful, feature-rich  
✅ **Apple Photos** - Beautiful gallery, smart organization  
✅ **Things 3** - Elegant task management  

## Apps to Avoid (UX)

❌ **Element** - Too technical, confusing onboarding  
❌ **Slack** - Too business-focused, overwhelming  
❌ **Discord** - Too gamified, chaotic  
❌ **Mastodon** - Too nerdy, intimidating

## Technical Inspiration

✅ **Matrix Protocol** - Decentralized, open, E2EE  
✅ **Syncthing** - P2P sync, no cloud  
✅ **Nextcloud** - Self-hosted, feature-rich  
✅ **Home Assistant** - Appliance-like setup  

## Anti-Patterns to Avoid

❌ **Premature optimization** - Ship fast, optimize later  
❌ **Feature creep** - Stay focused on 3 core features  
❌ **Perfect code** - Done > Perfect  
❌ **Building for yourself** - Build for your mum  

---

# FINAL WORDS FOR THE AI AGENT

## Your Mission

Build software that lets families own their digital lives. Not because they're privacy nerds, but because it just works better.

## Your Constraints

- Three features only (Messages, Photos, Tasks)
- Setup in <5 minutes
- Works offline
- No cloud dependencies
- Beautiful UX (Element is the anti-pattern)

## Your Success Criteria

- Wife uses it without help
- Non-technical friend completes setup alone
- Users prefer it to WhatsApp
- Zero "what's a homeserver?" questions

## When in Doubt

Ask: "Would my mum understand this?"

If no → simplify.

---

**Now go build something families will love. 🏠**

---

**Created**: 2025-11-15
**Status**: Placeholder - needs full content from artifacts
