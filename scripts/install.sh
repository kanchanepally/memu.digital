#!/bin/bash
# =============================================================================
# Memu OS - Revised Installer (v4.0)
# =============================================================================
# 
# This script implements TWO-STAGE BOOT:
#   Stage A: Prepare environment (no containers running)
#   Stage B: Hand off to Setup Wizard (which starts containers in order)
#
# Key insight: We DON'T start docker compose here. The wizard does that
# AFTER it has created all the config files.
# =============================================================================

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Memu OS - The Private Family Cloud                          ║"
echo "║   v4.0 (Two-Stage Boot)                                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# =============================================================================
# STAGE A: Environment Preparation (No Containers Yet)
# =============================================================================

PROJECT_ROOT=$(pwd)
REAL_USER="${SUDO_USER:-$(whoami)}"

echo -e "${YELLOW}[Stage A] Preparing Environment${NC}"

# -----------------------------------------------------------------------------
# A1: Check Prerequisites
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A1] Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Installing...${NC}"
    apt-get update -qq
    apt-get install -y docker.io docker-compose-v2
fi

# Verify Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker daemon not running. Starting...${NC}"
    systemctl start docker
    systemctl enable docker
fi

# -----------------------------------------------------------------------------
# A2: Check Hardware (RAM)
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A2] Checking hardware...${NC}"

TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM_MB" -lt 7500 ]; then
    echo -e "${YELLOW}[!] WARNING: Less than 8GB RAM detected (${TOTAL_RAM_MB}MB).${NC}"
    echo "    AI features may be limited. Recommended: 16GB for full experience."
    sleep 2
fi

# -----------------------------------------------------------------------------
# A3: Setup Swap (Critical for AI Stability)
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A3] Configuring swap...${NC}"

if [ ! -f /swapfile ]; then
    echo "    Creating 8GB swap file..."
    fallocate -l 8G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "    Swap configured."
else
    echo "    Swap already exists."
fi

# -----------------------------------------------------------------------------
# A4: Install Python Dependencies for Wizard
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A4] Installing wizard dependencies...${NC}"

apt-get install -y python3-pip curl -qq

# Install Flask with flags to handle Ubuntu's pre-installed packages
pip install flask requests --break-system-packages --ignore-installed 2>/dev/null || \
pip3 install flask requests --break-system-packages --ignore-installed

# -----------------------------------------------------------------------------
# A5: Create Directory Structure with Correct Permissions
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A5] Creating directory structure...${NC}"

# These directories MUST exist before Docker tries to mount them
mkdir -p synapse
mkdir -p photos
mkdir -p backups
mkdir -p nginx/conf.d

# Synapse needs write access for signing keys and logs
chmod 777 synapse/

# Fix ownership for the real user (not root)
chown -R $REAL_USER:$REAL_USER synapse photos backups nginx

echo "    Directories created with correct permissions."

# -----------------------------------------------------------------------------
# A6: Create Placeholder Config Files
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A6] Creating placeholder configurations...${NC}"

# Element config - MUST exist before Docker tries to mount it
# (Docker will create a directory instead of a file if this doesn't exist)
if [ ! -f element-config.json ]; then
    cat > element-config.json << 'ELEMENT_EOF'
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
ELEMENT_EOF
    echo "    Created element-config.json placeholder"
fi

# Nginx config - placeholder that returns "setup in progress"
cat > nginx/conf.d/default.conf << 'NGINX_EOF'
server {
    listen 80;
    server_name localhost;
    
    location / {
        return 200 'Memu setup in progress. Visit port 8888 to continue.';
        add_header Content-Type text/plain;
    }
}
NGINX_EOF
echo "    Created nginx placeholder config"

# -----------------------------------------------------------------------------
# A7: Create Base .env File
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A7] Creating environment configuration...${NC}"

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)

# Check if .env already exists (preserve Tailscale key if so)
EXISTING_TS_KEY=""
if [ -f .env ]; then
    EXISTING_TS_KEY=$(grep "^TAILSCALE_AUTH_KEY=" .env | cut -d'=' -f2)
fi

cat > .env << ENV_EOF
# ===========================================
# MEMU SUITE - ENVIRONMENT CONFIGURATION
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# ===========================================

# --- GENERAL ---
SERVER_NAME=memu.local
TZ=$(cat /etc/timezone 2>/dev/null || echo "UTC")

# --- DATABASE ---
DB_USER=memu_user
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=immich

# --- PHOTOS ---
UPLOAD_LOCATION=./photos

# --- CHAT ---
SYNAPSE_REPORT_STATS=no

# --- AI ---
AI_ENABLED=true
OLLAMA_MODEL=llama3.2
MACHINE_LEARNING_WORKERS=1
MACHINE_LEARNING_WORKER_TIMEOUT=120

# --- BOT (populated by wizard after user creation) ---
MATRIX_BOT_USERNAME=@memu_bot:memu.local
MATRIX_BOT_TOKEN=

# --- NETWORKING ---
TAILSCALE_AUTH_KEY=${EXISTING_TS_KEY}
ENV_EOF

echo "    Created .env with secure database password"

# -----------------------------------------------------------------------------
# A8: Collect Tailscale Key (if not already set)
# -----------------------------------------------------------------------------
if [ -z "$EXISTING_TS_KEY" ]; then
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo "  REMOTE ACCESS SETUP (Optional)"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  To access Memu from outside your home network, you need Tailscale."
    echo ""
    echo "  1. Go to: https://login.tailscale.com/admin/settings/keys"
    echo "  2. Click 'Generate auth key'"
    echo "  3. Copy the key (starts with 'tskey-auth-...')"
    echo ""
    echo "  Press ENTER to skip (you can add it later in the web wizard)"
    echo ""
    read -p "  Paste Tailscale Auth Key: " TS_KEY
    
    if [ -n "$TS_KEY" ]; then
        sed -i "s|^TAILSCALE_AUTH_KEY=.*|TAILSCALE_AUTH_KEY=$TS_KEY|" .env
        echo "    Tailscale key saved."
    else
        echo "    Skipped. You can add this in the web wizard."
    fi
fi

# -----------------------------------------------------------------------------
# A9: Install Systemd Services
# -----------------------------------------------------------------------------
echo -e "${GREEN}[A9] Installing system services...${NC}"

# Setup Wizard Service (runs on port 8888 to avoid conflict with nginx/80)
cat > /etc/systemd/system/memu-setup.service << WIZARD_EOF
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
Environment=WIZARD_PORT=8888

[Install]
WantedBy=multi-user.target
WIZARD_EOF

# Production Service (will be enabled by wizard after setup completes)
cat > /etc/systemd/system/memu-production.service << PROD_EOF
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
PROD_EOF

systemctl daemon-reload
echo "    Systemd services installed."

# =============================================================================
# STAGE A COMPLETE - Hand Off to Wizard
# =============================================================================

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Stage A Complete - Environment Prepared                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Starting Setup Wizard...${NC}"
echo ""

# Start the wizard
systemctl enable memu-setup.service
systemctl start memu-setup.service

# Wait a moment for it to start
sleep 3

# Get IP addresses for user
LOCAL_IP=$(hostname -I | awk '{print $1}')
HOSTNAME=$(hostname)

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   NEXT STEP: Open the Setup Wizard                            ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  On a device connected to the same network, open:"
echo ""
echo -e "    ${BLUE}http://${LOCAL_IP}:8888${NC}"
echo ""
echo "  Or try:"
echo -e "    ${BLUE}http://${HOSTNAME}.local:8888${NC}"
echo ""
echo "  The wizard will guide you through the rest of the setup."
echo ""
echo -e "${YELLOW}  Note: Do NOT run 'docker compose up' manually.${NC}"
echo -e "${YELLOW}        The wizard handles this in the correct order.${NC}"
echo ""