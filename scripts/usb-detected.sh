#!/bin/bash
# =============================================================================
# Memu USB Detection Handler
# =============================================================================
# Called by udev when a USB drive is inserted.
# Creates a marker file for the backup manager to pick up.
#
# Usage: Called automatically by udev rule
# =============================================================================

DEVICE="$1"
MARKER_DIR="/tmp/memu"
MARKER_FILE="$MARKER_DIR/usb_detected"

# Create marker directory if needed
mkdir -p "$MARKER_DIR"

# Log the detection
echo "$(date -Iseconds) USB device detected: $DEVICE" >> "$MARKER_DIR/usb.log"

# Create marker file with device info
echo "$DEVICE" > "$MARKER_FILE"

# The backup_manager.py will pick this up and handle the copy
exit 0
