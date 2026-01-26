# Automated Backup System - Feature Specification

**Status:** In Development
**Version:** 1.0
**Last Updated:** 2025-01-26

---

## 1. Overview

### 1.1 Problem Statement

Memu families currently have no reliable way to:
- Know if their data is backed up
- Receive alerts if backups fail
- Easily backup to external media (USB drives)
- Restore their data after a hardware failure

The existing `backup.sh` script:
- Only backs up PostgreSQL data and Ollama models
- **Misses critical data:** Photos, Synapse media/keys, configuration files
- Requires manual terminal execution
- Provides no status visibility on headless systems
- Has no restore capability

### 1.2 Solution

A complete automated backup system with:
- Full data backup (photos, chat, AI, config)
- Daily automated scheduling
- Status visibility via Element bot
- Failure notifications
- USB drive support for offsite backups
- Interactive restore capability

---

## 2. User Stories

### 2.1 Core Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US1 | Family member | check backup status via chat | I know my data is safe without using terminal |
| US2 | Family member | be notified if backup fails | I can take action before data loss |
| US3 | Non-technical spouse | get weekly USB reminder | I remember to create offsite backup |
| US4 | Family member | plug in USB and have backup copied | offsite backup is effortless |
| US5 | System admin | have daily automated backups | data is protected without manual intervention |
| US6 | System admin | restore from backup after failure | I can recover from hardware issues |
| US7 | Family member | know photos are backed up | my memories are protected |

### 2.2 User Interactions

**Checking Status (US1):**
```
User: /backup-status

Bot (healthy):
"Backup Status:
Last backup: Today 2:05 AM (312 MB)
Local backups: 7 stored (2.1 GB total)
USB backup: 2 days ago
Health: All systems healthy"

Bot (warning):
"Backup Status:
Last backup: Today 2:05 AM (312 MB)
USB backup: 12 days ago
Health: USB backup overdue - plug in your backup drive!"
```

**Failure Notification (US2):**
```
Bot (automatically):
"Backup Alert
Last night's backup failed: Disk full
Action needed: Free up space or add storage

Use /backup-status for details"
```

**Weekly USB Reminder (US3):**
```
Bot (Sunday 10am, if no USB backup in 7+ days):
"Weekly Backup Reminder
It's been 9 days since your last USB backup.

Plug in your backup drive to save a copy of your family's data.
Current backup size: ~2.1 GB"
```

**USB Backup Confirmation (US4):**
```
Bot (after USB detected and copy complete):
"USB Backup Complete
Copied latest backup to 'SanDisk_Family' drive.
File: memu_backup_20250126_020500.tar.gz (312 MB)

Safe to remove the drive."
```

---

## 3. Architecture

### 3.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           MEMU BACKUP SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐        ┌───────────────────────────────┐         │
│  │  systemd timer   │──2am──▶│  scripts/backup.sh            │         │
│  │  (memu-backup)   │        │  - Stops services briefly     │         │
│  └──────────────────┘        │  - Creates tar.gz archive     │         │
│                              │  - Restarts services          │         │
│                              │  - Writes status to DB        │         │
│                              └───────────────┬───────────────┘         │
│                                              │                          │
│  ┌──────────────────┐                        ▼                          │
│  │  USB Detection   │        ┌───────────────────────────────┐         │
│  │  (udev rule)     │──────▶│  backup_manager.py            │         │
│  └──────────────────┘        │  - Monitor backup health      │         │
│                              │  - Handle USB copy            │         │
│                              │  - Query backup status        │         │
│                              │  - Send notifications         │         │
│  ┌──────────────────┐        └───────────────┬───────────────┘         │
│  │  Element Chat    │                        │                          │
│  │  /backup-status  │◀───────────────────────┘                          │
│  └──────────────────┘                                                   │
│                              ┌───────────────────────────────┐         │
│                              │  PostgreSQL (backup_history)  │         │
│                              │  - timestamp, size, status    │         │
│                              │  - usb_copied_at, errors      │         │
│                              └───────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow

```
1. SCHEDULED BACKUP (2am daily)
   systemd timer → backup.sh → creates archive → writes DB record → exits

   On failure: backup.sh writes error to DB
   backup_manager.py detects error → sends Matrix message

2. USB DETECTION
   USB inserted → udev rule fires → creates marker file
   backup_manager.py detects → copies backup → sends confirmation

3. STATUS CHECK
   User: /backup-status → bot.py → backup_manager.py → queries DB → response

4. WEEKLY REMINDER
   backup_manager.py checks last USB timestamp weekly → sends reminder if > 7 days
```

### 3.3 What Gets Backed Up

| Data Type | Location | Backed Up |
|-----------|----------|-----------|
| Photos/Videos | `./photos` | Yes |
| PostgreSQL (chat, metadata) | `pgdata` volume | Yes |
| Synapse media/keys | `./synapse` | Yes |
| Ollama models | `ollama_data` volume | Yes |
| Config files | `.env`, `element-config.json`, `nginx/` | Yes |
| Redis cache | `redisdata` volume | No (ephemeral) |
| Immich ML models | `model_cache` volume | No (re-downloadable) |

### 3.4 Backup Archive Structure

```
memu_backup_YYYYMMDD_HHMMSS.tar.gz
├── pgdata/              PostgreSQL data
├── ollama/              AI models
├── photos/              Immich uploads
├── synapse/             Matrix media and keys
├── config/
│   ├── .env
│   ├── element-config.json
│   └── nginx/
└── metadata.json        Backup info (timestamp, version, checksums)
```

### 3.5 File Changes

| File | Action | Purpose |
|------|--------|---------|
| `scripts/backup.sh` | Modify | Complete backup of all data |
| `scripts/restore.sh` | New | Interactive restore |
| `scripts/backup-notify.sh` | New | Write status to DB |
| `services/intelligence/src/backup_manager.py` | New | Backup orchestration |
| `services/intelligence/src/bot.py` | Modify | Add `/backup-status` command |
| `services/intelligence/src/memory.py` | Modify | Add `backup_history` table |
| `services/systemd/memu-backup.service` | New | Oneshot backup service |
| `services/systemd/memu-backup.timer` | New | Daily 2am timer |
| `udev/99-memu-usb.rules` | New | USB detection |

---

## 4. Success Criteria

### 4.1 Functional Requirements

| Requirement | Metric | Test Method |
|-------------|--------|-------------|
| Backup completeness | All 5 data sources included | Verify tar contents |
| Backup automation | Runs daily at 2am | Check systemd timer |
| Bot status command | Response within 5 seconds | Timing test |
| Failure notification | Alert within 15 minutes | Inject failure |
| USB detection | Detected within 30 seconds | Manual test |
| USB copy | Completes without error | Verify file on USB |
| Restore script | Successfully restores all data | Full restore test |

### 4.2 Non-Functional Requirements

| Requirement | Metric |
|-------------|--------|
| Backup time | Under 30 minutes for 50GB data |
| Service downtime | Under 5 minutes during backup |
| Disk usage | Retain 7 local backups, auto-prune older |
| Error handling | All errors logged and notified |

### 4.3 Definition of Done

- [ ] All tests pass (unit + integration)
- [ ] Manual QA by non-technical family member
- [ ] Documentation updated (user guide, architecture)
- [ ] No increase in startup time
- [ ] Works on fresh install

---

## 5. Test Plan

### 5.1 Test Philosophy

Following TDD (Test-Driven Development):
1. Write tests first
2. Tests define expected behavior
3. Implementation makes tests pass
4. Refactor while keeping tests green

### 5.2 Test Categories

| Category | Framework | Files |
|----------|-----------|-------|
| Python unit tests | pytest | `tests/test_backup_manager.py`, `tests/test_memory.py` |
| Bot command tests | pytest | `tests/test_bot.py` |
| Bash script tests | BATS | `tests/test_backup.bats` |
| Integration tests | pytest + subprocess | `tests/integration/test_backup_integration.py` |

### 5.3 Key Test Cases

**Backup Manager Tests:**
1. `test_get_backup_status_healthy` - Status shows green when backups working
2. `test_get_backup_status_usb_overdue` - Warning when USB > 7 days
3. `test_get_backup_status_failed` - Critical when backup failed
4. `test_should_send_usb_reminder` - Reminder logic works
5. `test_format_status_message` - Human-readable output

**Bot Command Tests:**
6. `test_process_message_backup_status` - Bot responds to command
7. `test_backup_status_formatting` - Response is user-friendly

**Database Tests:**
8. `test_init_db_creates_backup_table` - Table created on init
9. `test_record_backup` - Backup recorded correctly
10. `test_get_backup_count` - Count query works

**Bash Script Tests:**
11. `test_backup_script_idempotent` - Can run twice safely
12. `test_backup_creates_directory` - Creates ./backups if missing
13. `test_backup_includes_metadata` - metadata.json in archive
14. `test_backup_pruning` - Keeps only 7 backups

**Integration Tests:**
15. `test_backup_creates_valid_archive` - Full archive verification
16. `test_backup_records_to_database` - Status in DB after run
17. `test_restore_works` - Full restore successful

---

## 6. Implementation Plan

### 6.1 Sessions

| Session | Deliverable | Effort |
|---------|-------------|--------|
| 1 | Database schema for backup tracking | 2 hours |
| 2 | Enhanced backup script (all data sources) | 2 hours |
| 3 | Backup manager Python module | 2 hours |
| 4 | `/backup-status` bot command | 2 hours |
| 5 | Scheduled daily backups (systemd) | 2 hours |
| 6 | Failure notifications via bot | 2 hours |
| 7 | USB detection and copy | 2 hours |
| 8 | Weekly USB reminder | 1 hour |
| 9 | Restore script | 2 hours |
| 10 | Documentation and QA | 2 hours |

### 6.2 Dependencies

```
Session 1 (DB Schema)
    │
    ├──▶ Session 2 (Backup Script) ──▶ Session 5 (Scheduled) ──▶ Session 7 (USB) ──▶ Session 8 (Reminder)
    │
    └──▶ Session 3 (Manager) ──▶ Session 4 (Bot Commands)
                            └──▶ Session 6 (Notifications)

Session 9 (Restore) - After Session 2
Session 10 (Docs) - After all others
```

---

## 7. Configuration

### 7.1 New Environment Variables

```bash
# --- BACKUP ---
BACKUP_DIR=./backups
BACKUP_RETENTION_COUNT=7
BACKUP_NOTIFICATION_ROOM=!roomid:server
```

### 7.2 Database Schema Addition

```sql
CREATE TABLE IF NOT EXISTS backup_history (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    status TEXT NOT NULL,  -- 'success', 'failed', 'in_progress'
    error TEXT,
    duration_seconds INT,
    usb_copied_at TIMESTAMP,
    notification_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backup_created ON backup_history(created_at DESC);
```

---

## 8. Design Decisions

### 8.1 Why Stop Services During Backup?

**Decision:** Stop all containers during backup.

**Rationale:** Ensures data consistency across PostgreSQL, photos, and Synapse.

**Trade-off:** ~2-5 minutes downtime at 2am. Acceptable for family use.

**Future:** Implement hot backup using pg_dump + rsync for zero-downtime.

### 8.2 Why 7 Backup Retention?

**Decision:** Keep 7 local backups.

**Rationale:** Covers "I deleted something last week" scenarios. ~14GB storage for typical family.

### 8.3 Why Sunday 10am for USB Reminder?

**Decision:** Sunday 10am weekly reminder.

**Rationale:** Weekend morning when family is likely home, after breakfast, before activities.

### 8.4 Why udev for USB Detection?

**Decision:** Use udev rules rather than polling.

**Rationale:** Event-driven, instant detection, no CPU overhead, standard Linux mechanism.

---

## 9. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Backup takes too long | Future: incremental backups |
| USB not detected | Provide manual copy command fallback |
| Services don't restart | Health checks with timeout and notification |
| Disk fills up | Aggressive pruning, size warnings in status |
| Restore fails | Test restore process on every release |

---

## 10. Future Enhancements

- Hot backup (zero downtime) using pg_dump + rsync
- Incremental backups for large photo libraries
- Offsite backup to cloud (encrypted, user-provided key)
- Backup verification (automated restore test)
- Admin dashboard for visual status

---

## Appendix: Related Files

- `scripts/backup.sh` - Current backup script
- `services/intelligence/src/bot.py` - Bot command handlers
- `services/intelligence/src/memory.py` - Database operations
- `docker-compose.yml` - Volume definitions
- `docs/user_guide.md` - User documentation (to update)
- `docs/architecture.md` - System architecture (to update)
