#!/bin/bash
# =============================================================================
# Memu USB Backup Script
# =============================================================================
# Copies the latest backup to a USB drive.
#
# Usage: ./usb-backup.sh [device]
#        If device not specified, auto-detects mounted USB drives.
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
USB_MOUNT_BASE="/media"
MARKER_FILE="/tmp/memu/usb_detected"
RESULT_FILE="/tmp/memu/usb_result"

# Find the latest backup
find_latest_backup() {
    local latest=$(ls -1t "$BACKUP_DIR"/memu_backup_*.tar.gz 2>/dev/null | head -1)
    if [ -z "$latest" ]; then
        error "No backups found in $BACKUP_DIR"
        exit 1
    fi
    echo "$latest"
}

# Find mounted USB drive
find_usb_mount() {
    local device="$1"

    # If device specified, find its mount point
    if [ -n "$device" ]; then
        local mount_point=$(findmnt -n -o TARGET "$device" 2>/dev/null)
        if [ -n "$mount_point" ]; then
            echo "$mount_point"
            return
        fi

        # Try to mount it
        local temp_mount="/mnt/memu_usb_$$"
        mkdir -p "$temp_mount"
        if mount "$device" "$temp_mount" 2>/dev/null; then
            echo "$temp_mount"
            return
        fi
    fi

    # Auto-detect: look for USB mounts
    for mount_dir in /media/* /mnt/*; do
        if [ -d "$mount_dir" ] && mountpoint -q "$mount_dir" 2>/dev/null; then
            # Check if it's a USB device
            local dev=$(findmnt -n -o SOURCE "$mount_dir" 2>/dev/null)
            if [ -n "$dev" ] && udevadm info --query=property "$dev" 2>/dev/null | grep -q "ID_USB_DRIVER=usb-storage"; then
                echo "$mount_dir"
                return
            fi
        fi
    done

    # Also check /run/media/$USER/*
    for mount_dir in /run/media/*/; do
        if [ -d "$mount_dir" ] && mountpoint -q "$mount_dir" 2>/dev/null; then
            echo "$mount_dir"
            return
        fi
    done

    return 1
}

# Get USB drive label
get_usb_label() {
    local mount_point="$1"
    local device=$(findmnt -n -o SOURCE "$mount_point" 2>/dev/null)

    if [ -n "$device" ]; then
        local label=$(lsblk -n -o LABEL "$device" 2>/dev/null | head -1)
        if [ -n "$label" ]; then
            echo "$label"
            return
        fi
    fi

    # Fall back to mount point name
    basename "$mount_point"
}

# Copy backup to USB
copy_to_usb() {
    local backup="$1"
    local usb_mount="$2"
    local backup_name=$(basename "$backup")

    log "Copying backup to USB drive..."
    log "  Source: $backup"
    log "  Destination: $usb_mount"

    # Create memu_backups directory on USB
    mkdir -p "$usb_mount/memu_backups"

    # Copy with progress
    if command -v rsync &> /dev/null; then
        rsync -ah --progress "$backup" "$usb_mount/memu_backups/"
    else
        cp "$backup" "$usb_mount/memu_backups/"
    fi

    # Sync to ensure write completes
    sync

    log "Backup copied successfully!"

    # Get size
    local size=$(du -h "$usb_mount/memu_backups/$backup_name" 2>/dev/null | cut -f1)
    echo "$size"
}

# Write result for backup manager to read
write_result() {
    local status="$1"
    local message="$2"
    local label="$3"
    local filename="$4"
    local size="$5"

    cat > "$RESULT_FILE" << EOF
{
    "status": "$status",
    "message": "$message",
    "usb_label": "$label",
    "filename": "$filename",
    "size": "$size",
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# =============================================================================
# Main
# =============================================================================

DEVICE="$1"

# Check for marker file (from udev)
if [ -f "$MARKER_FILE" ] && [ -z "$DEVICE" ]; then
    DEVICE=$(cat "$MARKER_FILE")
    rm -f "$MARKER_FILE"
fi

log "=== Memu USB Backup ==="

# Find USB mount point
USB_MOUNT=$(find_usb_mount "$DEVICE")

if [ -z "$USB_MOUNT" ]; then
    error "No USB drive found. Please insert a USB drive and try again."
    write_result "error" "No USB drive found" "" "" ""
    exit 1
fi

USB_LABEL=$(get_usb_label "$USB_MOUNT")
log "Found USB drive: $USB_LABEL ($USB_MOUNT)"

# Find latest backup
LATEST_BACKUP=$(find_latest_backup)
BACKUP_NAME=$(basename "$LATEST_BACKUP")
log "Latest backup: $BACKUP_NAME"

# Copy to USB
SIZE=$(copy_to_usb "$LATEST_BACKUP" "$USB_MOUNT")

# Write success result
write_result "success" "Backup copied to USB" "$USB_LABEL" "$BACKUP_NAME" "$SIZE"

# Update database - mark latest backup as USB copied
if [ -f "$SCRIPT_DIR/backup-notify.sh" ]; then
    # Get backup ID from database and update usb_copied_at
    # For now, we'll let the backup_manager handle this via the result file
    :
fi

log ""
log "=== USB Backup Complete ==="
log "Safe to remove the USB drive."
