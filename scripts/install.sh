#!/bin/bash
# =============================================================================
# Memu OS - Universal Installer (v3.1 x86)
# =============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Memu OS - The Private Family Cloud                          ║"
echo "║   v3.1 (Certified for Intel N100)                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect Real User (for permissions)
REAL_USER="${SUDO_USER:-$(whoami)}"
PROJECT_ROOT=$(pwd)

# 1. Check Hardware (RAM)
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
if [ "$TOTAL_RAM_MB" -lt 7500 ]; then
    echo -e "${RED}[!] WARNING: Less than 8GB RAM detected.${NC}"
    echo "    Memu requires 8GB+ for AI features."
    sleep 3
fi

# 2. Setup Swap (Critical for AI Stability)
if [ ! -f /swapfile ]; then
    echo -e "${GREEN}[+] Creating 8GB Swap File...${NC}"
    fallocate -l 8G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# 3. Install Dependencies
echo -e "${GREEN}[+] Installing System Dependencies...${NC}"
apt-get update -qq
apt-get install -y docker.io docker-compose-v2 curl python3-pip

# 4. Prepare Directories (Fix Permissions)
# Prevents Docker from creating these as 'root'
echo -e "${GREEN}[+] Configuring Permissions...${NC}"
mkdir -p synapse photos backups nginx/conf.d
chown -R $REAL_USER:$REAL_USER synapse photos backups nginx

# 5. Generate Setup Wizard Service
cat > /etc/systemd/system/memu-setup.service << EOF
[Unit]
Description=Memu OS Setup Wizard
After=network.target docker.service

[Service]
Type=simple
User=root
WorkingDirectory=${PROJECT_ROOT}/bootstrap
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload

# 6. Configuration & Network
if [ ! -f .env ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo "  NETWORK CONFIGURATION"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo "  1. Go to: [https://login.tailscale.com/admin/settings/keys](https://login.tailscale.com/admin/settings/keys)"
    echo "  2. Generate an 'Auth Key'"
    echo ""
    read -p "  Paste Auth Key: " TS_KEY
    
    # Copy template and fill key
    if [ -f .env.example ]; then
        cp .env.example .env
        sed -i "s|TAILSCALE_AUTH_KEY=.*|TAILSCALE_AUTH_KEY=$TS_KEY|" .env
    else
        echo "TAILSCALE_AUTH_KEY=$TS_KEY" > .env
    fi
fi

# 7. Launch
echo -e "${GREEN}[+] Booting Memu OS...${NC}"
docker compose up -d

echo ""
echo -e "${GREEN}SUCCESS!${NC}"
echo "Dashboard: http://$(hostname -I | awk '{print $1}')"