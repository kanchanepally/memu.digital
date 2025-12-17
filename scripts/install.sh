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

# 1. Prerequisites Check
echo -e "${BLUE}[1/2] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed.${NC}"
    echo "Please install Docker first: curl -sSL https://get.docker.com | sh"
    exit 1
fi
echo -e "${GREEN}✓ Docker is ready${NC}"

# 2. Systemd Service Setup
echo -e "\n${BLUE}[2/2] Configuring system services...${NC}"

# Get absolute path to project root
PROJECT_ROOT=$(pwd)
USER_NAME=$(whoami)

echo "Detected Project Root: $PROJECT_ROOT"
echo "Detected User: $USER_NAME"

# Update service files with correct paths
# We use a temp file or direct sed on the source files before copying
sed -i "s|WorkingDirectory=.*|WorkingDirectory=${PROJECT_ROOT}/bootstrap|g" systemd/memu-setup.service
sed -i "s|User=.*|User=${USER_NAME}|g" systemd/memu-setup.service

sed -i "s|WorkingDirectory=.*|WorkingDirectory=${PROJECT_ROOT}|g" systemd/memu-production.service
sed -i "s|User=.*|User=${USER_NAME}|g" systemd/memu-production.service

# Copy to systemd directory
echo "Installing services (requires sudo)..."
sudo cp systemd/memu-setup.service /etc/systemd/system/
sudo cp systemd/memu-production.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable memu-setup.service

echo ""
echo -e "${GREEN}System Bootstrap Complete!${NC}"
echo "------------------------------------------------"
echo "To begin the Setup Wizard, run:"
echo -e "${BLUE}  sudo systemctl start memu-setup.service${NC}"
echo ""
echo "Then open your browser and visit:"
echo -e "${GREEN}  http://$(hostname).local${NC}"
echo "------------------------------------------------"