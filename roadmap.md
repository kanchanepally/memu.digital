# Hearth: The Only Roadmap You Need

**Last Updated**: 2025-11-16 (End of Day 1)  
**Status**: ✅ Week 1 Backend Complete!  
**Goal**: Working product for your family by December 1st

---

## YOUR CURRENT SITUATION (AS OF NOV 16, 2025 - 1:00 PM)

**What you have NOW** ✅:
- Docker Compose stack (fully working!)
- PostgreSQL 15 (with correct C locale)
- Matrix/Synapse (healthy and running)
- Element web (accessible at localhost:8080)
- 2 test accounts created (hari, rach)
- First messages sent successfully
- Message persistence working
- All containers healthy

**What you DON'T have**:
- Working mobile app
- Photos service (API)
- Tasks service (API)
- Daily usage data
- Any real validation yet

**Reality check**: You cannot validate the product until you and your wife use it daily for 2 weeks minimum. That starts NOW.

---

## THE DECISION: Follow the "Weekend Guide" First

Of all your documents, the **"Getting Started Weekend"** guide is the most practical. Here's why:

1. ✅ Gets you to "working" fastest
2. ✅ Uses what you already have
3. ✅ Focuses on daily usage validation
4. ✅ Delays AI until after core works
5. ✅ No premature optimization

**The Problem**: Even the weekend guide is too ambitious for where you are.

---

## YOUR ACTUAL NEXT STEPS (Week by Week)

### ✅ WEEK 1 - DAY 1 (Nov 16): COMPLETE!

**What you accomplished today** (2 hours):
- [x] Fixed Synapse configuration (generated homeserver.yaml)
- [x] Fixed PostgreSQL locale issue (POSTGRES_INITDB_ARGS)
- [x] Fixed docker-compose.yml to use local folders
- [x] All services healthy (postgres, synapse, element, intelligence)
- [x] Created 2 accounts (hari, rach) via CLI
- [x] Sent first message successfully
- [x] Verified message persistence

**Blockers encountered & resolved**:
- Synapse config wasn't generating → Fixed with explicit generate command
- Docker volumes being deleted → Changed to local folder mounts
- PostgreSQL locale mismatch → Added POSTGRES_INITDB_ARGS
- Web registration failing → Used CLI workaround (will fix next week)

---

### 📍 WEEK 1 - DAYS 2-7 (Nov 17-22): Daily Usage & Observation

**Goal**: Use Element web daily to validate if the core experience is worth building on.

**Your ONLY tasks**:
1. **Send 5+ messages per day** between hari and rach accounts
2. **Share 1 photo per day** via Element
3. **Track friction in daily-standup.md**:
   - What's slow?
   - What's confusing?
   - What breaks?
   - What's missing that you ACTUALLY need (not nice-to-have)?
4. **Test stability**:
   - Restart containers once → messages persist?
   - Refresh browser → messages persist?
   - Use on different devices → works?

**What to document each day**:
```markdown
## Nov 17, 2025
Time spent: 15 minutes
Messages sent: 7
Photos shared: 1

What worked: Messages appeared instantly
What was annoying: Can't see when message was delivered
What broke: Nothing
Would wife use this? Maybe, but needs mobile app

Decision: Continue testing
```

**DO NOT**:
- ❌ Build anything new
- ❌ Start the mobile app
- ❌ Add AI features
- ❌ Write Photos/Tasks APIs
- ❌ Touch docker-compose.yml
- ❌ Research Cloudflare Tunnels
- ❌ Think about monetization

**Success criteria for Week 1**:
- [ ] Used it every single day (7/7 days)
- [ ] Sent 35+ messages total (5/day × 7 days)
- [ ] Shared 7+ photos
- [ ] Zero data loss incidents
- [ ] Services stayed up 24/7
- [ ] You can honestly say: "This messaging part works well enough to build on"

---

### 🎯 WEEK 1 - DAY 8 (Nov 23): DECISION POINT

**After 7 days of real use, answer these questions**:

1. **Did the backend stay stable?** (Yes/No)
2. **Is Element fast enough?** (Yes/No)
3. **Did you actually prefer it to WhatsApp for any use case?** (Yes/No)
4. **What are the top 3 most annoying things?**
5. **If you had to use ONLY this for family chat, could you?** (Yes/No)
6. **Does your wife agree to test it?** (Yes/No)

**If 4+ answers are "No"**: Stop here. The foundation is broken. Fix Element experience first or reconsider Matrix entirely.

**If 4+ answers are "Yes"**: Proceed to Week 2.

---

### WEEK 2 (Nov 24-30): Add Photos & Tasks Backend APIs

**Goal**: Backend APIs exist for photos and tasks (NO mobile app yet).

**Prerequisites**:
- Week 1 decision was "YES" to proceed
- Backend has been stable for 7 days
- You understand the core UX problems

#### Day 1-2 (Nov 24-25): Photos API
```bash
# On your Pi (SSH or directly)
cd ~/hearth-os  # or wherever your code is

# Check what's actually running
docker compose ps

# If anything is stopped, restart
docker compose restart

# Check logs for errors
docker compose logs synapse
docker compose logs postgres

# Test Synapse is responding
curl http://localhost:8008/_matrix/client/versions
```

**Success criteria**:
- [ ] All containers show "Up"
- [ ] Can access Element web at http://PI_IP
- [ ] Can create account
- [ ] Can send message to yourself
- [ ] Message persists after refreshing page

**If this doesn't work**, stop everything else and fix it first.

#### Day 2 (Sunday): Add Database Schema

Your current setup is missing the actual Hearth-specific tables:

```bash
# SSH to Pi
cd ~/hearth-os

# Create the init-db.sql if it doesn't exist
cat > init-db.sql << 'EOF'
-- Users table (extends Matrix users)
CREATE TABLE IF NOT EXISTS hearth_users (
    id SERIAL PRIMARY KEY,
    matrix_id VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Photos table
CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    caption TEXT,
    uploaded_by VARCHAR(255) REFERENCES hearth_users(matrix_id),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    matrix_event_id VARCHAR(255)
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    category VARCHAR(50) DEFAULT 'general',
    notes TEXT,
    due_date DATE,
    created_by VARCHAR(255) REFERENCES hearth_users(matrix_id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    completed_by VARCHAR(255)
);

-- Memories table (for AI later)
CREATE TABLE IF NOT EXISTS memories (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50),
    created_by VARCHAR(255) REFERENCES hearth_users(matrix_id),
    created_at TIMESTAMP DEFAULT NOW()
);
EOF

# Apply the schema
docker compose exec postgres psql -U hearth -d hearth -f /docker-entrypoint-initdb.d/01-init.sql
```

**Success criteria**:
- [ ] Tables created without errors
- [ ] Can query: `docker compose exec postgres psql -U hearth -d hearth -c "\dt"`
- [ ] See: hearth_users, photos, tasks, memories tables

#### Days 3-7 (Mon-Fri): Daily Usage Test

**Your only job**: Send at least 5 messages each day via Element web.

Track in a note:
```
Nov 16: Sent 7 messages. Element is slow. Notifications don't work on phone.
Nov 17: Sent 5 messages. Getting used to it. Still prefer WhatsApp.
Nov 18: ...
```

**DO NOT BUILD ANYTHING NEW THIS WEEK.**

Just observe:
- Does it stay up?
- Is it fast enough?
- What's actually annoying about Element?
- Would this be useful with better UI?

---

### WEEK 2 (Nov 23-29): Add Photos & Tasks Services

**Goal**: Backend APIs exist for photos and tasks.

#### Create Photos Service

```bash
# On your Pi
cd ~/hearth-os
mkdir -p services/photos/src

cat > services/photos/src/api.py << 'EOF'
from fastapi import FastAPI, UploadFile, File, HTTPException
from datetime import datetime
import psycopg2
import os
import uuid

app = FastAPI()

DB = {
    'host': 'postgres',
    'database': os.getenv('DB_NAME', 'hearth'),
    'user': os.getenv('DB_USER', 'hearth'),
    'password': os.getenv('DB_PASSWORD')
}

UPLOAD_DIR = "/data/photos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_photo(file: UploadFile = File(...), caption: str = None):
    # Generate unique filename
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(filepath, 'wb') as f:
        f.write(await file.read())
    
    # Save to database
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO photos (filename, caption, uploaded_at) VALUES (%s, %s, %s) RETURNING id",
        (filename, caption, datetime.now())
    )
    photo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    
    return {"id": photo_id, "filename": filename}

@app.get("/photos")
def list_photos():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, caption, uploaded_at FROM photos ORDER BY uploaded_at DESC")
    photos = [{"id": r[0], "filename": r[1], "caption": r[2], "uploaded_at": str(r[3])} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"photos": photos}

@app.get("/photo/{photo_id}")
def get_photo(photo_id: int):
    # Return file from disk
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("SELECT filename FROM photos WHERE id = %s", (photo_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    if not result:
        raise HTTPException(status_code=404, detail="Photo not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(UPLOAD_DIR, result[0]))
EOF

# Create Dockerfile
cat > services/photos/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn psycopg2-binary python-multipart
COPY src/ .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create requirements.txt
cat > services/photos/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
python-multipart==0.0.6
EOF
```

#### Create Tasks Service

```bash
mkdir -p services/tasks/src

cat > services/tasks/src/api.py << 'EOF'
from fastapi import FastAPI
import psycopg2
import os
from datetime import datetime

app = FastAPI()

DB = {
    'host': 'postgres',
    'database': os.getenv('DB_NAME', 'hearth'),
    'user': os.getenv('DB_USER', 'hearth'),
    'password': os.getenv('DB_PASSWORD')
}

@app.post("/tasks")
def create_task(title: str, category: str = "general", notes: str = None):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, category, notes, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
        (title, category, notes, datetime.now())
    )
    task_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {"id": task_id, "title": title, "category": category}

@app.get("/tasks")
def list_tasks(category: str = None, completed: bool = False):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    
    if category:
        cur.execute(
            "SELECT id, title, category, completed FROM tasks WHERE category = %s AND completed = %s ORDER BY created_at DESC",
            (category, completed)
        )
    else:
        cur.execute(
            "SELECT id, title, category, completed FROM tasks WHERE completed = %s ORDER BY created_at DESC",
            (completed,)
        )
    
    tasks = [{"id": r[0], "title": r[1], "category": r[2], "completed": r[3]} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return {"tasks": tasks}

@app.patch("/tasks/{task_id}/complete")
def complete_task(task_id: int):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute(
        "UPDATE tasks SET completed = true, completed_at = %s WHERE id = %s",
        (datetime.now(), task_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "completed"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "deleted"}
EOF

# Create Dockerfile
cat > services/tasks/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn psycopg2-binary
COPY src/ .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > services/tasks/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
psycopg2-binary==2.9.9
EOF
```

#### Update docker-compose.yml

```bash
cd ~/hearth-os

# Add to docker-compose.yml (append these services)
cat >> docker-compose.yml << 'EOF'

  photos:
    build: ./services/photos
    container_name: hearth_photos
    restart: unless-stopped
    networks:
      - hearth
    volumes:
      - photos_data:/data/photos
    environment:
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    ports:
      - "8001:8000"
    depends_on:
      - postgres

  tasks:
    build: ./services/tasks
    container_name: hearth_tasks
    restart: unless-stopped
    networks:
      - hearth
    environment:
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    ports:
      - "8002:8000"
    depends_on:
      - postgres

volumes:
  postgres_data:
  synapse_data:
  photos_data:

networks:
  hearth:
    driver: bridge
EOF

# Build and start new services
docker compose up -d --build photos tasks
```

#### Test the APIs

```bash
# Test tasks API
curl http://localhost:8002/tasks

# Create a task
curl -X POST "http://localhost:8002/tasks?title=Buy%20milk&category=shopping"

# Test photos API
curl http://localhost:8001/photos
```

**Success criteria for Week 2**:
- [ ] Photos API responds
- [ ] Tasks API responds
- [ ] Can create task via curl
- [ ] Can upload photo via curl
- [ ] Data persists in PostgreSQL

---

### WEEK 3-4 (Dec 1-14): Mobile App - Messaging ONLY

**Goal**: Chat screen that looks like WhatsApp, connects to your Pi.

This is where you need React Native expertise. The architecture:

```
React Native App
    â†"
Matrix JS SDK (matrix-js-sdk)
    â†"
http://YOUR_PI_IP:8008 (Synapse)
```

**Critical decisions for mobile app**:
1. **Framework**: React Native (you already decided this)
2. **Matrix SDK**: `matrix-js-sdk` (official)
3. **UI Library**: React Native Paper (Material Design)
4. **State**: Zustand (simple)

**Scope for Weeks 3-4**:
- [ ] Login screen (username/password)
- [ ] Connect to `http://PI_IP:8008`
- [ ] Chat list screen
- [ ] Chat detail screen (send/receive text)
- [ ] That's it - NO photos, NO tasks, NO AI

**Do NOT build**:
- Photos tab (Week 5)
- Tasks tab (Week 5)
- Settings (Week 6)
- AI features (Week 8+)
- QR code onboarding (Week 6)

**File structure**:
```
hearth-mobile/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.tsx
│   │   ├── ChatsScreen.tsx
│   │   └── ChatDetailScreen.tsx
│   ├── services/
│   │   └── matrix.ts
│   ├── store/
│   │   └── chat.ts
│   └── App.tsx
├── package.json
└── README.md
```

I can generate the complete React Native starter code if you need it, but the key is: **ONLY MESSAGING for these 2 weeks**.

---

### WEEK 5-6 (Dec 15-28): Add Photos & Tasks Tabs

Now connect your backend APIs to the mobile app.

**Photos Tab**:
- Grid view of photos
- Upload button
- View detail
- Calls `http://PI_IP:8001/upload` and `http://PI_IP:8001/photos`

**Tasks Tab**:
- Category view
- Task list per category
- Add/complete tasks
- Calls `http://PI_IP:8002/tasks`

---

### WEEK 7-8 (Dec 29 - Jan 11): Polish & Family Testing

**Goal**: Your wife can use it without your help.

Focus:
- [ ] Onboarding flow (create account in app)
- [ ] Settings screen (minimal)
- [ ] Notifications (push via Matrix)
- [ ] Error handling
- [ ] Loading states
- [ ] Fix all crashes

**Success criteria**:
- [ ] Wife uses it for 3 days without asking questions
- [ ] App doesn't crash
- [ ] Feels "fast enough"
- [ ] She prefers it to WhatsApp for family chat (unlikely but measure)

---

### WEEK 9-12 (Jan 12 - Feb 8): Field Testing

**Goal**: 3 other families using it.

This is where you learn if anyone actually wants this.

**Recruiting**:
- Friends with kids
- Privacy-conscious acquaintances
- School parent group

**What you provide**:
- Pre-configured Pi (you set up)
- Mobile app (TestFlight/Play Store beta)
- 30-min setup call
- Weekly check-ins

**What you measure**:
- Daily active usage
- Messages sent per day
- Support requests
- "Would pay $X" survey responses

---

### WEEK 13+: AI Features (IF the above works)

**Only build AI if**:
- You're using it daily
- 3+ families are using it daily
- They're actually asking for AI features

**AI scope**:
1. `/remember` and `/recall` commands
2. Natural language task creation ("we need milk" → shopping list)
3. Daily summary (`/summarize today`)

**Implementation**:
```bash
# Add Ollama to docker-compose.yml
cat >> docker-compose.yml << 'EOF'

  ollama:
    image: ollama/ollama:latest
    container_name: hearth_ollama
    restart: unless-stopped
    networks:
      - hearth
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
EOF

# Pull model
docker compose exec ollama ollama pull phi3:mini
```

Then create the Intelligence service that reads from Matrix messages and processes with Ollama.

---

## WHAT TO IGNORE FOR NOW

**Do NOT work on these until Week 13+**:

❌ Cloudflare Tunnels (remote access)
❌ Production hardware specs
❌ Backup systems
❌ Pricing tiers
❌ Multi-user sovereignty architecture
❌ Beautiful metal cases
❌ Forensic evidence packages
❌ School edition
❌ Any monetization discussions

**Why?** You don't know if the core product is useful yet.

---

## THE CRITICAL PATH

```
Week 1:  Backend stable (Matrix + DB)
Week 2:  Photos/Tasks APIs exist
Week 3-4: Mobile app (messaging only)
Week 5-6: Mobile app (photos + tasks)
Week 7-8: Polish + wife testing
Week 9-12: 3 families testing
         â†"
     DECISION POINT
         â†"
  Is this useful?
         â†"
    YES → Week 13: Add AI
    NO  → Pivot or stop
```

**Total time to decision**: 12 weeks (by Feb 8, 2026)

---

## YOUR NEXT 3 ACTIONS (Right Now)

1. **SSH to your Pi** and run:
   ```bash
   cd ~/hearth-os
   docker compose ps
   ```
   
2. **Fix whatever is broken** in that output

3. **Send yourself a message** via Element web at `http://PI_IP`

**That's it for today.** Don't read any other documents. Don't design pricing. Don't think about AI.

Just get the backend stable.

---

## CONFLICT RESOLUTION TABLE

| Conflicting Decision | Weekend Guide | Product Bible | Solution Design | **OFFICIAL DECISION** |
|---------------------|---------------|---------------|-----------------|----------------------|
| When add AI? | Never | Week 13+ | Day 1 | **Week 13+ (after core works)** |
| Remote access? | Not mentioned | Maybe later | Cloudflare Tunnels | **Local only until Week 13+** |
| Hardware? | Any Pi | Pi 5 | Pi 5 + NVMe | **Whatever you have now** |
| First milestone? | Chat this weekend | 10 families in 90 days | Commercial launch | **Backend stable by Week 1** |
| Mobile app priority? | Not started | Week 3-4 | Not detailed | **Week 3-4 (after APIs work)** |

---

## QUESTIONS YOU MIGHT HAVE

**Q: What about Cloudflare Tunnels?**  
A: Not needed for local testing. Add in Week 13+ if you want remote access.

**Q: When do I build the QR code onboarding?**  
A: Week 6, after core features work. Right now, manual IP configuration is fine.

**Q: Should I use Element or build my app first?**  
A: Use Element web for Week 1-2 to validate backend. Build mobile app Week 3+.

**Q: What if my wife won't test it?**  
A: Then you don't have product-market fit. Fix that before building more.

**Q: When do I add the beautiful metal case?**  
A: Never, unless 50+ families are using it daily.

---

## DAILY STANDUP FORMAT

Every day, answer these 3 questions in a note:

```
Date: 2025-11-16

Yesterday: Got Synapse running, sent first message
Today: Fix PostgreSQL connection, add schema
Blockers: Don't know how to check if DB initialized correctly

Hours worked: 2
Feeling: Excited but overwhelmed
```

This keeps you honest and focused.

---

## FINAL WORD

You have a **complexity addiction**. Every document you've created adds 10 more decisions before validating if anyone wants this.

**The cure**: Build the simplest version that tests your core thesis:

> "Families want to own their chat data and are willing to run a Pi at home."

Everything else is a distraction until you validate that.

**Start with Week 1, Step 1, Action 1.**

Nothing else matters until that works.