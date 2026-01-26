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
log "Step 1/6: Backing up configuration files..."

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
log "Step 2/6: Backing up Synapse data..."

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
log "Step 3/6: Backing up photos..."

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
# Step 4: Stop services for consistent database backup
# -----------------------------------------------------------------------------
log "Step 4/6: Stopping services for database consistency..."

cd "$PROJECT_DIR"
docker compose down 2>/dev/null || docker-compose down 2>/dev/null || {
    error "Failed to stop services"
    record_backup_status "failed" "Failed to stop Docker services"
    exit 1
}

# -----------------------------------------------------------------------------
# Step 5: Backup Docker volumes (PostgreSQL, Ollama)
# -----------------------------------------------------------------------------
log "Step 5/6: Backing up database and AI models..."

# Create volume backups using Alpine container
docker run --rm \
    -v memu-suite_pgdata:/data/pgdata:ro \
    -v memu-suite_ollama_data:/data/ollama:ro \
    -v "$TEMP_DIR:/backup" \
    alpine sh -c "
        mkdir -p /backup/pgdata /backup/ollama
        cp -a /data/pgdata/. /backup/pgdata/ 2>/dev/null || true
        cp -a /data/ollama/. /backup/ollama/ 2>/dev/null || true
    " || {
    error "Failed to backup Docker volumes"
    # Restart services before exiting
    docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null
    record_backup_status "failed" "Failed to backup Docker volumes"
    exit 1
}

log "  - pgdata (PostgreSQL)"
log "  - ollama (AI models)"

# -----------------------------------------------------------------------------
# Step 6: Restart services
# -----------------------------------------------------------------------------
log "Step 6/6: Restarting services..."

docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null || {
    error "Failed to restart services"
    record_backup_status "failed" "Failed to restart Docker services"
    exit 1
}

# -----------------------------------------------------------------------------
# Create metadata.json
# -----------------------------------------------------------------------------
log "Creating backup metadata..."

cat > "$TEMP_DIR/metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "created_at": "$(date -Iseconds)",
    "memu_version": "1.0.0",
    "hostname": "$(hostname)",
    "data_sources": [
        "pgdata",
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
