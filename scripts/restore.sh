#!/bin/bash
# =============================================================================
# Memu System Restore Script
# =============================================================================
# Restores a Memu system from a backup archive.
#
# IMPORTANT: This is a destructive operation. All current data will be replaced
# with the backup data.
#
# Usage: ./restore.sh [backup_file]
#        If no backup file specified, shows list of available backups.
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
TEMP_DIR=""

# Cleanup function
cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        log "Cleaning up temporary files..."
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# =============================================================================
# Functions
# =============================================================================

list_backups() {
    echo ""
    echo "Available backups in $BACKUP_DIR:"
    echo ""

    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR"/*.tar.gz 2>/dev/null)" ]; then
        error "No backups found in $BACKUP_DIR"
        exit 1
    fi

    local i=1
    for backup in $(ls -1t "$BACKUP_DIR"/memu_backup_*.tar.gz 2>/dev/null); do
        local filename=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local date_part=$(echo "$filename" | sed 's/memu_backup_\([0-9]*\)_\([0-9]*\).*/\1/')
        local formatted_date=$(echo "$date_part" | sed 's/\([0-9]\{4\}\)\([0-9]\{2\}\)\([0-9]\{2\}\)/\1-\2-\3/')

        printf "  %2d) %s (%s) - %s\n" "$i" "$filename" "$size" "$formatted_date"
        i=$((i + 1))
    done
    echo ""
}

select_backup() {
    local backups=($(ls -1t "$BACKUP_DIR"/memu_backup_*.tar.gz 2>/dev/null))
    local count=${#backups[@]}

    if [ "$count" -eq 0 ]; then
        error "No backups found"
        exit 1
    fi

    echo -n "Enter backup number (1-$count) or 'q' to quit: "
    read selection

    if [ "$selection" = "q" ] || [ "$selection" = "Q" ]; then
        echo "Cancelled."
        exit 0
    fi

    if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt "$count" ]; then
        error "Invalid selection"
        exit 1
    fi

    BACKUP_FILE="${backups[$((selection - 1))]}"
}

verify_backup() {
    local backup="$1"

    if [ ! -f "$backup" ]; then
        error "Backup file not found: $backup"
        exit 1
    fi

    info "Verifying backup integrity..."

    # Check if it's a valid tar.gz
    if ! tar -tzf "$backup" > /dev/null 2>&1; then
        error "Backup file is corrupted or not a valid archive"
        exit 1
    fi

    # Check for required directories
    local contents=$(tar -tzf "$backup")
    local has_pgdata=$(echo "$contents" | grep -c "pgdata/" || true)
    local has_config=$(echo "$contents" | grep -c "config/" || true)

    if [ "$has_pgdata" -eq 0 ]; then
        warn "Backup does not contain PostgreSQL data (pgdata/)"
    fi

    if [ "$has_config" -eq 0 ]; then
        warn "Backup does not contain configuration files (config/)"
    fi

    # Check for metadata
    if echo "$contents" | grep -q "metadata.json"; then
        info "Backup metadata found"
        TEMP_DIR=$(mktemp -d)
        tar -xzf "$backup" -C "$TEMP_DIR" metadata.json 2>/dev/null || true
        if [ -f "$TEMP_DIR/metadata.json" ]; then
            local timestamp=$(cat "$TEMP_DIR/metadata.json" | grep -o '"created_at"[^,]*' | cut -d'"' -f4)
            info "Backup created: $timestamp"
        fi
    fi

    log "Backup verification passed"
}

confirm_restore() {
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                        WARNING                                ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  This will REPLACE all current Memu data with the backup."
    echo ""
    echo "  The following will be overwritten:"
    echo "    - PostgreSQL database (chat history, metadata)"
    echo "    - Photos and videos"
    echo "    - Synapse data (Matrix media, encryption keys)"
    echo "    - AI models"
    echo "    - Configuration files"
    echo ""
    echo -e "  ${YELLOW}This action cannot be undone.${NC}"
    echo ""
    echo -n "Type 'RESTORE' to confirm: "
    read confirmation

    if [ "$confirmation" != "RESTORE" ]; then
        echo "Cancelled."
        exit 0
    fi
}

do_restore() {
    local backup="$1"

    TEMP_DIR=$(mktemp -d)

    # Step 1: Stop all services
    log "Step 1/5: Stopping all services..."
    cd "$PROJECT_DIR"
    docker compose down 2>/dev/null || docker-compose down 2>/dev/null || true

    # Step 2: Extract backup
    log "Step 2/5: Extracting backup archive..."
    tar -xzf "$backup" -C "$TEMP_DIR"

    # Step 3: Restore Docker volumes
    log "Step 3/5: Restoring database and AI models..."

    # Remove existing volumes and recreate
    docker volume rm memu-suite_pgdata 2>/dev/null || true
    docker volume rm memu-suite_ollama_data 2>/dev/null || true
    docker volume create memu-suite_pgdata
    docker volume create memu-suite_ollama_data

    # Copy data back using Alpine container
    docker run --rm \
        -v memu-suite_pgdata:/data/pgdata \
        -v memu-suite_ollama_data:/data/ollama \
        -v "$TEMP_DIR:/backup:ro" \
        alpine sh -c "
            cp -a /backup/pgdata/. /data/pgdata/ 2>/dev/null || true
            cp -a /backup/ollama/. /data/ollama/ 2>/dev/null || true
        "

    log "  - pgdata restored"
    log "  - ollama restored"

    # Step 4: Restore files
    log "Step 4/5: Restoring files..."

    # Restore photos
    if [ -d "$TEMP_DIR/photos" ]; then
        local upload_location="${UPLOAD_LOCATION:-$PROJECT_DIR/photos}"
        mkdir -p "$upload_location"
        rsync -a --delete "$TEMP_DIR/photos/" "$upload_location/" 2>/dev/null || \
            cp -r "$TEMP_DIR/photos/"* "$upload_location/" 2>/dev/null || true
        log "  - photos restored"
    fi

    # Restore synapse
    if [ -d "$TEMP_DIR/synapse" ]; then
        mkdir -p "$PROJECT_DIR/synapse"
        rsync -a "$TEMP_DIR/synapse/" "$PROJECT_DIR/synapse/" 2>/dev/null || \
            cp -r "$TEMP_DIR/synapse/"* "$PROJECT_DIR/synapse/" 2>/dev/null || true
        log "  - synapse restored"
    fi

    # Restore config files
    if [ -d "$TEMP_DIR/config" ]; then
        if [ -f "$TEMP_DIR/config/.env" ]; then
            cp "$TEMP_DIR/config/.env" "$PROJECT_DIR/.env"
            log "  - .env restored"
        fi
        if [ -f "$TEMP_DIR/config/element-config.json" ]; then
            cp "$TEMP_DIR/config/element-config.json" "$PROJECT_DIR/element-config.json"
            log "  - element-config.json restored"
        fi
        if [ -d "$TEMP_DIR/config/nginx" ]; then
            cp -r "$TEMP_DIR/config/nginx" "$PROJECT_DIR/"
            log "  - nginx config restored"
        fi
    fi

    # Step 5: Restart services
    log "Step 5/5: Starting services..."
    docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null

    # Wait for services to be healthy
    log "Waiting for services to start..."
    sleep 10

    # Check service health
    if docker ps --format '{{.Names}}' | grep -q 'memu_postgres'; then
        log "  - Database: Running"
    else
        warn "  - Database: Not running"
    fi

    if docker ps --format '{{.Names}}' | grep -q 'memu_synapse'; then
        log "  - Chat: Running"
    else
        warn "  - Chat: Not running"
    fi

    if docker ps --format '{{.Names}}' | grep -q 'memu_photos'; then
        log "  - Photos: Running"
    else
        warn "  - Photos: Not running"
    fi
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Memu System Restore                              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if backup file was provided as argument
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
    # If it's a relative path, try backup directory
    if [ ! -f "$BACKUP_FILE" ] && [ -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        BACKUP_FILE="$BACKUP_DIR/$BACKUP_FILE"
    fi
else
    # Show list and let user select
    list_backups
    select_backup
fi

info "Selected backup: $(basename "$BACKUP_FILE")"
echo ""

# Verify the backup
verify_backup "$BACKUP_FILE"

# Confirm with user
confirm_restore

# Do the restore
echo ""
log "Starting restore process..."
echo ""

do_restore "$BACKUP_FILE"

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              Restore Complete!                                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Your Memu system has been restored from backup."
echo ""
echo "  Next steps:"
echo "    1. Check that all services are running: docker ps"
echo "    2. Test chat at: http://localhost"
echo "    3. Test photos at: http://localhost:2283"
echo ""
echo "  If you encounter issues, check logs with: docker compose logs"
echo ""
