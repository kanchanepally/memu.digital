#!/bin/bash
# =============================================================================
# Memu Backup Notification Script
# =============================================================================
# Records backup status to the PostgreSQL database.
# Called by backup.sh after backup completes or fails.
#
# Usage: ./backup-notify.sh <filename> <size_bytes> <status> <duration> [error_msg]
# =============================================================================

set -e

FILENAME="$1"
SIZE_BYTES="$2"
STATUS="$3"
DURATION="$4"
ERROR_MSG="${5:-}"

# Validate arguments
if [ -z "$FILENAME" ] || [ -z "$SIZE_BYTES" ] || [ -z "$STATUS" ] || [ -z "$DURATION" ]; then
    echo "Usage: $0 <filename> <size_bytes> <status> <duration> [error_msg]"
    exit 1
fi

# Get script directory and project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_DIR/.env" ]; then
    source "$PROJECT_DIR/.env"
fi

# Database connection details
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-immich}"
DB_USER="${DB_USER:-memu_user}"
DB_PASSWORD="${DB_PASSWORD:-}"

# Escape single quotes in error message for SQL
ERROR_MSG_ESCAPED=$(echo "$ERROR_MSG" | sed "s/'/''/g")

# Build SQL query
if [ -n "$ERROR_MSG" ]; then
    SQL="INSERT INTO backup_history (filename, size_bytes, status, duration_seconds, error) VALUES ('$FILENAME', $SIZE_BYTES, '$STATUS', $DURATION, '$ERROR_MSG_ESCAPED');"
else
    SQL="INSERT INTO backup_history (filename, size_bytes, status, duration_seconds) VALUES ('$FILENAME', $SIZE_BYTES, '$STATUS', $DURATION);"
fi

# Execute via Docker if container is running, otherwise try direct connection
if docker ps --format '{{.Names}}' | grep -q 'memu_postgres'; then
    # Container is running, use docker exec
    docker exec memu_postgres psql -U "$DB_USER" -d "$DB_NAME" -c "$SQL" 2>/dev/null
elif command -v psql &> /dev/null; then
    # Try direct connection
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "$SQL" 2>/dev/null
else
    # Can't connect to database, log to file instead
    echo "[$(date -Iseconds)] $STATUS: $FILENAME ($SIZE_BYTES bytes, ${DURATION}s) $ERROR_MSG" >> "$PROJECT_DIR/backups/backup.log"
fi

exit 0
