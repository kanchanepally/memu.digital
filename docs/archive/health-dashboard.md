# Health Monitoring Dashboard - Feature Specification

**Status:** Planned
**Priority:** High
**Estimated Sessions:** 6-8
**Last Updated:** 2025-01-26

---

## 1. Overview

### 1.1 Problem Statement

Memu runs on headless hardware with no screen. Currently, families have no way to:
- See if all services are running
- Know when something fails silently
- Check system resource usage (disk, memory)
- Diagnose issues without SSH access

The only interaction points are Element (chat) and Immich (photos). If a service fails, users may not notice until they try to use it.

### 1.2 Solution

A simple web dashboard accessible at `http://memu.local/admin` that shows:
- Service health status (green/yellow/red)
- Backup status summary
- Storage usage
- Recent activity
- Quick actions (restart services, run backup)

Combined with proactive bot notifications for critical issues.

---

## 2. User Stories

### 2.1 Core Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US1 | Family member | see all services at a glance | I know everything is working |
| US2 | Family member | be notified when services fail | I can take action before it affects family |
| US3 | Non-technical user | see simple green/yellow/red status | I don't need to understand technical details |
| US4 | System admin | check disk and memory usage | I know when to add storage |
| US5 | Family member | restart a service from the dashboard | I don't need terminal access |
| US6 | System admin | see recent backup status | I know data is protected |

### 2.2 User Interactions

**Viewing Dashboard (US1, US3):**
```
User navigates to: http://memu.local/admin

Dashboard shows:
┌─────────────────────────────────────────────────────────┐
│  Memu Health Dashboard                        [Refresh] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Services                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │ Chat    │ │ Photos  │ │ AI      │ │ Database│       │
│  │   🟢    │ │   🟢    │ │   🟢    │ │   🟢    │       │
│  │ Healthy │ │ Healthy │ │ Healthy │ │ Healthy │       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │
│                                                         │
│  Backup Status                                          │
│  Last backup: 6 hours ago (245 MB) ✓                   │
│  USB backup: 3 days ago                                 │
│                                                         │
│  Storage                                                │
│  [██████████░░░░░░░░░░] 234 GB / 1 TB (23%)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Service Degraded (US2, US3):**
```
Bot notification in Element:
"Service Alert: Photos service is not responding.
 View dashboard: http://memu.local/admin"

Dashboard shows:
┌─────────┐
│ Photos  │
│   🟡    │
│ Degraded│
│ [Restart]│
└─────────┘
```

**Service Down (US2):**
```
Bot notification:
"CRITICAL: Database service is down.
 Chat and Photos may not work.
 View dashboard: http://memu.local/admin"

Dashboard shows:
┌─────────┐
│ Database│
│   🔴    │
│  Down   │
│ [Restart]│
└─────────┘
```

---

## 3. Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        HEALTH MONITORING SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │   Web Browser    │                                                   │
│  │ memu.local/admin │                                                   │
│  └────────┬─────────┘                                                   │
│           │                                                             │
│           ▼                                                             │
│  ┌──────────────────┐        ┌───────────────────────────────┐         │
│  │   Nginx Proxy    │        │   Health Check Service        │         │
│  │   /admin route   │───────▶│   (Python, runs in           │         │
│  └──────────────────┘        │    intelligence container)    │         │
│                              │                               │         │
│                              │   - Polls all services        │         │
│                              │   - Stores status in DB       │         │
│                              │   - Triggers notifications    │         │
│                              └───────────────┬───────────────┘         │
│                                              │                          │
│                                              ▼                          │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │                    Services Monitored                     │          │
│  │                                                          │          │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │          │
│  │  │ Synapse │  │ Immich  │  │ Ollama  │  │ Postgres│     │          │
│  │  │  :8008  │  │  :3001  │  │ :11434  │  │  :5432  │     │          │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │          │
│  │                                                          │          │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                  │          │
│  │  │  Redis  │  │ Immich  │  │  Nginx  │                  │          │
│  │  │  :6379  │  │   ML    │  │   :80   │                  │          │
│  │  └─────────┘  └─────────┘  └─────────┘                  │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                         │
│  ┌──────────────────┐        ┌───────────────────────────────┐         │
│  │   PostgreSQL     │◀───────│   health_status table         │         │
│  │                  │        │   - service_name              │         │
│  │                  │        │   - status (up/degraded/down) │         │
│  │                  │        │   - last_check                │         │
│  │                  │        │   - response_time_ms          │         │
│  └──────────────────┘        └───────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Health Check Logic

```python
SERVICES = {
    'synapse': {
        'name': 'Chat',
        'url': 'http://synapse:8008/_matrix/client/versions',
        'timeout': 5
    },
    'immich': {
        'name': 'Photos',
        'url': 'http://immich_server:3001/api/server-info/ping',
        'timeout': 10
    },
    'ollama': {
        'name': 'AI',
        'url': 'http://ollama:11434/api/version',
        'timeout': 5
    },
    'postgres': {
        'name': 'Database',
        'check': 'pg_isready',
        'timeout': 5
    },
    'redis': {
        'name': 'Cache',
        'check': 'redis-cli ping',
        'timeout': 2
    }
}

STATUS_LEVELS = {
    'healthy': 'Service responding normally',
    'degraded': 'Service slow or partially working',
    'down': 'Service not responding'
}
```

### 3.3 Dashboard Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin` | GET | Dashboard HTML page |
| `/admin/api/status` | GET | JSON status of all services |
| `/admin/api/storage` | GET | Disk usage information |
| `/admin/api/backup` | GET | Backup status summary |
| `/admin/api/restart/<service>` | POST | Restart a service |

### 3.4 File Structure

```
memu-os/
├── services/
│   └── intelligence/
│       └── src/
│           ├── health_monitor.py    # NEW: Health check logic
│           ├── dashboard_routes.py  # NEW: Flask routes for /admin
│           └── bot.py               # MODIFY: Add health alerts
│
├── bootstrap/
│   ├── app.py                       # MODIFY: Add /admin routes
│   └── templates/
│       └── dashboard.html           # NEW: Dashboard template
│
└── nginx/
    └── conf.d/
        └── default.conf             # MODIFY: Add /admin location
```

---

## 4. Success Criteria

### 4.1 Functional Requirements

| Requirement | Metric | Test Method |
|-------------|--------|-------------|
| Dashboard loads | Under 2 seconds | Timing test |
| Status updates | Every 60 seconds | Verify refresh |
| Service detection | All 7 services monitored | Check each |
| Failure notification | Within 5 minutes of failure | Stop service, time alert |
| Restart works | Service recovers | Click restart, verify |
| Storage accurate | Within 1% of actual | Compare with `df` |

### 4.2 Non-Functional Requirements

| Requirement | Metric |
|-------------|--------|
| Mobile friendly | Works on phone browser |
| No authentication | Local network only (via Tailscale) |
| Low overhead | < 1% CPU for monitoring |
| Graceful degradation | Dashboard works even if some services down |

### 4.3 Definition of Done

- [ ] All tests pass
- [ ] Dashboard accessible at /admin
- [ ] All 7 services show correct status
- [ ] Bot sends alert when service fails
- [ ] Restart button works
- [ ] Storage usage displays correctly
- [ ] Works on mobile browser
- [ ] Documentation updated

---

## 5. Implementation Plan

### 5.1 Sessions

| Session | Deliverable | Effort |
|---------|-------------|--------|
| 1 | Database schema for health_status table | 1 hour |
| 2 | Health monitor module (check all services) | 2 hours |
| 3 | Dashboard HTML template | 2 hours |
| 4 | Dashboard API routes | 2 hours |
| 5 | Bot health alerts | 1 hour |
| 6 | Service restart functionality | 1 hour |
| 7 | Storage monitoring | 1 hour |
| 8 | Documentation and QA | 1 hour |

### 5.2 Session Details

**Session 1: Database Schema**
- Add `health_status` table to memory.py
- Fields: service_name, status, last_check, response_time_ms, error_message
- Add query methods: record_health_check(), get_current_status(), get_health_history()

**Session 2: Health Monitor Module**
- Create `health_monitor.py`
- Implement check for each service type (HTTP, PostgreSQL, Redis)
- Background loop checking every 60 seconds
- Store results in database

**Session 3: Dashboard Template**
- Create `dashboard.html` with service cards
- Color-coded status (green/yellow/red)
- Backup status section
- Storage usage bar
- Auto-refresh every 30 seconds

**Session 4: Dashboard API Routes**
- Add routes to bootstrap/app.py or create dashboard_routes.py
- `/admin` - serve dashboard HTML
- `/admin/api/status` - JSON status
- `/admin/api/storage` - disk usage
- Update nginx to route /admin

**Session 5: Bot Health Alerts**
- Add health check to bot's background loop
- Send alert when service changes from healthy to degraded/down
- Rate limit notifications (don't spam)
- Include dashboard link in message

**Session 6: Service Restart**
- `/admin/api/restart/<service>` endpoint
- Execute `docker restart <container>`
- Return success/failure
- Security: only allow from local network

**Session 7: Storage Monitoring**
- Get disk usage for key directories
- Photos, backups, database
- Calculate percentage used
- Warn at 80%, critical at 90%

**Session 8: Documentation and QA**
- Update user guide with dashboard info
- Test on mobile browser
- Test failure scenarios
- Update architecture docs

### 5.3 Dependencies

```
Session 1 (DB Schema)
    │
    └──▶ Session 2 (Health Monitor) ──▶ Session 5 (Bot Alerts)
                │
                └──▶ Session 3 (Template) ──▶ Session 4 (Routes) ──▶ Session 6 (Restart)
                                                      │
                                                      └──▶ Session 7 (Storage)

Session 8 (Docs) - After all others
```

---

## 6. Technical Details

### 6.1 Database Schema

```sql
CREATE TABLE IF NOT EXISTS health_status (
    id SERIAL PRIMARY KEY,
    service_name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'healthy', 'degraded', 'down'
    response_time_ms INT,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_service ON health_status(service_name);
CREATE INDEX IF NOT EXISTS idx_health_checked ON health_status(checked_at DESC);

-- Keep only last 24 hours of history
-- Cleanup job: DELETE FROM health_status WHERE checked_at < NOW() - INTERVAL '24 hours'
```

### 6.2 Health Check Implementation

```python
class HealthMonitor:
    async def check_http_service(self, name: str, url: str, timeout: int) -> dict:
        """Check HTTP-based service health."""
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                elapsed = (time.time() - start) * 1000

                if response.status_code == 200:
                    return {'status': 'healthy', 'response_time_ms': int(elapsed)}
                else:
                    return {'status': 'degraded', 'response_time_ms': int(elapsed),
                            'error': f'HTTP {response.status_code}'}
        except httpx.TimeoutException:
            return {'status': 'degraded', 'error': 'Timeout'}
        except Exception as e:
            return {'status': 'down', 'error': str(e)}

    async def check_all_services(self) -> dict:
        """Check all services and return status dict."""
        results = {}
        for service_id, config in SERVICES.items():
            if 'url' in config:
                results[service_id] = await self.check_http_service(
                    service_id, config['url'], config['timeout']
                )
            # ... handle other check types
        return results
```

### 6.3 Dashboard HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Memu Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        /* Mobile-first responsive design */
        /* Use brand colors from BRAND.md */
    </style>
</head>
<body>
    <header>
        <h1>Memu Health Dashboard</h1>
        <button onclick="refresh()">Refresh</button>
    </header>

    <section id="services">
        <h2>Services</h2>
        <div class="service-grid">
            <!-- Populated by JavaScript -->
        </div>
    </section>

    <section id="backup">
        <h2>Backup Status</h2>
        <!-- Backup info -->
    </section>

    <section id="storage">
        <h2>Storage</h2>
        <!-- Storage bar -->
    </section>

    <script>
        async function loadStatus() {
            const response = await fetch('/admin/api/status');
            const data = await response.json();
            renderServices(data);
        }

        // Auto-refresh every 30 seconds
        setInterval(loadStatus, 30000);
        loadStatus();
    </script>
</body>
</html>
```

---

## 7. Security Considerations

- Dashboard only accessible via Tailscale (not public internet)
- No authentication required (trusted network)
- Restart actions logged
- No sensitive data displayed (no passwords, tokens)
- Rate limiting on restart endpoint

---

## 8. Future Enhancements

- Historical graphs (uptime over time)
- Email/SMS alerts for critical issues
- Auto-restart failed services
- Resource usage trends
- Log viewer
- Configuration editor

---

## Appendix: Related Files

- `docker-compose.yml` - Service health check definitions
- `services/intelligence/src/bot.py` - Bot notification code
- `bootstrap/app.py` - Web server for dashboard
- `.claude/BRAND.md` - UI styling guidelines
