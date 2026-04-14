#!/bin/bash
# =============================================================================
# Memu System Backup Script
# =============================================================================
# Creates a complete backup of all Memu data:
# - PostgreSQL database (chat history, Immich metadata, bot memory)
# - Photos and videos (Immich uploads)
# - Synapse media and encryption keys
# - Ollama AI models
# - Configuration files
#
# Usage: ./backup.sh
# Scheduled via systemd timer (memu-backup.timer) at 2am daily
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
# BACKUP_DIR and TMPDIR can be overridden via environment (e.g. in the
# systemd unit) to point at a secondary drive like /mnt/memu-data/backups.
# If TMPDIR is set, `mktemp -d` below will use it automatically.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
RETENTION_COUNT="${BACKUP_RETENTION_COUNT:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="memu_backup_$TIMESTAMP.tar.gz"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILE"
TEMP_DIR=$(mktemp -d)
START_TIME=$(date +%s)

# Load environment variables if .env exists
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
fi

UPLOAD_LOCATION="${UPLOAD_LOCATION:-$PROJECT_DIR/photos}"

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Record backup status to database
record_backup_status() {
    local status="$1"
    local error_msg="$2"
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local size=0

    if [ -f "$BACKUP_PATH" ]; then
        size=$(stat -f%z "$BACKUP_PATH" 2>/dev/null || stat -c%s "$BACKUP_PATH" 2>/dev/null || echo "0")
    fi

    # Call the notify script if it exists
    if [ -f "$SCRIPT_DIR/backup-notify.sh" ]; then
        "$SCRIPT_DIR/backup-notify.sh" "$BACKUP_FILE" "$size" "$status" "$duration" "$error_msg"
    fi
}

# =============================================================================
# Main Backup Process
# =============================================================================

log "=== Memu System Backup ==="
log "Timestamp: $TIMESTAMP"
log "Backup location: $BACKUP_PATH"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create staging directory structure
mkdir -p "$TEMP_DIR/config"
mkdir -p "$TEMP_DIR/synapse"
mkdir -p "$TEMP_DIR/photos"

# -----------------------------------------------------------------------------
# Step 1: Backup configuration files (no downtime needed)
# -----------------------------------------------------------------------------
log "Step 1/5: Backing up configuration files..."

# Copy .env (contains secrets - essential for restore)
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "$TEMP_DIR/config/"
    log "  - .env"
fi

# Copy Element config
if [ -f "$PROJECT_DIR/element-config.json" ]; then
    cp "$PROJECT_DIR/element-config.json" "$TEMP_DIR/config/"
    log "  - element-config.json"
fi

# Copy nginx configuration
if [ -d "$PROJECT_DIR/nginx" ]; then
    cp -r "$PROJECT_DIR/nginx" "$TEMP_DIR/config/"
    log "  - nginx/"
fi

# -----------------------------------------------------------------------------
# Step 2: Backup Synapse data (media, keys)
# -----------------------------------------------------------------------------
log "Step 2/5: Backing up Synapse data..."

if [ -d "$PROJECT_DIR/synapse" ]; then
    # Copy everything except large log files
    rsync -a --exclude='*.log' --exclude='homeserver.log*' \
        "$PROJECT_DIR/synapse/" "$TEMP_DIR/synapse/" 2>/dev/null || \
        cp -r "$PROJECT_DIR/synapse/"* "$TEMP_DIR/synapse/" 2>/dev/null || true
    log "  - synapse/ (media, keys, config)"
else
    warn "  - synapse/ directory not found, skipping"
fi

# -----------------------------------------------------------------------------
# Step 3: Backup photos (can be large, may take time)
# -----------------------------------------------------------------------------
log "Step 3/5: Backing up photos..."

if [ -d "$UPLOAD_LOCATION" ]; then
    # Use rsync for efficient copy, fall back to cp
    rsync -a "$UPLOAD_LOCATION/" "$TEMP_DIR/photos/" 2>/dev/null || \
        cp -r "$UPLOAD_LOCATION/"* "$TEMP_DIR/photos/" 2>/dev/null || true

    photo_count=$(find "$TEMP_DIR/photos" -type f 2>/dev/null | wc -l | tr -d ' ')
    log "  - $photo_count files from photos/"
else
    warn "  - Photos directory not found at $UPLOAD_LOCATION, skipping"
fi

# -----------------------------------------------------------------------------
# Step 4: Hot backup of PostgreSQL (no downtime)
# -----------------------------------------------------------------------------
# pg_dumpall captures ALL databases (immich, synapse, memu_core, etc) in a
# single consistent SQL dump. The database stays up — no compose-down,
# which means no boot-ordering race the next morning.
log "Step 4/5: Backing up database (hot backup - services stay running)..."

mkdir -p "$TEMP_DIR/database"

cd "$PROJECT_DIR"

docker exec memu_postgres pg_dumpall -U "${DB_USER:-memu_user}" > "$TEMP_DIR/database/all_databases.sql" 2>/dev/null || {
    error "Failed to backup database"
    record_backup_status "failed" "pg_dumpall failed"
    exit 1
}

log "  - PostgreSQL (all databases via pg_dumpall)"

# -----------------------------------------------------------------------------
# Step 5: Backup Ollama models (no downtime needed - read-only copy)
# -----------------------------------------------------------------------------
log "Step 5/5: Backing up AI models..."

docker run --rm \
    -v memu-suite_ollama_data:/data/ollama:ro \
    -v "$TEMP_DIR:/backup" \
    alpine sh -c "
        mkdir -p /backup/ollama
        cp -a /data/ollama/. /backup/ollama/ 2>/dev/null || true
    " || {
    warn "Failed to backup Ollama models (non-fatal - can re-download)"
}

log "  - ollama (AI models)"

# -----------------------------------------------------------------------------
# Create metadata.json
# -----------------------------------------------------------------------------
log "Creating backup metadata..."

cat > "$TEMP_DIR/metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "created_at": "$(date -Iseconds)",
    "memu_version": "1.1.0",
    "backup_format": "sql_dump",
    "hostname": "$(hostname)",
    "data_sources": [
        "database_sql",
        "ollama",
        "photos",
        "synapse",
        "config"
    ],
    "photo_count": $photo_count,
    "notes": "Created by Memu backup script"
}
EOF

# -----------------------------------------------------------------------------
# Create final archive
# -----------------------------------------------------------------------------
log "Creating backup archive..."

cd "$TEMP_DIR"
tar czf "$BACKUP_PATH" .

BACKUP_SIZE=$(stat -f%z "$BACKUP_PATH" 2>/dev/null || stat -c%s "$BACKUP_PATH" 2>/dev/null || echo "0")
BACKUP_SIZE_HUMAN=$(numfmt --to=iec-i --suffix=B "$BACKUP_SIZE" 2>/dev/null || echo "${BACKUP_SIZE} bytes")

log "Archive created: $BACKUP_SIZE_HUMAN"

# -----------------------------------------------------------------------------
# Prune old backups (keep only RETENTION_COUNT most recent)
# -----------------------------------------------------------------------------
log "Pruning old backups (keeping $RETENTION_COUNT most recent)..."

cd "$BACKUP_DIR"
backup_count=$(ls -1 memu_backup_*.tar.gz 2>/dev/null | wc -l | tr -d ' ')

if [ "$backup_count" -gt "$RETENTION_COUNT" ]; then
    delete_count=$((backup_count - RETENTION_COUNT))
    ls -1t memu_backup_*.tar.gz | tail -n "$delete_count" | while read old_backup; do
        log "  - Removing: $old_backup"
        rm -f "$old_backup"
    done
fi

# -----------------------------------------------------------------------------
# Record success
# -----------------------------------------------------------------------------
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

record_backup_status "success" ""

log ""
log "=== Backup Complete ==="
log "File: $BACKUP_PATH"
log "Size: $BACKUP_SIZE_HUMAN"
log "Duration: ${DURATION}s"
log ""
log "To restore, run: ./scripts/restore.sh"
