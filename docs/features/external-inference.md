# External Inference Offload - Feature Specification

**Status:** Planned
**Priority:** Medium
**Estimated Sessions:** 3-4
**Last Updated:** 2025-01-26

---

## 1. Overview

### 1.1 Problem Statement

Memu runs AI inference locally on the hub hardware (typically Intel N100). This works but has limitations:

- **Slow responses** - N100 CPU takes 10-30 seconds for LLM responses
- **Photo processing delays** - Immich ML face/object detection is slow
- **No GPU utilization** - Many users have gaming PCs with powerful GPUs sitting idle
- **Resource contention** - AI tasks compete with chat/photo services

User feedback:
> "Something you might plan to allow is the option to outsource model running. My end goal is to have it use my working/gaming machine's GPU for its tasks, that way the lab can be just regular compute and storage."

### 1.2 Solution

Allow users to optionally point Memu's AI services to external servers:

1. **Ollama (bot AI)** - Already supports external URL via `OLLAMA_HOST`
2. **Immich ML** - Supports external URL via `MACHINE_LEARNING_URL`

This is a configuration change, not a code change. We need:
- Setup wizard option to configure external inference
- Documentation for setting up Ollama/Immich ML on another machine
- Health checks for external services

---

## 2. User Stories

### 2.1 Core Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US1 | Power user | run AI on my gaming PC's GPU | responses are instant instead of 30 seconds |
| US2 | Family admin | configure external AI in the setup wizard | I don't need to edit config files |
| US3 | User | fall back to local AI if external unavailable | the system still works when gaming PC is off |
| US4 | User | see which AI backend is being used | I know why responses are fast/slow |

### 2.2 User Interactions

**Setup Wizard (US2):**
```
┌─────────────────────────────────────────────────────────────┐
│  AI Configuration                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Where should Memu run AI tasks?                           │
│                                                             │
│  ○ On this device (default)                                │
│    Slower but always available. Works offline.             │
│                                                             │
│  ● On another computer                                      │
│    Faster if you have a GPU. Requires that computer        │
│    to be running.                                          │
│                                                             │
│    Ollama URL: [http://192.168.1.50:11434    ]            │
│    Immich ML URL: [http://192.168.1.50:3003  ] (optional) │
│                                                             │
│    [ Test Connection ]                                     │
│                                                             │
│    Status: ✓ Connected to Ollama (RTX 4080 detected)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Bot Status (US4):**
```
User: /backup-status

Bot: **Backup Status**
Last backup: 6 hours ago (245 MB)
...

User: /ai-status

Bot: **AI Configuration**
Ollama: External (192.168.1.50:11434)
  Model: llama3.2
  Status: Connected

Immich ML: Local
  Status: Running
```

---

## 3. Architecture

### 3.1 Current vs External Flow

**Current (Local):**
```
┌─────────────────────────────────────────────────────────┐
│                     MEMU HUB                            │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Bot     │───▶│ Ollama  │───▶│ CPU     │            │
│  │         │    │ (local) │    │ (slow)  │            │
│  └─────────┘    └─────────┘    └─────────┘            │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Immich  │───▶│ ML      │───▶│ CPU     │            │
│  │ Server  │    │ (local) │    │ (slow)  │            │
│  └─────────┘    └─────────┘    └─────────┘            │
└─────────────────────────────────────────────────────────┘
```

**External (GPU):**
```
┌─────────────────────────────────────────────────────────┐
│                     MEMU HUB                            │
│  ┌─────────┐                                           │
│  │ Bot     │─────────────────────────────┐             │
│  └─────────┘                             │             │
│                                          │             │
│  ┌─────────┐                             │             │
│  │ Immich  │─────────────────────────────┼──┐          │
│  │ Server  │                             │  │          │
│  └─────────┘                             │  │          │
└──────────────────────────────────────────┼──┼──────────┘
                                           │  │
                    Tailscale Network      │  │
                                           │  │
┌──────────────────────────────────────────┼──┼──────────┐
│                   GAMING PC              │  │          │
│  ┌─────────┐    ┌─────────┐             │  │          │
│  │ Ollama  │◀───│ GPU     │◀────────────┘  │          │
│  │ :11434  │    │ (fast)  │                │          │
│  └─────────┘    └─────────┘                │          │
│                                            │          │
│  ┌─────────┐    ┌─────────┐               │          │
│  │ Immich  │◀───│ GPU     │◀──────────────┘          │
│  │ ML:3003 │    │ (fast)  │                          │
│  └─────────┘    └─────────┘                          │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Configuration

**Environment Variables (.env):**
```bash
# AI Configuration
# Leave empty or 'local' for on-device AI
# Set to URL for external inference

# Ollama for bot commands (/summarize, /remind extraction)
OLLAMA_HOST=http://ollama:11434          # Local (default)
# OLLAMA_HOST=http://192.168.1.50:11434  # External

# Immich ML for photo processing (face detection, search)
# Leave unset for local, or set external URL
# MACHINE_LEARNING_URL=http://192.168.1.50:3003
```

### 3.3 File Changes

| File | Change |
|------|--------|
| `.env.example` | Add external inference examples |
| `bootstrap/app.py` | Add AI configuration step to wizard |
| `bootstrap/templates/setup.html` | Add AI config UI |
| `services/intelligence/src/config.py` | Already supports OLLAMA_HOST |
| `services/intelligence/src/bot.py` | Add /ai-status command |
| `docker-compose.yml` | Add MACHINE_LEARNING_URL to Immich |
| `docs/user_guide.md` | Add external AI setup guide |

---

## 4. Success Criteria

### 4.1 Functional Requirements

| Requirement | Metric | Test Method |
|-------------|--------|-------------|
| External Ollama works | Bot responds using external | Test /summarize |
| External Immich ML works | Photos processed by external | Upload photo, check |
| Fallback to local | Works when external offline | Stop external, test |
| Connection test | Shows success/failure | Click test in wizard |
| Status command | Shows current configuration | Test /ai-status |

### 4.2 Definition of Done

- [ ] Setup wizard allows external AI configuration
- [ ] Connection test validates external URL
- [ ] Bot works with external Ollama
- [ ] Immich ML works with external URL
- [ ] /ai-status command shows configuration
- [ ] Documentation complete
- [ ] Works with Tailscale (cross-device)

---

## 5. Implementation Plan

### 5.1 Sessions

| Session | Deliverable | Effort |
|---------|-------------|--------|
| 1 | Update .env.example and docker-compose.yml | 30 min |
| 2 | Add AI configuration to setup wizard | 2 hours |
| 3 | Add /ai-status bot command | 1 hour |
| 4 | Documentation (setup guide for external AI) | 1 hour |

### 5.2 Session Details

**Session 1: Configuration Updates**
- Update `.env.example` with external AI examples
- Add `MACHINE_LEARNING_URL` to Immich services in docker-compose.yml
- Verify existing `OLLAMA_HOST` support in config.py

**Session 2: Setup Wizard**
- Add "AI Configuration" step to wizard
- Radio buttons: "On this device" / "On another computer"
- URL input fields for Ollama and Immich ML
- "Test Connection" button with feedback
- Save to .env file

**Session 3: Bot Status Command**
- Add `/ai-status` command to bot.py
- Show Ollama configuration (local vs URL)
- Show connection status
- Show model name if available

**Session 4: Documentation**
- Update user guide with "Advanced: External AI" section
- Step-by-step guide to set up Ollama on gaming PC
- Step-by-step guide for Immich ML external
- Tailscale configuration tips
- Troubleshooting common issues

---

## 6. External Setup Guide (Draft)

### 6.1 Setting Up Ollama on Gaming PC

```bash
# On Windows gaming PC:
# 1. Download Ollama from https://ollama.ai
# 2. Install and run

# 3. Configure to listen on network (not just localhost)
# Edit environment variable:
OLLAMA_HOST=0.0.0.0:11434

# 4. Pull the model
ollama pull llama3.2

# 5. Test it works
curl http://localhost:11434/api/version

# 6. On Memu hub, set in .env:
OLLAMA_HOST=http://<gaming-pc-tailscale-ip>:11434
```

### 6.2 Setting Up Immich ML Externally

```bash
# On gaming PC with NVIDIA GPU:

# 1. Install Docker with NVIDIA support
# 2. Run Immich ML container:

docker run -d \
  --name immich_ml \
  --gpus all \
  -p 3003:3003 \
  ghcr.io/immich-app/immich-machine-learning:release

# 3. On Memu hub, set in .env:
MACHINE_LEARNING_URL=http://<gaming-pc-tailscale-ip>:3003
```

### 6.3 Tailscale Considerations

- Both Memu hub and gaming PC must be on same Tailnet
- Use Tailscale IP (100.x.x.x) for reliable connectivity
- Gaming PC must be online for external AI to work
- If gaming PC offline, Memu falls back to local (if configured)

---

## 7. Future Enhancements

- Auto-discovery of Ollama/ML services on Tailnet
- Load balancing between local and external
- Model selection in wizard
- Performance comparison (local vs external)
- Scheduled external (use GPU at night, local during day)

---

## Appendix: Current Code Support

**config.py already supports OLLAMA_HOST:**
```python
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
```

**brain.py already uses it:**
```python
self.ollama_url = Config.OLLAMA_HOST
# ...
response = await client.post(f"{self.ollama_url}/api/generate", ...)
```

**docker-compose.yml needs MACHINE_LEARNING_URL added:**
```yaml
immich_server:
  environment:
    - MACHINE_LEARNING_URL=${MACHINE_LEARNING_URL:-}  # Add this
```

This feature is 80% configuration, 20% wizard UI.
