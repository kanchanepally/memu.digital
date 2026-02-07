#!/bin/bash
# =============================================================================
# Memu TLS Certificate Renewal Script
# =============================================================================
# Renews Tailscale HTTPS certificates and reloads nginx.
# Tailscale certs are valid for 90 days; this runs weekly via systemd timer.
#
# Usage: ./renew-certs.sh
# Scheduled via systemd timer (memu-cert-renew.timer) weekly
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

log "Starting TLS certificate renewal..."

# Check if Tailscale container is running
if ! docker ps --filter "name=memu_tailscale" --format '{{.Status}}' | grep -q "Up"; then
    warn "Tailscale container is not running. Skipping cert renewal."
    exit 0
fi

# Get Tailscale FQDN
TS_HOSTNAME=$(docker exec memu_tailscale tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty' | sed 's/\.$//')

if [ -z "$TS_HOSTNAME" ]; then
    warn "Could not determine Tailscale hostname. Skipping cert renewal."
    exit 0
fi

log "Renewing certificate for: ${TS_HOSTNAME}"

# Generate/renew certificate
if docker exec memu_tailscale tailscale cert \
    --cert-file "/certs/${TS_HOSTNAME}.crt" \
    --key-file "/certs/${TS_HOSTNAME}.key" \
    "${TS_HOSTNAME}" 2>&1; then
    log "Certificate renewed successfully."
else
    error "Certificate renewal failed."
    exit 1
fi

# Reload nginx to pick up new certs
if docker ps --filter "name=memu_proxy" --format '{{.Status}}' | grep -q "Up"; then
    docker exec memu_proxy nginx -s reload 2>/dev/null && \
        log "Nginx reloaded with new certificates." || \
        warn "Failed to reload nginx."
else
    warn "Nginx proxy is not running. Certificate saved but not loaded."
fi

log "Certificate renewal complete."
