#!/bin/bash
# Memu OS - System Bootstrapper
# This script installs the systemd services required to run the Web Setup Wizard.
# It does NOT configure the application itself.

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Memu OS - System Installer       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════╝${NC}"
echo ""

# Get the actual user who invoked sudo (not root)
REAL_USER="${SUDO_USER:-$(whoami)}"
REAL_HOME=$(eval echo ~$REAL_USER)
PROJECT_ROOT=$(pwd)

echo "Detected User: $REAL_USER"
echo "Detected Home: $REAL_HOME"
echo "Project Root: $PROJECT_ROOT"
echo ""

# 1. Prerequisites Check
echo -e "${BLUE}[1/3] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker first: curl -sSL https://get.docker.com | sh"
    exit 1
fi
echo -e "${GREEN}✓ Docker is ready${NC}"

# 2. Python Dependencies (for Bootstrap Wizard)
echo -e "\n${BLUE}[2/3] Installing Python dependencies...${NC}"
echo "This may take 1-2 minutes..."

# Install pip and flask
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-requests > /dev/null 2>&1
sudo pip3 install flask --quiet --break-system-packages 2>/dev/null || sudo pip3 install flask --quiet

echo -e "${GREEN}✓ Python dependencies installed${NC}"

# 3. Prepare Directories & Permissions
echo -e "\n${BLUE}[3/3] Configuring system services...${NC}"

# Create necessary directories with correct permissions
mkdir -p ./synapse
mkdir -p ./nginx/conf.d
chown -R $REAL_USER:$REAL_USER ./synapse
chown -R $REAL_USER:$REAL_USER ./nginx
chmod 755 ./synapse

# Update service files with correct paths
echo "Updating service configurations..."

# Create working copies of service files with correct paths
cat > /tmp/memu-setup.service << EOF
[Unit]
Description=Memu OS Setup Wizard
After=network.target

[Service]
User=${REAL_USER}
WorkingDirectory=${PROJECT_ROOT}/bootstrap
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

cat > /tmp/memu-production.service << EOF
[Unit]
Description=Memu OS Main Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
User=${REAL_USER}
WorkingDirectory=${PROJECT_ROOT}
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
EOF

# Copy to systemd directory
sudo cp /tmp/memu-setup.service /etc/systemd/system/
sudo cp /tmp/memu-production.service /etc/systemd/system/

# Clean up temp files
rm /tmp/memu-setup.service /tmp/memu-production.service

sudo systemctl daemon-reload
sudo systemctl enable memu-setup.service

echo ""
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}   System Bootstrap Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo ""
echo "To begin the Setup Wizard, run:"
echo -e "${BLUE}  sudo systemctl start memu-setup.service${NC}"
echo ""
echo "Then open your browser and visit:"
echo -e "${GREEN}  http://$(hostname).local${NC}"
echo ""
echo "Or if .local doesn't work, find your IP with:"
echo -e "${BLUE}  hostname -I${NC}"
echo ""