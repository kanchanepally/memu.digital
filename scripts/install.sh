#!/bin/bash
# =============================================================================
# Memu OS - Silent Installer (v4.1)
# =============================================================================
#
# TESTED: January 18, 2026 on DigitalOcean (8GB Ubuntu 24.04)
# 
# This script is 100% SILENT - no prompts, no user input.
# All configuration happens in the Web Wizard.
#
# FIXES FROM v4.0:
# - Removed all `read -p` prompts (unattended install)
# - Creates placeholder configs BEFORE docker touches them
# - Proper directory permissions for Synapse
# - IDEMPOTENT: Preserves existing passwords/configs if re-run
# =============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[MEMU]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Memu OS - The Private Family Cloud                          ║"
echo "║   v4.1 (Silent Install)                                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

PROJECT_ROOT=$(pwd)
REAL_USER="${SUDO_USER:-$(whoami)}"
WIZARD_PORT=8888

log "Starting silent installation..."

# -----------------------------------------------------------------------------
# A1: Install System Dependencies
# -----------------------------------------------------------------------------
log "Installing system dependencies..."

apt-get update -qq
apt-get install -y -qq docker.io docker-compose-v2 curl python3-pip jq > /dev/null 2>&1

systemctl start docker 2>/dev/null || true
systemctl enable docker 2>/dev/null || true

pip install flask requests --break-system-packages --ignore-installed -q 2>/dev/null || \
pip3 install flask requests --break-system-packages --ignore-installed -q 2>/dev/null || true

# -----------------------------------------------------------------------------
# A2: Check Hardware
# -----------------------------------------------------------------------------
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM_MB" -lt 7500 ]; then
    warn "Less than 8GB RAM detected (${TOTAL_RAM_MB}MB). AI features may be limited."
fi

# -----------------------------------------------------------------------------
# A3: Setup Swap
# -----------------------------------------------------------------------------
if [ ! -f /swapfile ]; then
    log "Creating swap file..."
    fallocate -l 8G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1M count=8192 status=none
    chmod 600 /swapfile
    mkswap /swapfile > /dev/null
    swapon /swapfile
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# -----------------------------------------------------------------------------
# A4: Create Directory Structure
# -----------------------------------------------------------------------------
log "Creating directory structure..."

mkdir -p synapse photos backups nginx/conf.d bootstrap/templates
chmod 777 synapse/
chown -R $REAL_USER:$REAL_USER synapse photos backups nginx 2>/dev/null || true

# -----------------------------------------------------------------------------
# A5: Create Placeholder Config Files (CRITICAL)
# -----------------------------------------------------------------------------
log "Checking configuration files..."

# Element config - Only create if missing (don't overwrite working config)
if [ ! -f element-config.json ]; then
    cat > element-config.json << 'EOF'
{
    "default_server_config": {
        "m.homeserver": {
            "base_url": "http://localhost:8008",
            "server_name": "memu.local"
        }
    },
    "brand": "Memu",
    "default_theme": "light"
}
EOF
    log "Created placeholder element-config.json"
fi

# Nginx placeholder - Only create if missing
if [ ! -f nginx/conf.d/default.conf ]; then
    cat > nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name localhost;
    location / {
        return 200 'Memu setup in progress. Visit port 8888 to continue.';
        add_header Content-Type text/plain;
    }
}
EOF
    log "Created placeholder nginx config"
fi

# Synapse log config (Always safe to ensure)
cat > synapse/memu.local.log.config << 'EOF'
version: 1
formatters:
  precise:
    format: '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(request)s - %(message)s'
handlers:
  console:
    class: logging.StreamHandler
    formatter: precise
root:
    level: INFO
    handlers: [console]
disable_existing_loggers: false
EOF

# -----------------------------------------------------------------------------
# A6: Create or Update .env (PRESERVE SECRETS)
# -----------------------------------------------------------------------------
log "Configuring environment..."

# Initialize defaults
DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)
EXISTING_TS_KEY=""
EXISTING_BOT_TOKEN=""

# Read existing values if .env exists
if [ -f .env ]; then
    EXISTING_DB_PASS=$(grep "^DB_PASSWORD=" .env 2>/dev/null | cut -d'=' -f2)
    [ -n "$EXISTING_DB_PASS" ] && DB_PASSWORD=$EXISTING_DB_PASS
    
    EXISTING_TS_KEY=$(grep "^TAILSCALE_AUTH_KEY=" .env 2>/dev/null | cut -d'=' -f2)
    EXISTING_BOT_TOKEN=$(grep "^MATRIX_BOT_TOKEN=" .env 2>/dev/null | cut -d'=' -f2)
    log "Preserved existing credentials from .env"
fi

cat > .env << EOF
# Memu Configuration (v4.1)
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

SERVER_NAME=memu.local
TZ=$(cat /etc/timezone 2>/dev/null || echo "UTC")

DB_USER=memu_user
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=immich

UPLOAD_LOCATION=./photos
SYNAPSE_REPORT_STATS=no

AI_ENABLED=true
OLLAMA_MODEL=llama3.2
MACHINE_LEARNING_WORKERS=1
MACHINE_LEARNING_WORKER_TIMEOUT=120

MATRIX_BOT_USERNAME=@memu_bot:memu.local
MATRIX_BOT_TOKEN=${EXISTING_BOT_TOKEN}

TAILSCALE_AUTH_KEY=${EXISTING_TS_KEY}
EOF

# -----------------------------------------------------------------------------
# A7: Install Systemd Services
# -----------------------------------------------------------------------------
log "Installing system services..."

cat > /etc/systemd/system/memu-setup.service << EOF
[Unit]
Description=Memu OS Setup Wizard
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_ROOT}/bootstrap
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=WIZARD_PORT=${WIZARD_PORT}
Environment=PROJECT_ROOT=${PROJECT_ROOT}

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/memu-production.service << EOF
[Unit]
Description=Memu OS Production Stack
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${PROJECT_ROOT}
ExecStart=/usr/bin/docker compose -f docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.yml down

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

# -----------------------------------------------------------------------------
# START WIZARD
# -----------------------------------------------------------------------------
log "Starting Setup Wizard..."

systemctl enable memu-setup.service
systemctl start memu-setup.service

sleep 3

LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Installation Complete - Open the Setup Wizard               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  On a device connected to the same network, open:"
echo ""
echo -e "    ${BLUE}http://${LOCAL_IP}:${WIZARD_PORT}${NC}"
echo ""
echo "  Or try: http://${HOSTNAME}.local:${WIZARD_PORT}"
echo ""
echo -e "  ${YELLOW}The wizard will guide you through the rest.${NC}"
echo ""